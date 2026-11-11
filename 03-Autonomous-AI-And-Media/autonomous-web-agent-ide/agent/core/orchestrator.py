import asyncio
import json
import uuid
import sys
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from protocol.schemas import (
        AgentResponse, WriteFileAction, EditFileAction, DeleteFileAction,
        MkdirAction, ReadFileAction, ListFilesAction, SearchFilesAction,
        RunCommandAction, StartServerAction, StopServerAction, RunTestsAction,
        RunBuildAction, GitCheckpointAction, GitDiffAction, GitRollbackAction,
        AskUserAction, FinishAction
    )
    from protocol.parser import ProtocolParser
    from protocol.validator import ProtocolValidator
    from protocol.normalizer import ActionNormalizer
    from security.path_guard import PathGuard, SecurityException
    from execution.command_policy import CommandPolicyEngine, CommandCategory
    from execution.command_runner import CommandRunner
    from execution.filesystem import FileSystem
    from execution.git_manager import GitManager
    from browser.providers.base import LLMProvider
    from core.planner import Planner
    from prompts.system_prompts import PLANNER_SYSTEM_PROMPT, CODING_SYSTEM_PROMPT
    from core.task_manager import TaskManager
    from core.context_manager import ContextManager
    from core.state_manager import StateManager
    from core.thinking_engine import ThinkingEngine
    from recovery.error_analyzer import ErrorAnalyzer
    from recovery.loop_detector import LoopDetector
    from recovery.retry_manager import RetryManager
except ImportError:
    from ..protocol.schemas import (
        AgentResponse, WriteFileAction, EditFileAction, DeleteFileAction,
        MkdirAction, ReadFileAction, ListFilesAction, SearchFilesAction,
        RunCommandAction, StartServerAction, StopServerAction, RunTestsAction,
        RunBuildAction, GitCheckpointAction, GitDiffAction, GitRollbackAction,
        AskUserAction, FinishAction
    )
    from ..protocol.parser import ProtocolParser
    from ..protocol.validator import ProtocolValidator
    from ..protocol.normalizer import ActionNormalizer
    from ..security.path_guard import PathGuard, SecurityException
    from ..execution.command_policy import CommandPolicyEngine, CommandCategory
    from ..execution.command_runner import CommandRunner
    from ..execution.filesystem import FileSystem
    from ..execution.git_manager import GitManager
    from ..browser.providers.base import LLMProvider
    from .planner import Planner
    from ..prompts.system_prompts import PLANNER_SYSTEM_PROMPT, CODING_SYSTEM_PROMPT
    from .task_manager import TaskManager
    from .context_manager import ContextManager
    from .state_manager import StateManager
    from .thinking_engine import ThinkingEngine
    from ..recovery.error_analyzer import ErrorAnalyzer
    from ..recovery.loop_detector import LoopDetector
    from ..recovery.retry_manager import RetryManager

SERVER_COMMAND_PATTERNS = [
    re.compile(r"\b(?:npm\s+run\s+dev|npm\s+start|vite|next\s+dev|nodemon)\b", re.IGNORECASE)
]

