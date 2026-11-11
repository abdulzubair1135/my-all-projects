import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from config import console

class ADBTool:
    """
    Android Debug Bridge (ADB) Tool for OmniDev: detects devices, installs APKs, captures Logcat.
    """
    @staticmethod
    def get_connected_devices() -> List[Dict[str, str]]:
        try:
            out = subprocess.check_output(["adb", "devices"], text=True, stderr=subprocess.DEVNULL)
            devices = []
            for line in out.strip().splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 2:
                    devices.append({"serial": parts[0], "status": parts[1]})
            return devices
        except Exception:
            return []

    @staticmethod
    def install_apk(apk_path: Path, device_serial: Optional[str] = None) -> Dict[str, Any]:
        cmd = ["adb"]
        if device_serial:
            cmd.extend(["-s", device_serial])
        cmd.extend(["install", "-r", str(apk_path.resolve())])

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            success = "Success" in res.stdout
            return {
                "success": success,
                "output": res.stdout or res.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def capture_logcat(lines: int = 100) -> str:
        try:
            cmd = f"adb logcat -d -t {lines}"
            out = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL)
            return out
        except Exception as e:
            return f"Logcat error: {e}"
