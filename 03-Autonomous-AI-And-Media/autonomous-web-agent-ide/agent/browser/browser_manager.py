import asyncio
import os
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from playwright.async_api import async_playwright, BrowserContext, Page, Playwright
except ImportError:
    async_playwright = None
    BrowserContext = None
    Page = None
    Playwright = None

class BrowserManager:
    def __init__(self, profile_dir: Optional[str] = None, headless: bool = False):
        root_dir = Path(__file__).resolve().parent.parent.parent
        self.profile_dir = Path(profile_dir).resolve() if profile_dir else (root_dir / "browser-profile").resolve()
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.playwright: Optional[Any] = None
        self.context: Optional[Any] = None
        self.page: Optional[Any] = None

    async def initialize(self) -> Page:
        if async_playwright is None:
            raise RuntimeError("Playwright is not installed. Install with `pip install playwright && playwright install chromium`.")

        if self.context and self.page and not self.page.is_closed():
            return self.page

        self.playwright = await async_playwright().start()

        # Launch persistent browser context to retain cookies and login session
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.profile_dir),
            headless=self.headless,
            viewport={"width": 1280, "height": 800},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        pages = self.context.pages
        self.page = pages[0] if pages else await self.context.new_page()
        return self.page

    async def restart(self) -> Page:
        await self.close()
        return await self.initialize()

    async def is_captcha_or_verification_present(self, page: Optional[Page] = None) -> bool:
        target_page = page or self.page
        if not target_page:
            return False
        
        captcha_selectors = [
            "iframe[src*='recaptcha']",
            "iframe[src*='hcaptcha']",
            "iframe[src*='cloudflare']",
            "div[class*='captcha']",
            "div[class*='geetest']",
            "text=Please verify you are human",
            "text=Security Verification"
        ]

        for sel in captcha_selectors:
            try:
                elem = await target_page.query_selector(sel)
                if elem and await elem.is_visible():
                    return True
            except Exception:
                pass
        return False

    async def is_logged_in(self, logged_in_selectors: list, page: Optional[Page] = None) -> bool:
        target_page = page or self.page
        if not target_page:
            return False

        for sel in logged_in_selectors:
            try:
                elem = await target_page.query_selector(sel)
                if elem and await elem.is_visible():
                    return True
            except Exception:
                pass
        return False

    async def close(self):
        try:
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception:
            pass
        finally:
            self.context = None
            self.page = None
            self.playwright = None