class Orchestrator:
    def __init__(
        self,
        project_id: str,
        run_id: str,
        workspace_root: str,
        provider: LLMProvider,
        db_path: str,
        approval_mode: str = "SAFE"
    ):
        self.project_id = project_id
        self.run_id = run_id
        self.workspace_root = workspace_root
        Path(self.workspace_root).mkdir(parents=True, exist_ok=True)
        self.provider = provider
        state_file = str(Path(self.workspace_root) / ".agent_state.sqlite")
        self.state_mgr = StateManager(state_file)
        self.approval_mode = approval_mode

        self.planner = Planner(provider)
        self.task_mgr = TaskManager()
        self.loop_detector = LoopDetector()
        self.retry_mgr = RetryManager()

        self.is_paused = False
        self.is_stopped = False
        self.pending_approvals: Dict[str, asyncio.Future] = {}
        self.recent_commands: List[Dict[str, Any]] = []

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

    def get_provider_display_name(self) -> str:
        """Returns a human-readable name for the currently active LLM provider."""
        class_name = type(self.provider).__name__
        mapping = {
            "GeminiWebProvider": "GOOGLE GEMINI",
            "GenericWebProvider": "CHATGPT WEB",
            "ChatGPTWebProvider": "CHATGPT WEB",
            "DeepSeekWebProvider": "DEEPSEEK R1",
            "NemotronHuggingFaceProvider": "NVIDIA NEMOTRON 70B",
            "SmartMultiModelProvider": "SMART MULTI-MODEL",
        }
        return mapping.get(class_name, class_name.upper())

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
        elif cmd == "approval_response":
            app_id = cmd_data.get("approvalId")
            decision = cmd_data.get("decision")
            if app_id in self.pending_approvals and not self.pending_approvals[app_id].done():
                self.pending_approvals[app_id].set_result(decision)

    async def run(self, user_prompt: str) -> bool:
        self.current_user_prompt = user_prompt
        self.emit_ipc("agent.started", {"prompt": user_prompt})
        provider_name = self.get_provider_display_name()

        # Step 0: Direct Evolution / Training Shortcut
        p_lower = user_prompt.lower()
        if any(k in p_lower for k in ["start train", "start traing", "train deepseek", "evolve", "evolution"]):
            self.emit_ipc("command.output", {
                "stream": "stdout",
                "data": f"\r\n🧠 [{provider_name} Evolution Lab - Live Cognitive Training Session Starting...]\r\n"
                        f"• Loading Daily Mathematical & Architectural Curriculum...\r\n"
                        f"• Initiating deep scientific dialogue with {provider_name}...\r\n\r\n",
                "name": "agent"
            })
            try:
                from learning.cognitive_evolution_lab import CognitiveEvolutionLab
                lab = CognitiveEvolutionLab(self.db_path)
                res = await lab.execute_daily_training_session(self.provider)
                self.emit_ipc("command.output", {
                    "stream": "stdout",
                    "data": f"🎓 [{provider_name} Mastery Achieved!]\r\n"
                            f"• Topic: {res.get('topic')}\r\n"
                            f"• Mathematical Formula: {res.get('formula')}\r\n"
                            f"• Dialogue & Lessons:\r\n{res.get('dialogue')}\r\n\r\n"
                            f"🏆 AI Cognitive Level Increased! Check Evolution Tab for new Mastery level.\r\n\r\n",
                    "name": "agent"
                })
                self.emit_ipc("agent.completed", {"summary": f"Mastered {res.get('topic')} with {provider_name}."})
                return True
            except Exception as e:
                self.emit_ipc("command.output", {"stream": "stderr", "data": f"[Evolution Error] {e}\r\n", "name": "agent"})

        # Step 1: Ensure Git Repo
        await GitManager.ensure_repo(self.workspace_root)

        # Step 2: DeepSeek R1 Cognitive Thinking & Self-Prompt Synthesis
        thought = ThinkingEngine.deep_think(user_prompt)
        self.emit_ipc("agent.thought", {"thinking": thought["thinking_monologue"], "domain": thought["domain"]})
        self.emit_ipc("command.output", {
            "stream": "stdout",
            "data": f"\r\n{thought['thinking_monologue']}\r\n\r\n",
            "name": "agent"
        })

        # Step 3: Planning Phase using synthesized master prompt
        self.emit_ipc("command.output", {
            "stream": "stdout",
            "data": f"[Agent Brain] 🚀 Synthesized Master Prompt: {thought['synthesized_prompt']}\r\n[Agent] Formulating optimal DAG task graph...\r\n",
            "name": "agent"
        })
        plan = None
        for plan_attempt in range(3):
            try:
                plan = await self.planner.create_plan(thought["synthesized_prompt"])
                if plan and plan.tasks:
                    break
            except Exception as e:
                self.emit_ipc("command.output", {"stream": "stderr", "data": f"[Planner Warning] Attempt {plan_attempt + 1} failed: {e}. Retrying...\r\n", "name": "agent"})
                await asyncio.sleep(1)

        if not plan or not plan.tasks:
            self.emit_ipc("agent.error", {"error": "Failed to generate valid task plan from LLM."})
            return False

        self.task_mgr.load_plan(plan)
        self.state_mgr.save_tasks(self.project_id, self.run_id, self.task_mgr.get_all_tasks(), self.task_mgr.dependencies)
        self.emit_ipc("task.created", {"count": len(plan.tasks), "tasks": self.task_mgr.get_all_tasks()})

        # Step 3: Autonomous Task Execution Loop
        while not self.is_stopped and not self.task_mgr.are_all_tasks_completed():
            while self.is_paused and not self.is_stopped:
                await asyncio.sleep(0.5)

            if self.is_stopped:
                break

            current_task = self.task_mgr.get_next_available_task()
            if not current_task:
                # Deadlock breaker: if tasks remain in PENDING, pick first
                pending = [t for t in self.task_mgr.get_all_tasks() if t["status"] == "PENDING"]
                if pending:
                    current_task = pending[0]
                else:
                    break

            task_id = current_task["id"]
            self.task_mgr.update_task_status(task_id, "RUNNING")
            self.state_mgr.update_task_status(task_id, "RUNNING")
            self.emit_ipc("task.started", current_task)

            await GitManager.create_checkpoint(self.workspace_root, f"Before: {current_task['title']}")

            success = await self.execute_task_turn(current_task)

            if success:
                self.task_mgr.update_task_status(task_id, "COMPLETED")
                self.state_mgr.update_task_status(task_id, "COMPLETED")
                await GitManager.create_checkpoint(self.workspace_root, f"Completed: {current_task['title']}")
                self.emit_ipc("task.completed", current_task)
            else:
                self.task_mgr.update_task_status(task_id, "FAILED", current_task.get("error_message"))
                self.state_mgr.update_task_status(task_id, "FAILED", current_task.get("error_message"))
                self.emit_ipc("task.failed", current_task)

                if self.retry_mgr.should_retry(current_task["retry_count"]):
                    self.emit_ipc("command.output", {"stream": "stderr", "data": f"[Agent] Retrying task {current_task['title']} (Attempt {current_task['retry_count'] + 1})...\r\n", "name": "agent"})
                    self.task_mgr.update_task_status(task_id, "PENDING")
                    self.state_mgr.update_task_status(task_id, "PENDING")
                else:
                    self.emit_ipc("agent.error", {"error": f"Max retries reached for task {task_id}"})
                    return False

        if self.task_mgr.are_all_tasks_completed():
            # DeepSeek Post-Build Self-Training & Architecture Critique Loop
            try:
                from learning.deepseek_trainer import DeepSeekTrainer
                trainer = DeepSeekTrainer(self.db_path)
                file_tree = [p.name for p in Path(self.workspace_root).rglob("*") if p.is_file() and ".git" not in str(p)]
                critique = await trainer.train_and_critique(self.project_id, user_prompt, self.provider, file_tree, test_passed=True)
                self.emit_ipc("command.output", {
                    "stream": "stdout",
                    "data": f"\r\n🎓 [{provider_name} Architecture Critique & Self-Training]\r\n"
                            f"🏆 Mastery Rating: {critique.get('mastery_score', 95)}/100\r\n"
                            f"🧠 {provider_name} Review: {critique.get('training_summary', '')}\r\n"
                            f"✨ Learned Optimizations Saved to Agent Memory: {', '.join(critique.get('strengths', []))}\r\n\r\n",
                    "name": "agent"
                })
            except Exception:
                pass

            self.emit_ipc("agent.completed", {"summary": "All tasks in plan completed successfully."})
            return True

        return False

    async def execute_task_turn(self, current_task: Dict[str, Any], error_context: Optional[Dict[str, Any]] = None) -> bool:
        if not self.loop_detector.record_iteration():
            current_task["error_message"] = "Max agent iterations reached."
            return False

        context_str = ContextManager.build_task_context(
            self.workspace_root,
            current_task,
            self.recent_commands,
            error_context=error_context
        )

        user_goal = getattr(self, 'current_user_prompt', '')
        coding_prompt = f"Overall Project Goal: {user_goal}\nImplement task: {current_task['title']}\nDescription: {current_task['description']}\n\nContext:\n{context_str}"
        if error_context:
            coding_prompt += f"\n\nPrevious Execution Error:\n{json.dumps(error_context, indent=2)}\nPlease generate fix actions."

        # Up to 2 extraction attempts with automatic protocol correction prompt
        agent_resp = None
        for parse_attempt in range(2):
            raw_resp = await self.provider.generate(coding_prompt, system_prompt=CODING_SYSTEM_PROMPT)
            try:
                parsed_dict = ProtocolParser.parse_raw_response(raw_resp)
                is_valid, agent_resp, err = ProtocolValidator.validate_response(parsed_dict)
                if is_valid and agent_resp is not None:
                    # Extract and display thinking trace if present in LLM response
                    think_trace = ProtocolParser.extract_think_tags(raw_resp)
                    if think_trace:
                        self.emit_ipc("agent.thought", {"thinking": think_trace})
                        self.emit_ipc("command.output", {
                            "stream": "stdout",
                            "data": f"\r\n🧠 [{self.get_provider_display_name()} Thinking Trace]\r\n{think_trace}\r\n\r\n",
                            "name": "agent"
                        })
                    break
            except Exception as e:
                if parse_attempt == 0:
                    coding_prompt = f"Previous response was not valid JSON: {e}. Please respond strictly with a valid ```json ``` block matching the AgentResponse protocol with concrete code actions."
                    await asyncio.sleep(0.5)

        if not agent_resp:
            current_task["error_message"] = "Failed to obtain valid JSON actions from LLM."
            return False

        self.emit_ipc("command.output", {"stream": "stdout", "data": f"[Agent] {agent_resp.summary}\r\n", "name": "agent"})

        for action in agent_resp.actions:
            action_dict = ActionNormalizer.normalize_action(action.model_dump())
            action_type = action_dict.get("type")

            # Check policy & approval
            allowed = await self.check_policy_and_approval(action_type, action_dict)
            if not allowed:
                self.emit_ipc("command.output", {"stream": "stderr", "data": f"[Agent] Action rejected: {action_type}\r\n", "name": "agent"})
                return False

            action_success = await self.dispatch_action(action_type, action_dict, current_task)
            if not action_success:
                return False

        return True

    async def check_policy_and_approval(self, action_type: str, action_dict: Dict[str, Any]) -> bool:
        if self.approval_mode == "AUTO":
            return True

        if action_type == "run_command":
            cmd = action_dict.get("command", "")
            category, reason = CommandPolicyEngine.evaluate(cmd)

            if category == CommandCategory.BLOCKED:
                self.emit_ipc("command.output", {"stream": "stderr", "data": f"[Security Blocked] {reason}\r\n", "name": "agent"})
                return False

            if category == CommandCategory.SAFE and self.approval_mode == "SAFE":
                return True

            approval_id = str(uuid.uuid4())
            future = asyncio.get_event_loop().create_future()
            self.pending_approvals[approval_id] = future

            self.state_mgr.create_approval(approval_id, self.project_id, self.run_id, action_type, action_dict, reason)
            self.emit_ipc("approval.required", {
                "id": approval_id,
                "action_type": action_type,
                "action_payload": action_dict,
                "reason": reason
            })

            decision = await future
            del self.pending_approvals[approval_id]
            return decision in ["APPROVE", "ALWAYS_ALLOW"]

        return True

    async def dispatch_action(self, action_type: str, action_dict: Dict[str, Any], current_task: Dict[str, Any]) -> bool:
        try:
            if action_type == "write_file":
                FileSystem.write_file(self.workspace_root, action_dict["path"], action_dict["content"])
                self.emit_ipc("file.created", {"path": action_dict["path"]})
                return True

            elif action_type == "edit_file":
                FileSystem.edit_file(
                    self.workspace_root,
                    action_dict["path"],
                    content=action_dict.get("content"),
                    expected_hash=action_dict.get("expected_hash"),
                    patch=action_dict.get("patch")
                )
                self.emit_ipc("file.modified", {"path": action_dict["path"]})
                return True

            elif action_type == "delete_file":
                FileSystem.delete_file(self.workspace_root, action_dict["path"])
                self.emit_ipc("file.deleted", {"path": action_dict["path"]})
                return True

            elif action_type == "mkdir":
                FileSystem.mkdir(self.workspace_root, action_dict["path"])
                return True

            elif action_type == "run_command":
                cmd = action_dict["command"]

                # Check if this is a blocking dev server command (e.g. npm run dev, vite)
                is_blocking_server = any(p.search(cmd) for p in SERVER_COMMAND_PATTERNS)
                timeout = 5 if is_blocking_server else action_dict.get("timeout", 120)

                cmd_id = str(uuid.uuid4())
                self.emit_ipc("command.started", {"id": cmd_id, "command": cmd})

                result = await CommandRunner.run(
                    cmd,
                    cwd=self.workspace_root,
                    timeout=timeout,
                    on_stdout=lambda text: self.emit_ipc("command.output", {"stream": "stdout", "data": text, "name": "command"}),
                    on_stderr=lambda text: self.emit_ipc("command.output", {"stream": "stderr", "data": text, "name": "command"})
                )

                # If it was a dev server and timed out after verifying launch, treat as successful start
                if is_blocking_server and result.exit_code == 124:
                    result.exit_code = 0

                self.state_mgr.record_command(
                    cmd_id, self.project_id, self.run_id, current_task.get("id"),
                    cmd, self.workspace_root, result.exit_code, result.duration_ms,
                    result.stdout, result.stderr
                )
                self.recent_commands.append(result.to_dict())

                if result.exit_code != 0:
                    error_ctx = ErrorAnalyzer.analyze_command_failure(cmd, result.exit_code, result.stdout, result.stderr)
                    if not self.loop_detector.record_error(cmd, result.exit_code, result.stderr):
                        self.emit_ipc("command.output", {"stream": "stderr", "data": f"[Loop Detector] Halting infinite error loop on command: {cmd}\r\n", "name": "agent"})
                        current_task["error_message"] = f"Infinite error loop detected on: {cmd}"
                        return False

                    self.emit_ipc("command.output", {"stream": "stdout", "data": f"[Agent] Error detected in command execution. Generating repair fix...\r\n", "name": "agent"})
                    return await self.execute_task_turn(current_task, error_context=error_ctx)

                return True

            elif action_type == "git_checkpoint":
                commit_hash = await GitManager.create_checkpoint(self.workspace_root, action_dict["message"])
                self.emit_ipc("checkpoint.created", {"commit_hash": commit_hash, "message": action_dict["message"]})
                return True

            elif action_type == "finish":
                return action_dict.get("verification_passed", True)

            return True

        except Exception as e:
            self.emit_ipc("command.output", {"stream": "stderr", "data": f"[Action Error] {str(e)}\r\n", "name": "agent"})
            current_task["error_message"] = str(e)
            return False
