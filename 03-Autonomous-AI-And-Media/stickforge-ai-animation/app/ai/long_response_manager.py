"""
Long Response Manager for DeepSeek Web Automation.
Handles multi-part AI generation with guarded automatic Continue handling,
duplicate-click protection, and incremental SQLite persistence.
"""

from __future__ import annotations
import enum
import hashlib
import time
from typing import Callable, Dict, Any, List, Optional
from playwright.sync_api import Page

from app.core.logging_manager import get_logger
from app.browser.page_state_detector import PageStateDetector, PageState
from app.storage.repositories import AIJobRepository

logger = get_logger("long_response_mgr")


class LongResponseState(str, enum.Enum):
    IDLE = "IDLE"
    PREPARING_REQUEST = "PREPARING_REQUEST"
    SUBMITTING = "SUBMITTING"
    WAITING_FOR_RESPONSE = "WAITING_FOR_RESPONSE"
    GENERATING = "GENERATING"
    CONTINUE_AVAILABLE = "CONTINUE_AVAILABLE"
    CONTINUING = "CONTINUING"
    RESPONSE_COMPLETE = "RESPONSE_COMPLETE"
    VALIDATING_OUTPUT = "VALIDATING_OUTPUT"
    SAVING_OUTPUT = "SAVING_OUTPUT"
    SUCCESS = "SUCCESS"
    RETRY_WAIT = "RETRY_WAIT"
    SESSION_EXPIRED = "SESSION_EXPIRED"
    AUTHENTICATION_REQUIRED = "AUTHENTICATION_REQUIRED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class LongResponseManager:
    """Orchestrates long prompt responses across multiple Continue steps."""

    def __init__(
        self,
        page: Optional[Page] = None,
        max_continues: int = 10,
        continue_debounce_seconds: float = 2.0,
        repo: Optional[AIJobRepository] = None,
    ):
        self.page = page
        self.detector = PageStateDetector(page)
        self.max_continues = max_continues
        self.continue_debounce_seconds = continue_debounce_seconds
        self.repo = repo or AIJobRepository()

        self.current_state = LongResponseState.IDLE
        self._cancelled = False
        self._clicked_state_hashes: set[str] = set()

    def set_page(self, page: Page) -> None:
        self.page = page
        self.detector.set_page(page)

    def cancel(self) -> None:
        """Signal ongoing response capture to abort cleanly."""
        self._cancelled = True
        self.current_state = LongResponseState.CANCELLED
        logger.info("Long response capture cancelled by user.")

    def monitor_and_collect(
        self,
        job_id: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
        timeout_seconds: int = 240,
    ) -> str:
        """
        Polls the generation, automatically handles Continue button,
        persists segments incrementally, and returns stitched response text.
        """
        self._cancelled = False
        self._clicked_state_hashes.clear()
        self.current_state = LongResponseState.WAITING_FOR_RESPONSE

        start_time = time.time()
        segment_index = 0
        collected_segments: List[str] = []
        last_text = ""
        continue_count = 0

        def notify(prog: float, msg: str):
            if progress_callback:
                progress_callback(prog, msg)

        logger.info(f"Starting long response monitoring for job {job_id}...")
        notify(10.0, "Waiting for DeepSeek to begin responding...")

        while time.time() - start_time < timeout_seconds:
            if self._cancelled:
                self.repo.update_status(job_id, "CANCELLED", error_message="User cancelled.")
                return ""

            state, details = self.detector.detect_state()

            # 1. Check for Authentication Challenge or Login Required
            if state in [PageState.LOGIN_REQUIRED, PageState.SESSION_EXPIRED]:
                self.current_state = LongResponseState.SESSION_EXPIRED
                notify(0.0, "DeepSeek session expired. Manual login required.")
                self.repo.update_status(job_id, "FAILED", error_message="Session expired.")
                return ""

            if state == PageState.CHALLENGE_REQUIRED:
                self.current_state = LongResponseState.AUTHENTICATION_REQUIRED
                notify(0.0, "Security challenge (Cloudflare/CAPTCHA) detected. Please solve in browser.")
                time.sleep(2.0)
                continue

            # 2. Check for Error banner
            if state == PageState.ERROR_PAGE:
                self.current_state = LongResponseState.FAILED
                err = f"DeepSeek returned an error: {details}"
                notify(0.0, err)
                self.repo.update_status(job_id, "FAILED", error_message=err)
                return ""

            # 3. Active Streaming Generation
            if state == PageState.GENERATING:
                self.current_state = LongResponseState.GENERATING
                current_dom_text = self._extract_latest_response_text()
                if len(current_dom_text) > len(last_text):
                    last_text = current_dom_text
                    notify(30.0 + min(40.0, len(last_text) / 50.0), f"Generating story... ({len(last_text)} chars)")
                time.sleep(1.0)
                continue

            # 4. Continue Action Available
            if state == PageState.CONTINUE_AVAILABLE:
                self.current_state = LongResponseState.CONTINUE_AVAILABLE
                if continue_count >= self.max_continues:
                    logger.warning(f"Reached max continue limit ({self.max_continues}). Stopping.")
                    break

                # Safeguard: check state hash to prevent duplicate clicks
                current_dom_text = self._extract_latest_response_text()
                state_hash = hashlib.sha256(current_dom_text[-120:].encode("utf-8")).hexdigest()

                if state_hash in self._clicked_state_hashes:
                    logger.debug("Duplicate continue state detected. Waiting for response advancement...")
                    time.sleep(1.0)
                    continue

                # Save current segment before continuing
                if current_dom_text:
                    diff_segment = self._extract_segment_diff(current_dom_text, collected_segments)
                    if diff_segment.strip():
                        collected_segments.append(diff_segment)
                        self.repo.add_segment(job_id, segment_index, diff_segment)
                        segment_index += 1

                # Perform one guarded continue click
                notify(75.0, f"Triggering Continue ({continue_count + 1}/{self.max_continues})...")
                continue_btn = self.detector.find_continue_button()
                if continue_btn:
                    try:
                        self.current_state = LongResponseState.CONTINUING
                        continue_btn.click(timeout=3000)
                        self._clicked_state_hashes.add(state_hash)
                        continue_count += 1
                        logger.info(f"Safely executed Continue action #{continue_count}")
                        # Debounce wait
                        time.sleep(self.continue_debounce_seconds)
                    except Exception as e:
                        logger.warning(f"Continue button click attempt failed: {e}")
                time.sleep(1.0)
                continue

            # 5. Response Complete (Chat input active and no generation)
            if state == PageState.LOGGED_IN and last_text:
                self.current_state = LongResponseState.RESPONSE_COMPLETE
                current_dom_text = self._extract_latest_response_text()
                diff_segment = self._extract_segment_diff(current_dom_text, collected_segments)
                if diff_segment.strip():
                    collected_segments.append(diff_segment)
                    self.repo.add_segment(job_id, segment_index, diff_segment)
                    segment_index += 1
                break

            time.sleep(1.0)

        # Stitch all segments safely
        final_text = self._stitch_segments(collected_segments, last_text)
        self.current_state = LongResponseState.SUCCESS
        notify(100.0, f"AI generation completed successfully ({len(final_text)} chars).")
        self.repo.update_status(job_id, "COMPLETED", result_json=final_text)
        return final_text

    def _extract_latest_response_text(self) -> str:
        """Extract text from the most recent assistant message bubble in the DOM."""
        if not self.page or self.page.is_closed():
            return ""
        try:
            # DeepSeek message bubble containers
            bubbles = self.page.locator(".ds-markdown, div[class*='message-content'], div.markdown")
            count = bubbles.count()
            if count > 0:
                return bubbles.nth(count - 1).inner_text()
        except Exception as e:
            logger.debug(f"Could not extract assistant bubble: {e}")
        return ""

    def _extract_segment_diff(self, full_text: str, prior_segments: List[str]) -> str:
        """Extract only the new text added since prior segments."""
        already_collected = "".join(prior_segments)
        if full_text.startswith(already_collected):
            return full_text[len(already_collected):]
        return full_text

    def _stitch_segments(self, segments: List[str], fallback_full_text: str) -> str:
        """Stitch collected segments, eliminating duplicate boundary text."""
        if not segments:
            return fallback_full_text

        assembled = segments[0]
        for seg in segments[1:]:
            # Check overlap between tail of assembled and head of seg
            overlap_len = 0
            for i in range(min(len(assembled), len(seg), 80), 0, -1):
                if assembled.endswith(seg[:i]):
                    overlap_len = i
                    break
            assembled += seg[overlap_len:]

        # Validate assembled length against fallback
        if len(assembled) < len(fallback_full_text) * 0.8:
            return fallback_full_text
        return assembled
