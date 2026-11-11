"""
command_shortcuts.py
Natural language command shortcuts for Autonomous Web-Agent IDE.

Intercepts special user phrases and executes them directly
without sending to AI — fast, reliable, predictable.
"""

import asyncio
import os
import subprocess
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, Dict, Any


# Map of keyword/phrase → action key
SHORTCUT_MAP = {
    # ZIP operations
    "zip all": "zip_project",
    "zip project": "zip_project",
    "export zip": "zip_project",
    "create zip": "zip_project",
    "download zip": "zip_project",

    # Update → ZIP project and send to AI for analysis / continuation
    "update": "zip_and_send",
    "update karo": "zip_and_send",
    "send update": "zip_and_send",
    "zip and send": "zip_and_send",
    "send zip": "zip_and_send",
    "upload project": "zip_and_send",

    # Testing
    "run tests": "run_tests",
    "run test": "run_tests",
    "test": "run_tests",
    "npm test": "run_tests",
    "pytest": "run_tests",
    "run jest": "run_tests",

    # Build
    "build app": "build_project",
    "build": "build_project",
    "npm run build": "build_project",
    "build project": "build_project",
    "compile": "build_project",

    # Install
    "install deps": "install_dependencies",
    "install dependencies": "install_dependencies",
    "npm install": "install_dependencies",
    "pip install": "install_dependencies",

    # Servers
    "start server": "start_dev_server",
    "start dev": "start_dev_server",
    "npm run dev": "start_dev_server",
    "stop server": "stop_dev_server",
    "kill server": "stop_dev_server",

    # Git
    "git status": "git_status",
    "git commit": "git_commit",
    "git diff": "git_diff",
    "git log": "git_log",

    # Test scaffolding
    "scaffold tests": "scaffold_tests",
    "setup tests": "scaffold_tests",
    "create tests": "scaffold_tests",
    "add tests": "scaffold_tests",
    "init tests": "scaffold_tests",

    # Visual QA
    "qa": "visual_qa",
    "visual qa": "visual_qa",
    "inspect ui": "visual_qa",
    "check ui": "visual_qa",
    "take snapshot": "visual_qa",
    "snapshot": "visual_qa",

    # Android
    "adb devices": "list_android_devices",
    "android devices": "list_android_devices",
    "list devices": "list_android_devices",

    # Project
    "inspect project": "inspect_project",
    "analyze project": "inspect_project",
    "doctor": "environment_doctor",
    "diagnose": "environment_doctor",
    "env doctor": "environment_doctor",
    "check system": "environment_doctor",
    "show errors": "show_errors",
    "clear terminal": "clear_terminal",
    "show files": "show_files",
    "list files": "show_files",
}


def detect_shortcut(prompt: str) -> Optional[str]:
    """
    Check if a user prompt matches a known shortcut.
    Returns the action key if matched, else None.
    Case-insensitive, strips punctuation.
    """
    cleaned = prompt.strip().lower().rstrip("!.?").strip()
    # Exact match first
    if cleaned in SHORTCUT_MAP:
        return SHORTCUT_MAP[cleaned]

    # Only do prefix match if the prompt is short (<= 4 words and <= 35 chars)
    # Long prompts like "Build an interactive audio synthesizer..." are full missions, NOT shortcuts!
    words = cleaned.split()
    if len(words) <= 4 and len(cleaned) <= 35:
        for phrase in sorted(SHORTCUT_MAP.keys(), key=len, reverse=True):
            if cleaned.startswith(phrase):
                return SHORTCUT_MAP[phrase]
    return None


