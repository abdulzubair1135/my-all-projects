"""
chrome_session.py  —  v2 FIXED
================================
3 Problems solved:

PROBLEM 1 — CDP Timeout:
  - connect_over_cdp se pehle HTTP /json/close se ghost tabs band karta hai
  - Timeout 30000ms (was 15000ms)
  - Agar connect fail ho toh Chrome process kill + restart karta hai

PROBLEM 3 — Tab Overload:
  - HTTP-based tab closer (bina playwright ke)
  - Sirf deepseek.com aur studio.youtube.com tabs rakhta hai

Usage:
    import chrome_session
    page = chrome_session.get_or_open_page("deepseek.com", "https://chat.deepseek.com")
    chrome_session.close_page_safe(page)
"""

import time
import subprocess
import os
import urllib.request
import urllib.error
import json as _json

from playwright.sync_api import sync_playwright, Browser, BrowserContext

# ─── Config ────────────────────────────────────────────────────────────────────
CDP_URL        = "http://127.0.0.1:9222"
CONNECT_TIMEOUT = 30000   # ms — was 15000, increased for busy Chrome
MAX_RETRIES     = 4
RETRY_DELAY     = 4       # seconds between retries

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]
CHROME_USER_DIR = r"C:\chrome_dev"

# ─── Internal state ────────────────────────────────────────────────────────────
_playwright_instance = None
_browser: Browser        = None
_context: BrowserContext = None


# ──────────────────────────────────────────────────────────────────────────────
# HTTP helpers  (no Playwright needed — avoids the websocket lock entirely)
# ──────────────────────────────────────────────────────────────────────────────

def _http_get(path: str, timeout: int = 5):
    """Return parsed JSON from Chrome DevTools HTTP endpoint."""
    url = f"{CDP_URL}{path}"
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return _json.loads(r.read())


def _http_close_tab(tab_id: str):
    """Close a tab via HTTP (no WebSocket needed)."""
    try:
        urllib.request.urlopen(f"{CDP_URL}/json/close/{tab_id}", timeout=5)
    except Exception:
        pass


def cleanup_ghost_tabs(keep_keywords=("deepseek.com", "studio.youtube.com")):
    """
    [PROBLEM 3 FIX] HTTP-based tab cleanup — closes all tabs that don't
    match keep_keywords.  Runs *before* connect_over_cdp so CDP handshake
    is not blocked by 20 ghost tabs.
    """
    try:
        tabs = _http_get("/json")
    except Exception as e:
        print(f"[CHROME] Tab cleanup skipped (Chrome not ready): {e}", flush=True)
        return

    closed = 0
    for tab in tabs:
        url  = tab.get("url", "")
        tid  = tab.get("id", "")
        kind = tab.get("type", "")

        # Keep only normal pages matching our keywords
        if kind != "page":
            continue  # skip background, extensions, omnibox etc.
        if any(kw in url for kw in keep_keywords):
            continue
        if url in ("", "about:blank"):
            continue

        _http_close_tab(tid)
        closed += 1

    if closed:
        print(f"[CHROME] Cleaned {closed} ghost tabs via HTTP.", flush=True)
        time.sleep(1)


# ──────────────────────────────────────────────────────────────────────────────
# Chrome process launcher / killer
# ──────────────────────────────────────────────────────────────────────────────

def _kill_chrome_on_port():
    """Kill any Chrome process using port 9222."""
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if "9222" in line and "LISTENING" in line:
                pid = line.strip().split()[-1]
                subprocess.run(["taskkill", "/F", "/PID", pid],
                               capture_output=True)
                print(f"[CHROME] Killed stale Chrome PID {pid}", flush=True)
    except Exception as e:
        print(f"[CHROME] Kill attempt warning: {e}", flush=True)


