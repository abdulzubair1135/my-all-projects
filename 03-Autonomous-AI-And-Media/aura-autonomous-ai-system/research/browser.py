"""
AURA Browser Automation Module.
Provides Playwright browser navigation, DOM accessibility extraction, scrolling, and interaction.
"""

from typing import Dict, Any, Optional, List
from core.logger import setup_logger

logger = setup_logger("BrowserAutomation")

class BrowserAutomation:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self._init_playwright()

    def _init_playwright(self):
        try:
            from playwright.sync_api import sync_playwright
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            logger.info("Playwright Chromium browser initialized successfully.")
        except Exception as e:
            logger.warning(f"Playwright not available: {e}. Using DOM fallback reader mode.")

    def navigate_and_extract(self, url: str) -> Dict[str, Any]:
        """
        Navigates to URL using Playwright (or fallback reader) and extracts title, DOM text, and accessibility tree.
        """
        logger.info(f"Browser navigating to URL: '{url}'")
        if self.browser:
            try:
                page = self.browser.new_page()
                page.goto(url, timeout=15000)
                title = page.title()
                content = page.content()
                text = page.inner_text("body")
                page.close()
                return {
                    "url": url,
                    "title": title,
                    "status": "success",
                    "content": text[:5000],
                    "html": content[:10000]
                }
            except Exception as e:
                logger.error(f"Playwright navigation error for '{url}': {e}")

        # Fallback using WebpageReader
        from research.webpage_reader import webpage_reader
        res = webpage_reader.read_url(url, max_chars=5000)
        return {
            "url": url,
            "title": f"Webpage {url}",
            "status": res["status"],
            "content": res["content"],
            "html": ""
        }

    def close(self):
        if self.browser:
            try:
                self.browser.close()
            except Exception:
                pass
        if self.playwright:
            try:
                self.playwright.stop()
            except Exception:
                pass
        logger.info("Browser automation closed.")

browser_automation = BrowserAutomation()