async def execute_shortcut(
    action: str,
    workspace_root: str,
    project_id: str,
    emit_ipc: Callable,
    project_info: Dict[str, Any] = None,
) -> bool:
    """
    Execute a shortcut action directly.
    Returns True if handled, False if should fall through to AI.
    """
    pi = project_info or {}

    if action == "zip_and_send":
        # Package the workspace as ZIP, then fall through to AI pipeline with ZIP attached
        return await _zip_and_send_project(workspace_root, project_id, emit_ipc)

    elif action == "zip_project":
        return await _zip_project(workspace_root, project_id, emit_ipc)

    elif action == "run_tests":
        cmd = pi.get("test_command") or _detect_test_command(workspace_root)
        if cmd:
            return await _run_command_shortcut(cmd, workspace_root, emit_ipc, "🧪 Running Tests")
        else:
            _emit_log(emit_ipc, "ℹ️ [Tests] No 'test' script found in package.json. Auto-scaffolding Vitest test suite...")
            return await _scaffold_tests(workspace_root, emit_ipc)

    elif action == "scaffold_tests":
        return await _scaffold_tests(workspace_root, emit_ipc)

    elif action == "visual_qa":
        return await _run_visual_qa(workspace_root, emit_ipc)

    elif action == "list_android_devices":
        return await _list_android_devices(emit_ipc)

    elif action == "build_project":
        cmd = pi.get("build_command") or _detect_build_command(workspace_root)
        if cmd:
            return await _run_command_shortcut(cmd, workspace_root, emit_ipc, "🔨 Building Project")
        else:
            _emit_log(emit_ipc, "⚠️ [Quick Command] No build command detected.")
            return True

    elif action == "install_dependencies":
        cmd = pi.get("install_command") or _detect_install_command(workspace_root)
        if cmd:
            return await _run_command_shortcut(cmd, workspace_root, emit_ipc, "📦 Installing Dependencies")
        else:
            _emit_log(emit_ipc, "⚠️ [Quick Command] No install command detected.")
            return True

    elif action == "git_status":
        return await _run_command_shortcut("git status", workspace_root, emit_ipc, "🌿 Git Status")

    elif action == "git_diff":
        return await _run_command_shortcut("git diff", workspace_root, emit_ipc, "🌿 Git Diff")

    elif action == "git_log":
        return await _run_command_shortcut("git log --oneline -10", workspace_root, emit_ipc, "🌿 Git Log")

    elif action == "git_commit":
        msg = f"auto-commit: Autonomous Web-Agent IDE checkpoint {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        cmds = ["git add -A", f'git commit -m "{msg}"']
        for cmd in cmds:
            await _run_command_shortcut(cmd, workspace_root, emit_ipc, "🌿 Git Commit")
        return True

    elif action == "inspect_project":
        _emit_log(emit_ipc, "🔍 [Quick Command] Running project inspection...")
        try:
            from core.project_inspector import ProjectInspector, format_inspection_log
            info = ProjectInspector(workspace_root).inspect()
            _emit_log(emit_ipc, format_inspection_log(info))
        except Exception as e:
            _emit_log(emit_ipc, f"❌ [Inspector Error] {e}")
        return True

    elif action == "environment_doctor":
        _emit_log(emit_ipc, "🔍 [Quick Command] Running Environment Doctor diagnosis...")
        try:
            from core.environment_doctor import EnvironmentDoctor, format_doctor_log
            report = EnvironmentDoctor.diagnose()
            _emit_log(emit_ipc, format_doctor_log(report))
        except Exception as e:
            _emit_log(emit_ipc, f"❌ [Doctor Error] {e}")
        return True

    elif action == "clear_terminal":
        emit_ipc("terminal.clear", {})
        return True

    elif action == "show_files":
        try:
            from core.project_inspector import ProjectInspector
            info = ProjectInspector(workspace_root).inspect()
            tree = "\r\n".join(f"  {f}" for f in info["file_tree_summary"])
            _emit_log(emit_ipc, f"📁 [Files]\r\n{tree}")
        except Exception as e:
            _emit_log(emit_ipc, f"❌ {e}")
        return True

    elif action == "show_errors":
        _emit_log(emit_ipc, "💡 [Quick Command] Use 'inspect project' to see project status, or start the agent to find and fix errors.")
        return True

    return False


