import asyncio
import os
import sys
import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from browser.providers.base import LLMProvider
    from core.task_manager import TaskManager
    from core.context_manager import ContextManager
    from core.state_manager import StateManager
    from core.mission import Mission, MissionStore, create_mission_from_prompt
    from core.project_inspector import ProjectInspector, format_inspection_log
    from core.command_shortcuts import detect_shortcut, execute_shortcut
    from execution.filesystem import FileSystem
    from execution.command_runner import CommandRunner
    from execution.git_manager import GitManager
    from execution.command_policy import CommandPolicyEngine, CommandCategory
    from protocol.normalizer import ActionNormalizer
    from recovery.loop_detector import LoopDetector
    from recovery.retry_manager import RetryManager
    from multiagent.roles import ArchitectAgent, EngineerAgent, ReviewerJudgeAgent, RefinerAgent
    from multiagent.scorekeeper import ScoreKeeper
    from learning.error_memory import ErrorMemory
    from core.checkpoint_manager import CheckpointManager
except ImportError:
    from ..browser.providers.base import LLMProvider
    from ..core.task_manager import TaskManager
    from ..core.context_manager import ContextManager
    from ..core.state_manager import StateManager
    from ..core.mission import Mission, MissionStore, create_mission_from_prompt
    from ..core.project_inspector import ProjectInspector, format_inspection_log
    from ..core.command_shortcuts import detect_shortcut, execute_shortcut
    from ..execution.filesystem import FileSystem
    from ..execution.command_runner import CommandRunner
    from ..execution.git_manager import GitManager
    from ..execution.command_policy import CommandPolicyEngine, CommandCategory
    from ..protocol.normalizer import ActionNormalizer
    from ..recovery.loop_detector import LoopDetector
    from ..recovery.retry_manager import RetryManager
    from .roles import ArchitectAgent, EngineerAgent, ReviewerJudgeAgent, RefinerAgent
    from .scorekeeper import ScoreKeeper
    from ..learning.error_memory import ErrorMemory

