import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from playwright.sync_api import sync_playwright
import config
from config import console

class BrowserTool:
    """
    Playwright Browser Automation & Visual QA Tool for OmniDev.
    """
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.screenshots_dir = config.OUTPUTS_DIR / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def test_url(self, url: str, take_screenshot: bool = True, wait_seconds: int = 3) -> Dict[str, Any]:
        console.print(f"[cyan]Browser QA testing URL:[/cyan] {url}")
        console_logs: List[str] = []
        page_errors: List[str] = []

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(viewport={"width": 1280, "height": 800})
                page = context.new_page()

                page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))
                page.on("pageerror", lambda err: page_errors.append(str(err)))

                page.goto(url, wait_until="networkidle", timeout=15000)
                time.sleep(wait_seconds)

                screenshot_path = None
                if take_screenshot:
                    filename = f"qa_snap_{int(time.time())}.png"
                    screenshot_path = str((self.screenshots_dir / filename).resolve())
                    page.screenshot(path=screenshot_path, full_page=True)

                title = page.title()
                browser.close()

                return {
                    "success": len(page_errors) == 0,
                    "title": title,
                    "screenshot_path": screenshot_path,
                    "console_logs": console_logs,
                    "page_errors": page_errors
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "console_logs": console_logs,
                    "page_errors": page_errors
                }
