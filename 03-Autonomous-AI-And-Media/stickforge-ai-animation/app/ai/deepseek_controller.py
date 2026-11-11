"""
DeepSeek Web Browser Controller for StickForge AI.
Coordinates visible persistent Chromium automation, prompt submission, and response monitoring.
"""

from __future__ import annotations
import threading
import time
from typing import Callable, Dict, Any, Optional
from playwright.sync_api import Page

from app.core.config import get_config
from app.core.logging_manager import get_logger
from app.core.event_bus import get_event_bus
from app.browser.browser_manager import get_browser_manager, BrowserManager
from app.browser.page_state_detector import PageStateDetector, PageState
from app.ai.long_response_manager import LongResponseManager
from app.storage.repositories import AIJobRepository

logger = get_logger("deepseek_controller")


class DeepSeekController:
    """High-level controller for DeepSeek visible web automation."""

    def __init__(self, browser_mgr: Optional[BrowserManager] = None):
        self.browser_mgr = browser_mgr or get_browser_manager()
        self.config = get_config()
        self.detector = PageStateDetector()
        self.long_response_mgr = LongResponseManager()
        self.job_repo = AIJobRepository()
        self.event_bus = get_event_bus()
        self._lock = threading.RLock()
        self._active_job_id: Optional[str] = None

    def connect_or_launch(self) -> Dict[str, Any]:
        """Launch dedicated persistent browser and navigate to DeepSeek on dedicated thread."""
        with self._lock:
            self.browser_mgr.launch(force_visible=True)

            def _inspect_and_nav(page: Page) -> Dict[str, Any]:
                self.detector.set_page(page)
                self.long_response_mgr.set_page(page)

                current_url = page.url
                if "deepseek.com" not in current_url:
                    page.goto(self.config.browser.deepseek_url, wait_until="domcontentloaded", timeout=45000)
                    time.sleep(2.0)

                state, details = self.detector.detect_state()
                logger.info(f"DeepSeek connection check: {state.value} ({details})")
                return {"state": state.value, "details": details}

            return self.browser_mgr.execute_on_page(_inspect_and_nav)

    def check_session(self) -> Dict[str, Any]:
        """Verify if current browser tab is logged in and ready for prompts."""
        with self._lock:
            if not self.browser_mgr.is_running():
                return {"state": PageState.DISCONNECTED.value, "ready": False, "details": "Browser not launched."}

            def _check(page: Page) -> Dict[str, Any]:
                self.detector.set_page(page)
                state, details = self.detector.detect_state()
                ready = (state == PageState.LOGGED_IN)
                return {"state": state.value, "ready": ready, "details": details}

            return self.browser_mgr.execute_on_page(_check)

    def focus_browser(self) -> None:
        """Bring the visible DeepSeek window to the foreground."""
        self.browser_mgr.focus()

    def submit_prompt(
        self,
        job_id: str,
        project_id: str,
        task_type: str,
        prompt: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> str:
        """
        Submits a structured prompt into DeepSeek chat input and captures the response.
        Executed thread-safely through BrowserManager executor.
        """
        with self._lock:
            self._active_job_id = job_id
            self.job_repo.create_job(job_id, project_id, task_type, "deepseek_browser", prompt)

        def notify(prog: float, msg: str):
            if progress_callback:
                progress_callback(prog, msg)
            self.event_bus.publish("ai_progress", job_id=job_id, progress=prog, message=msg)

        # 1. Ensure browser is open and session is active
        notify(5.0, "Checking browser connection...")
        status = self.connect_or_launch()

        state_val = status.get("state")
        if state_val in [PageState.LOGIN_REQUIRED.value, PageState.CHALLENGE_REQUIRED.value, PageState.ERROR_PAGE.value, PageState.UNEXPECTED_PAGE.value]:
            self.browser_mgr.focus()
            if state_val == PageState.CHALLENGE_REQUIRED.value or "403" in str(status.get("details")):
                err_msg = (
                    "DeepSeek is currently showing a CloudFront 403 block or Cloudflare challenge.\n"
                    "Please solve the verification in the open Chromium browser, or switch AI Provider to 'Local Offline AI' in Story Studio to generate instantly."
                )
            elif state_val == PageState.LOGIN_REQUIRED.value:
                err_msg = (
                    "DeepSeek requires user login.\n"
                    "Please log in manually in the open Chromium browser window, then try again."
                )
            else:
                err_msg = (
                    f"DeepSeek browser interface is not ready ({state_val}).\n"
                    "Check the open Chromium browser, or switch AI Provider to 'Local Offline AI'."
                )
            notify(0.0, err_msg)
            raise RuntimeError(err_msg)

        # 2. Page operations inside browser thread
        def _exec_prompt_submission(page: Page) -> str:
            notify(15.0, "Locating chat input box...")
            self.detector.set_page(page)
            self.long_response_mgr.set_page(page)

            chat_input = self.detector.find_chat_input()
            if not chat_input:
                notify(0.0, "Chat input box not found. Page may still be loading.")
                raise RuntimeError("Chat input element not found in DeepSeek interface.")

            # 3. Enter prompt text and submit
            notify(25.0, "Entering prompt into DeepSeek...")
            chat_input.click()
            chat_input.fill(prompt)
            time.sleep(0.5)

            # Submit via Enter key
            page.keyboard.press("Enter")
            notify(30.0, "Prompt submitted. Awaiting DeepSeek generation...")

            # 4. Long response monitoring with Continue support
            return self.long_response_mgr.monitor_and_collect(
                job_id=job_id,
                progress_callback=notify,
                timeout_seconds=self.config.ai.request_timeout_seconds,
            )

        try:
            result = self.browser_mgr.execute_on_page(_exec_prompt_submission)
        finally:
            with self._lock:
                self._active_job_id = None

        return result

    def cancel_current_request(self) -> None:
        """Abort active prompt submission or response capture."""
        with self._lock:
            if self._active_job_id:
                logger.info(f"Cancelling active AI job: {self._active_job_id}")
                self.long_response_mgr.cancel()
                self._active_job_id = None


_deepseek_controller: Optional[DeepSeekController] = None


def get_deepseek_controller() -> DeepSeekController:
    global _deepseek_controller
    if _deepseek_controller is None:
        _deepseek_controller = DeepSeekController()
    return _deepseek_controller