def _launch_chrome():
    """Launch Chrome with remote debugging on port 9222."""
    chosen = "chrome.exe"
    for p in CHROME_PATHS:
        if os.path.exists(p):
            chosen = p
            break

    args = [
        chosen,
        "--remote-debugging-port=9222",
        f"--user-data-dir={CHROME_USER_DIR}",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    subprocess.Popen(args)
    print("[CHROME] Chrome launched. Waiting 4s for startup...", flush=True)
    time.sleep(4)


def _chrome_reachable() -> bool:
    try:
        _http_get("/json/version", timeout=3)
        return True
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────────────────────
# Singleton browser connection
# ──────────────────────────────────────────────────────────────────────────────

def _get_browser() -> Browser:
    """
    Return a live CDP-connected Browser.
    Strategy:
      1. cleanup ghost tabs via HTTP first (prevents CDP lock)
      2. try connect_over_cdp with 30s timeout
      3. on failure: kill Chrome, relaunch, retry once more
    """
    global _playwright_instance, _browser

    for attempt in range(MAX_RETRIES):
        # Step A: HTTP cleanup before connecting
        cleanup_ghost_tabs()

        try:
            # Re-use existing live connection
            if _browser and _browser.is_connected():
                return _browser

            # Stop stale playwright
            if _playwright_instance:
                try:
                    _playwright_instance.stop()
                except Exception:
                    pass

            _playwright_instance = sync_playwright().start()
            _browser = _playwright_instance.chromium.connect_over_cdp(
                CDP_URL, timeout=CONNECT_TIMEOUT
            )
            print(f"[CHROME] Connected on attempt {attempt + 1}", flush=True)
            return _browser

        except Exception as e:
            print(f"[CHROME] Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}", flush=True)

            if attempt < MAX_RETRIES - 1:
                # Try to recover: kill & restart Chrome if port is dead
                if not _chrome_reachable():
                    print("[CHROME] Chrome unreachable — restarting...", flush=True)
                    _kill_chrome_on_port()
                    time.sleep(2)
                    _launch_chrome()
                else:
                    print(f"[CHROME] Chrome alive but CDP busy. Waiting {RETRY_DELAY}s...", flush=True)
                    time.sleep(RETRY_DELAY)

    raise RuntimeError(
        f"[CHROME] Could not connect to Chrome on {CDP_URL} "
        f"after {MAX_RETRIES} retries. "
        "Chrome manually kholo: start_deepseek_chrome.bat"
    )


def _get_context() -> BrowserContext:
    global _context
    browser = _get_browser()
    _context = browser.contexts[0]
    return _context


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def get_or_open_page(url_keyword: str, navigate_url: str, reuse: bool = True):
    """
    Return an existing tab whose URL contains url_keyword, OR open a new one.
    Always brings the page to front.

    Args:
        url_keyword  : substring to find in existing tabs (e.g. 'deepseek.com')
        navigate_url : URL to navigate to if no matching tab found
        reuse        : if False, always open a new tab
    """
    context = _get_context()

    if reuse:
        for tab in context.pages:
            if url_keyword in tab.url:
                try:
                    tab.bring_to_front()
                    return tab
                except Exception:
                    pass  # Tab may be dead; fall through

    page = context.new_page()
    page.goto(navigate_url, wait_until="domcontentloaded", timeout=30000)
    page.bring_to_front()
    return page


def close_page_safe(page):
    """Close a page without raising if it's already closed or None."""
    try:
        if page and not page.is_closed():
            page.close()
    except Exception as e:
        print(f"[CHROME] Page close warning: {e}", flush=True)


def close_all_extra_tabs(keep_url_keywords=("deepseek.com", "studio.youtube.com")):
    """
    Close all PAGE-type tabs that don't match keep_url_keywords.
    Uses HTTP close first (faster, no CDP lock risk). Only cleans Playwright pages if already connected.
    """
    # 1. HTTP-based close (preferred and safe)
    cleanup_ghost_tabs(keep_keywords=keep_url_keywords)

    # 2. Only check Playwright if already connected (NEVER trigger a new connection/restart for cleanup!)
    global _context
    if _context is not None:
        try:
            for tab in list(_context.pages):
                should_keep = any(kw in tab.url for kw in keep_url_keywords)
                if not should_keep and tab.url not in ("about:blank", "chrome://newtab/", ""):
                    close_page_safe(tab)
        except Exception:
            pass


def shutdown():
    """Gracefully stop the playwright instance."""
    global _playwright_instance, _browser, _context
    try:
        if _playwright_instance:
            _playwright_instance.stop()
    except Exception:
        pass
    _playwright_instance = None
    _browser = None
    _context = None
    print("[CHROME] Session shut down.", flush=True)
