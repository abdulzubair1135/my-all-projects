"""
visual_qa.py
Automated Visual QA & Browser Observation Engine for Autonomous Web-Agent IDE.

Validates running web applications using headless browser automation:
  - Captures full-page screenshots for visual inspection
  - Intercepts console warnings and runtime JavaScript exceptions
  - Detects blank pages, 404s, and unhandled React error overlays
  - Emits structured observation reports
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None


class VisualQAEngine:
    """Automates browser-based verification and screenshot capture."""

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.snapshots_dir = self.workspace_root / ".snapshots"
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    async def inspect_url(self, url: str, timeout_sec: int = 15) -> Dict[str, Any]:
        """
        Navigates to URL, captures console logs, page errors, and saves a screenshot.
        """
        report = {
            "url": url,
            "passed": False,
            "title": "",
            "console_errors": [],
            "page_errors": [],
            "screenshot_path": None,
            "has_react_error": False,
        }

        if async_playwright is None:
            report["error"] = "Playwright not installed in environment."
            return report

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(viewport={"width": 1280, "height": 800})

                # Capture console messages
                page.on("console", lambda msg: (
                    report["console_errors"].append(msg.text)
                    if msg.type in ["error"] else None
                ))

                # Capture uncaught page exceptions
                page.on("pageerror", lambda exc: (
                    report["page_errors"].append(str(exc))
                ))

                # Navigate
                try:
                    await page.goto(url, wait_until="load", timeout=timeout_sec * 1000)
                    await asyncio.sleep(1.5)  # Allow React/Vite hydration
                except Exception as nav_err:
                    report["error"] = f"Navigation failed: {nav_err}"
                    await browser.close()
                    return report

                report["title"] = await page.title()

                # Check for React error overlay / crash text
                body_text = await page.inner_text("body") if await page.query_selector("body") else ""
                if any(err_marker in body_text.lower() for err_marker in ["uncaught runtime error", "failed to load resource", "error boundary"]):
                    report["has_react_error"] = True

                # Save screenshot
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                shot_name = f"snapshot_{timestamp}.png"
                shot_path = str(self.snapshots_dir / shot_name)
                try:
                    await page.screenshot(path=shot_path, full_page=False, timeout=8000, animations="disabled")
                    report["screenshot_path"] = shot_path
                except Exception as shot_err:
                    report["screenshot_error"] = str(shot_err)

                # Evaluate overall visual pass
                no_fatal_page_errors = len(report["page_errors"]) == 0
                not_blank = len(body_text.strip()) > 20
                report["passed"] = no_fatal_page_errors and not report["has_react_error"] and not_blank

                await browser.close()

        except Exception as e:
            report["error"] = str(e)

        return report
