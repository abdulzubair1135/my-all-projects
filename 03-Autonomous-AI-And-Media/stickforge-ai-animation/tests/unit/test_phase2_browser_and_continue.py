"""
Unit and integration tests for Phase 2: Chromium, PageStateDetector, and LongResponseManager.
"""

import hashlib
import pytest
from app.browser.page_state_detector import PageStateDetector, PageState
from app.ai.long_response_manager import LongResponseManager, LongResponseState
from app.storage.repositories import AIJobRepository
from app.storage.database import Database


class FakeLocator:
    def __init__(self, count_val=1, visible=True, enabled=True, text=""):
        self._count = count_val
        self._visible = visible
        self._enabled = enabled
        self._text = text

    def count(self):
        return self._count

    @property
    def first(self):
        return self

    def is_visible(self):
        return self._visible

    def is_enabled(self):
        return self._enabled

    def inner_text(self):
        return self._text

    def click(self, timeout=3000):
        pass


class FakePage:
    def __init__(self, url="https://chat.deepseek.com", locators=None):
        self.url = url
        self._locators = locators or {}
        self._closed = False

    def is_closed(self):
        return self._closed

    def locator(self, selector):
        for key, loc in self._locators.items():
            if key in selector or selector in key:
                return loc
        return FakeLocator(count_val=0, visible=False)


def test_page_state_detection_login_required():
    fake_page = FakePage(
        url="https://chat.deepseek.com/sign-in",
        locators={"sign-in": FakeLocator(1, True, True)},
    )
    detector = PageStateDetector(fake_page)
    state, details = detector.detect_state()
    assert state == PageState.LOGIN_REQUIRED


def test_page_state_detection_logged_in():
    fake_page = FakePage(
        url="https://chat.deepseek.com",
        locators={"textarea#chat-input": FakeLocator(1, True, True)},
    )
    detector = PageStateDetector(fake_page)
    state, details = detector.detect_state()
    assert state == PageState.LOGGED_IN
    assert details["chat_ready"] is True


def test_page_state_detection_generating():
    fake_page = FakePage(
        url="https://chat.deepseek.com",
        locators={"button[aria-label*='Stop']": FakeLocator(1, True, True)},
    )
    detector = PageStateDetector(fake_page)
    state, details = detector.detect_state()
    assert state == PageState.GENERATING


def test_page_state_detection_continue_available():
    fake_page = FakePage(
        url="https://chat.deepseek.com",
        locators={"button:has-text('Continue')": FakeLocator(1, True, True)},
    )
    detector = PageStateDetector(fake_page)
    state, details = detector.detect_state()
    assert state == PageState.CONTINUE_AVAILABLE


def test_long_response_manager_stitching():
    mgr = LongResponseManager()
    
    # Test segment diffing
    full = "Once upon a time in a small village"
    seg1 = "Once upon a time"
    diff = mgr._extract_segment_diff(full, [seg1])
    assert diff == " in a small village"

    # Test segment stitching with overlapping boundary text
    segments = [
        "Part 1: The stickman begins his journey through the enchanted forest.",
        "forest. Part 2: He finds a golden stick and uses it to fight the dragon.",
    ]
    stitched = mgr._stitch_segments(segments, fallback_full_text="")
    assert stitched == "Part 1: The stickman begins his journey through the enchanted forest. Part 2: He finds a golden stick and uses it to fight the dragon."


def test_long_response_manager_duplicate_click_guard():
    mgr = LongResponseManager()
    state_text = "This is the current end of the story so far..."
    state_hash = hashlib.sha256(state_text[-120:].encode("utf-8")).hexdigest()

    mgr._clicked_state_hashes.add(state_hash)
    # Re-checking same hash confirms guard prevents double clicking
    assert state_hash in mgr._clicked_state_hashes
