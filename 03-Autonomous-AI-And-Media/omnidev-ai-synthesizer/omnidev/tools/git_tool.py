import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from core.command_guard import CommandGuard
from config import console

class GitTool:
    """
    Git & GitHub Automation Tool for OmniDev.
    """
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = Path(workspace_dir)

    def init_repo(self) -> Dict[str, Any]:
        res = subprocess.run(["git", "init"], cwd=self.workspace_dir, capture_output=True, text=True)
        return {"success": res.returncode == 0, "output": res.stdout}

    def status(self) -> Dict[str, Any]:
        res = subprocess.run(["git", "status", "--porcelain"], cwd=self.workspace_dir, capture_output=True, text=True)
        return {"success": res.returncode == 0, "status": res.stdout}

    def commit_all(self, message: str) -> Dict[str, Any]:
        diff_res = subprocess.run(["git", "diff"], cwd=self.workspace_dir, capture_output=True, text=True)
        if diff_res.stdout:
            redacted = CommandGuard.redact_secrets(diff_res.stdout)
            if redacted != diff_res.stdout:
                return {"success": False, "error": "Commit blocked: API key detected in diff!"}

        subprocess.run(["git", "add", "-A"], cwd=self.workspace_dir, capture_output=True)
        res = subprocess.run(["git", "commit", "-m", message], cwd=self.workspace_dir, capture_output=True, text=True)
        return {"success": res.returncode == 0, "output": res.stdout}

    def push(self, remote: str = "origin", branch: str = "main") -> Dict[str, Any]:
        res = subprocess.run(["git", "push", remote, branch], cwd=self.workspace_dir, capture_output=True, text=True)
        return {"success": res.returncode == 0, "output": res.stdout or res.stderr}
