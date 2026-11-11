import sys
import os
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from rich.console import Console
console = Console(force_terminal=True, legacy_windows=False)

# Base Paths
OMNIDEV_DIR = Path(__file__).resolve().parent
WORKSPACE_DIR = OMNIDEV_DIR.parent
CHROME_PROFILE_DIR = OMNIDEV_DIR / "chrome_profile"
OUTPUTS_DIR = OMNIDEV_DIR / "outputs"

# Ensure directories exist
CHROME_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# Chrome Settings
CHROME_DEBUG_PORT = 9222
CHROME_CDP_URL = f"http://127.0.0.1:{CHROME_DEBUG_PORT}"

POSSIBLE_CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
]

def get_chrome_executable() -> str:
    for path in POSSIBLE_CHROME_PATHS:
        if os.path.exists(path):
            return path
    return "chrome.exe"

# AI Web URLs
DEEPSEEK_URL = "https://chat.deepseek.com"
GEMINI_URL = "https://gemini.google.com"

# Brain Selection ('deepseek', 'gemini', 'api', 'auto')
DEFAULT_BRAIN = os.getenv("OMNIDEV_BRAIN", "deepseek")

# Agent & Debugger Settings
MAX_DEBUG_RETRIES = 5
COMMAND_TIMEOUT_SECONDS = 120
SERVER_START_TIMEOUT = 15
DEFAULT_APP_PORT = 8000

# Optional API Keys (if user provides them in env)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
