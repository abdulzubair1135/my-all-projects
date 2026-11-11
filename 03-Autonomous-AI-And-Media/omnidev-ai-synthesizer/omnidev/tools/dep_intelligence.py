import json
from pathlib import Path
from typing import Dict, Any, List
from config import console

class DependencyIntelligence:
    """
    Dependency Intelligence for OmniDev:
    Detects package managers, reads dependencies and lockfiles, and identifies version conflicts.
    """
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = Path(workspace_dir)

    def scan_dependencies(self) -> Dict[str, Any]:
        info = {
            "package_manager": "None",
            "dependencies": {},
            "lockfile_present": False
        }

        # Check Node.js
        pkg_json = self.workspace_dir / "package.json"
        if pkg_json.exists():
            info["package_manager"] = "npm"
            try:
                data = json.loads(pkg_json.read_text(encoding="utf-8"))
                info["dependencies"].update(data.get("dependencies", {}))
                info["dependencies"].update(data.get("devDependencies", {}))
            except Exception:
                pass
            info["lockfile_present"] = (self.workspace_dir / "package-lock.json").exists()

        # Check Python
        req_txt = self.workspace_dir / "requirements.txt"
        if req_txt.exists():
            info["package_manager"] = "pip"
            deps = {}
            for line in req_txt.read_text(encoding="utf-8").splitlines():
                if line.strip() and not line.startswith("#"):
                    parts = line.split("==")
                    deps[parts[0].strip()] = parts[1].strip() if len(parts) > 1 else "latest"
            info["dependencies"].update(deps)

        return info
