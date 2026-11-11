"""
Page State Detector for DeepSeek Web Interface.
Accurately identifies authentication status, ongoing generation, Continue actions, and security challenges.
"""

from __future__ import annotations
import enum
from typing import Optional, Dict, Any, Tuple
from playwright.sync_api import Page, Locator

from app.core.logging_manager import get_logger

logger = get_logger("page_state_detector")


class PageState(str, enum.Enum):
    DISCONNECTED = "DISCONNECTED"
    UNEXPECTED_PAGE = "UNEXPECTED_PAGE"
    LOGIN_REQUIRED = "LOGIN_REQUIRED"
    CHALLENGE_REQUIRED = "CHALLENGE_REQUIRED"
    LOGGED_IN = "LOGGED_IN"
    GENERATING = "GENERATING"
    CONTINUE_AVAILABLE = "CONTINUE_AVAILABLE"
    RESPONSE_COMPLETE = "RESPONSE_COMPLETE"
    ERROR_PAGE = "ERROR_PAGE"


# Robust selectors for DeepSeek web elements
SELECTORS = {
    "login_indicators": [
        "a[href*='/sign-in']",
        "a[href*='/login']",
        "button:has-text('Log in')",
        "button:has-text('Sign In')",
        "button:has-text('登录')",
        "button:has-text('注册')",
    ],
    "challenge_indicators": [
        "#challenge-running",
        "#cf-challenge-running",
        "iframe[src*='cloudflare']",
        "div:has-text('Checking your browser')",
        "div:has-text('Human verification')",
        "text='403 ERROR'",
        "text='Request blocked'",
        "text='The request could not be satisfied'",
    ],
    "chat_input": [
        "textarea#chat-input",
        "textarea[placeholder*='DeepSeek']",
        "textarea[placeholder*='Send a message']",
        "div[contenteditable='true']",
        "textarea",
    ],
    "stop_button": [
        "button[aria-label*='Stop']",
        "button:has-text('Stop')",
        "div[class*='stop-button']",
        "svg[class*='stop']",
    ],
    "continue_button": [
        "button:has-text('Continue')",
        "button:has-text('Continue generating')",
        "button:has-text('继续生成')",
        "div[role='button']:has-text('Continue')",
    ],
    "error_banner": [
        "div:has-text('An error occurred')",
        "div:has-text('Network error')",
        "div:has-text('Something went wrong')",
        "div:has-text('Server busy')",
        "h1:has-text('403 ERROR')",
        "h2:has-text('The request could not be satisfied')",
    ],
}


class PageStateDetector:
    """Evaluates the live DOM of the DeepSeek web app."""

    def __init__(self, page: Optional[Page] = None):
        self.page = page

    def set_page(self, page: Page) -> None:
        self.page = page

    def detect_state(self) -> Tuple[PageState, Dict[str, Any]]:
        """Evaluate DOM and return primary state with diagnostic details."""
        if not self.page or self.page.is_closed():
            return PageState.DISCONNECTED, {"reason": "Page is closed or None"}

        try:
            url = self.page.url.lower()

            # 1. Check for Cloudflare / Security Challenge
            for sel in SELECTORS["challenge_indicators"]:
                if self.page.locator(sel).count() > 0 and self.page.locator(sel).first.is_visible():
                    return PageState.CHALLENGE_REQUIRED, {"url": url, "matched_selector": sel}

            # 2. Check for explicit Login page or Login buttons
            if "login" in url or "sign-in" in url or "auth" in url:
                return PageState.LOGIN_REQUIRED, {"url": url, "reason": "URL matches auth path"}

            for sel in SELECTORS["login_indicators"]:
                loc = self.page.locator(sel)
                if loc.count() > 0 and loc.first.is_visible():
                    return PageState.LOGIN_REQUIRED, {"url": url, "matched_selector": sel}

            # 3. Check for Error banner
            for sel in SELECTORS["error_banner"]:
                loc = self.page.locator(sel)
                if loc.count() > 0 and loc.first.is_visible():
                    return PageState.ERROR_PAGE, {"url": url, "matched_selector": sel}

            # 4. Check for active generation (Stop button visible)
            for sel in SELECTORS["stop_button"]:
                loc = self.page.locator(sel)
                if loc.count() > 0 and loc.first.is_visible():
                    return PageState.GENERATING, {"url": url, "matched_selector": sel}

            # 5. Check if Continue action button is available
            for sel in SELECTORS["continue_button"]:
                loc = self.page.locator(sel)
                if loc.count() > 0 and loc.first.is_visible() and loc.first.is_enabled():
                    return PageState.CONTINUE_AVAILABLE, {"url": url, "matched_selector": sel}

            # 6. Check if Chat Input area is present (User is logged in and ready)
            for sel in SELECTORS["chat_input"]:
                loc = self.page.locator(sel)
                if loc.count() > 0 and loc.first.is_visible():
                    return PageState.LOGGED_IN, {"url": url, "chat_ready": True}

            # If on deepseek domain but cannot identify chat input or login
            if "deepseek.com" in url:
                return PageState.UNEXPECTED_PAGE, {"url": url, "reason": "DeepSeek loaded but unknown layout"}

            return PageState.UNEXPECTED_PAGE, {"url": url, "reason": "Not on DeepSeek domain"}

        except Exception as e:
            logger.error(f"Error evaluating page state: {e}")
            return PageState.ERROR_PAGE, {"exception": str(e)}

    def find_continue_button(self) -> Optional[Locator]:
        """Return the visible and enabled Continue button locator, if any."""
        if not self.page or self.page.is_closed():
            return None
        for sel in SELECTORS["continue_button"]:
            try:
                loc = self.page.locator(sel)
                if loc.count() > 0 and loc.first.is_visible() and loc.first.is_enabled():
                    return loc.first
            except Exception:
                pass
        return None

    def find_chat_input(self, timeout_ms: int = 4000) -> Optional[Locator]:
        """Return the visible chat input locator, waiting up to timeout_ms."""
        if not self.page or self.page.is_closed():
            return None
        per_sel = max(500, timeout_ms // len(SELECTORS["chat_input"]))
        for sel in SELECTORS["chat_input"]:
            try:
                loc = self.page.locator(sel)
                loc.first.wait_for(state="visible", timeout=per_sel)
                if loc.count() > 0 and loc.first.is_visible():
                    return loc.first
            except Exception:
                pass
        return None
