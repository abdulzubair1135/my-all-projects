import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from config import console

class DockerTool:
    """
    Docker & Container Engine for OmniDev:
    Generates Dockerfiles, starts docker-compose, captures container logs, and diagnoses failures.
    """
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = Path(workspace_dir)

    def build_image(self, tag: str = "omnidev_app:latest") -> Dict[str, Any]:
        res = subprocess.run(["docker", "build", "-t", tag, "."], cwd=self.workspace_dir, capture_output=True, text=True)
        return {"success": res.returncode == 0, "output": res.stdout or res.stderr}

    def compose_up(self) -> Dict[str, Any]:
        res = subprocess.run(["docker-compose", "up", "-d"], cwd=self.workspace_dir, capture_output=True, text=True)
        return {"success": res.returncode == 0, "output": res.stdout or res.stderr}

    def get_logs(self, container_name: str, lines: int = 50) -> str:
        try:
            out = subprocess.check_output(f"docker logs --tail {lines} {container_name}", shell=True, text=True)
            return out
        except Exception as e:
            return f"Docker logs error: {e}"