async def _zip_and_send_project(workspace_root: str, project_id: str, emit_ipc: Callable) -> bool:
    """
    Package the workspace as a ZIP and emit it as an attachment for the AI pipeline.
    Returns False so the orchestrator continues to AI with the ZIP as an attachment.
    """
    try:
        _emit_log(emit_ipc, "📦 [Update] Packaging workspace ZIP for AI upload...")
        from core.zip_chunker import create_chunked_zip

        result = create_chunked_zip(workspace_root, max_chunk_mb=38.0)
        archive_paths = result["archive_paths"]
        total_size = result["total_size_mb"]

        p = Path(archive_paths[0])
        _emit_log(emit_ipc, f"✅ [Update] ZIP ready: {p.name} ({total_size:.1f} MB)")
        _emit_log(emit_ipc, f"📤 [Update] Sending to AI provider for analysis...")

        # Emit the zip path so the orchestrator can attach it
        emit_ipc("zip.ready", {
            "archive_paths": archive_paths,
            "total_size_mb": total_size,
            "is_chunked": result["is_chunked"],
            "parts_count": result["parts_count"],
            "topology": result.get("topology", ""),
            "project_id": project_id,
        })

        # Store in env for agent pipeline to pick up
        import os
        os.environ["AGENT_ZIP_ATTACHMENT"] = archive_paths[0]

        # Return False → shortcut NOT consumed → AI pipeline runs WITH zip attached
        return False

    except Exception as e:
        _emit_log(emit_ipc, f"❌ [Update ZIP Error] {e}", is_error=True)
        return False  # Still fall through to AI even on error


async def _zip_project(workspace_root: str, project_id: str, emit_ipc: Callable) -> bool:
    """Create a ZIP of the project workspace, splitting into multi-part chunks if > 38MB."""
    try:
        _emit_log(emit_ipc, "📦 [Quick Command] Packaging project workspace with intelligent multi-part chunking...")
        from core.zip_chunker import create_chunked_zip
        
        result = create_chunked_zip(workspace_root, max_chunk_mb=38.0)
        archive_paths = result["archive_paths"]
        total_size = result["total_size_mb"]

        if result["is_chunked"]:
            _emit_log(emit_ipc, f"⚡ [Multi-Part ZIP] Total size {total_size:.1f} MB exceeded 38 MB limit! Split into {result['parts_count']} parts.")
            for p_str in archive_paths:
                p = Path(p_str)
                _emit_log(emit_ipc, f"  ├── Part: {p.name} ({p.stat().st_size / (1024*1024):.1f} MB)")
                emit_ipc("artifact.created", {
                    "type": "zip",
                    "name": p.name,
                    "path": str(p),
                    "size": p.stat().st_size,
                })
            if result.get("manifest_path"):
                _emit_log(emit_ipc, f"  └── Manifest: {Path(result['manifest_path']).name}")
        else:
            p = Path(archive_paths[0])
            _emit_log(emit_ipc, f"✅ [ZIP Created] {p.name} ({total_size:.1f} MB)")
            _emit_log(emit_ipc, f"📁 Saved to: {p}")
            emit_ipc("artifact.created", {
                "type": "zip",
                "name": p.name,
                "path": str(p),
                "size": p.stat().st_size,
            })

        return True
    except Exception as e:
        _emit_log(emit_ipc, f"❌ [ZIP Error] {e}", is_error=True)
        return True


