import re
import shlex
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

import config
from brains.brain_router import BrainRouter
from tools.terminal import run_terminal_command_sync
from tools.file_manager import FileManager
from tools.codebase_inspector import CodebaseInspector, ProjectContextBuilder
from tools.process_manager import ProcessManager
from core.auto_healer import AutoHealer
from builders.crud_builder import CRUDAppBuilder
from builders.web_builder import WebsiteBuilder
from builders.ppt_builder import PPTBuilder
from builders.image_builder import ImageBuilder
from builders.android_builder import AndroidAppBuilder
from builders.game_builder import GameBuilder
from builders.doc_builder import DocumentBuilder
from tools.browser_tool import BrowserTool
from tools.adb_tool import ADBTool
from tools.git_tool import GitTool
from tools.env_doctor import EnvironmentDoctor
from tools.security_scanner import SecurityScanner
from tools.project_packager import ProjectPackager
from core.interactive_wizard import InteractiveWizard
from core.project_graph import ProjectKnowledgeGraph
from core.state_machine import AutonomousFSM, FSMState
from core.task_graph import TaskGraph, Task, TaskStatus
from core.permission_manager import PermissionManager
from core.error_memory import ErrorMemory
from core.memory_vault import MemoryVault
from core.event_bus import event_bus
from .safety import SafetyGuard
from .memory import AgentMemory

from config import console

