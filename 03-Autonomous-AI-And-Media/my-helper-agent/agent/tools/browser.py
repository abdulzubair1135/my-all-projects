import os
import sys
import time
from playwright.sync_api import sync_playwright

def safe_log(msg: str):
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        try:
            sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
            sys.stdout.buffer.flush()
        except Exception:
            print(msg.encode("ascii", errors="replace").decode("ascii"), flush=True)

class LiveBrowserTool:
    """
    Live Automated Browser using Playwright Chromium:
    - Can run HEADED (visible window) so user can see live what agent is doing!
    - Handles searches, page navigation, live extraction.
    """
    def __init__(self, headless=True):
        self.headless = headless

    def live_search(self, query: str, visible: bool = False, on_step=None, max_results: int = 4) -> dict:
        """
        Launches Playwright Chromium, searches the web live, and extracts top articles.
        If visible=True, user actually sees the browser window pop up!
        """
        def log(msg):
            if on_step:
                on_step(msg)
            else:
                safe_log(msg)

        log(f">> [BROWSER] Launching Chromium (Visible Window={visible})...")
        results = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=not visible,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                )
                page = context.new_page()

                search_url = f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
                log(f">> [NAVIGATING] Opening DuckDuckGo: {search_url}")
                page.goto(search_url, timeout=25000)
                time.sleep(2)

                log(">> [EXTRACTING] Waiting for live search results to load...")
                try:
                    page.wait_for_selector("article, [data-testid='result']", timeout=12000)
                except Exception:
                    pass

                articles = page.query_selector_all("article, [data-testid='result']")
                log(f">> [FOUND] Found {len(articles)} result cards on page.")

                count = 0
                for art in articles:
                    if count >= max_results:
                        break
                    title_elem = art.query_selector("h2 a, [data-testid='result-title-a']")
                    snippet_elem = art.query_selector("[data-result='snippet'], [data-testid='result-snippet']")

                    if title_elem:
                        title = title_elem.inner_text().strip()
                        href = title_elem.get_attribute("href") or ""
                        snippet = snippet_elem.inner_text().strip() if snippet_elem else ""

                        log(f">> [SOURCE {count+1}] {title} -> {href[:65]}...")
                        results.append({"title": title, "link": href, "snippet": snippet})
                        count += 1

                if visible:
                    log(">> [VIEWING] Holding browser visible for 3 seconds...")
                    time.sleep(3)

                browser.close()
                log(">> [BROWSER] Completed live browser session.")

                return {
                    "success": True,
                    "query": query,
                    "results": results,
                    "message": f"Successfully extracted {len(results)} live results."
                }

        except Exception as e:
            log(f">> [BROWSER ERROR] {str(e)}")
            return {
                "success": False,
                "query": query,
                "results": [],
                "error": str(e)
            }
