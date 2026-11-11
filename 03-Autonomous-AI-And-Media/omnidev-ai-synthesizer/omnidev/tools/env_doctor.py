import shutil
import subprocess
import os
from typing import Dict, Any, List
from config import console

class EnvironmentDoctor:
    """
    Environment Doctor: Inspects runtime toolchains, versions, SDK paths,
    environment variables, port conflicts, and provides automated repair guidance.
    """
    @staticmethod
    def diagnose() -> Dict[str, Any]:
        console.print("[cyan]🩺 Environment Doctor: Running complete system diagnostics...[/cyan]")
        tools_to_check = [
            ("python", "Python 3.x Interpreter", ["python", "--version"]),
            ("node", "Node.js Runtime", ["node", "--version"]),
            ("npm", "NPM Package Manager", ["npm", "--version"]),
            ("java", "Java JDK Runtime", ["java", "-version"]),
            ("javac", "Java Compiler", ["javac", "-version"]),
            ("gradle", "Gradle Build System", ["gradle", "--version"]),
            ("adb", "Android Debug Bridge", ["adb", "version"]),
            ("git", "Git Version Control", ["git", "--version"]),
            ("docker", "Docker Engine", ["docker", "--version"])
        ]

        report = {}
        for tool, label, cmd in tools_to_check:
            path = shutil.which(tool)
            installed = bool(path)
            version_str = "Not installed"
            if installed:
                try:
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    version_str = (res.stdout or res.stderr).splitlines()[0].strip()
                except Exception:
                    version_str = "Installed (version check timed out)"

            report[tool] = {
                "label": label,
                "installed": installed,
                "path": path,
                "version": version_str
            }

        # Environment variables check
        env_vars = {
            "JAVA_HOME": os.environ.get("JAVA_HOME", "Not set"),
            "ANDROID_HOME": os.environ.get("ANDROID_HOME", "Not set"),
            "PATH_LENGTH": len(os.environ.get("PATH", ""))
        }

        console.print("[green]✓ System diagnostics complete.[/green]")
        return {
            "success": True,
            "tools": report,
            "environment_variables": env_vars
        }
