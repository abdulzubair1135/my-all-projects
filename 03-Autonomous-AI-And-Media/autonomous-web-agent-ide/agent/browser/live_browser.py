"""
Live Chromium Browser Window for Autonomous Web-Agent IDE
Keeps the browser open for real-time viewing and user interaction.
"""

import sys
import os
import asyncio
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parent.parent
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from browser.browser_manager import BrowserManager

SERVICE_URLS = {
    "gemini": "https://gemini.google.com/app",
    "gemini_web": "https://gemini.google.com/app",
    "deepseek": "https://chat.deepseek.com",
    "deepseek_web": "https://chat.deepseek.com",
    "chatgpt": "https://chatgpt.com",
    "chatgpt_web": "https://chatgpt.com"
}

async def launch_live(target: str = "gemini_web"):
    target_url = SERVICE_URLS.get(target.lower(), target)
    if not target_url.startswith("http"):
        target_url = "https://gemini.google.com/app"

    print(f"[Live Browser] Launching Chromium window with profile at {target_url}...")
    bm = BrowserManager(headless=False)
    page = await bm.initialize()

    try:
        await page.goto(target_url, wait_until="domcontentloaded", timeout=45000)
    except Exception as e:
        print(f"[Live Browser Notice] Navigation: {e}")

    print("[Live Browser] Window active. Waiting until window is closed by user...")
    try:
        while not page.is_closed():
            await asyncio.sleep(1)
    except Exception:
        pass
    finally:
        await bm.close()
        print("[Live Browser] Window closed.")

if __name__ == "__main__":
    provider_arg = sys.argv[1] if len(sys.argv) > 1 else "gemini_web"
    asyncio.run(launch_live(provider_arg))