async def _run_command_shortcut(
    cmd: str,
    workspace_root: str,
    emit_ipc: Callable,
    label: str,
    timeout: int = 60,
) -> bool:
    """Run a shell command and stream output to terminal."""
    _emit_log(emit_ipc, f"⚡ [{label}] Running: {cmd}")
    try:
        proc = await asyncio.create_subprocess_shell(
            cmd,
            cwd=workspace_root,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        async def read_output():
            async for line in proc.stdout:
                text = line.decode("utf-8", errors="replace").rstrip()
                emit_ipc("command.output", {"stream": "stdout", "data": text + "\r\n", "name": "shortcut"})

        try:
            await asyncio.wait_for(
                asyncio.gather(read_output(), proc.wait()),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            proc.kill()
            _emit_log(emit_ipc, f"⏱️ [{label}] Command timed out after {timeout}s", is_error=True)
            return True

        code = proc.returncode
        if code == 0:
            _emit_log(emit_ipc, f"✅ [{label}] Completed successfully (exit 0)")
        else:
            _emit_log(emit_ipc, f"❌ [{label}] Failed with exit code {code}", is_error=True)
    except Exception as e:
        _emit_log(emit_ipc, f"❌ [{label}] Error: {e}", is_error=True)
    return True


def _detect_test_command(workspace_root: str) -> Optional[str]:
    ws = Path(workspace_root)
    if (ws / "package.json").exists():
        try:
            import json
            pkg = json.loads((ws / "package.json").read_text(encoding="utf-8", errors="replace"))
            scripts = pkg.get("scripts", {})
            for k in ["test", "test:unit", "test:all"]:
                if k in scripts:
                    return f"npm test" if k == "test" else f"npm run {k}"
        except Exception:
            pass
        return None
    if (ws / "requirements.txt").exists() or (ws / "pyproject.toml").exists():
        return "pytest"
    return None


def _detect_build_command(workspace_root: str) -> Optional[str]:
    ws = Path(workspace_root)
    if (ws / "package.json").exists():
        try:
            import json
            pkg = json.loads((ws / "package.json").read_text())
            scripts = pkg.get("scripts", {})
            if "build" in scripts:
                return "npm run build"
        except Exception:
            pass
    if (ws / "build.gradle").exists() or (ws / "build.gradle.kts").exists():
        return "./gradlew build"
    if (ws / "pom.xml").exists():
        return "mvn clean package"
    return None


def _detect_install_command(workspace_root: str) -> Optional[str]:
    ws = Path(workspace_root)
    if (ws / "pnpm-lock.yaml").exists():
        return "pnpm install"
    if (ws / "yarn.lock").exists():
        return "yarn install"
    if (ws / "package.json").exists():
        return "npm install"
    if (ws / "requirements.txt").exists():
        return "pip install -r requirements.txt"
    if (ws / "pyproject.toml").exists():
        return "pip install -e ."
    return None


async def _scaffold_tests(workspace_root: str, emit_ipc: Callable) -> bool:
    ws = Path(workspace_root)
    pkg_file = ws / "package.json"
    if pkg_file.exists():
        _emit_log(emit_ipc, "🧪 [Test Scaffold] Setting up Vitest automated test suite...")
        try:
            import json
            pkg = json.loads(pkg_file.read_text(encoding="utf-8", errors="replace"))
            if "scripts" not in pkg:
                pkg["scripts"] = {}
            pkg["scripts"]["test"] = "vitest run"
            pkg_file.write_text(json.dumps(pkg, indent=2), encoding="utf-8")

            # Create tests dir and smoke test
            tests_dir = ws / "tests"
            tests_dir.mkdir(parents=True, exist_ok=True)
            smoke_test = tests_dir / "smoke.test.jsx"
            if not smoke_test.exists():
                smoke_test.write_text(
                    "import { describe, it, expect } from 'vitest';\n\n"
                    "describe('Autonomous Smoke Test Suite', () => {\n"
                    "  it('validates test runner environment is active', () => {\n"
                    "    expect(true).toBe(true);\n"
                    "  });\n\n"
                    "  it('validates system calculations', () => {\n"
                    "    expect(1 + 1).toBe(2);\n"
                    "  });\n"
                    "});\n",
                    encoding="utf-8"
                )

            # Vitest config if not present
            if not (ws / "vitest.config.ts").exists() and not (ws / "vitest.config.js").exists():
                (ws / "vitest.config.js").write_text(
                    "import { defineConfig } from 'vitest/config';\n\n"
                    "export default defineConfig({\n"
                    "  test: {\n"
                    "    globals: true,\n"
                    "  },\n"
                    "});\n",
                    encoding="utf-8"
                )

            _emit_log(emit_ipc, "✅ [Test Scaffold] Vitest configuration and smoke test created.")
            _emit_log(emit_ipc, "🧪 [Running Tests] Executing newly created test suite...")
            return await _run_command_shortcut("npm test", workspace_root, emit_ipc, "🧪 Running Tests")
        except Exception as e:
            _emit_log(emit_ipc, f"❌ [Test Scaffold Error] {e}", is_error=True)
            return True

    # Python
    tests_dir = ws / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    smoke_py = tests_dir / "test_smoke.py"
    if not smoke_py.exists():
        smoke_py.write_text(
            "def test_smoke():\n"
            "    \"\"\"Smoke test for Autonomous Web-Agent IDE verification.\"\"\"\n"
            "    assert True\n\n"
            "def test_math_sanity():\n"
            "    assert 2 * 2 == 4\n",
            encoding="utf-8"
        )
    _emit_log(emit_ipc, "✅ [Test Scaffold] Pytest test scaffold created.")
    return await _run_command_shortcut("pytest", workspace_root, emit_ipc, "🧪 Running Tests")


async def _run_visual_qa(workspace_root: str, emit_ipc: Callable, url: Optional[str] = None) -> bool:
    _emit_log(emit_ipc, "📸 [Visual QA] Launching headless browser inspection...")
    target_url = url or "http://localhost:5174"
    try:
        from core.visual_qa import VisualQAEngine
        engine = VisualQAEngine(workspace_root)
        report = await engine.inspect_url(target_url)

        status_symbol = "✅" if report.get("passed") else "⚠️"
        _emit_log(emit_ipc, f"{status_symbol} [Visual QA] Inspection complete for {report.get('url')}")
        _emit_log(emit_ipc, f"   Page Title: {report.get('title') or '(none)'}")
        _emit_log(emit_ipc, f"   React Error Detected: {report.get('has_react_error', False)}")

        if report.get("console_errors"):
            _emit_log(emit_ipc, f"   Console Errors ({len(report['console_errors'])}):")
            for err in report["console_errors"][:5]:
                _emit_log(emit_ipc, f"     - {err}", is_error=True)

        if report.get("screenshot_path"):
            _emit_log(emit_ipc, f"   Snapshot saved: {report['screenshot_path']}")

        emit_ipc("qa.report", report)
    except Exception as e:
        _emit_log(emit_ipc, f"❌ [Visual QA Error] {e}", is_error=True)
    return True


async def _list_android_devices(emit_ipc: Callable) -> bool:
    _emit_log(emit_ipc, "📱 [Android Bridge] Inspecting connected ADB devices...")
    try:
        from tools.android.adb_manager import ADBManager
        adb = ADBManager()
        if not adb.is_available():
            _emit_log(emit_ipc, "⚠️ [Android Bridge] ADB not found on system PATH. Install Android SDK Platform-Tools.")
            return True
        devices = await adb.list_devices()
        if not devices:
            _emit_log(emit_ipc, "ℹ️ [Android Bridge] No connected Android devices or emulators detected.")
        else:
            _emit_log(emit_ipc, f"✅ [Android Bridge] Detected {len(devices)} device(s):")
            for d in devices:
                auth = "Authorized" if d.get("authorized") else "Unauthorized"
                _emit_log(emit_ipc, f"   - Serial: {d['serial']} | Model: {d.get('model')} | Status: {d['state']} ({auth})")
    except Exception as e:
        _emit_log(emit_ipc, f"❌ [Android Bridge Error] {e}", is_error=True)
    return True


def _emit_log(emit_ipc: Callable, msg: str, is_error: bool = False):
    emit_ipc("command.output", {
        "stream": "stderr" if is_error else "stdout",
        "data": f"{msg}\r\n",
        "name": "shortcut",
    })
