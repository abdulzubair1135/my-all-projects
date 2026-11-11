"""
Pre-flight bootstrap and environment diagnostics for StickForge AI.
Verifies system dependencies, directory structures, and database readiness.
"""

from __future__ import annotations
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any

# Ensure project root is in sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from app.core.config import (
    PROJECT_ROOT,
    ASSETS_DIR,
    PROJECTS_DIR,
    BROWSER_USER_DATA_DIR,
    LOGS_DIR,
    CACHE_DIR,
    OUTPUT_DIR,
    DATABASE_PATH,
    get_config,
)
from app.core.logging_manager import setup_logging, get_logger
from app.storage.database import get_db

setup_logging()
logger = get_logger("bootstrap")


def run_preflight_checks() -> Dict[str, Any]:
    """Execute pre-flight checks and return diagnostic status dictionary."""
    results: Dict[str, Any] = {
        "python": {"status": "OK", "version": sys.version},
        "directories": {"status": "OK"},
        "database": {"status": "OK"},
        "ffmpeg": {"status": "PENDING"},
        "playwright": {"status": "PENDING"},
    }

    # 1. Verify Directories
    required_dirs = [
        ASSETS_DIR / "backgrounds",
        ASSETS_DIR / "music",
        ASSETS_DIR / "sound_effects",
        ASSETS_DIR / "templates",
        PROJECTS_DIR,
        BROWSER_USER_DATA_DIR,
        LOGS_DIR,
        CACHE_DIR,
        OUTPUT_DIR,
    ]
    for d in required_dirs:
        try:
            d.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            results["directories"] = {"status": "ERROR", "message": f"Failed creating {d}: {e}"}
            logger.error(f"Directory check failed for {d}: {e}")

    # 2. Verify Database
    try:
        db = get_db()
        # Verify schema table query
        cursor = db.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        results["database"] = {"status": "OK", "tables": table_count}
        logger.info(f"Database verified with {table_count} tables.")
    except Exception as e:
        results["database"] = {"status": "ERROR", "message": str(e)}
        logger.error(f"Database initialization failed: {e}")

    # 3. Verify FFmpeg
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        # Check python scripts path as fallback
        py_scripts_ffmpeg = Path(sys.executable).parent / "Scripts" / "ffmpeg.exe"
        if py_scripts_ffmpeg.exists():
            ffmpeg_path = str(py_scripts_ffmpeg)

    if ffmpeg_path:
        try:
            res = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True, timeout=5)
            first_line = res.stdout.splitlines()[0] if res.stdout else "Available"
            results["ffmpeg"] = {"status": "OK", "path": ffmpeg_path, "version": first_line}
            logger.info(f"FFmpeg verified: {first_line}")
        except Exception as e:
            results["ffmpeg"] = {"status": "WARNING", "path": ffmpeg_path, "message": str(e)}
    else:
        results["ffmpeg"] = {"status": "ERROR", "message": "FFmpeg binary not found."}
        logger.warning("FFmpeg was not detected in PATH.")

    # 4. Verify Playwright Chromium
    try:
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        pw_dir = Path(local_app_data) / "ms-playwright" if local_app_data else None
        chrome_bins = list(pw_dir.glob("chromium-*/chrome-win*/chrome.exe")) if (pw_dir and pw_dir.exists()) else []
        if chrome_bins:
            results["playwright"] = {"status": "OK", "executable_path": str(chrome_bins[0])}
            logger.info(f"Playwright Chromium verified: {chrome_bins[0]}")
        else:
            from playwright.sync_api import sync_playwright
            pw = sync_playwright().start()
            chromium_path = pw.chromium.executable_path
            pw.stop()
            results["playwright"] = {"status": "OK", "executable_path": chromium_path}
            logger.info(f"Playwright Chromium verified: {chromium_path}")
    except Exception as e:
        results["playwright"] = {"status": "WARNING", "message": str(e)}
        logger.warning(f"Playwright verification notice: {e}")

    return results


def main() -> int:
    """CLI entrypoint for launch_setup.bat and diagnostics."""
    logger.info("Starting StickForge AI Pre-flight Bootstrap...")
    results = run_preflight_checks()
    has_critical_error = False

    print("\n---------------------------------------------------------")
    print("           StickForge AI Pre-flight Diagnostics          ")
    print("---------------------------------------------------------")
    for key, val in results.items():
        status = val.get("status", "UNKNOWN")
        print(f"[{status:7s}] {key.capitalize()}: {val}")
        if status == "ERROR":
            has_critical_error = True
    print("---------------------------------------------------------\n")

    if has_critical_error:
        logger.error("Pre-flight bootstrap encountered critical issues.")
        return 1

    logger.info("Pre-flight checks passed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