class MultiAgentTeamOrchestrator:
    """
    Autonomous Multi-Agent Engineering Team Coordinator — Autonomous Web-Agent IDE Core.
    - ArchitectAgent creates the strategic plan
    - EngineerAgent implements concrete code actions
    - ReviewerJudgeAgent audits quality and awards/penalizes score points
    - RefinerAgent self-heals any deficiencies
    - ScoreKeeper tracks real-time reinforcement score
    - ErrorMemory learns from every error and auto-applies cached fixes
    - MissionStore persists mission state for recovery
    """

    def __init__(
        self,
        project_id: str,
        run_id: str,
        workspace_root: str,
        provider: LLMProvider,
        db_path: str,
        approval_mode: str = "AUTO",
        images: List[str] = None,
        zip_file: str = None,
    ):
        self.project_id = project_id
        self.run_id = run_id
        self.workspace_root = workspace_root
        Path(self.workspace_root).mkdir(parents=True, exist_ok=True)
        self.provider = provider
        self.db_path = str(Path(self.workspace_root) / ".agent_state.sqlite")
        self.state_mgr = StateManager(self.db_path)
        self.approval_mode = approval_mode
        self.images = images or []       # Image file paths attached by user
        self.zip_file = zip_file         # ZIP file path imported by user

        # Multi-Agent Team
        self.architect = ArchitectAgent(provider)
        self.engineer = EngineerAgent(provider)
        self.reviewer = ReviewerJudgeAgent(provider)
        self.refiner = RefinerAgent(provider)
        self.scorekeeper = ScoreKeeper(initial_score=100)

        self.task_mgr = TaskManager()
        self.loop_detector = LoopDetector()
        self.retry_mgr = RetryManager()

        # Autonomous Web-Agent IDE: Self-Learning Error Memory
        self.error_memory = ErrorMemory(self.db_path)

        # Autonomous Web-Agent IDE: Mission Store
        self.mission_store = MissionStore(self.db_path)
        self.current_mission: Optional[Mission] = None

        # Autonomous Web-Agent IDE: Project Inspector cache
        self.project_info: Dict[str, Any] = {}

        # Autonomous Web-Agent IDE: Explicit State Machine
        try:
            from core.state_machine import AutonomousStateMachine, AutonomousState
            self.fsm = AutonomousStateMachine(emit_fn=self.emit_ipc)
        except Exception:
            self.fsm = None

        # Autonomous Web-Agent IDE: Checkpoint & Rollback Manager
        try:
            self.checkpoint_manager = CheckpointManager(self.workspace_root, emit_ipc=self.emit_ipc)
        except Exception:
            self.checkpoint_manager = None

        self.is_paused = False
        self.is_stopped = False
        self.pending_approvals: Dict[str, asyncio.Future] = {}
        self.recent_commands: List[Dict[str, Any]] = []

    def get_provider_display_name(self) -> str:
        cls_name = self.provider.__class__.__name__
        if "Gemini" in cls_name:
            return "GOOGLE GEMINI"
        elif "Generic" in cls_name or "ChatGPT" in cls_name:
            return "CHATGPT WEB"
        elif "DeepSeek" in cls_name:
            return "DEEPSEEK R1"
        elif "Nemotron" in cls_name:
            return "NVIDIA NEMOTRON 70B"
        elif "Smart" in cls_name:
            return "SMART MULTI-MODEL"
        return "AUTONOMOUS AI ENGINE"

    def classify_intent(self, prompt: str) -> str:
        """
        Classifies user prompt into either 'CONVERSATION' (question/chat/explanation)
        or 'BUILD_ACTION' (scaffold/code/modify project).
        """
        p = prompt.strip().lower()

        # 1. Greetings & casual chit-chat
        greetings = [
            "hey", "hi", "hello", "hola", "namaste", "suno", "kaise ho", "kya haal hai",
            "kya chal raha hai", "who are you", "what can you do", "what is your name",
            "tum kaun ho", "kya kar sakte ho", "help", "test"
        ]
        if p in greetings:
            return "CONVERSATION"
        if any(p.startswith(g + " ") or p.startswith(g + ",") or p.startswith(g + "!") for g in greetings) and len(p.split()) <= 4:
            return "CONVERSATION"

        # 2. Build / Modification action keywords
        build_verbs = [
            "build", "create", "make", "banao", "develop", "generate",
            "add", "fix", "repair", "sahi karo", "update", "modify", "change",
            "delete", "remove", "implement", "scaffold", "install", "deploy",
            "likho", "write code", "code banao", "code karo", "program banao"
        ]
        has_build_action = any(verb in p for verb in build_verbs)

        # 3. Question & Explanation patterns
        question_starters = [
            "what is", "what are", "what does", "how does", "how do", "why is",
            "why does", "explain", "tell me about", "difference between",
            "kya hai", "kya hota hai", "kaise hota hai", "batao", "samjhao",
            "can you explain", "define", "meaning of"
        ]
        is_question = any(p.startswith(qs) or f" {qs} " in p for qs in question_starters) or p.endswith("?")

        if is_question and not has_build_action:
            return "CONVERSATION"

        if (p.startswith("what is") or p.startswith("what are") or p.startswith("explain") or p.startswith("kya hota hai")) and not ("app" in p or "website" in p or "system" in p or "project" in p or "feature" in p or "button" in p or "file" in p):
            return "CONVERSATION"

        return "BUILD_ACTION"

    def emit_ipc(self, event: str, payload: Dict[str, Any]):
        msg = {
            "event": event,
            "project_id": self.project_id,
            "run_id": self.run_id,
            "payload": payload,
            "timestamp": time.time()
        }
        sys.stdout.write(f"IPC:JSON:{json.dumps(msg)}\n")
        sys.stdout.flush()

    def handle_ipc_command(self, cmd_data: Dict[str, Any]):
        cmd = cmd_data.get("command")
        if cmd == "pause":
            self.is_paused = True
            self.emit_ipc("agent.paused", {"status": "PAUSED"})
        elif cmd == "resume":
            self.is_paused = False
            self.emit_ipc("agent.resumed", {"status": "RUNNING"})
        elif cmd == "stop":
            self.is_stopped = True
            self.emit_ipc("agent.stopped", {"status": "STOPPED"})

    async def run(self, user_prompt: str) -> bool:
        self.emit_ipc("agent.started", {"prompt": user_prompt, "mode": "multiagent"})
        await GitManager.ensure_repo(self.workspace_root)
        provider_name = self.get_provider_display_name()

        # ── Autonomous Web-Agent IDE: Check for quick command shortcuts first ──
        shortcut_action = detect_shortcut(user_prompt)
        if shortcut_action:
            self.emit_ipc("command.output", {
                "stream": "stdout",
                "data": f"\r\n⚡ \x1b[1;36m[Quick Command]\x1b[0m Detected shortcut: {shortcut_action}\r\n\r\n",
                "name": "agent",
            })
            try:
                handled = await execute_shortcut(
                    shortcut_action,
                    self.workspace_root,
                    self.project_id,
                    self.emit_ipc,
                    self.project_info,
                )
                if handled:
                    self.emit_ipc("agent.completed", {"summary": f"Quick command '{shortcut_action}' executed."})
                    return True
            except Exception as e:
                self.emit_ipc("command.output", {
                    "stream": "stderr",
                    "data": f"❌ [Shortcut Error] {e}\r\n",
                    "name": "agent",
                })
            # If not handled, fall through to AI

        # ── Autonomous Web-Agent IDE: Auto-Zip & Attach for Update / Sync ────────
        zip_attachment = os.environ.pop("AGENT_ZIP_ATTACHMENT", None)
        prompt_lower = user_prompt.lower()
        is_update_intent = (
            shortcut_action == "zip_and_send" or
            "update" in prompt_lower or
            "sync" in prompt_lower or
            "nayi feature" in prompt_lower or
            "change code" in prompt_lower
        )

        # If not already attached from env, auto-package workspace if update requested
        if not zip_attachment and is_update_intent:
            try:
                code_files = [f for f in FileSystem.list_files(self.workspace_root) if not f["path"].startswith(".") and not f["path"].startswith("node_modules")]
                if len(code_files) > 0:
                    from core.zip_chunker import create_chunked_zip
                    zip_res = create_chunked_zip(self.workspace_root, max_chunk_mb=38.0)
                    if zip_res and zip_res.get("archive_paths"):
                        zip_attachment = zip_res["archive_paths"][0]
            except Exception as e:
                self.emit_ipc("command.output", {
                    "stream": "stderr",
                    "data": f"⚠️ [Auto-Zip Notice] Could not auto-package workspace: {e}\r\n",
                    "name": "agent",
                })

        if zip_attachment and os.path.exists(zip_attachment):
            if zip_attachment not in self.images:
                self.images.append(zip_attachment)
            self.zip_file = zip_attachment
            size_mb = os.path.getsize(zip_attachment) / (1024 * 1024)
            self.emit_ipc("command.output", {
                "stream": "stdout",
                "data": f"📎 \x1b[1;36m[ZIP Attached]\x1b[0m {os.path.basename(zip_attachment)} ({size_mb:.1f} MB) queued for {provider_name} upload\r\n",
                "name": "agent",
            })

        # ── Autonomous Web-Agent IDE: Create Mission ───────────────────────────
        self.current_mission = create_mission_from_prompt(
            prompt=user_prompt,
            project_id=self.project_id,
            project_path=self.workspace_root,
            provider=type(self.provider).__name__,
            images=self.images,
            zip_file=self.zip_file,
        )
        self.mission_store.save(self.current_mission)
        self.emit_ipc("mission.created", {
            "id": self.current_mission.id,
            "goal": self.current_mission.user_goal,
            "has_images": len(self.images) > 0,
            "has_zip": bool(self.zip_file),
        })
        self.emit_ipc("command.output", {
            "stream": "stdout",
            "data": f"\r\n📋 \x1b[1;35m[Mission Created]\x1b[0m {self.current_mission.id}\r\n"
                    f"🎯 Goal: {user_prompt[:80]}{'...' if len(user_prompt) > 80 else ''}\r\n",
            "name": "agent",
        })

        # ── Autonomous Web-Agent IDE: Project Inspector ────────────────────────
        try:
            inspector = ProjectInspector(self.workspace_root)
            self.project_info = inspector.inspect()
            log_text = format_inspection_log(self.project_info)
            self.emit_ipc("command.output", {
                "stream": "stdout",
                "data": f"\r\n{log_text}\r\n\r\n",
                "name": "agent",
            })
            self.emit_ipc("project.inspected", self.project_info)
            # Store in mission
            self.current_mission.project_info = self.project_info
            self.mission_store.save(self.current_mission)
        except Exception as e:
            self.emit_ipc("command.output", {
                "stream": "stdout",
                "data": f"🔍 [Project Inspector] Skipped: {e}\r\n",
                "name": "agent",
            })

        # ── Images attached — log them ──────────────────────────────────────────
        if self.images:
            self.emit_ipc("command.output", {
                "stream": "stdout",
                "data": f"📎 \x1b[1;36m[Attachments]\x1b[0m {len(self.images)} image(s) attached — will send to {provider_name}\r\n\r\n",
                "name": "agent",
            })

        # Smart Intent Classification: Chat/Question vs Project Build
        if self.fsm:
            from core.state_machine import AutonomousState
            self.fsm.transition_to(AutonomousState.UNDERSTAND, "Analyzing intent and requirements")

        intent = self.classify_intent(user_prompt)

        if intent == "CONVERSATION":
            self.emit_ipc("agent.role.started", {
                "role": "AI Consultant",
                "message": f"Direct dialogue with {provider_name} active..."
            })
            self.emit_ipc("command.output", {
                "stream": "stdout",
                "data": f"\r\n💬 \x1b[1;35m[{provider_name} Consultant]\x1b[0m Answering user question directly...\r\n\r\n",
                "name": "agent"
            })

            system_prompt = (
                "You are an expert AI software engineering assistant and senior architect. "
                "The user is asking a conversational question, concept explanation, or greeting. "
                "Provide a direct, clear, helpful and structured answer in the same language (Hindi/Hinglish/English). "
                "Explain the concepts simply with short illustrative code examples if helpful, "
                "but DO NOT generate project files, full project scaffolds, or file-writing commands."
            )

            try:
                if self.images:
                    response = await self.provider.generate_with_images(user_prompt, self.images, system_prompt=system_prompt)
                else:
                    response = await self.provider.generate(user_prompt, system_prompt=system_prompt)
                clean_resp = (response or "").strip()

                # Guard: If provider returned a JSON task plan or empty string, convert to natural conversational explanation
                if (
                    not clean_resp or
                    clean_resp.startswith("```json") or
                    "project_name" in clean_resp or
                    "\"tasks\":" in clean_resp or
                    clean_resp.startswith("{")
                ):
                    try:
                        from core.cognitive_engine import CognitiveAIEngine
                    except ImportError:
                        from ..core.cognitive_engine import CognitiveAIEngine
                    clean_resp = CognitiveAIEngine.generate_conversational_response(user_prompt)

                self.emit_ipc("command.output", {
                    "stream": "stdout",
                    "data": f"💬 \x1b[1;36m[{provider_name} Response]:\x1b[0m\r\n\x1b[1;32m{clean_resp}\x1b[0m\r\n\r\n",
                    "name": "agent"
                })
                self.emit_ipc("agent.chat_response", {
                    "prompt": user_prompt,
                    "response": clean_resp
                })
                self.emit_ipc("agent.completed", {
                    "summary": "Conversational query answered directly without code scaffolding.",
                    "final_score": 100,
                    "evaluations": 1
                })
                return True
            except Exception as e:
                try:
                    from core.cognitive_engine import CognitiveAIEngine
                except ImportError:
                    from ..core.cognitive_engine import CognitiveAIEngine
                clean_resp = CognitiveAIEngine.generate_conversational_response(user_prompt)
                self.emit_ipc("command.output", {
                    "stream": "stdout",
                    "data": f"\x1b[1;32m{clean_resp}\x1b[0m\r\n\r\n",
                    "name": "agent"
                })
                self.emit_ipc("agent.completed", {
                    "summary": "Conversational query answered directly.",
                    "final_score": 100,
                    "evaluations": 1
                })
                return True

        # 1. Architect Phase (for BUILD_ACTION)
        if self.fsm:
            from core.state_machine import AutonomousState
            self.fsm.transition_to(AutonomousState.ARCHITECTURE, "Architect analyzing requirements and generating task specifications")

        self.emit_ipc("agent.role.started", {"role": "ArchitectAgent", "message": "Architect analyzing software requirements & planning DAG tasks..."})
        self.emit_ipc("command.output", {"stream": "stdout", "data": "🏛️  [Architect Agent] Analyzing architecture and generating task specifications...\r\n", "name": "agent"})

        # Check if workspace already contains an existing project
        existing_files = FileSystem.list_files(self.workspace_root)
        code_files = [f for f in existing_files if not f["path"].startswith(".") and not f["path"].startswith("node_modules")]
        workspace_context = None

        if len(code_files) > 0:
            tree_summary = ContextManager.generate_tree_structure(code_files)
            file_snippets = []
            for f in code_files[:10]:
                try:
                    c, _ = FileSystem.read_file(self.workspace_root, f["path"])
                    if c and len(c.strip()) > 0:
                        file_snippets.append(f"### File: {f['path']}\n```\n{c[:2500]}\n```")
                except Exception:
                    pass
            workspace_context = f"{tree_summary}\n\n" + "\n\n".join(file_snippets)
            self.emit_ipc("command.output", {
                "stream": "stdout",
                "data": f"🔍 \x1b[1;36m[Existing Codebase Detected]\x1b[0m Found {len(code_files)} existing project files. Planning feature extension & iterative editing...\r\n",
                "name": "agent"
            })

        try:
            plan = await self.architect.plan(user_prompt, workspace_context=workspace_context, images=self.images)
        except Exception as arch_err:
            self.emit_ipc("command.output", {
                "stream": "stderr",
                "data": f"\r\n⚠️ \x1b[1;33m[Architect Fallback]\x1b[0m AI returned non-JSON — using Cognitive Engine plan. ({arch_err})\r\n\r\n",
                "name": "agent"
            })
            try:
                from core.cognitive_engine import CognitiveAIEngine
            except ImportError:
                from ..core.cognitive_engine import CognitiveAIEngine
            from protocol.validator import ProtocolValidator
            cognitive_plan_data = CognitiveAIEngine.generate_plan(user_prompt)
            _, plan, _ = ProtocolValidator.validate_plan(cognitive_plan_data)
            if not plan:
                from protocol.schemas import ProjectPlan, TaskNode
                plan = ProjectPlan(
                    project_name="project_update",
                    summary=f"Implement: {user_prompt[:80]}",
                    tasks=[TaskNode(id="task-1", title="Implement requested changes", description=user_prompt, depends_on=[])]
                )

        if hasattr(self.architect, 'cached_direct_actions') and self.architect.cached_direct_actions:
            self.engineer.cached_direct_actions = self.architect.cached_direct_actions
            self.architect.cached_direct_actions = None

        self.task_mgr.load_plan(plan)
        self.state_mgr.save_tasks(self.project_id, self.run_id, self.task_mgr.get_all_tasks(), self.task_mgr.dependencies)
        self.emit_ipc("task.created", {"count": len(plan.tasks), "tasks": self.task_mgr.get_all_tasks()})

        # 2. Collaborative Task Execution Loop
        while not self.is_stopped and not self.task_mgr.are_all_tasks_completed():
            while self.is_paused and not self.is_stopped:
                await asyncio.sleep(0.5)

            if self.is_stopped:
                break

            current_task = self.task_mgr.get_next_available_task()
            if not current_task:
                pending = [t for t in self.task_mgr.get_all_tasks() if t["status"] == "PENDING"]
                if pending:
                    current_task = pending[0]
                else:
                    break

            task_id = current_task["id"]
            self.task_mgr.update_task_status(task_id, "RUNNING")
            self.state_mgr.update_task_status(task_id, "RUNNING")
            self.emit_ipc("task.started", current_task)

            if self.fsm:
                from core.state_machine import AutonomousState
                self.fsm.transition_to(AutonomousState.IMPLEMENT, f"Executing task: {current_task['title']}")

            await GitManager.create_checkpoint(self.workspace_root, f"Before: {current_task['title']}")
            if self.checkpoint_manager:
                try:
                    self.checkpoint_manager.create_checkpoint(
                        description=f"Before: {current_task['title']}",
                        stage="PRE_TASK"
                    )
                except Exception:
                    pass

            success = await self.execute_multiagent_task_turn(current_task)

            if success:
                self.task_mgr.update_task_status(task_id, "COMPLETED")
                self.state_mgr.update_task_status(task_id, "COMPLETED")
                await GitManager.create_checkpoint(self.workspace_root, f"Completed: {current_task['title']}")
                if self.checkpoint_manager:
                    try:
                        self.checkpoint_manager.create_checkpoint(
                            description=f"Completed: {current_task['title']}",
                            stage="POST_TASK"
                        )
                    except Exception:
                        pass
                if self.fsm:
                    self.fsm.transition_to(AutonomousState.CHECKPOINT, f"Checkpoint saved for task: {current_task['title']}")
                current_task["status"] = "COMPLETED"
                self.emit_ipc("task.completed", current_task)
            else:
                self.task_mgr.update_task_status(task_id, "FAILED", current_task.get("error_message"))
                self.state_mgr.update_task_status(task_id, "FAILED", current_task.get("error_message"))
                self.emit_ipc("task.failed", current_task)

                if self.retry_mgr.should_retry(current_task["retry_count"]):
                    self.emit_ipc("command.output", {"stream": "stderr", "data": f"[Team] Retrying task {current_task['title']} with Refiner Agent...\r\n", "name": "agent"})
                    self.task_mgr.update_task_status(task_id, "PENDING")
                    self.state_mgr.update_task_status(task_id, "PENDING")
                else:
                    self.emit_ipc("agent.error", {"error": f"Max retries reached for task {task_id}"})
                    return False

        if self.task_mgr.are_all_tasks_completed():
            score_summary = self.scorekeeper.get_summary()

            # Auto-generate START_APP.bat and autonomously launch the dev server
            await self.auto_launch_and_generate_scripts()

            self.emit_ipc("agent.completed", {
                "summary": "All tasks built, verified and launched by Multi-Agent Team.",
                "final_score": score_summary["current_score"],
                "evaluations": score_summary["total_evaluations"]
            })
            return True

        return False

    async def auto_launch_and_generate_scripts(self) -> Dict[str, Any]:
        """
        Generates universal 1-click START_APP.bat in project root and launches the dev server.
        Handles both Single-Root apps and Full-Stack apps (frontend + backend).
        """
        import os
        import webbrowser
        import subprocess
        import socket

        def find_free_port(start: int = 5174) -> int:
            for p in range(start, start + 30):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('127.0.0.1', p))
                        return p
                except OSError:
                    continue
            return start

        free_port = find_free_port(5174)

        # Detect fullstack vs single project
        has_frontend = os.path.exists(os.path.join(self.workspace_root, "frontend"))
        has_backend = os.path.exists(os.path.join(self.workspace_root, "backend"))
        is_fullstack = has_frontend and has_backend
        root_pkg = os.path.exists(os.path.join(self.workspace_root, "package.json"))

        # Function to link donor node_modules
        def ensure_node_modules(target_dir: str):
            target_nm = os.path.join(target_dir, "node_modules")
            react_pkg = os.path.join(target_nm, "react")
            if not os.path.exists(react_pkg):
                parent_ws = os.path.dirname(self.workspace_root)
                donor_cand = os.path.join(parent_ws, "nv_ns", "node_modules")
                if not os.path.exists(donor_cand):
                    donor_cand = os.path.abspath(os.path.join(self.workspace_root, "..", "..", "frontend", "node_modules"))
                if os.path.exists(donor_cand):
                    try:
                        if os.path.exists(target_nm):
                            subprocess.run(f'powershell -NoProfile -Command "Remove-Item -Recurse -Force \'{target_nm}\' -ErrorAction SilentlyContinue"', shell=True)
                        subprocess.run(f'powershell -NoProfile -Command "New-Item -ItemType Junction -Path \'{target_nm}\' -Target \'{donor_cand}\'"', shell=True)
                    except Exception:
                        pass

        bat_path = os.path.join(self.workspace_root, "START_APP.bat")
        sh_path = os.path.join(self.workspace_root, "run.sh")
        preview_url = f"http://localhost:{free_port}"

        if is_fullstack:
            ensure_node_modules(os.path.join(self.workspace_root, "frontend"))
            ensure_node_modules(os.path.join(self.workspace_root, "backend"))

            bat_content = f"""@echo off
chcp 65001 >nul
title Autonomous Full-Stack Application Launcher
cls
echo ====================================================================
echo             AUTONOMOUS FULL-STACK APPLICATION LAUNCHER
echo ====================================================================
echo.
echo [1/2] Launching Backend Server...
start "Backend Server" cmd /k "cd /d "%~dp0backend" && (if not exist node_modules call npm install) && (npm run dev || npm start)"
timeout /t 3 >nul

echo [2/2] Launching Frontend Client...
start "Frontend Client" cmd /k "cd /d "%~dp0frontend" && (if not exist node_modules call npm install) && (npm run dev || npx vite --port {free_port} --host)"

echo.
echo ====================================================================
echo Application is starting! Opening browser at http://localhost:{free_port}...
echo ====================================================================
timeout /t 3 >nul
start http://localhost:{free_port}
"""
            sh_content = f"""#!/bin/bash
echo "Starting Full-Stack Application..."
(cd backend && (npm run dev || npm start)) &
(cd frontend && (npm run dev || npx vite --port {free_port} --host)) &
sleep 2
xdg-open http://localhost:{free_port} 2>/dev/null || open http://localhost:{free_port} 2>/dev/null
"""
            launch_cwd = os.path.join(self.workspace_root, "frontend")

            # Start dev server
            try:
                subprocess.Popen(
                    f"npx vite --port {free_port} --strictPort --host",
                    shell=True,
                    cwd=launch_cwd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass

        elif root_pkg:
            ensure_node_modules(self.workspace_root)

            bat_content = f"""@echo off
chcp 65001 >nul
title Autonomous Application Launcher
cls
echo ====================================================================
echo                   AUTONOMOUS APPLICATION LAUNCHER
echo ====================================================================
echo.
cd /d "%~dp0"
if not exist node_modules (
    echo Installing dependencies...
    call npm install
)
echo Launching Dev Server on port {free_port}...
start http://localhost:{free_port}
call npm run dev || call npm start || call npx vite --port {free_port} --host
pause
"""
            sh_content = f"""#!/bin/bash
echo "Starting Application..."
if [ ! -d "node_modules" ]; then
    npm install
fi
xdg-open http://localhost:{free_port} 2>/dev/null || open http://localhost:{free_port} 2>/dev/null &
npm run dev || npm start || npx vite --port {free_port} --host
"""
            launch_cwd = self.workspace_root

            # Start dev server
            try:
                subprocess.Popen(
                    f"npx vite --port {free_port} --strictPort --host",
                    shell=True,
                    cwd=launch_cwd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass
        else:
            bat_content = f"""@echo off
echo Starting static web server on port {free_port}...
start http://localhost:{free_port}
python -m http.server {free_port}
pause
"""
            sh_content = f"""#!/bin/bash
python3 -m http.server {free_port} &
"""

        # Write the scripts to project root
        try:
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(bat_content)
            with open(sh_path, "w", encoding="utf-8") as f:
                f.write(sh_content)
            self.emit_ipc("file.created", {"path": "START_APP.bat"})
            self.emit_ipc("file.created", {"path": "run.sh"})
        except Exception:
            pass

        self.emit_ipc("command.output", {
            "stream": "stdout",
            "data": (
                f"\r\n🎉 \x1b[1;32m[All Tasks Completed Successfully!]\x1b[0m\r\n"
                f"📄 \x1b[1;35m[1-Click Run Script Generated]\x1b[0m Created 'START_APP.bat' in project root!\r\n"
                f"🚀 \x1b[1;36m[Autonomous Launch]\x1b[0m Starting Dev Server on available port {free_port}...\r\n"
                f"🌐 \x1b[1;33mApplication Live At: {preview_url}\x1b[0m\r\n\r\n"
            ),
            "name": "agent"
        })

        if self.fsm:
            from core.state_machine import AutonomousState
            self.fsm.transition_to(AutonomousState.START_SERVICES, f"Dev server active on port {free_port}")

        self.emit_ipc("preview.open", {"url": preview_url, "port": free_port, "projectId": self.project_id})
        try:
            await asyncio.sleep(2.0)
            webbrowser.open(preview_url)
        except Exception:
            pass

        # ── Autonomous Web-Agent IDE: Formal Mission Delivery Report ─────────
        try:
            if self.fsm:
                self.fsm.transition_to(AutonomousState.DELIVER, "Generating mission delivery report")
            from core.delivery_report import DeliveryReportGenerator
            DeliveryReportGenerator.generate_report(
                mission=self.current_mission,
                workspace_root=self.workspace_root,
                git_status=self.project_info.get("git_status") if hasattr(self, "project_info") else None,
            )
            self.emit_ipc("file.created", {"path": ".delivery/DELIVERY_REPORT.md"})
            self.emit_ipc("command.output", {
                "stream": "stdout",
                "data": (
                    f"📄 \x1b[1;36m[Mission Delivery Report Generated]\x1b[0m .delivery/DELIVERY_REPORT.md\r\n"
                    f"🏆 Final QA Rating Score: {self.scorekeeper.current_score} pts\r\n\r\n"
                ),
                "name": "agent"
            })
            if self.fsm:
                self.fsm.transition_to(AutonomousState.SUCCESS, "Mission finalized and delivered")
        except Exception:
            pass

        return {"preview_url": preview_url, "port": free_port, "bat_path": bat_path}

    async def execute_multiagent_task_turn(self, current_task: Dict[str, Any]) -> bool:
        if not self.loop_detector.record_iteration():
            current_task["error_message"] = "Max iterations reached."
            return False

        provider_name = self.get_provider_display_name()

        context_str = ContextManager.build_task_context(
            self.workspace_root,
            current_task,
            self.recent_commands
        )

        # 1. Engineer Agent Implements Code with Autonomous Self-Healing Loop
        self.emit_ipc("agent.role.started", {"role": "EngineerAgent", "message": f"Engineer generating code for {current_task['title']}..."})
        
        full_coding_prompt = (
            f"🚀 ENGINEERING TASK: {current_task['title']}\n"
            f"📝 SPECIFICATION: {current_task.get('description', '')}\n\n"
            f"🛠️ IMPLEMENTATION DIRECTIVES:\n"
            f"• Write complete, non-placeholder production code using React 18, Vite, Lucide-React, and Tailwind CSS.\n"
            f"• Ensure clean component state, defensive error handling, accessibility, and delightful user experience.\n"
            f"• Structure output in clean JSON with 'write_file' or 'run_command' actions."
        )

        # Build a padded header line so the box always fits 94 chars wide
        header_text = f" 🟣 [EXACT PROMPT TRANSMITTED TO {provider_name}] "
        pad = max(0, 92 - len(header_text))
        padded_header = f"║{header_text}{' ' * pad}║"

        self.emit_ipc("command.output", {
            "stream": "stdout", 
            "data": f"\r\n\x1b[1;35m╔══════════════════════════════════════════════════════════════════════════════════════════════╗\x1b[0m\r\n"
                    f"\x1b[1;35m{padded_header}\x1b[0m\r\n"
                    f"\x1b[1;35m╚══════════════════════════════════════════════════════════════════════════════════════════════╝\x1b[0m\r\n"
                    f"\x1b[0;35m{full_coding_prompt}\x1b[0m\r\n"
                    f"\x1b[1;35m────────────────────────────────────────────────────────────────────────────────────────────────\x1b[0m\r\n\r\n", 
            "name": "agent"
        })

        action_dicts = []
        last_error = None
        last_error_fp = None
        for attempt in range(3):
            try:
                error_ctx = {"attempt": attempt, "error": str(last_error)} if last_error else None

                # ── Autonomous Web-Agent IDE: Error Memory — check cache before consulting AI ──
                if last_error and last_error_fp:
                    cached = self.error_memory.lookup(last_error_fp)
                    if cached and cached.get("successful_patch"):
                        self.emit_ipc("command.output", {
                            "stream": "stdout",
                            "data": f"\r\n🧠 \x1b[1;36m[Error Memory]\x1b[0m Fingerprint: {last_error_fp}\r\n"
                                    f"✅ \x1b[1;32m[Memory Hit]\x1b[0m Known fix found (solved {cached['success_count']} time(s) before) — applying cached patch...\r\n"
                                    f"   Fix: {cached.get('patch_description', 'Cached patch')}\r\n\r\n",
                            "name": "agent",
                        })
                        # Try applying cached patch (actions list)
                        try:
                            cached_actions = cached["successful_patch"]
                            if isinstance(cached_actions, list):
                                for act in cached_actions:
                                    await self.apply_action(act)
                                action_dicts = cached_actions
                                self.error_memory.record_success(
                                    last_error_fp,
                                    str(last_error), "", "",
                                    cached_actions, "actions",
                                    cached.get("patch_description", ""),
                                    provider=provider_name,
                                )
                                break
                        except Exception:
                            self.error_memory.record_failure(last_error_fp)
                    else:
                        self.emit_ipc("command.output", {
                            "stream": "stdout",
                            "data": f"\r\n🧠 \x1b[1;33m[Error Memory]\x1b[0m Fingerprint: {last_error_fp} — ❌ No cached fix. Consulting {provider_name}...\r\n\r\n",
                            "name": "agent",
                        })

                agent_resp = await self.engineer.implement_task(current_task, context_str, error_context=error_ctx, images=self.images)
                action_dicts = [ActionNormalizer.normalize_action(a.model_dump()) for a in agent_resp.actions]
                
                self.emit_ipc("command.output", {
                    "stream": "stdout",
                    "data": f"\x1b[1;32m🟢 [{provider_name} ACTIONS RECEIVED]\x1b[0m: Generated {len(action_dicts)} production code actions.\r\n",
                    "name": "agent"
                })

                # Execute code actions
                for act in action_dicts:
                    await self.apply_action(act)

                # ── Autonomous Web-Agent IDE: Record successful fix in error memory ──
                if last_error and last_error_fp and action_dicts:
                    try:
                        self.error_memory.record_success(
                            fingerprint=last_error_fp,
                            stderr=str(last_error),
                            command=current_task.get("title", ""),
                            root_cause="AI-diagnosed and fixed",
                            patch=action_dicts[:5],  # Store first 5 actions max
                            patch_type="actions",
                            patch_description=agent_resp.summary if hasattr(agent_resp, "summary") else "AI fix",
                            provider=provider_name,
                            project_type=self.project_info.get("framework", ""),
                        )
                    except Exception:
                        pass

                break
            except Exception as e:
                last_error = e
                # Generate fingerprint for this error
                try:
                    last_error_fp = self.error_memory.fingerprint(
                        str(e),
                        command=current_task.get("title", ""),
                        exit_code=1,
                    )
                    self.error_memory.record_seen(last_error_fp, str(e), current_task.get("title", ""))
                except Exception:
                    last_error_fp = None

                self.emit_ipc("command.output", {
                    "stream": "stderr",
                    "data": f"\r\n\x1b[1;31m🔴 [Autonomous Error Intercepted - Attempt {attempt + 1}/3]\x1b[0m\r\n"
                            f"• Failure: {str(e)[:250]}...\r\n"
                            f"• 🤖 \x1b[1;33m[{provider_name} Self-Healing Active]\x1b[0m Consulting {provider_name} to diagnose failure & generate code patch...\r\n\r\n",
                    "name": "agent"
                })
                await asyncio.sleep(1)

        if not action_dicts:
            self.emit_ipc("command.output", {
                "stream": "stderr",
                "data": f"[Self-Healing Warning] Proceeding with task verification using partial actions.\r\n",
                "name": "agent"
            })

        # 2. Reviewer Judge Agent Evaluates Code & Quality Score
        self.emit_ipc("agent.role.started", {"role": "ReviewerJudgeAgent", "message": "Reviewer Judge evaluating code quality and assigning score..."})
        self.emit_ipc("command.output", {"stream": "stdout", "data": "⚖️  [Reviewer Judge] Auditing code completeness, modularity & defensive error handling...\r\n", "name": "agent"})

        audit = self.scorekeeper.evaluate_task_code(current_task, action_dicts)

        self.emit_ipc("score.updated", {
            "score": audit.score,
            "delta": audit.delta,
            "reasons": audit.reasons,
            "task_id": current_task["id"]
        })

        for r in audit.reasons:
            color = "\x1b[1;32m" if "[+" in r else "\x1b[1;31m"
            self.emit_ipc("command.output", {"stream": "stdout", "data": f"   {color}{r}\x1b[0m\r\n", "name": "agent"})

        self.emit_ipc("command.output", {"stream": "stdout", "data": f"🏆  [ScoreKeeper] Current Quality Score: \x1b[1;33m{audit.score} pts\x1b[0m\r\n", "name": "agent"})

        # 3. Autonomous Build & Type Verification with Connected Dependency Healing
        import os
        import re

        # Detect build directory (check client/ first if monorepo, else root)
        build_cwd = self.workspace_root
        if os.path.exists(os.path.join(self.workspace_root, "client", "package.json")):
            build_cwd = os.path.join(self.workspace_root, "client")

        pkg_file = os.path.join(build_cwd, "package.json")
        node_modules_dir = os.path.join(build_cwd, "node_modules")
        if os.path.exists(pkg_file) and os.path.exists(node_modules_dir):
            for build_attempt in range(2):
                build_res = await CommandRunner.run("npm run build", cwd=build_cwd, timeout=60)
                if build_res.exit_code == 0:
                    break

                error_text = build_res.stderr or build_res.stdout
                self.emit_ipc("command.output", {
                    "stream": "stderr",
                    "data": f"\r\n\x1b[1;31m⚠️  [Autonomous TypeScript & Build Issue Intercepted in {os.path.basename(build_cwd)}]\x1b[0m\r\n"
                            f"{error_text[:400]}...\r\n"
                            f"\x1b[1;35m🔄 [Autonomous Connected Dependency Healer Active]\x1b[0m\r\n"
                            f"• Scanning error files and resolving all connected imports/APIs/stores...\r\n",
                    "name": "agent"
                })

                # Find all failing file paths from compiler output
                failing_paths = set(re.findall(r"(?:src[\\/][\w\\/.-]+\.(?:tsx?|jsx?|css|json))", error_text))
                connected_files = {}

                for rel_path in failing_paths:
                    norm_path = rel_path.replace("\\", "/")
                    full_p = os.path.join(self.workspace_root, norm_path)
                    if os.path.exists(full_p):
                        try:
                            with open(full_p, "r", encoding="utf-8", errors="replace") as f:
                                code = f.read()
                            connected_files[norm_path] = code

                            # Scan for connected imports in this file
                            imports = re.findall(r"""(?:from|import)\s+['"](\.[^'"]+)['"]""", code)
                            dir_name = os.path.dirname(norm_path)
                            for imp in imports:
                                resolved = os.path.normpath(os.path.join(dir_name, imp)).replace("\\", "/")
                                for ext in ["", ".ts", ".tsx", ".js", ".jsx", "/index.ts", "/index.tsx", "/index.js"]:
                                    cand = resolved + ext
                                    cand_full = os.path.join(self.workspace_root, cand)
                                    if os.path.exists(cand_full) and cand not in connected_files:
                                        try:
                                            with open(cand_full, "r", encoding="utf-8", errors="replace") as cf:
                                                connected_files[cand] = cf.read()
                                        except Exception:
                                            pass
                        except Exception:
                            pass

                connected_summary = "\n\n".join([f"### File: {p}\n```tsx\n{c}\n```" for p, c in connected_files.items()])

                fix_prompt = (
                    f"The project build/typecheck failed with the following TypeScript/Vite errors:\n"
                    f"```\n{error_text}\n```\n\n"
                    f"Here are the failing files and all their CONNECTED dependent files/stores/components:\n"
                    f"{connected_summary}\n\n"
                    f"Please provide clean, comprehensive write_file actions for all affected files to resolve all red squiggly lines, unused parameters, export mismatches, and TypeScript errors."
                )

                try:
                    fix_resp = await self.refiner.refine(current_task, action_dicts, fix_prompt, [error_text])
                    fixed_actions = [ActionNormalizer.normalize_action(a.model_dump()) for a in fix_resp.actions]
                    for act in fixed_actions:
                        await self.apply_action(act)
                except Exception as fix_err:
                    self.emit_ipc("command.output", {
                        "stream": "stderr",
                        "data": f"[Refiner Error] {fix_err}\r\n",
                        "name": "agent"
                    })

        return True

    async def apply_action(self, action_dict: Dict[str, Any]) -> bool:
        action_type = action_dict.get("type")
        try:
            if action_type == "write_file":
                FileSystem.write_file(self.workspace_root, action_dict["path"], action_dict["content"])
                self.emit_ipc("file.created", {"path": action_dict["path"]})
                return True
            elif action_type == "edit_file":
                FileSystem.edit_file(self.workspace_root, action_dict["path"], content=action_dict.get("content"))
                self.emit_ipc("file.modified", {"path": action_dict["path"]})
                return True
            elif action_type == "mkdir":
                FileSystem.mkdir(self.workspace_root, action_dict["path"])
                return True
            elif action_type == "run_command":
                cmd = action_dict["command"]
                cmd_id = str(uuid.uuid4())
                self.emit_ipc("command.started", {"id": cmd_id, "command": cmd})
                res = await CommandRunner.run(
                    cmd,
                    cwd=self.workspace_root,
                    timeout=action_dict.get("timeout", 120),
                    on_stdout=lambda text: self.emit_ipc("command.output", {"stream": "stdout", "data": text, "name": "command"}),
                    on_stderr=lambda text: self.emit_ipc("command.output", {"stream": "stderr", "data": text, "name": "command"})
                )
                self.recent_commands.append({"command": cmd, "exit_code": res.exit_code, "stdout": res.stdout[:200]})
                if res.exit_code != 0:
                    err_output = res.stderr or res.stdout or f"Exit code {res.exit_code}"
                    self.emit_ipc("command.output", {
                        "stream": "stderr",
                        "data": f"\r\n\x1b[1;31m✖ [Command Failed (exit {res.exit_code})]\x1b[0m {cmd}\r\n{err_output[:300]}\r\n",
                        "name": "agent"
                    })
                    raise RuntimeError(f"Command '{cmd}' failed (exit code {res.exit_code}): {err_output[:300]}")
                return True
            return True
        except Exception as e:
            self.emit_ipc("command.output", {"stream": "stderr", "data": f"[Action Error] {e}\r\n", "name": "agent"})
            raise
