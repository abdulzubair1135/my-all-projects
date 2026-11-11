"""
project_inspector.py
Automatic project detection and analysis for Autonomous Web-Agent IDE.

Inspects a workspace directory and returns structured info about:
  - Language (Python, Node.js, Java, etc.)
  - Framework (React, FastAPI, Express, Spring, etc.)
  - Package manager (npm, pip, gradle, etc.)
  - Entry point
  - Build/test/run commands
  - File structure summary
  - Git status
"""

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


class ProjectInspector:
    """
    Inspect a workspace and return structured project metadata.
    Used when importing a ZIP or starting a new session.
    """

    def __init__(self, workspace_root: str):
        self.root = Path(workspace_root)

    def inspect(self) -> Dict[str, Any]:
        """Full project inspection. Returns structured metadata."""
        result = {
            "workspace": str(self.root),
            "exists": self.root.exists(),
            "language": None,
            "languages": [],
            "framework": None,
            "frameworks": [],
            "package_manager": None,
            "entry_point": None,
            "build_command": None,
            "test_command": None,
            "run_command": None,
            "install_command": None,
            "dependencies": [],
            "dev_dependencies": [],
            "scripts": {},
            "file_count": 0,
            "file_tree_summary": [],
            "git_initialized": False,
            "git_branch": None,
            "git_status": None,
            "has_tests": False,
            "has_docker": False,
            "has_ci": False,
            "detected_ports": [],
            "description": "",
            "errors": [],
        }

        if not self.root.exists():
            result["errors"].append("Workspace directory does not exist")
            return result

        # File scan
        all_files = self._scan_files()
        result["file_count"] = len(all_files)
        result["file_tree_summary"] = self._build_tree_summary(all_files)

        # Language + framework detection
        self._detect_language_and_framework(all_files, result)

        # Commands
        self._detect_commands(result)

        # Git
        self._detect_git(result)

        # Features
        result["has_tests"] = self._has_tests(all_files)
        result["has_docker"] = any(
            f in [p.name for p in all_files] for f in ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]
        )
        result["has_ci"] = self.root.joinpath(".github", "workflows").exists()

        # Build description
        result["description"] = self._build_description(result)

        return result

    def _scan_files(self) -> List[Path]:
        """Scan all non-ignored files in the workspace."""
        IGNORE = {
            "node_modules", ".git", "__pycache__", ".venv", "venv",
            "dist", "build", ".next", ".nuxt", "target", "bin", "obj",
            ".gradle", ".idea", ".vscode", ".uploads", "*.pyc",
        }
        files = []
        try:
            for p in self.root.rglob("*"):
                if p.is_file():
                    parts = set(p.parts)
                    if not any(ig in str(p) for ig in IGNORE):
                        files.append(p)
        except Exception:
            pass
        return files[:500]  # cap at 500 files

    def _build_tree_summary(self, files: List[Path]) -> List[str]:
        """Build a concise tree summary (top-level dirs + important files)."""
        seen_dirs = set()
        summary = []
        for f in files:
            rel = f.relative_to(self.root)
            parts = rel.parts
            if len(parts) == 1:
                summary.append(str(rel))
            elif parts[0] not in seen_dirs:
                seen_dirs.add(parts[0])
                summary.append(f"{parts[0]}/")
        return sorted(summary)[:30]

    def _detect_language_and_framework(self, files: List[Path], result: Dict):
        """Detect primary language and frameworks."""
        file_names = {f.name for f in files}
        file_exts = {f.suffix.lower() for f in files}

        # Python
        if "requirements.txt" in file_names or "pyproject.toml" in file_names or ".py" in file_exts:
            result["languages"].append("Python")
            result["package_manager"] = "pip"

            # Python frameworks
            reqs = self._read_file_safe("requirements.txt") or self._read_file_safe("pyproject.toml") or ""
            if re.search(r'\bfastapi\b', reqs, re.I):
                result["frameworks"].append("FastAPI")
            if re.search(r'\bflask\b', reqs, re.I):
                result["frameworks"].append("Flask")
            if re.search(r'\bdjango\b', reqs, re.I):
                result["frameworks"].append("Django")
            if re.search(r'\bpytest\b', reqs, re.I):
                result["has_tests"] = True

        # Node.js / JavaScript / TypeScript
        if "package.json" in file_names:
            result["languages"].append("JavaScript")
            if ".ts" in file_exts or ".tsx" in file_exts:
                result["languages"].append("TypeScript")

            pkg = self._read_json_safe("package.json") or {}
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            scripts = pkg.get("scripts", {})
            result["scripts"] = scripts
            result["dependencies"] = list(pkg.get("dependencies", {}).keys())
            result["dev_dependencies"] = list(pkg.get("devDependencies", {}).keys())

            # Framework detection
            if "react" in deps:
                result["frameworks"].append("React")
            if "next" in deps:
                result["frameworks"].append("Next.js")
            if "vue" in deps:
                result["frameworks"].append("Vue")
            if "nuxt" in deps:
                result["frameworks"].append("Nuxt")
            if "@angular/core" in deps:
                result["frameworks"].append("Angular")
            if "express" in deps:
                result["frameworks"].append("Express")
            if "@nestjs/core" in deps:
                result["frameworks"].append("NestJS")
            if "vite" in deps:
                result["frameworks"].append("Vite")

            # Package manager detection
            if (self.root / "pnpm-lock.yaml").exists():
                result["package_manager"] = "pnpm"
            elif (self.root / "yarn.lock").exists():
                result["package_manager"] = "yarn"
            else:
                result["package_manager"] = "npm"

            # Entry point
            main = pkg.get("main")
            if main:
                result["entry_point"] = main

        # Java / Kotlin / Android
        if "build.gradle" in file_names or "build.gradle.kts" in file_names or "pom.xml" in file_names:
            result["languages"].append("Java")
            if ".kt" in file_exts:
                result["languages"].append("Kotlin")
            if "pom.xml" in file_names:
                result["package_manager"] = "Maven"
                result["frameworks"].append("Maven")
            else:
                result["package_manager"] = "Gradle"
                result["frameworks"].append("Gradle")
            if "AndroidManifest.xml" in file_names:
                result["frameworks"].append("Android")

        # Set primary language (first detected)
        if result["languages"]:
            result["language"] = result["languages"][0]
        if result["frameworks"]:
            result["framework"] = result["frameworks"][0]

    def _detect_commands(self, result: Dict):
        """Detect build, test, and run commands."""
        scripts = result.get("scripts", {})

        if result["language"] == "Python" or "Python" in result["languages"]:
            result["install_command"] = "pip install -r requirements.txt"
            result["test_command"] = "pytest" if (self.root / "tests").exists() or (self.root / "test").exists() else "python -m pytest"
            # Find main entry point
            for candidate in ["main.py", "app.py", "server.py", "run.py", "manage.py"]:
                if (self.root / candidate).exists():
                    result["entry_point"] = candidate
                    if "FastAPI" in result["frameworks"]:
                        result["run_command"] = f"uvicorn {candidate.replace('.py', '')}:app --reload"
                    elif "Flask" in result["frameworks"]:
                        result["run_command"] = f"python {candidate}"
                    else:
                        result["run_command"] = f"python {candidate}"
                    break

        elif "package.json" in os.listdir(self.root) if self.root.exists() else []:
            pm = result["package_manager"] or "npm"
            result["install_command"] = f"{pm} install"

            if "build" in scripts:
                result["build_command"] = f"{pm} run build"
            if "test" in scripts:
                result["test_command"] = f"{pm} test"
            elif "test:unit" in scripts:
                result["test_command"] = f"{pm} run test:unit"

            for dev_key in ["dev", "start:dev", "serve", "start"]:
                if dev_key in scripts:
                    result["run_command"] = f"{pm} run {dev_key}"
                    break

        elif "Gradle" in result["frameworks"]:
            result["install_command"] = "./gradlew dependencies"
            result["build_command"] = "./gradlew build"
            result["test_command"] = "./gradlew test"
            if "Android" in result["frameworks"]:
                result["build_command"] = "./gradlew assembleDebug"
                result["run_command"] = "adb install -r app/build/outputs/apk/debug/app-debug.apk"

        elif "Maven" in result["frameworks"]:
            result["build_command"] = "mvn clean package"
            result["test_command"] = "mvn test"
            result["run_command"] = "mvn spring-boot:run"

    def _detect_git(self, result: Dict):
        """Detect git state."""
        try:
            subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.root, capture_output=True, timeout=3
            )
            result["git_initialized"] = True

            branch = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.root, capture_output=True, text=True, timeout=3
            ).stdout.strip()
            result["git_branch"] = branch or "main"

            status = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.root, capture_output=True, text=True, timeout=3
            ).stdout.strip()
            result["git_status"] = status or "clean"
        except Exception:
            result["git_initialized"] = False

    def _has_tests(self, files: List[Path]) -> bool:
        dirs = {f.parent.name for f in files}
        file_names = {f.name for f in files}
        return (
            "tests" in dirs or "test" in dirs or "__tests__" in dirs
            or any(f.startswith("test_") or f.endswith("_test.py") or f.endswith(".test.js") for f in file_names)
        )

    def _read_file_safe(self, name: str) -> Optional[str]:
        try:
            return (self.root / name).read_text(encoding="utf-8", errors="replace")
        except Exception:
            return None

    def _read_json_safe(self, name: str) -> Optional[Dict]:
        content = self._read_file_safe(name)
        if not content:
            return None
        try:
            return json.loads(content)
        except Exception:
            return None

    def _build_description(self, result: Dict) -> str:
        """Build a human-readable description."""
        parts = []
        if result["frameworks"]:
            parts.append(" + ".join(result["frameworks"]))
        elif result["languages"]:
            parts.append(" + ".join(result["languages"]))

        if result["package_manager"]:
            parts.append(result["package_manager"])

        parts.append(f"{result['file_count']} files")

        if result["git_initialized"] and result["git_branch"]:
            parts.append(f"git:{result['git_branch']}")

        return " / ".join(parts)


