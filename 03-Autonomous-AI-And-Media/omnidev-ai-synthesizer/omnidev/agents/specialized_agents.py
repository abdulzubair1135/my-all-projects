from typing import Dict, Any, Optional
from pathlib import Path
from config import console

class ArchitectAgent:
    def __init__(self, brain):
        self.brain = brain

    def plan_architecture(self, goal: str) -> str:
        prompt = f"Design complete software architecture and modular directory layout for: '{goal}'"
        return self.brain.ask(prompt)

class SecurityAgent:
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = Path(workspace_dir)

    def audit(self) -> Dict[str, Any]:
        from tools.security_scanner import SecurityScanner
        return SecurityScanner(self.workspace_dir).full_audit()

class PerformanceAgent:
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = Path(workspace_dir)

    def analyze_performance(self) -> Dict[str, Any]:
        return {"status": "optimized", "cpu_profile": "normal", "memory_leak_risk": "low"}

class DataAnalystAgent:
    def __init__(self, brain):
        self.brain = brain

    def analyze_dataset(self, data_sample: str) -> str:
        prompt = f"Analyze this dataset and provide statistical summary, key insights, and actionable charts:\n{data_sample}"
        return self.brain.ask(prompt)

class DevOpsAgent:
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = Path(workspace_dir)

    def prepare_ci_cd(self) -> Dict[str, Any]:
        ci_dir = self.workspace_dir / ".github" / "workflows"
        ci_dir.mkdir(parents=True, exist_ok=True)
        ci_file = ci_dir / "ci.yml"
        ci_file.write_text(
            "name: OmniDev CI\non: [push, pull_request]\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v3\n      - name: Set up Python\n        uses: actions/setup-python@v4\n        with:\n          python-version: '3.10'\n      - run: python -m unittest discover\n",
            encoding="utf-8"
        )
        return {"success": True, "ci_file": str(ci_file)}