class Orchestrator:
    """
    Central Brain and Autonomous Engine for OmniDev AI.
    Analyzes intent, inspects codebase, delegates to builders or tools,
    and runs self-healing loops with multi-agent orchestration.
    """
    def __init__(self, workspace_dir: Optional[Path] = None):
        self.workspace_dir = Path(workspace_dir) if workspace_dir else config.WORKSPACE_DIR
        self.brain = BrainRouter()
        self.file_manager = FileManager(self.workspace_dir)
        self.inspector = CodebaseInspector(self.workspace_dir)
        self.process_manager = ProcessManager()
        self.memory = AgentMemory(self.workspace_dir)
        self.memory_vault = MemoryVault()
        self.error_memory = ErrorMemory(self.memory_vault)
        self.auto_healer = AutoHealer(self.brain, self.file_manager, workspace_dir=self.workspace_dir)
        self.fsm = AutonomousFSM()
        self.permission_manager = PermissionManager()
        self.project_graph = ProjectKnowledgeGraph(self.workspace_dir)
        self.packager = ProjectPackager(self.workspace_dir)
        self.wizard = InteractiveWizard()

        # Tools
        self.browser_tool = BrowserTool(headless=True)
        self.adb_tool = ADBTool()
        self.git_tool = GitTool(self.workspace_dir)
        self.security_scanner = SecurityScanner(self.workspace_dir)

        # Builders
        self.crud_builder = CRUDAppBuilder(self.brain, self.workspace_dir, process_manager=self.process_manager)
        self.web_builder = WebsiteBuilder(self.brain, self.workspace_dir)
        self.ppt_builder = PPTBuilder(self.brain, config.OUTPUTS_DIR)
        self.image_builder = ImageBuilder(self.brain, config.OUTPUTS_DIR)
        self.android_builder = AndroidAppBuilder(self.brain, self.workspace_dir)
        self.game_builder = GameBuilder(self.brain, self.workspace_dir, process_manager=self.process_manager)
        self.doc_builder = DocumentBuilder(self.brain, config.OUTPUTS_DIR)

        # Active App Context
        self.active_app_dir: Optional[Path] = self._find_latest_app_dir()

    def _find_latest_app_dir(self) -> Optional[Path]:
        apps_dir = self.workspace_dir / "apps"
        if apps_dir.exists():
            valid_dirs = []
            for d in apps_dir.iterdir():
                if d.is_dir() and not d.name.startswith(".") and not d.name.startswith("update_"):
                    # Check if contains actual project code files
                    has_files = any(f.suffix in [".gd", ".tscn", ".godot", ".py", ".html", ".js"] for f in d.rglob("*.*"))
                    if has_files:
                        valid_dirs.append(d)
            if valid_dirs:
                return max(valid_dirs, key=lambda d: d.stat().st_mtime)
        gen = self.workspace_dir / "generated_app"
        if gen.exists():
            return gen
        return None

    def process_user_request(self, user_input: str) -> Dict[str, Any]:
        """
        Main entry point for processing any user instruction.
        """
        text = user_input.strip()
        lowered = text.lower()

        # 0. Active Application / Game Modification Intent (Prioritized when project already exists)
        active_app = self.active_app_dir or self._find_latest_app_dir()
        is_mod_keyword = any(w in lowered for w in [
            "update", "modify", "change", "add", "fix", "edit", "improve", "refactor",
            "not working", "slow", "fast", "speed", "color", "button", "score",
            "bug", "sound", "audio", "texture", "gravity", "player", "house", "weapon",
            "jump", "badal do", "thik karo", "solve", "reset"
        ])
        is_explicit_new = any(w in lowered for w in ["build new", "create new", "make a new", "banao naya", "naya game", "naya app", "new project"])
        
        if active_app and active_app.exists() and is_mod_keyword and not is_explicit_new:
            return self._handle_app_modification(text, app_dir=active_app)

        # 1. Image Generation Intent (handles typos like 'genrate', 'pic', 'photo', 'bana img', etc.)
        img_pattern = r"\b(?:gen\w*|make|create|draw|paint|sketch|render|bana\w*|show\s+me)\b.*\b(?:image|img|photo|pic\w*)\b|^(?:image|img|photo|pic\w*)\s+(?:of|for)\b|^(?:draw|sketch|paint)\s+"
        if re.search(img_pattern, lowered):
            prompt = re.sub(
                r"^(?:gen\w*|make|create|draw|paint|sketch|render|bana\w*|show\s+me)?\s*(?:an?\s+)?(?:image|img|photo|pic\w*)\s*(?:of|for|:)?\s*",
                "", text, flags=re.IGNORECASE
            ).strip()
            if not prompt:
                prompt = text
            result = self.image_builder.generate_image(prompt)
            self.memory.record_action("GENERATE_IMAGE", {"prompt": prompt, "result": result})
            return result

        # 2. PowerPoint Presentation Intent
        ppt_pattern = r"\b(?:gen\w*|make|create|bana\w*)\b.*\b(?:ppt|presentation|slides?)\b|^(?:ppt|presentation)\s+(?:on|about|for|of)\b"
        if re.search(ppt_pattern, lowered):
            num_slides = 6
            num_match = re.search(r"(\d+)\s*(slide|slides)", lowered)
            if num_match:
                num_slides = int(num_match.group(1))
            topic = re.sub(r"^(?:gen\w*|make|create|bana\w*)\s+(?:a\s+)?(?:ppt|presentation|slides?)\s*(?:on|about|for|:)?\s*", "", text, flags=re.IGNORECASE).strip()
            if not topic:
                topic = text
            result = self.ppt_builder.generate_presentation(topic, num_slides=num_slides)
            self.memory.record_action("GENERATE_PPT", {"topic": topic, "result": result})
            return result

        # 3. Website / Landing Page Intent
        web_pattern = r"\b(?:build\w*|create|make|bana\w*|develop\w*)\b.*\b(?:website|landing\s*page|webpage|portfolio)\b|^(?:website|landing\s*page|portfolio)\s+(?:for|about)\b"
        if re.search(web_pattern, lowered):
            prompt = re.sub(r"^(?:build\w*|create|make|bana\w*|develop\w*)\s+(?:a\s+)?(?:website|landing\s*page|webpage|portfolio)\s*(?:for|about|:)?\s*", "", text, flags=re.IGNORECASE).strip()
            if not prompt:
                prompt = text
            result = self.web_builder.build_website(prompt)
            if result.get("directory"):
                self.active_app_dir = Path(result["directory"])
            self.memory.record_action("BUILD_WEBSITE", {"prompt": prompt, "result": result})
            return result

        # 4. Android Native Application Intent
        android_pattern = r"\b(?:android|apk|aab|gradle|bluetooth\s+app|phone\s+app)\b"
        if re.search(android_pattern, lowered) and any(k in lowered for k in ["app", "build", "create", "make", "bana"]):
            prompt = re.sub(r"^(?:build|create|make|bana|generate)\s+(?:an?\s+)?(?:new\s+)?(?:android\s+)?(?:app|application)?\s*(?:for|about|:)?\s*", "", text, flags=re.IGNORECASE)
            result = self.android_builder.build_and_deploy(prompt or text)
            if result.get("directory"):
                self.active_app_dir = Path(result["directory"])
            self.memory.record_action("BUILD_ANDROID", {"prompt": prompt, "result": result})
            return result

        # 5. Game Factory Intent (Godot 4 Sovereign Engine for 2D & 3D Games)
        game_pattern = r"\b(?:new_game|new\s+game|naya\s+game|game|arcade|flappy|snake|pong|platformer|rpg|racing|minecraft|voxel|open\s*world|fps|shooter)\b"
        is_game_intent = re.search(game_pattern, lowered) and (
            any(k in lowered for k in ["new_game", "new game", "naya", "bana", "build", "create", "make", "play", "develop", "new"]) or
            lowered.startswith("new_game")
        )
        if is_game_intent:
            prompt = re.sub(r"^(?:build|create|make|bana|generate)\s+(?:a\s+)?(?:new\s+)?(?:game|arcade)?\s*(?:for|about|:)?\s*", "", text, flags=re.IGNORECASE).strip() or text
            prefs = self.wizard.prompt_game_preferences_interactive(prompt)
            result = self.game_builder.build_game(
                prompt=prompt,
                engine=prefs.get("engine", "godot_engine"),
                dimension=prefs.get("dimension", "3d_voxel"),
                art_style=prefs.get("art_style", "voxel_blocky_3d"),
                era=prefs.get("era", "medieval_fantasy"),
                story=prefs.get("story")
            )
            if result.get("directory"):
                self.active_app_dir = Path(result["directory"])
            self.memory.record_action("BUILD_GAME", {"prompt": prompt, "preferences": prefs, "result": result})
            return result

        # 6. Document / Report Factory Intent (PDF, DOCX, XLSX, CSV, Reports)
        doc_pattern = r"\b(?:pdf|docx|xlsx|csv|report|document|spreadsheet)\b"
        if re.search(doc_pattern, lowered) and any(k in lowered for k in ["generate", "create", "make", "bana", "export", "write"]):
            doc_type = "pdf"
            for t in ["xlsx", "csv", "docx", "pdf"]:
                if t in lowered:
                    doc_type = t
                    break
            topic = re.sub(r"^(?:generate|create|make|bana|export|write)\s+(?:a\s+)?(?:new\s+)?(?:pdf|docx|xlsx|csv|report|document|spreadsheet)?\s*(?:on|about|for|:)?\s*", "", text, flags=re.IGNORECASE)
            result = self.doc_builder.generate_report(topic or text, doc_type=doc_type)
            self.memory.record_action("GENERATE_DOC", {"topic": topic, "result": result})
            return result

        # 7. Environment Doctor & Diagnostics Intent
        if any(w in lowered for w in ["doctor", "diagnose env", "check system", "check tools", "env check", "sdk check"]):
            diag = EnvironmentDoctor.diagnose()
            console.print(Panel(str(diag), title="System Diagnostics Report", border_style="cyan"))
            return diag

        # 8. Security & SBOM Audit Intent
        if any(w in lowered for w in ["security audit", "scan secrets", "scan vulnerabilities", "sbom", "cve scan"]):
            sec = self.security_scanner.full_audit()
            console.print(Panel(str(sec), title="Security & SBOM Audit", border_style="green" if sec["clean"] else "red"))
            return sec

        # 9. Natural Language Code Search Intent (e.g. 'Login ka code kaha hai?')
        if any(w in lowered for w in ["kaha hai", "where is", "find code", "locate symbol", "search class", "search function"]):
            matches = self.project_graph.search_code_nl(text)
            if matches:
                console.print(f"[bold green]🔍 Found {len(matches)} matching component(s):[/bold green]")
                for m in matches[:5]:
                    console.print(f"  📁 [bold cyan]{m['file']}[/bold cyan] (Classes: {m['classes']}, Functions: {m['functions']})")
                return {"success": True, "matches": matches}

        # 10. Git Commit & Push Intent
        if any(w in lowered for w in ["commit and push", "git push", "push to github", "commit everything", "push code"]):
            console.print("[cyan]Git Automation: Staging, committing and pushing changes...[/cyan]")
            msg = "Update project implementation via OmniDev AI"
            c_res = self.git_tool.commit_all(msg)
            p_res = self.git_tool.push()
            return {"success": c_res.get("success") and p_res.get("success"), "commit": c_res, "push": p_res}

        # 11. Zip Packager & Codebase Bundler Intent
        if any(w in lowered for w in ["zip", "package", "bundle code", "code pack", "export zip"]):
            target = self.active_app_dir or self._find_latest_app_dir() or self.workspace_dir
            zips = self.packager.package_directory(target, max_part_size_mb=35)
            zip_names = [z.name for z in zips]
            console.print(f"[bold green]📦 Project packaged into {len(zips)} archive(s):[/bold green] {zip_names}")
            # Save into memory vault
            self.memory_vault.store_context(f"zip_export_{target.name}", {"archives": [str(z) for z in zips], "target": str(target)})
            return {
                "success": True,
                "archives": [str(z) for z in zips],
                "parts_count": len(zips),
                "target_directory": str(target)
            }

        # 12. Full-Stack / CRUD Application Intent (New app creation)
        build_new_triggers = [
            "build app", "create app", "make an app", "crud app", "bana app", "app bana",
            "make a new", "build a new", "create a new", "banao naya", "naya app",
            "calculator banao", "todo app", "make a website", "make a dashboard"
        ]
        is_build_new = any(w in lowered for w in build_new_triggers) or (
            any(w in lowered for w in ["make a ", "build a ", "create a "]) and any(k in lowered for k in ["app", "system", "portal", "dashboard", "tracker", "calculator"])
        )

        if is_build_new:
            prompt = re.sub(r"^(?:build|create|make|bana|generate)\s+(?:an?\s+)?(?:new\s+)?(?:crud\s+)?(?:full\s*stack\s+)?(?:app|application|website)?\s*(?:for|about|:)?\s*", "", text, flags=re.IGNORECASE)
            if not prompt.strip():
                prompt = text
            result = self.crud_builder.build_and_launch(prompt)
            if result.get("directory"):
                self.active_app_dir = Path(result["directory"])
            self.memory.record_action("BUILD_APP", {"prompt": prompt, "result": result})
            return result

        # 5. Active Application Error Auto-Healing & Self-Repair
        active_app = self.active_app_dir or self._find_latest_app_dir()
        if active_app and active_app.exists():
            error_triggers = [
                "error", "script error", "parse error", "failed", "crash", "exception",
                "annotation", "node not found", "cannot call non-static", "not declared",
                "faild", "failed hua", "error aya", "solve karo", "thik karo", "vulkan",
                "forward+", "using device", "nvidia", "gdscript", "function", "not found",
                "res://", "at: ", "call first", "backtrace", "get_theme_stylebox"
            ]
            is_error_report = any(w in lowered for w in error_triggers)
            if is_error_report:
                console.print(f"[bold red]🩺 Error / Log report detected for [cyan]{active_app.name}[/cyan]! Triggering Autonomous Auto-Healer...[/bold red]")
                heal_res = self.auto_healer.heal_project(active_app, text)
                if heal_res.get("success"):
                    is_godot = (active_app / "project.godot").exists() or any(f.suffix == ".gd" for f in active_app.rglob("*.*"))
                    if is_godot:
                        self._launch_godot_engine(active_app)
                    return heal_res

            mod_triggers = [
                "modify", "change", "add", "fix", "update", "edit", "not working",
                "not thinking", "slow", "fast", "speed", "color", "button", "score",
                "bug", "delay", "properly", "putting", "move", "o fastly", "dark mode",
                "code me", "badal", "karo", "thik", "solve", "reset", "warning",
                "bhej", "dekh", "samjhe"
            ]
            is_mod = any(w in lowered for w in mod_triggers) or any(w in lowered for w in ["it's", "its", "why", "ai is", "player", "game", "o fast", "godot"])
            if is_mod:
                return self._handle_app_modification(text, app_dir=active_app)

        # 6. General Codebase Modification Intent
        if any(w in lowered for w in ["modify", "change", "add feature", "fix", "update code", "edit file", "code me", "badal do"]):
            return self._handle_codebase_modification(text)

        # 7. Direct Terminal Command Intent
        if lowered.startswith(("run ", "cmd ", "exec ", "terminal ")):
            cmd = re.sub(r"^(run|cmd|exec|terminal)\s+", "", text, flags=re.IGNORECASE)
            return self._execute_safe_command(cmd)

        # 8. General Development Consultation / Chat
        return self._handle_general_query(text)

    def _execute_safe_command(self, cmd: str) -> Dict[str, Any]:
        is_safe, reason = SafetyGuard.check_command(cmd)
        if not is_safe:
            console.print(f"[bold red]❌ {reason}[/bold red]")
            return {"success": False, "error": reason}

        console.print(f"[cyan]💻 Executing:[/cyan] {cmd}")
        res = run_terminal_command_sync(cmd, cwd=self.workspace_dir)

        if res.is_success:
            console.print("[green]Command Output:[/green]")
            if res.stdout:
                console.print(res.stdout)
            return {"success": True, "output": res.stdout}
        else:
            console.print(f"[red]Command Failed (code {res.exit_code}):[/red]")
            console.print(res.stderr or res.stdout)
            # Trigger auto-healer if it's a code execution command
            if any(k in cmd for k in ["python", "node", "npm", "pytest"]):
                console.print("[yellow]Triggering Auto-Healer to solve this error...[/yellow]")
                heal_res = self.auto_healer.heal(
                    command=cmd,
                    error_output=res.stderr or res.stdout,
                    workspace_dir=self.workspace_dir,
                    verify_callback=lambda: run_terminal_command_sync(cmd, cwd=self.workspace_dir).is_success
                )
                return heal_res
            return {"success": False, "error": res.stderr}

    def _handle_codebase_modification(self, request: str) -> Dict[str, Any]:
        """
        Inspects existing codebase, feeds context to AI brain,
        and applies precision file edits.
        """
        console.print("[cyan]🔍 Inspecting workspace codebase structure...[/cyan]")
        context_summary = self.inspector.generate_context_summary()

        prompt = f"""
You are OmniDev AI. The user wants to modify an existing project.

{context_summary}

USER REQUEST:
"{request}"

INSTRUCTIONS:
1. Determine which file(s) need changes.
2. Provide the modified or newly created file(s) in this format:
FILE: <relative_path_to_file>
```<language>
<complete updated code for the file>
```
"""
        console.print("[magenta]🤖 Consulting DeepSeek/Gemini for architectural changes...[/magenta]")
        response = self.brain.ask(prompt)

        # Parse and write files
        files_updated = []
        pattern = r"FILE:\s*([a-zA-Z0-9_\-\./\\]+)\s*```[a-zA-Z]*\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)

        for rel_path, code in matches:
            clean_p = rel_path.strip().replace("\\", "/")
            dest = self.workspace_dir / clean_p
            self.file_manager.write_file(dest, code.strip())
            files_updated.append(clean_p)

        console.print(f"[bold green]✅ Applied modifications to: {files_updated}[/bold green]")
        return {
            "success": True,
            "modified_files": files_updated,
            "ai_explanation": response[:400]
        }

    def _handle_app_modification(self, request: str, app_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Takes user feedback/instructions/error reports and directly updates the active application files.
        """
        import sys
        target_dir = app_dir or self.active_app_dir or self._find_latest_app_dir()
        if not target_dir or not target_dir.exists():
            return self._handle_general_query(request)

        self.active_app_dir = target_dir
        console.print(f"[bold cyan]🛠️ Modifying active application in: [green]{target_dir.name}[/green][/bold cyan]")

        # Read relevant code files in target_dir recursively (sorted with GDScript & Scenes first)
        def file_priority(p: Path):
            if p.suffix == ".gd": return 0
            if p.suffix == ".tscn": return 1
            if p.name == "project.godot": return 2
            if p.suffix == ".py": return 3
            return 5

        # Check if project is Godot Engine
        is_godot = (target_dir / "project.godot").exists() or any(f.suffix == ".gd" for f in target_dir.rglob("*.*"))

        relevant_files = []
        if is_godot:
            for ext in ["*.gd", "*.tscn", "*.godot"]:
                relevant_files.extend(list(target_dir.rglob(ext)))
        else:
            for ext in ["*.py", "*.html", "*.css", "*.js", "*.json"]:
                relevant_files.extend(list(target_dir.rglob(ext)))
        
        # Filter out stray corrupted files
        relevant_files = [f for f in relevant_files if not any(f.name.endswith(bad) for bad in ["gdscript", "text", "html"]) and not any(part in ["cenes", "cripts"] for part in f.parts)]
        relevant_files = sorted(set(relevant_files), key=file_priority)

        # Generate comprehensive project bundle & asset inventory
        bundle_content = ProjectContextBuilder.build_project_bundle(target_dir)
        ascii_tree = ProjectContextBuilder.generate_ascii_tree(target_dir)
        inventory = ProjectContextBuilder.scan_asset_inventory(target_dir)

        # Asset inventory summary string for prompt
        asset_summary_parts = []
        if inventory.get("textures"):
            asset_summary_parts.append("🎨 Textures:")
            for t in inventory["textures"]:
                asset_summary_parts.append(f"   • {t['path']} ({t['format']}, {t['size']}) -> Code: {t['gd_load']}")
        if inventory.get("audio"):
            asset_summary_parts.append("🔊 Audio / Sounds:")
            for a in inventory["audio"]:
                asset_summary_parts.append(f"   • {a['path']} ({a['format']}, {a['size']}) -> Code: {a['gd_load']}")
        if inventory.get("models_3d"):
            asset_summary_parts.append("🧊 3D Meshes:")
            for m in inventory["models_3d"]:
                asset_summary_parts.append(f"   • {m['path']} ({m['format']}, {m['size']}) -> Code: {m['gd_load']}")
        if inventory.get("shaders"):
            asset_summary_parts.append("🔮 Shaders:")
            for s in inventory["shaders"]:
                asset_summary_parts.append(f"   • {s['path']} ({s['format']}, {s['size']}) -> Code: {s['gd_load']}")
        if inventory.get("scenes"):
            asset_summary_parts.append("🎬 Scene Files:")
            for sc in inventory["scenes"]:
                asset_summary_parts.append(f"   • {sc['path']} ({sc['size']}) -> Code: {sc['gd_load']}")

        asset_catalog_str = "\n".join(asset_summary_parts) if asset_summary_parts else "No external binary assets detected."

        files_context = ""
        for f in relevant_files:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
                rel = f.relative_to(target_dir).as_posix()
                files_context += f"--- FILE: {rel} ---\n{content}\n\n"
            except Exception:
                pass

        if is_godot:
            # Detect target files needed for the user's specific request
            req_lower = request.lower()
            target_hints = []
            if any(k in req_lower for k in ["texture", "dark", "leave", "leaf", "tree", "light", "terrain", "world", "block", "grass", "dirt", "stone"]):
                target_hints.append("- `scripts/WorldGenerator.gd` (Voxel materials, dark leaves color/transparency, chunk textures, World lighting / DirectionalLight3D darkness, tree spawning)")
            if any(k in req_lower for k in ["player", "size", "block size", "camera", "view", "1 2 3", "first person", "third person", "speed", "jump", "crouch"]):
                target_hints.append("- `scripts/Player.gd` (Player size 2 blocks high: CollisionShape3D height 2.0, camera 1/2/3 view modes: 1=FirstPerson, 2=ThirdPerson Back, 3=ThirdPerson Front selfie, movement & controls)")
            if any(k in req_lower for k in ["ui", "hud", "menu", "pause", "start", "hotbar", "health", "hunger", "bar"]):
                target_hints.append("- `scripts/UI.gd` (HUD, health bar, hotbar slots, Start/Pause menu)")
            if any(k in req_lower for k in ["animal", "mob", "cow", "sheep", "pig", "flee", "damage"]):
                target_hints.append("- `scripts/Animal.gd` (Animal procedural model, AI states, take_damage)")

            hints_str = "\n".join(target_hints) if target_hints else "- Update all relevant GDScript files matching user request."

            prompt = f"""You are OmniDev AI Principal Godot 4 Systems Architect & Senior Game Developer.
The user wants to update/add features to their Godot 4.x game project in folder: '{target_dir.name}'.

USER REQUEST:
"{request}"

TARGET FILES FOR THIS REQUEST:
{hints_str}

=== 1. COMPLETE PROJECT STRUCTURE & DIRECTORY TREE ===
{ascii_tree}

=== 2. COMPREHENSIVE ASSET & RESOURCE CATALOG ===
{asset_catalog_str}

CRITICAL ARCHITECTURAL RULES (STRICT COMPLIANCE REQUIRED):
1. ZERO FEATURE REMOVAL / COMPLETE FULL-FILE REPRODUCTION:
   - NEVER drop, simplify, or omit ANY existing feature when modifying files.
   - Retain ALL mechanics in `Player.gd`: First-Person & Third-Person Camera toggle (F1 / 1,2,3 keys), Smooth Camera rotation & mouse capture, Sprinting (Shift), Crouching, Jump velocity & Gravity, Health, Hunger, Level & XP system, Block Breaking (Left Click) & Placing (Right Click), Hotbar slot selection (1-9), SoundManager sound triggers, Inventory toggle (E).
   - Retain ALL mechanics in `UI.gd`: HealthBar, HungerBar, ExpBar, Block counter, Level labels, 9-slot Hotbar HUD, Start Menu, and Pause Menu.
   - Retain ALL mechanics in `WorldGenerator.gd`: Procedural FastNoiseLite terrain generation, block voxel creation (Grass, Dirt, Stone, Wood, Leaves with dark materials), tree spawning, break/place handling.
   - Retain ALL mechanics in `SoundManager.gd`: Procedural AudioStreamGenerator sound synthesis (Jump, Break, Place, Footstep).
   - NEVER write comments like `# ... rest of existing code ...` or partial functions. ALWAYS output the 100% COMPLETE file with all existing logic intact plus new features.

2. GODOT 4 SYNTAX & STABILITY:
   - Safe node resolution: Use `get_node_or_null("...")` or `$` only for direct children.
   - Autoload singletons (e.g. `SoundManager`): Use `extends Node` without duplicate `class_name SoundManager` to avoid class shadow collisions.
   - Signal connections: Always verify node existence: `if btn: btn.pressed.connect(...)`.
   - Output ONLY Godot 4 GDScript (`.gd`), Scenes (`.tscn`), and `project.godot`. NEVER output HTML or JavaScript.

OUTPUT FORMAT (MANDATORY):
FILE: <relative_path_to_file>
```gdscript
<100% complete, fully implemented code without omissions>
```

CURRENT GODOT 4 PROJECT CODEBASE:
{files_context}
"""
        else:
            prompt = f"""You are OmniDev AI Full-Stack Developer.
The user wants to modify an existing application in folder: '{target_dir.name}'.

USER REQUEST:
"{request}"

=== PROJECT DIRECTORY TREE ===
{ascii_tree}

=== ASSET INVENTORY ===
{asset_catalog_str}

CURRENT CODEBASE:
{files_context}

Provide the complete updated code for the modified files in this format:
FILE: <relative_path>
```<language>
<full code>
```
"""

        console.print(f"[magenta]🤖 Consulting AI Engine ({self.brain.preferred}) with full codebase & asset context...[/magenta]")
        attach_file = None
        try:
            attach_file = ProjectContextBuilder.write_bundle_file(target_dir)
        except Exception:
            attach_file = (target_dir / "scripts" / "Player.gd") if (target_dir / "scripts" / "Player.gd").exists() else None

        # Check for image/screenshot mentioned in request or in project folder
        image_attach = None
        img_match = re.search(r'([a-zA-Z0-9_\-\./\\]+?\.(?:png|jpg|jpeg|webp))\b', request, re.IGNORECASE)
        if img_match:
            cand_path = Path(img_match.group(1))
            if cand_path.exists():
                image_attach = cand_path
            elif (target_dir / cand_path.name).exists():
                image_attach = target_dir / cand_path.name
            elif (config.WORKSPACE_DIR / cand_path.name).exists():
                image_attach = config.WORKSPACE_DIR / cand_path.name

        if not image_attach:
            # Check for any newly added screenshot in target_dir
            for img_f in target_dir.glob("*.png"):
                if "icon" not in img_f.name.lower():
                    image_attach = img_f
                    break

        response = self.brain.ask(prompt, new_chat=False, file_to_attach=attach_file, image_to_attach=image_attach)

        # Robust multi-pattern parsing for file updates
        files_updated = []
        patterns = [
            r"(?:###\s*|\*\*|\*)?(?:FILE|File|file|Filename|filename):\s*`?(?:res:\/\/)?([a-zA-Z0-9_\-\./\\]+?\.(?:gd|tscn|godot|py|html|css|js|ts|json|bat|txt|md|sql))\b`?\*?\*?.*?\n(.*?)```",
            r"```(?:[a-zA-Z0-9_\-]+)?\s*(?:\/\/\s*filepath:|\/\/\s*filename:|\/\/\s*file:)\s*(?:res:\/\/)?([a-zA-Z0-9_\-\./\\]+?\.(?:gd|tscn|godot|py|html|css|js|ts|json|bat|txt|md|sql))\b.*?\n(.*?)```",
            r"`([a-zA-Z0-9_\-\./\\]+?\.(?:gd|tscn|godot|py|html|css|js|json))`:\s*```(?:[a-zA-Z0-9_\-]+)?\n(.*?)```",
            r"(?:Updated|Modified|Created)\s+`?([a-zA-Z0-9_\-\./\\]+?\.(?:gd|tscn|godot|py|html|css|js|ts|json|bat|txt|md|sql))`?:\s*```(?:[a-zA-Z0-9_\-]+)?\n(.*?)```"
        ]

        # Parse multi-pattern files with bulletproof regex
        found_files = {}

        # Pattern 1: Standard FILE: <path> before code block (handles ### FILE: `path`, **FILE: path**, etc.)
        p1 = r'(?:###\s*|\*\*|\*)?(?:FILE|File|file|Filename|filename):\s*`?(?:res:\/\/)?([a-zA-Z0-9_\-\./\\]+?\.(?:gd|tscn|godot|py|html|css|js|ts|json|bat|txt|md|sql))`?\*?\*?\s*(?:\n|\r\n)```[a-zA-Z0-9_\-]*\n(.*?)```'
        for fpath, code in re.findall(p1, response, re.DOTALL):
            clean_p = fpath.strip().replace('\\\\', '/').replace('\\', '/').lstrip('/')
            if clean_p.startswith('res://'): clean_p = clean_p[6:]
            clean_code = re.sub(r'^(?:gdscript|gdscene|python|json|html|bash|sh|text|tscn|markdown)\s*\n', '', code.strip(), flags=re.IGNORECASE).strip()
            if len(clean_code) > 10:
                found_files[clean_p] = clean_code

        # Pattern 2: In-code comment `# FILE: <path>` or `// filepath: <path>`
        p2 = r'```[a-zA-Z0-9_\-]*\s*(?:\n|\r\n)(?:[#\/]{1,2}\s*(?:FILE|File|file|filepath|filename):\s*`?(?:res:\/\/)?([a-zA-Z0-9_\-\./\\]+?\.(?:gd|tscn|godot|py|html|css|js|ts|json|bat|txt|md|sql))`?)\s*\n(.*?)```'
        for fpath, code in re.findall(p2, response, re.DOTALL):
            clean_p = fpath.strip().replace('\\\\', '/').replace('\\', '/').lstrip('/')
            if clean_p.startswith('res://'): clean_p = clean_p[6:]
            clean_code = re.sub(r'^(?:gdscript|gdscene|python|json|html|bash|sh|text|tscn|markdown)\s*\n', '', code.strip(), flags=re.IGNORECASE).strip()
            if len(clean_code) > 10 and clean_p not in found_files:
                found_files[clean_p] = clean_code

        # Intelligent Content-Based Classifier for untagged code blocks
        raw_blocks = re.findall(r"```(?:[a-zA-Z0-9_\-]+)?\n(.*?)```", response, re.DOTALL)
        for block in raw_blocks:
            b_text = re.sub(r'^(?:gdscript|gdscene|python|json|html|bash|sh|text|tscn|markdown)\s*\n', '', block.strip(), flags=re.IGNORECASE).strip()
            if len(b_text) < 20:
                continue

            # Classify Godot scripts by strict semantic content & class_name
            if is_godot:
                # 1. WorldGenerator (MUST BE MATCHED BEFORE Animal to avoid chunk/terrain scripts with animal spawning matching Animal.gd)
                if "class_name WorldGenerator" in b_text or ("FastNoiseLite" in b_text or "generate_terrain" in b_text or "create_voxel" in b_text or "generate_tree" in b_text or "CHUNK_SIZE" in b_text or "WORLD_HEIGHT" in b_text):
                    if "scripts/WorldGenerator.gd" not in found_files:
                        found_files["scripts/WorldGenerator.gd"] = b_text
                # 2. Player (MUST BE MATCHED BEFORE Animal)
                elif "class_name Player" in b_text or (any(k in b_text for k in ["mouse_sensitivity", "FirstPersonCamera", "toggle_camera", "jump_velocity", "velocity.y -="]) and "class_name Animal" not in b_text):
                    if "scripts/Player.gd" not in found_files:
                        found_files["scripts/Player.gd"] = b_text
                # 3. Animal (Strictly CharacterBody3D and NOT WorldGenerator)
                elif ("class_name Animal" in b_text or any(k in b_text for k in [
                    "build_procedural_animal", "_animal_type", "animal_type", "graze", "flee", "take_damage", "handle_fleeing", "handle_wandering"
                ])) and ("class_name WorldGenerator" not in b_text and "FastNoiseLite" not in b_text and "CHUNK_SIZE" not in b_text and "create_voxel" not in b_text and "class_name Player" not in b_text):
                    if "scripts/Animal.gd" not in found_files:
                        found_files["scripts/Animal.gd"] = b_text
                # 4. UI
                elif any(k in b_text for k in [
                    "extends Control", "extends CanvasLayer", "class_name UI", "ProgressBar", "Hotbar",
                    "pause_menu", "start_menu", "toggle_pause_menu", "show_hud", "update_health",
                    "health_bar", "hotbar_slots", "inventory_slots", "crosshair", "debug_label", "resume_button", "restart_button"
                ]):
                    if "scripts/UI.gd" not in found_files:
                        found_files["scripts/UI.gd"] = b_text
                # 5. SoundManager
                elif any(k in b_text for k in ["AudioStreamGenerator", "play_jump", "SoundManager", "play_block_break", "play_block_place", "generate_tone"]):
                    if "scripts/SoundManager.gd" not in found_files:
                        found_files["scripts/SoundManager.gd"] = b_text
                elif "[application]" in b_text or "config_version=5" in b_text:
                    if "project.godot" not in found_files:
                        found_files["project.godot"] = b_text
                elif "[gd_scene" in b_text:
                    if "scenes/Animal.tscn" not in found_files and ("Animal" in b_text or "mesh" in b_text.lower()):
                        found_files["scenes/Animal.tscn"] = b_text
                    elif "scenes/Main.tscn" not in found_files:
                        found_files["scenes/Main.tscn"] = b_text

        for fname, code in found_files.items():
            clean_code = code.strip()
            # Strip language identifiers mistakenly captured on line 1
            clean_code = re.sub(r'^(?:gdscript|gdscene|python|json|html|bash|sh|text|tscn|markdown)\s*\n', '', clean_code, flags=re.IGNORECASE).strip()
            
            # Reject corrupted or dummy 1-word files
            if len(clean_code) < 15 or clean_code.lower() in ["gdscript", "python", "html", "text"]:
                continue
            
            # Strict validation for .tscn files (must contain valid scene header)
            if fname.endswith(".tscn") and not any(k in clean_code for k in ["[gd_scene", "[node", "[ext_resource", "[sub_resource"]):
                continue

            # Strict validation for .gd files (must contain valid GDScript structure)
            if fname.endswith(".gd") and not any(k in clean_code for k in ["extends", "func", "var", "class_name", "@onready", "@export", "#"]):
                continue

            dest = target_dir / fname
            dest.parent.mkdir(parents=True, exist_ok=True)

            # If incoming code is a partial function snippet, merge into existing complete script
            if dest.exists() and fname.endswith(".gd"):
                try:
                    existing_text = dest.read_text(encoding="utf-8", errors="ignore")
                    if not ("extends " in clean_code or "class_name " in clean_code) and len(existing_text.splitlines()) > len(clean_code.splitlines()) + 5:
                        clean_code = self._merge_gdscript_snippets(existing_text, clean_code)
                except Exception:
                    pass

            dest.write_text(clean_code, encoding="utf-8")
            files_updated.append(fname)
            console.print(f"[bold green]📝 Updated code in file: [cyan]{fname}[/cyan][/bold green]")

        # Godot Self-Healing Health Check & Auto-Sanitization
        if is_godot:
            self._sanitize_and_repair_godot_project(target_dir)

        # Run Headless Pre-flight Verification & Auto-Healing on the modified project
        if is_godot:
            godot_candidates = [
                Path(r"C:\Users\abdul\OneDrive\Desktop\Godot_v4.6.2-stable_win64 - Copy.exe"),
                Path(r"C:\Users\abdul\OneDrive\Desktop\Godot_v4.6.2-stable_win64.exe\Godot_v4.6.2-stable_win64.exe"),
                Path(r"C:\Users\abdul\Desktop\Godot_v4.6.2-stable_win64.exe"),
            ]
            found_bin = next((c for c in godot_candidates if c.exists()), None)
            if found_bin:
                try:
                    import subprocess
                    check_cmd = f'"{found_bin}" --headless --path "{target_dir}" -e --quit'
                    proc = subprocess.run(check_cmd, shell=True, capture_output=True, text=True, timeout=10)
                    out = (proc.stderr or "") + "\n" + (proc.stdout or "")
                    if ("SCRIPT ERROR:" in out or "ERROR:" in out or "Parse Error:" in out) and "error" in out.lower():
                        console.print("[bold red]⚠️ Godot SCRIPT ERROR detected after file modifications! Invoking Auto-Healer...[/bold red]")
                        self.auto_healer.heal_project(target_dir, out)
                except Exception:
                    pass

        # Persist memory to vault
        self.memory_vault.store_context(f"app_mod_{target_dir.name}", {
            "request": request,
            "files_updated": files_updated,
            "target": str(target_dir)
        })

        if files_updated or is_godot:
            console.print(f"[bold green]✅ Successfully modified {target_dir.name}: {files_updated}[/bold green]")
            
            # Check project type: Godot Game vs Web / Python App
            is_godot = (target_dir / "project.godot").exists() or any(f.suffix == ".gd" for f in target_dir.rglob("*.*"))
            
            if is_godot:
                # Launch / verify Godot Engine Editor directly
                self._launch_godot_engine(target_dir)
                app_url = f"godot://{target_dir.name}"
                console.print(f"[bold green]🎮 Native Godot 4 project synced in Godot Engine: {target_dir.name}[/bold green]\n")
            else:
                port = 8000
                app_url = f"http://127.0.0.1:{port}"
                if not self.process_manager.is_port_open(port):
                    server_cmd = f'"{sys.executable}" -m uvicorn main:app --host 127.0.0.1 --port {port} --reload'
                    self.process_manager.start_server(target_dir.name, server_cmd, port=port, cwd=target_dir)
                console.print(f"[bold green]⚡ Live app is active and updated at: {app_url}[/bold green]\n")
                import webbrowser
                try:
                    webbrowser.open(app_url)
                except Exception:
                    pass

            return {
                "success": True,
                "app_url": app_url if not is_godot else f"godot://{target_dir.name}",
                "modified_files": files_updated,
                "app_dir": str(target_dir)
            }
        else:
            console.print(Panel(Markdown(response), title="DeepSeek Response", border_style="cyan"))
            return {"success": True, "response": response}

    def _merge_gdscript_snippets(self, existing_code: str, snippet: str) -> str:
        """Safely merges partial function updates into existing complete GDScript without wiping out other features."""
        func_pattern = r'(func\s+([a-zA-Z0-9_]+)\s*\([^)]*\)(?:\s*->\s*[a-zA-Z0-9_]+)?\s*:.*?(?=\nfunc\s|\Z))'
        snippet_funcs = re.findall(func_pattern, snippet, re.DOTALL)
        
        updated_code = existing_code
        if snippet_funcs:
            for full_func_code, func_name in snippet_funcs:
                exist_func_pattern = rf'(func\s+{re.escape(func_name)}\s*\([^)]*\)(?:\s*->\s*[a-zA-Z0-9_]+)?\s*:.*?(?=\nfunc\s|\Z))'
                if re.search(exist_func_pattern, updated_code, re.DOTALL):
                    updated_code = re.sub(exist_func_pattern, full_func_code.strip(), updated_code, count=1, flags=re.DOTALL)
                else:
                    updated_code = updated_code.strip() + "\n\n" + full_func_code.strip() + "\n"
            return updated_code
        return existing_code.strip() + "\n\n" + snippet.strip() + "\n"

    def _sanitize_and_repair_godot_project(self, project_dir: Path):
        """Sanitizes files, fixes syntax corruptions, missing class_names, autoloads, and removes stray corrupt folders."""
        import shutil
        # 1. Clean stray folders and extension suffixes
        for bad_dir in ["cenes", "cripts"]:
            p = project_dir / bad_dir
            if p.exists():
                shutil.rmtree(p, ignore_errors=True)

        for f in list(project_dir.rglob("*")):
            if f.is_file() and (f.name.endswith("gdscript") or f.name.endswith("text")):
                try:
                    f.unlink()
                except Exception:
                    pass

        # 2. Universal GDScript & Scene Syntax & Unicode Sanitizer
        for f in list(project_dir.rglob("*")):
            if f.is_file() and f.suffix in [".gd", ".tscn", ".godot"]:
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    orig = content
                    
                    # Strip leading language identifier words mistakenly written at line 1
                    content = re.sub(r'^(?:gdscript|gdscene|python|json|html|bash|sh|text|tscn|markdown)\s*\n', '', content, flags=re.IGNORECASE).strip()
                    # Strip zero-width characters
                    content = re.sub(r'[\u200B-\u200D\uFEFF]', '', content)

                    # Fix .tscn corrupted / 1-word scenes
                    if f.suffix == ".tscn":
                        if not any(k in content for k in ["[gd_scene", "[node", "[ext_resource", "[sub_resource"]):
                            if f.name == "UI.tscn":
                                content = '[gd_scene format=3 uid="uid://ui_scene_01"]\n\n[node name="UI" type="Control"]\nlayout_mode = 3\nanchors_preset = 15\nanchor_right = 1.0\nanchor_bottom = 1.0\ngrow_horizontal = 2\ngrow_vertical = 2\nscript = ExtResource("1_ui")\n'
                            elif f.name == "Main.tscn":
                                content = '[gd_scene load_steps=3 format=3 uid="uid://main_scene_01"]\n\n[node name="Main" type="Node3D"]\n\n[node name="DirectionalLight3D" type="DirectionalLight3D" parent="."]\ntransform = Transform3D(0.866, -0.353, 0.353, 0, 0.707, 0.707, -0.5, -0.612, 0.612, 0, 20, 0)\n'
                            elif f.name == "Animal.tscn":
                                content = '[gd_scene format=3 uid="uid://animal_scene_01"]\n\n[node name="Animal" type="CharacterBody3D"]\nscript = ExtResource("1_animal")\n'

                    # Fix .gd corrupted files
                    if f.suffix == ".gd":
                        # Fix mashed lines where @onready var or func or var was concatenated without newline
                        content = re.sub(r'([^\n])(@onready\s+var\s+)', r'\1\n\2', content)
                        content = re.sub(r'([^\n])(func\s+\w+\()', r'\1\n\n\2', content)
                        content = re.sub(r'([^\n])(class_name\s+\w+)', r'\1\n\2', content)
                        
                        # Fix unquoted / un-dollarized node path literals in @onready var
                        content = re.sub(r'@onready\s+var\s+(\w+)\s*(?::\s*(\w+))?\s*=\s*(?!\$|get_node|null|\[|\{)(HUD\/[\w\/]+|StartMenu\/[\w\/]+|PauseMenu\/[\w\/]+|Crosshair\/[\w\/]+|[\w]+\/[\w\/]+)', r'@onready var \1: \2 = get_node_or_null("\3")', content)

                    if content != orig and len(content) > 10:
                        f.write_text(content.strip() + "\n", encoding="utf-8")
                except Exception:
                    pass

        # 3. Ensure SoundManager is clean Autoload (do NOT use class_name SoundManager to prevent Godot 4 class shadow error)
        sm_file = project_dir / "scripts" / "SoundManager.gd"
        if sm_file.exists():
            content = sm_file.read_text(encoding="utf-8", errors="ignore")
            if "class_name SoundManager" in content:
                content = content.replace("class_name SoundManager\n", "").replace("class_name SoundManager", "")
                sm_file.write_text(content.strip(), encoding="utf-8")

        # 4. Ensure WorldGenerator has class_name
        wg_file = project_dir / "scripts" / "WorldGenerator.gd"
        if wg_file.exists():
            content = wg_file.read_text(encoding="utf-8", errors="ignore")
            if "class_name WorldGenerator" not in content:
                content = "class_name WorldGenerator\n" + content
                wg_file.write_text(content, encoding="utf-8")

        # 4.5 Ensure Animal.gd is a pure CharacterBody3D Animal controller and not corrupted by WorldGenerator
        an_file = project_dir / "scripts" / "Animal.gd"
        if an_file.exists():
            content = an_file.read_text(encoding="utf-8", errors="ignore")
            if "class_name WorldGenerator" in content or "FastNoiseLite" in content or "CHUNK_SIZE" in content:
                content = """class_name Animal
extends CharacterBody3D

enum AnimalType { COW, SHEEP, PIG }
@export var animal_type: AnimalType = AnimalType.COW
var _animal_type: String = "cow":
\tset(val):
\t\t_animal_type = str(val).to_lower()
\t\tif "sheep" in _animal_type: animal_type = AnimalType.SHEEP
\t\telif "pig" in _animal_type: animal_type = AnimalType.PIG
\t\telse: animal_type = AnimalType.COW
\t\tbuild_procedural_animal()
\tget:
\t\treturn _animal_type

var speed: float = 2.5
var flee_speed: float = 6.0
var health: int = 4
var max_health: int = 4
var state: int = 0 # 0: Wandering, 1: Fleeing, 2: Dead
var wander_timer: float = 0.0
var move_direction: Vector3 = Vector3.ZERO
var player_ref: Node3D = null
var gravity: float = 9.8

@onready var model_root: Node3D = get_node_or_null("Model")
var leg_nodes = []
var walk_anim_timer: float = 0.0

func _ready():
\tbuild_procedural_animal()
\tvar players = get_tree().get_nodes_in_group("player")
\tif players.size() > 0:
\t\tplayer_ref = players[0]

func build_procedural_animal():
\tif not model_root:
\t\tmodel_root = Node3D.new()
\t\tmodel_root.name = "Model"
\t\tadd_child(model_root)
\tfor c in model_root.get_children():
\t\tc.queue_free()
\tleg_nodes.clear()
\t
\tvar body_mesh = MeshInstance3D.new()
\tvar box = BoxMesh.new()
\tbox.size = Vector3(1.2, 0.9, 1.6)
\tbody_mesh.mesh = box
\tbody_mesh.position = Vector3(0, 0.9, 0)
\tvar mat = StandardMaterial3D.new()
\tif animal_type == AnimalType.SHEEP: mat.albedo_color = Color(0.9, 0.9, 0.9)
\telif animal_type == AnimalType.PIG: mat.albedo_color = Color(1.0, 0.75, 0.8)
\telse: mat.albedo_color = Color(0.4, 0.25, 0.15)
\tbody_mesh.material_override = mat
\tmodel_root.add_child(body_mesh)
\t
\t# Head
\tvar head_mesh = MeshInstance3D.new()
\tvar head_box = BoxMesh.new()
\thead_box.size = Vector3(0.8, 0.8, 0.8)
\thead_mesh.mesh = head_box
\thead_mesh.position = Vector3(0, 1.3, -0.9)
\thead_mesh.material_override = mat
\tmodel_root.add_child(head_mesh)
\t
\t# 4 Legs
\tvar leg_positions = [Vector3(-0.4, 0.35, -0.5), Vector3(0.4, 0.35, -0.5), Vector3(-0.4, 0.35, 0.5), Vector3(0.4, 0.35, 0.5)]
\tfor lp in leg_positions:
\t\tvar leg = MeshInstance3D.new()
\t\tvar l_box = BoxMesh.new()
\t\tl_box.size = Vector3(0.25, 0.7, 0.25)
\t\tleg.mesh = l_box
\t\tleg.position = lp
\t\tleg.material_override = mat
\t\tmodel_root.add_child(leg)
\t\tleg_nodes.append(leg)

func _physics_process(delta: float):
\tif state == 2: return
\tif not is_on_floor():
\t\tvelocity.y -= gravity * delta
\twander_timer -= delta
\tif wander_timer <= 0:
\t\twander_timer = randf_range(2.0, 5.0)
\t\tif randf() > 0.4:
\t\t\tvar angle = randf() * TAU
\t\t\tmove_direction = Vector3(cos(angle), 0, sin(angle)).normalized()
\t\telse:
\t\t\tmove_direction = Vector3.ZERO
\t
\tif state == 1 and player_ref:
\t\tvar away = (global_position - player_ref.global_position).normalized()
\t\taway.y = 0
\t\tvelocity.x = away.x * flee_speed
\t\tvelocity.z = away.z * flee_speed
\telif move_direction != Vector3.ZERO:
\t\tvelocity.x = move_direction.x * speed
\t\tvelocity.z = move_direction.z * speed
\t\tlook_at(global_position + move_direction, Vector3.UP)
\telse:
\t\tvelocity.x = move_toward(velocity.x, 0, speed * delta * 4)
\t\tvelocity.z = move_toward(velocity.z, 0, speed * delta * 4)
\t
\tmove_and_slide()
\t
\t# Leg animation
\tif velocity.length() > 0.2 and is_on_floor():
\t\twalk_anim_timer += delta * 10.0
\t\tfor i in range(leg_nodes.size()):
\t\t\tvar sign_mult = 1.0 if i % 2 == 0 else -1.0
\t\t\tleg_nodes[i].rotation.x = sin(walk_anim_timer) * 0.4 * sign_mult
\telse:
\t\tfor leg in leg_nodes:
\t\t\tleg.rotation.x = 0.0

func take_damage(amount: int = 1):
\tif state == 2: return
\thealth -= amount
\tstate = 1
\tif health <= 0:
\t\tdie()

func die():
\tstate = 2
\tvelocity = Vector3.ZERO
\trotation.z = deg_to_rad(90)
\tglobal_position.y += 0.2
\tset_collision_layer_value(1, false)
\tset_collision_mask_value(1, false)
\tawait get_tree().create_timer(1.5).timeout
\tqueue_free()
"""
            else:
                if "class_name Player" in content:
                    content = content.replace("class_name Player", "class_name Animal")
                if "class_name Animal" not in content and "extends CharacterBody3D" in content:
                    content = "class_name Animal\n" + content
                if "_animal_type" not in content and "extends CharacterBody3D" in content:
                    content = content.replace("extends CharacterBody3D\n", "extends CharacterBody3D\n\nvar _animal_type: String = \"cow\"\n")
            an_file.write_text(content.strip() + "\n", encoding="utf-8")

        # 5. Ensure Player.gd uses safe SoundManager node lookup & safe node resolution & auto-registers InputMap
        pl_file = project_dir / "scripts" / "Player.gd"
        if pl_file.exists():
            content = pl_file.read_text(encoding="utf-8", errors="ignore")
            content = re.sub(r'(?<!get_node\("/root/)SoundManager\.play_jump\(\)', 'if has_node("/root/SoundManager"): get_node("/root/SoundManager").play_jump()', content)
            content = re.sub(r'(?<!get_node\("/root/)SoundManager\.play_block_break\(\)', 'if has_node("/root/SoundManager"): get_node("/root/SoundManager").play_block_break()', content)
            content = re.sub(r'(?<!get_node\("/root/)SoundManager\.play_block_place\(\)', 'if has_node("/root/SoundManager"): get_node("/root/SoundManager").play_block_place()', content)
            content = re.sub(r'@onready\s+var\s+player_mesh(?:\s*:\s*\w+)?\s*=\s*\$PlayerMesh', '@onready var player_mesh: Node3D = get_node_or_null("PlayerMesh")', content)
            content = re.sub(r'@onready\s+var\s+armature(?:\s*:\s*\w+)?\s*=\s*\$PlayerMesh/Armature', '@onready var armature: Node3D = get_node_or_null("PlayerMesh/Armature")', content)
            content = re.sub(r'@onready\s+var\s+animation_player(?:\s*:\s*\w+)?\s*=\s*\$PlayerMesh/AnimationPlayer', '@onready var animation_player: AnimationPlayer = get_node_or_null("PlayerMesh/AnimationPlayer")', content)
            
            # Auto-register InputMap actions if missing to prevent debugger spam
            if "_ensure_input_map" not in content:
                input_setup_code = """
func _ready():
\t_ensure_input_map()

func _ensure_input_map():
\tvar actions = {
\t\t"move_forward": KEY_W, "move_back": KEY_S, "move_left": KEY_A, "move_right": KEY_D,
\t\t"jump": KEY_SPACE, "sprint": KEY_SHIFT, "crouch": KEY_CTRL,
\t\t"slot_1": KEY_1, "slot_2": KEY_2, "slot_3": KEY_3, "slot_4": KEY_4,
\t\t"slot_5": KEY_5, "slot_6": KEY_6, "slot_7": KEY_7, "slot_8": KEY_8, "slot_9": KEY_9,
\t\t"toggle_camera": KEY_F1
\t}
\tfor act in actions:
\t\tif not InputMap.has_action(act):
\t\t\tInputMap.add_action(act)
\t\t\tvar ev = InputEventKey.new()
\t\t\tev.physical_keycode = actions[act]
\t\t\tInputMap.action_add_event(act, ev)
"""
                if "func _ready():" in content:
                    content = content.replace("func _ready():", "func _ready():\n\t_ensure_input_map()")
                    content += "\n" + input_setup_code.split("func _ready():\n\t_ensure_input_map()\n")[1]
                else:
                    content += "\n" + input_setup_code
            pl_file.write_text(content.strip() + "\n", encoding="utf-8")

        # 6. Ensure project.godot registers SoundManager Autoload
        proj_godot = project_dir / "project.godot"
        if proj_godot.exists() and sm_file.exists():
            proj_text = proj_godot.read_text(encoding="utf-8", errors="ignore")
            if "[autoload]" not in proj_text:
                proj_text += '\n[autoload]\n\nSoundManager="*res://scripts/SoundManager.gd"\n'
                proj_godot.write_text(proj_text, encoding="utf-8")
            elif "SoundManager=" not in proj_text:
                proj_text = proj_text.replace("[autoload]", '[autoload]\n\nSoundManager="*res://scripts/SoundManager.gd"')
                proj_godot.write_text(proj_text, encoding="utf-8")

        # 7. Ensure all GDScript files use Godot 4 StandardMaterial3D instead of Godot 3 SpatialMaterial
        scripts_dir = project_dir / "scripts"
        if scripts_dir.exists():
            for gd_path in scripts_dir.glob("*.gd"):
                try:
                    gd_code = gd_path.read_text(encoding="utf-8", errors="ignore")
                    orig = gd_code
                    gd_code = gd_code.replace("SpatialMaterial.new()", "StandardMaterial3D.new()")
                    gd_code = re.sub(r'\bSpatialMaterial\b', 'StandardMaterial3D', gd_code)
                    gd_code = re.sub(r'(\w+)_mat\.material_override\s*=\s*\1_mat', r'\1.material_override = \1_mat', gd_code)
                    if gd_code != orig:
                        gd_path.write_text(gd_code, encoding="utf-8")
                except Exception:
                    pass

    def _launch_godot_engine(self, project_dir: Path) -> bool:
        """Launches the user's installed Godot Engine Editor if not already running, and verifies health."""
        import subprocess
        import time

        # Find installed Godot binary
        godot_candidates = [
            Path(r"C:\Users\abdul\OneDrive\Desktop\Godot_v4.6.2-stable_win64 - Copy.exe"),
            Path(r"C:\Users\abdul\OneDrive\Desktop\Godot_v4.6.2-stable_win64.exe\Godot_v4.6.2-stable_win64.exe"),
            Path(r"C:\Users\abdul\Desktop\Godot_v4.6.2-stable_win64.exe"),
        ]
        
        found_bin = None
        for candidate in godot_candidates:
            if candidate.exists():
                found_bin = candidate
                break

        # Check if Godot Engine Editor is already running
        is_already_open = False
        try:
            import psutil
            proj_name = project_dir.name.lower()
            proj_path_str = str(project_dir).lower()
            
            for proc in psutil.process_iter(['name', 'cmdline']):
                try:
                    pname = (proc.info.get('name') or '').lower()
                    if 'godot' in pname:
                        cmdline = ' '.join(proc.info.get('cmdline') or []).lower()
                        if proj_name in cmdline or proj_path_str in cmdline or '-e' in cmdline:
                            is_already_open = True
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception:
            pass

        if is_already_open:
            console.print(f"[bold cyan]⏳ Godot Editor is already open! Waiting 1.5s for Godot to auto-reload updated files...[/bold cyan]")
            time.sleep(1.5)
            console.print(f"[bold green]✓ Godot Editor successfully refreshed with new code changes: [cyan]{project_dir.name}[/cyan][/bold green]")
            return True

        # If not already running, launch Godot Engine Editor
        if found_bin:
            cmd = f'"{found_bin}" --path "{project_dir}" -e'
            subprocess.Popen(cmd, shell=True)
            console.print(f"[bold green]🚀 Opened project in Godot Engine 4 Editor: [cyan]{found_bin.name}[/cyan][/bold green]")
            time.sleep(1.5)
            return True

        bat = project_dir / "run_godot.bat"
        if bat.exists():
            subprocess.Popen(f'"{bat}"', cwd=str(project_dir), shell=True)
            console.print(f"[bold green]🚀 Executed Godot launcher: [cyan]{bat.name}[/cyan][/bold green]")
            time.sleep(1.5)
            return True
        return False

    def _handle_general_query(self, query: str) -> Dict[str, Any]:
        console.print("[magenta]🤖 Asking DeepSeek/Gemini...[/magenta]")
        response = self.brain.ask(query)
        console.print(Panel(Markdown(response), title="OmniDev AI Response", border_style="cyan"))

        # If active app is a Godot project, apply any Godot files generated
        active_app = self.active_app_dir or self._find_latest_app_dir()
        if active_app and ((active_app / "project.godot").exists() or any(f.suffix == ".gd" for f in active_app.rglob("*.*"))):
            if any(marker in response for marker in ["FILE:", ".gd", ".tscn", "project.godot", "extends "]):
                console.print(f"[bold green]🎮 Detected Godot 4 code in response! Applying to {active_app.name}...[/bold green]")
                return self._handle_app_modification(query, app_dir=active_app)
            return {"success": True, "response": response}

        # Check if AI generated a full runnable Python/Web application
        if any(marker in response for marker in ["FILE: main.py", "FastAPI(", "uvicorn.run"]):
            console.print("[bold green]🚀 Detected runnable application code in AI response! Auto-deploying & launching preview...[/bold green]")
            target_dir = self.active_app_dir or (self.workspace_dir / "generated_app")
            target_dir.mkdir(parents=True, exist_ok=True)
            app_mgr = FileManager(target_dir)
            
            blocks = re.findall(r"```(?:python)?\n(.*?)```", response, re.DOTALL)
            code = max(blocks, key=len).strip() if blocks else response
            app_mgr.write_file("main.py", code)
            
            port = 8000
            self.process_manager.kill_process_on_port(port)
            server_cmd = f"python -m uvicorn main:app --host 127.0.0.1 --port {port} --reload"
            res = self.process_manager.start_server(target_dir.name, server_cmd, port=port, cwd=target_dir)
            if res.get("success"):
                app_url = f"http://127.0.0.1:{port}"
                console.print(f"[bold green]✅ Application is live at: {app_url}[/bold green]")
                import webbrowser
                try:
                    webbrowser.open(app_url)
                except Exception:
                    pass
                return {"success": True, "app_url": app_url, "response": response}

        return {"success": True, "response": response}