def inspect_project(workspace_root: str) -> Dict[str, Any]:
    """Convenience function — inspect a project workspace."""
    return ProjectInspector(workspace_root).inspect()


def format_inspection_log(info: Dict[str, Any]) -> str:
    """Format inspection result as terminal log lines."""
    lines = [
        f"🔍 [Project Inspector] Workspace: {info['workspace']}",
        f"📦 Detected: {info['description'] or 'Unknown project type'}",
    ]
    if info["language"]:
        lines.append(f"   Language:  {', '.join(info['languages'])}")
    if info["frameworks"]:
        lines.append(f"   Framework: {', '.join(info['frameworks'])}")
    if info["package_manager"]:
        lines.append(f"   Pkg Mgr:   {info['package_manager']}")
    if info["entry_point"]:
        lines.append(f"   Entry:     {info['entry_point']}")
    if info["run_command"]:
        lines.append(f"   Run:       {info['run_command']}")
    if info["build_command"]:
        lines.append(f"   Build:     {info['build_command']}")
    if info["test_command"]:
        lines.append(f"   Test:      {info['test_command']}")
    lines.append(f"   Files:     {info['file_count']}")
    if info["has_tests"]:
        lines.append("   ✅ Tests directory found")
    if info["has_docker"]:
        lines.append("   🐳 Docker configuration found")
    if info["git_initialized"]:
        lines.append(f"   🌿 Git: branch={info['git_branch']} | {info['git_status'][:50] if info['git_status'] else 'clean'}")
    return "\r\n".join(lines)
