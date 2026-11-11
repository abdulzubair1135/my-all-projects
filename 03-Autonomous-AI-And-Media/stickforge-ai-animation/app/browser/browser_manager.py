"""
Browser Manager for StickForge AI.
Controls visible Chromium browser instances using Playwright with dedicated persistent profiles.
Preserves user sessions securely without extracting plaintext cookies.
Features single-thread executor confinement to guarantee thread safety across Qt worker threads.
"""

from __future__ import annotations
import concurrent.futures
import os
import queue
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from playwright.sync_api import sync_playwright, BrowserContext, Page, Playwright

from app.core.config import BROWSER_USER_DATA_DIR, get_config
from app.core.logging_manager import get_logger
from app.core.event_bus import get_event_bus

logger = get_logger("browser_manager")


class BrowserWorkerThread(threading.Thread):
    """Dedicated background thread owning Playwright to guarantee thread-safe operation."""

    def __init__(self):
        super().__init__(name="PlaywrightBrowserWorker", daemon=True)
        self.task_queue: queue.Queue = queue.Queue()
        self._running = True

    def run(self):
        while self._running:
            try:
                task = self.task_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if task is None:
                break

            func, args, kwargs, future = task
            try:
                result = func(*args, **kwargs)
                future.set_result(result)
            except Exception as e:
                future.set_exception(e)
            finally:
                self.task_queue.task_done()

    def submit(self, func: Callable, *args, **kwargs) -> Any:
        future = concurrent.futures.Future()
        self.task_queue.put((func, args, kwargs, future))
        return future.result(timeout=60)

    def stop(self):
        self._running = False
        self.task_queue.put(None)


class BrowserManager:
    """Manages dedicated persistent Chromium sessions."""

    def __init__(self, user_data_dir: Optional[Path] = None):
        self.user_data_dir = user_data_dir or BROWSER_USER_DATA_DIR
        self.config = get_config()
        self._worker: Optional[BrowserWorkerThread] = None
        self.playwright: Optional[Playwright] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.event_bus = get_event_bus()

    def _ensure_worker(self) -> BrowserWorkerThread:
        if self._worker is None or not self._worker.is_alive():
            self._worker = BrowserWorkerThread()
            self._worker.start()
        return self._worker

    def is_running(self) -> bool:
        """Check if browser process and page are active."""
        if not self._worker or not self._worker.is_alive():
            return False
        return self._ensure_worker().submit(self._is_running_impl)

    def _is_running_impl(self) -> bool:
        if not self.context or not self.page:
            return False
        try:
            return not self.page.is_closed()
        except Exception:
            return False

    def launch(self, force_visible: bool = True) -> Any:
        """Launch visible persistent Chromium session on dedicated thread."""
        return self._ensure_worker().submit(self._launch_impl, force_visible)

    def _launch_impl(self, force_visible: bool = True):
        if self._is_running_impl():
            logger.info("Browser already running. Bringing page to focus.")
            self._focus_impl()
            return self.page

        self.user_data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Launching Chromium with persistent profile: {self.user_data_dir}")

        if not self.playwright:
            self.playwright = sync_playwright().start()

        # Visible mode by default unless explicitly headless
        headless = False if force_visible else self.config.browser.headless

        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=headless,
            slow_mo=self.config.browser.slow_mo_ms,
            viewport={
                "width": self.config.browser.viewport_width,
                "height": self.config.browser.viewport_height,
            },
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized",
                "--no-default-browser-check",
                "--disable-infobars",
            ],
            ignore_default_args=["--enable-automation"],
        )

        if len(self.context.pages) > 0:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()

        self.event_bus.publish("browser_launched", visible=not headless)
        logger.info("Visible persistent Chromium session established.")
        return self.page

    def navigate(self, url: str) -> None:
        """Navigate active page to URL with timeout handling."""
        self._ensure_worker().submit(self._navigate_impl, url)

    def _navigate_impl(self, url: str) -> None:
        if not self._is_running_impl():
            self._launch_impl()
        logger.info(f"Navigating to: {url}")
        assert self.page is not None
        self.page.goto(url, timeout=self.config.browser.navigation_timeout_ms, wait_until="domcontentloaded")

    def focus(self) -> None:
        """Bring browser page to foreground."""
        if self._worker and self._worker.is_alive():
            self._ensure_worker().submit(self._focus_impl)

    def _focus_impl(self) -> None:
        if self.page and not self.page.is_closed():
            try:
                self.page.bring_to_front()
            except Exception as e:
                logger.debug(f"Could not bring page to front: {e}")

    def take_screenshot(self, output_path: Path) -> Optional[Path]:
        """Capture diagnostic screenshot."""
        if not self._worker or not self._worker.is_alive():
            return None
        return self._ensure_worker().submit(self._take_screenshot_impl, output_path)

    def _take_screenshot_impl(self, output_path: Path) -> Optional[Path]:
        if self.page and not self.page.is_closed():
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                self.page.screenshot(path=str(output_path), full_page=False)
                return output_path
            except Exception as e:
                logger.warning(f"Screenshot capture failed: {e}")
        return None

    def execute_on_page(self, callback: Callable[[Page], Any]) -> Any:
        """Execute arbitrary page inspection or action on the dedicated thread."""
        return self._ensure_worker().submit(lambda: callback(self.page))

    def close(self) -> None:
        """Safely close context and Playwright instance without wiping profile."""
        if self._worker and self._worker.is_alive():
            self._ensure_worker().submit(self._close_impl)

    def _close_impl(self) -> None:
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
        except Exception as e:
            logger.warning(f"Error during browser shutdown: {e}")
        finally:
            self.context = None
            self.page = None
            self.playwright = None
            self.event_bus.publish("browser_closed")
            logger.info("Browser session closed cleanly.")


# Singleton BrowserManager
_browser_manager: Optional[BrowserManager] = None


def get_browser_manager() -> BrowserManager:
    global _browser_manager
    if _browser_manager is None:
        _browser_manager = BrowserManager()
    return _browser_manager
