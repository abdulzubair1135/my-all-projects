import subprocess
import os
import re

class TerminalTool:
    """
    Executes commands safely in the workspace.
    Supports PowerShell, Command Prompt, Git, Node, Python.
    Prevents nested PowerShell invocation errors.
    """
    def __init__(self, workspace_root=None):
        self.workspace_root = workspace_root or os.getcwd()

    def run(self, cmd: str, timeout: int = 60, cwd: str = None) -> dict:
        work_dir = cwd or self.workspace_root
        
        # Guard against accidental catastrophic commands
        lower_cmd = cmd.lower()
        if "format " in lower_cmd or "del /s /q c:\\windows" in lower_cmd or "rm -rf /" in lower_cmd:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command blocked: Potentially destructive system command.",
                "exit_code": -1
            }

        # Clean nested powershell wrappers
        clean_cmd = cmd.strip()
        if re.match(r"^powershell(\.exe)?\s+(-command|-c)\s+", clean_cmd, flags=re.IGNORECASE):
            clean_cmd = re.sub(r"^powershell(\.exe)?\s+(-command|-c)\s+", "", clean_cmd, flags=re.IGNORECASE).strip()
            if (clean_cmd.startswith('"') and clean_cmd.endswith('"')) or (clean_cmd.startswith("'") and clean_cmd.endswith("'")):
                clean_cmd = clean_cmd[1:-1]

        try:
            # Run directly via PowerShell
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", clean_cmd],
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace"
            )
            return {
                "success": proc.returncode == 0,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
                "exit_code": proc.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds.",
                "exit_code": -2
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -3
            }
