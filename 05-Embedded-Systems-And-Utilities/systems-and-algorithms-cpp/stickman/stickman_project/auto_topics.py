import re
import json
import time
from playwright.sync_api import sync_playwright

def fetch_trending_stickman_topics():
    prompt = (
        "Give me 10 highly relatable, viral, and funny Hindi situation topics for YouTube Shorts stickman animations "
        "(topics like daily life struggles, exam panic, office meetings, Indian parents logic, overthinking at 3 AM). "
        "Output strictly as a valid JSON array of strings only. Example: [\"topic 1\", \"topic 2\"]"
    )

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        context = browser.contexts[0]
        page = None
        for p_tab in context.pages:
            if "deepseek.com" in p_tab.url:
                page = p_tab
                break
        if not page:
            page = context.new_page()
            page.goto("https://chat.deepseek.com")
            time.sleep(4)

        page.bring_to_front()
        box = page.wait_for_selector("textarea", timeout=15000)
        box.click()
        box.fill(prompt)
        box.press("Enter")
        time.sleep(5)

        for _ in range(40):
            if not page.query_selector('div[aria-label="Stop"], button:has-text("Stop")'):
                break
            time.sleep(1)

        time.sleep(2)
        elements = page.query_selector_all(".ds-markdown, .markdown")
        raw_text = elements[-1].inner_text() if elements else page.locator("body").inner_text()

        match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if match:
            topics = json.loads(match.group(0))
            with open("topics.txt", "a", encoding="utf-8") as f:
                for t in topics:
                    f.write(f"\n{t}")
            print(f"[SUCCESS] {len(topics)} viral topics added to topics.txt!")

if __name__ == "__main__":
    fetch_trending_stickman_topics()