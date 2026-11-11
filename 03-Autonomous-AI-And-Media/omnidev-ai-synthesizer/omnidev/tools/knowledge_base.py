import os
import re
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

from config import console, OMNIDEV_DIR
from tools.terminal import run_terminal_command_sync
from tools.file_manager import FileManager
from tools.process_manager import ProcessManager

class ErrorKnowledgeBase:
    """
    Autonomous Self-Learning Knowledge Base for OmniDev AI.
    
    1. Instant Local Fixes: Automatically fixes common errors (missing pip/npm packages,
       UnicodeDecodeError, port conflicts, missing files) in 0.1s without asking DeepSeek.
    2. Self-Learning Memory: Whenever DeepSeek or local fixes resolve an error, the solution
       is cached in 'error_memory.json'. In the future, OmniDev fixes the same problem
       instantly on its own without consuming AI tokens or browser calls!
    """
    def __init__(self, memory_file: Optional[Path] = None):
        self.memory_file = memory_file or (OMNIDEV_DIR / "error_memory.json")
        self.data: Dict[str, Any] = {
            "version": "1.0",
            "learned_solutions": {},
            "error_stats": {}
        }
        self._load()

    def _load(self):
        if self.memory_file.exists():
            try:
                self.data = json.loads(self.memory_file.read_text(encoding="utf-8"))
            except Exception:
                pass

    def save(self):
        try:
            self.memory_file.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
        except Exception:
            pass

    def normalize_error(self, error_text: str) -> str:
        """
        Extracts a clean, normalized error signature for matching.
        """
        lines = [line.strip() for line in error_text.splitlines() if line.strip()]
        for line in reversed(lines):
            if any(err in line for err in [
                "Error:", "Exception:", "errno", "failed", "404", "500", "Traceback"
            ]):
                cleaned = re.sub(r'0x[0-9a-fA-F]+', '0x...', line)
                cleaned = re.sub(r'line \d+', 'line X', cleaned)
                return cleaned[:150]
        return (lines[-1] if lines else "Unknown Error")[:150]

    def try_local_auto_fix(self, error_output: str, workspace_dir: Path) -> Optional[str]:
        """
        Attempts to fix the error locally in 0.1s without calling DeepSeek/AI.
        Returns a description of the applied fix, or None if unknown.
        """
        file_mgr = FileManager(workspace_dir)

        # 1. Missing Python Module / Dependency
        py_mod_match = re.search(r"(?:ModuleNotFoundError|ImportError):\s*No module named ['\"]([^'\"]+)['\"]", error_output)
        if not py_mod_match:
            py_mod_match = re.search(r"cannot import name \S+ from ['\"]([^'\"]+)['\"]", error_output)
        if py_mod_match:
            pkg_name = py_mod_match.group(1).split(".")[0]
            console.print(f"[bold cyan]🧠 [Autonomous Memory] Detected missing Python package: '{pkg_name}'. Auto-installing...[/bold cyan]")
            run_terminal_command_sync(f"pip install {pkg_name} -q", timeout=60)
            return f"Auto-installed missing Python package '{pkg_name}'"

        # 2. Missing Node.js Module
        node_mod_match = re.search(r"Cannot find module ['\"]([^'\"]+)['\"]", error_output)
        if node_mod_match:
            pkg_name = node_mod_match.group(1)
            console.print(f"[bold cyan]🧠 [Autonomous Memory] Detected missing Node module: '{pkg_name}'. Auto-installing...[/bold cyan]")
            run_terminal_command_sync(f"npm install {pkg_name} --save", cwd=workspace_dir, timeout=60)
            return f"Auto-installed missing Node module '{pkg_name}'"

        # 3. Windows UnicodeDecodeError ('charmap' / cp1252 / emojis in HTML or files)
        if "UnicodeDecodeError" in error_output or "'charmap' codec can't decode" in error_output:
            console.print("[bold cyan]🧠 [Autonomous Memory] Detected Windows cp1252 Unicode issue. Patching all file open calls with UTF-8...[/bold cyan]")
            patched = False
            for py_file in workspace_dir.glob("**/*.py"):
                try:
                    content = py_file.read_text(encoding="utf-8", errors="ignore")
                    fixed = re.sub(
                        r'\bopen\(([^)]+)\)',
                        lambda m: m.group(0) if "encoding" in m.group(1) or "wb" in m.group(1) or "rb" in m.group(1)
                        else (f'open({m.group(1)}, encoding="utf-8")' if "," in m.group(1) else f'open({m.group(1)}, "r", encoding="utf-8")'),
                        content
                    )
                    if fixed != content:
                        py_file.write_text(fixed, encoding="utf-8")
                        patched = True
                except Exception:
                    pass
            if patched:
                return "Patched python file open() operations with UTF-8 encoding"

        # 4. Port Conflict / Address already in use (WinError 10048)
        if "10048" in error_output or "Address already in use" in error_output or "address already in use" in error_output:
            console.print("[bold cyan]🧠 [Autonomous Memory] Detected port conflict. Forcefully clearing port 8000...[/bold cyan]")
            ProcessManager.kill_process_on_port(8000)
            time.sleep(1)
            return "Forcefully freed port 8000"

        # 5. Check Learned Solutions from Memory
        sig = self.normalize_error(error_output)
        if sig in self.data.get("learned_solutions", {}):
            recipe = self.data["learned_solutions"][sig]
            console.print(f"[bold green]💡 [Autonomous Memory] Found previously learned fix for: '{sig}'[/bold green]")
            if "file_patches" in recipe:
                for rel_path, patch_content in recipe["file_patches"].items():
                    target_file = workspace_dir / rel_path
                    if target_file.exists():
                        target_file.write_text(patch_content, encoding="utf-8")
                        return f"Applied learned fix from memory to {rel_path}"

        return None

    def record_successful_fix(self, error_output: str, files_updated: List[str], workspace_dir: Path):
        """
        Caches a successful fix into memory so next time it is fixed instantly.
        """
        sig = self.normalize_error(error_output)
        patches = {}
        for fname in files_updated:
            p = workspace_dir / fname
            if p.exists() and p.is_file():
                try:
                    txt = p.read_text(encoding="utf-8", errors="ignore")
                    if len(txt) < 30000:
                        patches[fname] = txt
                except Exception:
                    pass

        self.data.setdefault("learned_solutions", {})[sig] = {
            "timestamp": time.time(),
            "files_updated": files_updated,
            "file_patches": patches
        }
        self.data.setdefault("error_stats", {})[sig] = self.data.get("error_stats", {}).get(sig, 0) + 1
        self.save()
        console.print(f"[bold green]💾 Saved solution to Autonomous Memory! In the future, this error will be auto-solved without calling DeepSeek.[/bold green]")
