"""
environment_doctor.py
System & Environment Diagnostic Doctor for Autonomous Web-Agent IDE.

Inspects toolchains, runtimes, package managers, and ports:
  - Python, Node.js (npm, yarn, pnpm)
  - Git, Chrome/Chromium
  - Java/JDK, Android SDK & ADB
  - Docker, Port availability
Provides actionable recommendations for missing or misconfigured tools.
"""

import os
import shutil
import socket
import subprocess
import sys
from typing import Dict, Any, List


class EnvironmentDoctor:
    """Diagnoses host development environment and returns health report."""

    @staticmethod
    def diagnose() -> Dict[str, Any]:
        report = {
            "platform": sys.platform,
            "overall_status": "READY",
            "tools": {},
            "ports": {},
            "recommendations": []
        }

        # 1. Python
        py_ver = sys.version.split()[0]
        report["tools"]["python"] = {
            "installed": True,
            "version": py_ver,
            "path": sys.executable,
            "ready": True
        }

        # 2. Node.js & npm / pnpm / yarn
        node_path = shutil.which("node")
        if node_path:
            node_ver = EnvironmentDoctor._run_cmd(["node", "--version"])
            report["tools"]["node"] = {
                "installed": True,
                "version": node_ver,
                "path": node_path,
                "ready": True
            }
        else:
            report["tools"]["node"] = {"installed": False, "ready": False}
            report["recommendations"].append("Node.js is not found on PATH. Install Node.js v18+.")

        for pm in ["npm", "pnpm", "yarn"]:
            pm_path = shutil.which(pm)
            report["tools"][pm] = {
                "installed": bool(pm_path),
                "path": pm_path or None,
                "version": EnvironmentDoctor._run_cmd([pm, "--version"]) if pm_path else None
            }

        # 3. Git
        git_path = shutil.which("git")
        if git_path:
            git_ver = EnvironmentDoctor._run_cmd(["git", "--version"])
            report["tools"]["git"] = {
                "installed": True,
                "version": git_ver,
                "path": git_path,
                "ready": True
            }
        else:
            report["tools"]["git"] = {"installed": False, "ready": False}
            report["recommendations"].append("Git is not found on PATH. Install Git for version control.")

        # 4. Chrome / Chromium
        chrome_cand = [
            os.getenv("CHROME_PATH"),
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            shutil.which("chrome"),
            shutil.which("google-chrome"),
            shutil.which("chromium"),
        ]
        found_chrome = next((c for c in chrome_cand if c and os.path.exists(c)), None)
        report["tools"]["chrome"] = {
            "installed": bool(found_chrome),
            "path": found_chrome,
            "ready": bool(found_chrome)
        }
        if not found_chrome:
            report["recommendations"].append("Google Chrome or Chromium not detected for web browser automation.")

        # 5. Java / JDK
        java_path = shutil.which("java")
        java_home = os.getenv("JAVA_HOME")
        report["tools"]["java"] = {
            "installed": bool(java_path),
            "path": java_path,
            "java_home": java_home,
            "version": EnvironmentDoctor._run_cmd(["java", "-version"]) if java_path else None,
            "ready": bool(java_path)
        }

        # 6. Android SDK & ADB
        adb_path = shutil.which("adb")
        android_home = os.getenv("ANDROID_HOME") or os.getenv("ANDROID_SDK_ROOT")
        report["tools"]["adb"] = {
            "installed": bool(adb_path),
            "path": adb_path,
            "android_home": android_home,
            "version": EnvironmentDoctor._run_cmd(["adb", "version"]) if adb_path else None,
            "ready": bool(adb_path)
        }

        # 7. Docker
        docker_path = shutil.which("docker")
        report["tools"]["docker"] = {
            "installed": bool(docker_path),
            "path": docker_path,
            "version": EnvironmentDoctor._run_cmd(["docker", "--version"]) if docker_path else None,
            "ready": bool(docker_path)
        }

        # 8. Check critical ports
        ports_to_check = {
            3001: "Backend Controller",
            5173: "Frontend Vite IDE",
            5174: "Generated Live App",
            9222: "Chrome Remote CDP"
        }
        for port, label in ports_to_check.items():
            in_use = EnvironmentDoctor._is_port_in_use(port)
            report["ports"][port] = {
                "label": label,
                "in_use": in_use,
                "status": "OCCUPIED / ACTIVE" if in_use else "AVAILABLE"
            }

        # Determine overall status
        crit_tools = ["python", "node", "git"]
        missing_crit = [t for t in crit_tools if not report["tools"].get(t, {}).get("installed")]
        if missing_crit:
            report["overall_status"] = "WARNING — MISSING CORE TOOLS"
        else:
            report["overall_status"] = "HEALTHY"

        return report

    @staticmethod
    def _run_cmd(args: List[str]) -> str:
        try:
            res = subprocess.run(args, capture_output=True, text=True, timeout=3)
            out = res.stdout.strip() or res.stderr.strip()
            return out.split("\n")[0] if out else "Unknown"
        except Exception:
            return "Unknown"

    @staticmethod
    def _is_port_in_use(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)
            return s.connect_ex(("127.0.0.1", port)) == 0


def format_doctor_log(report: Dict[str, Any]) -> str:
    """Formats diagnosis into readable terminal output."""
    lines = [
        "[+] \x1b[1;36m[Autonomous Web-Agent IDE — Environment Doctor]\x1b[0m",
        f"Overall System Status: \x1b[1;32m{report['overall_status']}\x1b[0m\r\n",
        "  Toolchain Health:",
    ]
    for tool, info in report["tools"].items():
        icon = "[OK]" if info.get("installed") else "[--]"
        ver = f"({info.get('version', '')})" if info.get("version") else ""
        lines.append(f"   {icon} {tool:<8}: {ver or ('Not Installed' if not info.get('installed') else 'Installed')}")

    lines.append("\r\n  Port Allocation:")
    for port, info in report["ports"].items():
        state = "\x1b[1;32mACTIVE\x1b[0m" if info["in_use"] else "\x1b[90mFREE\x1b[0m"
        lines.append(f"   * Port {port:<5} [{info['label']}]: {state}")

    if report["recommendations"]:
        lines.append("\r\n  Recommendations:")
        for r in report["recommendations"]:
            lines.append(f"   ! {r}")

    return "\r\n".join(lines)
