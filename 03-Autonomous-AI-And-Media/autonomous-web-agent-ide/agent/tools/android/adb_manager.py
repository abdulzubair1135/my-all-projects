"""
adb_manager.py
Android Device Bridge (ADB) Manager for Autonomous Web-Agent IDE.

Provides safe operations for physical Android devices and emulators:
  - Device detection & state inspection
  - APK installation & uninstallation
  - Package launch & termination
  - Device screenshot capture
  - Logcat stream retrieval
"""

import asyncio
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional


class ADBManager:
    """Manages connected Android devices and APK lifecycles via ADB."""

    def __init__(self, adb_path: Optional[str] = None):
        self.adb_bin = adb_path or shutil.which("adb") or "adb"

    def is_available(self) -> bool:
        """Returns True if ADB is found on system PATH."""
        return bool(shutil.which(self.adb_bin))

    async def list_devices(self) -> List[Dict[str, Any]]:
        """Lists connected Android devices with authorization status."""
        if not self.is_available():
            return []

        devices = []
        try:
            proc = await asyncio.create_subprocess_exec(
                self.adb_bin, "devices", "-l",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            lines = stdout.decode("utf-8", errors="replace").strip().split("\n")

            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                serial = parts[0]
                state = parts[1] if len(parts) > 1 else "unknown"

                model = "Unknown"
                device_name = "Device"
                for p in parts[2:]:
                    if p.startswith("model:"):
                        model = p.split(":", 1)[1]
                    elif p.startswith("device:"):
                        device_name = p.split(":", 1)[1]

                devices.append({
                    "serial": serial,
                    "state": state,
                    "model": model,
                    "name": device_name,
                    "authorized": state == "device"
                })
        except Exception:
            pass

        return devices

    async def get_device_info(self, serial: str) -> Dict[str, Any]:
        """Queries OS version, SDK level, screen resolution, and battery."""
        info = {"serial": serial, "os_version": None, "sdk": None, "resolution": None}
        try:
            release = await self._run_shell(serial, "getprop ro.build.version.release")
            sdk = await self._run_shell(serial, "getprop ro.build.version.sdk")
            wm = await self._run_shell(serial, "wm size")

            info["os_version"] = release.strip() or "Unknown"
            info["sdk"] = sdk.strip() or "Unknown"
            if "size:" in wm.lower():
                info["resolution"] = wm.split(":")[-1].strip()
        except Exception:
            pass
        return info

    async def install_apk(self, serial: str, apk_path: str) -> Dict[str, Any]:
        """Installs or upgrades an APK on the target device."""
        if not os.path.exists(apk_path):
            return {"success": False, "error": f"APK not found at {apk_path}"}

        try:
            proc = await asyncio.create_subprocess_exec(
                self.adb_bin, "-s", serial, "install", "-r", apk_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            out = stdout.decode("utf-8", errors="replace")
            err = stderr.decode("utf-8", errors="replace")

            success = "success" in out.lower()
            return {"success": success, "output": out, "error": err if not success else None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def launch_package(self, serial: str, package_name: str) -> bool:
        """Launches the default monkey activity of a package."""
        try:
            res = await self._run_shell(serial, f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
            return "events injected: 1" in res.lower()
        except Exception:
            return False

    async def take_screenshot(self, serial: str, output_path: str) -> bool:
        """Captures device display directly into a PNG file on host."""
        try:
            out_file = Path(output_path)
            out_file.parent.mkdir(parents=True, exist_ok=True)

            proc = await asyncio.create_subprocess_exec(
                self.adb_bin, "-s", serial, "exec-out", "screencap", "-p",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            if stdout and len(stdout) > 1000:
                out_file.write_bytes(stdout)
                return True
            return False
        except Exception:
            return False

    async def get_logcat(self, serial: str, lines: int = 50) -> str:
        """Retrieves recent logcat entries."""
        try:
            res = await self._run_shell(serial, f"logcat -d -t {lines}")
            return res
        except Exception:
            return ""

    async def _run_shell(self, serial: str, command: str) -> str:
        proc = await asyncio.create_subprocess_exec(
            self.adb_bin, "-s", serial, "shell", command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        return stdout.decode("utf-8", errors="replace").strip()
