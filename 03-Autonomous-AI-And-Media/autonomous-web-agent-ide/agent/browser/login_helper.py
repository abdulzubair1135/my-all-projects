"""
Autonomous Web-Agent Browser Session & Login Assistant
Interactive helper that allows 1-click persistent authentication for
DeepSeek, Google Gemini, and ChatGPT.
"""

import sys
import os
import asyncio
import time
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parent.parent
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from browser.browser_manager import BrowserManager

SERVICE_URLS = {
    "1": ("DeepSeek Web", "https://chat.deepseek.com"),
    "2": ("Google Gemini Web", "https://gemini.google.com/app"),
    "3": ("ChatGPT Web", "https://chatgpt.com")
}

async def run_login_helper(service_choice: str = "1"):
    service_name, target_url = SERVICE_URLS.get(service_choice, ("DeepSeek Web", "https://chat.deepseek.com"))

    print("=" * 70)
    print(f"       WEB LLM LOGIN ASSISTANT - {service_name.upper()}")
    print("=" * 70)
    print("\n[1/3] Launching Chromium with persistent profile (`browser-profile/`)...")
    
    bm = BrowserManager(headless=False)
    page = await bm.initialize()
    
    print(f"[2/3] Navigating to {target_url}...")
    try:
        await page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"[Notice] Navigation: {e}")

    print("\n" + "=" * 70)
    print(f">>> PLEASE COMPLETE LOGIN TO {service_name.upper()} IN THE OPENED WINDOW <<<")
    print("Once you log in, your session is saved permanently in `browser-profile/`.")
    print("The agent is actively monitoring and will automatically detect when you finish.")
    print("=" * 70 + "\n")

    login_detected = False
    start_time = time.time()
    max_wait = 300  # 5 minutes

    chat_input_selectors = [
        "textarea#chat-input",
        "textarea[placeholder*='Message DeepSeek']",
        "textarea[placeholder*='DeepSeek']",
        "textarea[placeholder*='Message']",
        "div[contenteditable='true']",
        "rich-textarea textarea",
        "button[aria-label*='Send']",
        "div[class*='chat-input']",
        "div[class*='ds-avatar']",
        "model-response",
        "a[href*='accounts.google.com/SignOut']"
    ]

    while time.time() - start_time < max_wait:
        try:
            if page.is_closed():
                print("[Info] Browser window was closed.")
                break

            for sel in chat_input_selectors:
                elem = await page.query_selector(sel)
                if elem and await elem.is_visible():
                    login_detected = True
                    break

            if login_detected:
                print(f"\n[SUCCESS] {service_name} Login successfully detected!")
                print("[3/3] Session cookies and profile state saved permanently.")
                print("You can now close the browser or start your build in the IDE.\n")
                await asyncio.sleep(3)
                break
        except Exception:
            pass

        await asyncio.sleep(2)

    if not login_detected:
        print("\n[Notice] Timeout reached. Cookies so far were saved to `browser-profile/`.")

    await bm.close()
    print("\n[DONE] Login Assistant finished.")

if __name__ == "__main__":
    choice = sys.argv[1] if len(sys.argv) > 1 else "1"
    asyncio.run(run_login_helper(choice))
