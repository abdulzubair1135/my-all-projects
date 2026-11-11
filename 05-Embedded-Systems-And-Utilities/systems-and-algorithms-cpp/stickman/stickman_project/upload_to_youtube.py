import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
"""
upload_to_youtube.py  —  FIXED VERSION
----------------------------------------
Fixes:
1. sync_playwright() block hataya → chrome_session (shared singleton) use karta hai
2. Upload ke baad YouTube Studio page properly close hoti hai
3. Error pe exception re-raise karta hai taaki caller decide kar sake
"""

import os
import glob
import json
import time
import chrome_session

OUTPUT_DIR = "pipeline_output"


def get_latest_meta_package():
    meta_files = glob.glob(os.path.join(OUTPUT_DIR, "meta_*.json"))
    if not meta_files:
        print("[!] Koi meta package nahi mila!")
        return None
    latest_file = max(meta_files, key=os.path.getctime)
    with open(latest_file, "r", encoding="utf-8") as f:
        return json.load(f)


def upload_short_via_chrome(meta_data):
    video_path = meta_data["video_path"]
    title = meta_data["title"]
    description = meta_data["description"]
    tags = ", ".join(meta_data["tags"])

    print("\n" + "=" * 55)
    print(f"[*] Uploading to YouTube Studio: {title}")
    print(f"[*] Video File: {video_path}")
    print("=" * 55)

    page = None
    try:
        # Problem 1 fix: shared session use karo, naya playwright nahi
        page = chrome_session.get_or_open_page(
            "studio.youtube.com",
            "https://studio.youtube.com",
            reuse=True
        )
        page.bring_to_front()
        time.sleep(1.5)

        # Auto-dismiss dialogs
        page.on("dialog", lambda dialog: dialog.dismiss())

        # Check if upload dialog already open
        file_input = page.query_selector('input[type="file"]')
        if not file_input:
            print("[*] Clicking Upload button on dashboard...")
            upload_trigger = page.locator(
                'button[aria-label="Upload videos"], '
                'ytcp-icon-button[aria-label="Upload videos"], '
                '#upload-button, button:has-text("Create")'
            ).first
            upload_trigger.click()
            time.sleep(1.5)

            sub_item = page.locator('tp-yt-paper-item:has-text("Upload videos"), #text-item-0')
            if sub_item.count() > 0 and sub_item.first.is_visible():
                sub_item.first.click()
                time.sleep(1.5)

            print("[*] Dropping video file into uploader...")
            file_input = page.wait_for_selector('input[type="file"]', state="attached", timeout=30000)
            file_input.set_input_files(video_path)
            print("[*] Video dispatched! Form load ho raha hai...")
        else:
            print("[*] Upload modal pehle se khula hua mila!")

        time.sleep(2)
        body_text = page.locator("body").inner_text()
        if "Daily upload limit reached" in body_text:
            print("\n" + "!" * 60)
            print("[!] YOUTUBE DAILY UPLOAD LIMIT REACHED!")
            print("[!] Aaj ka YouTube upload quota khatam ho gaya hai. 24 ghante wait karein ya channel one-time verification karein.")
            print("!" * 60 + "\n")
            return "LIMIT_REACHED"

        # 1. Fill Title
        print("[*] Ensuring Title...")
        title_box = page.wait_for_selector(
            '#title-textarea #textbox, #textbox[aria-label*="title" i]',
            timeout=35000
        )
        title_box.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.3)
        title_box.fill(title)

        # 2. Fill Description
        desc_box = page.query_selector('#description-textarea #textbox, #textbox[aria-label*="description" i]')
        if desc_box:
            desc_box.click()
            desc_box.fill(description + "\n\n" + tags)

        # 3. Audience Selection
        print("[*] Setting audience to 'No, it's not Made for Kids'...")
        kids_target = page.locator(
            'tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"], '
            "tp-yt-paper-radio-button:has-text(\"No, it's not made for kids\")"
        ).first
        kids_target.scroll_into_view_if_needed()
        time.sleep(1)
        kids_target.click()
        time.sleep(1.5)

        # 4. Step through Next buttons
        print("[*] Advancing to Visibility tab...")
        for step_num in range(3):
            next_btn = page.wait_for_selector(
                '#next-button, button:has-text("Next")', state="visible", timeout=15000
            )
            while next_btn.get_attribute("aria-disabled") == "true":
                time.sleep(1)
            next_btn.click()
            time.sleep(2)

        # 5. Visibility: Public
        print("[*] Selecting Public...")
        public_radio = page.locator(
            'tp-yt-paper-radio-button[name="PUBLIC"], '
            'tp-yt-paper-radio-button:has-text("Public")'
        ).first
        public_radio.click()
        time.sleep(1.5)

        # 6. Publish
        print("[*] Publishing video...")
        done_btn = page.wait_for_selector('#done-button, button:has-text("Publish")', timeout=10000)
        done_btn.click()

        print("\n" + "=" * 55)
        print("[SUCCESS] Video is Officially Published to YouTube Shorts!")
        print("=" * 55)

    except Exception as e:
        print(f"[!] Upload error: {e}")
        raise

    finally:
        # Problem 3 fix: tab close karo upload ke baad
        chrome_session.close_page_safe(page)
        print("[*] YouTube Studio tab closed (clean).", flush=True)


if __name__ == "__main__":
    pkg = get_latest_meta_package()
    if pkg:
        upload_short_via_chrome(pkg)
