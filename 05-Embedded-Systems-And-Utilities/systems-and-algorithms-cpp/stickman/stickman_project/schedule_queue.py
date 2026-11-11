import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

"""
schedule_queue.py
-----------------
Automates YouTube Studio upload with YouTube Daily Upload Limit Detection.
"""

import os
import time
import chrome_session

class DailyUploadLimitReached(Exception):
    """Raised when YouTube Studio displays 'Daily upload limit reached'."""
    pass

def check_daily_limit(page):
    """
    Checks if YouTube Studio modal shows 'Daily upload limit reached' alert banner.
    Returns True if limit is hit, else False.
    """
    try:
        limit_locator = page.locator('text="Daily upload limit reached", [aria-label*="Daily upload limit" i]')
        if limit_locator.count() > 0 and limit_locator.first.is_visible():
            return True
        # Check text in body or dialog
        body_text = page.locator('ytcp-uploads-dialog, ytcp-dialog, body').inner_text()
        if "Daily upload limit reached" in body_text:
            return True
    except Exception:
        pass
    return False

def schedule_video_on_youtube(meta_data, release_time):
    video_path = meta_data["video_path"]
    title = meta_data["title"]
    description = meta_data["description"]
    tags = ", ".join(meta_data["tags"])

    print("\n" + "=" * 55)
    print(f"[*] YouTube Uploading: {title}")
    print(f"[*] Target Schedule: {release_time.strftime('%b %d, %Y %I:%M %p')}")
    print("=" * 55)

    page = None
    try:
        page = chrome_session.get_or_open_page(
            "studio.youtube.com",
            "https://studio.youtube.com",
            reuse=True
        )
        time.sleep(2)
        page.on("dialog", lambda dialog: dialog.dismiss())

        # Check if daily limit was already open
        if check_daily_limit(page):
            raise DailyUploadLimitReached("Daily upload limit reached on YouTube Studio!")

        # Upload trigger
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

        file_input = page.wait_for_selector('input[type="file"]', state="attached", timeout=30000)
        file_input.set_input_files(video_path)
        print("[*] Video dispatched to YouTube Studio...")

        # Wait 3-4s and check if YouTube immediately flags Daily upload limit
        time.sleep(3)
        if check_daily_limit(page):
            raise DailyUploadLimitReached("Daily upload limit reached on YouTube Studio!")

        title_box = page.wait_for_selector(
            '#title-textarea #textbox, #textbox[aria-label*="title" i]',
            timeout=35000
        )
        time.sleep(2)

        # Check again during form load
        if check_daily_limit(page):
            raise DailyUploadLimitReached("Daily upload limit reached on YouTube Studio!")

        title_box.click()
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        time.sleep(0.3)
        title_box.fill(title)

        desc_box = page.query_selector('#description-textarea #textbox, #textbox[aria-label*="description" i]')
        if desc_box:
            desc_box.click()
            desc_box.fill(description + "\n\n" + tags)

        kids_target = page.locator(
            'tp-yt-paper-radio-button[name="VIDEO_MADE_FOR_KIDS_NOT_MFK"], '
            "tp-yt-paper-radio-button:has-text(\"No, it's not made for kids\")"
        ).first
        kids_target.scroll_into_view_if_needed()
        kids_target.click()
        time.sleep(1.5)

        for _ in range(3):
            next_btn = page.wait_for_selector(
                '#next-button, button:has-text("Next")', state="visible", timeout=15000
            )
            while next_btn.get_attribute("aria-disabled") == "true":
                # If disabled, verify whether Daily limit was hit
                if check_daily_limit(page):
                    raise DailyUploadLimitReached("Daily upload limit reached on YouTube Studio!")
                time.sleep(1)
            next_btn.click()
            time.sleep(2)

        public_radio = page.locator(
            'tp-yt-paper-radio-button[name="PUBLIC"], '
            'tp-yt-paper-radio-button:has-text("Public")'
        ).first
        public_radio.click()
        time.sleep(1.5)

        done_btn = page.wait_for_selector('#done-button, button:has-text("Publish")', timeout=10000)
        done_btn.click()
        print(f"[SUCCESS] Video successfully published on YouTube Studio!")
        time.sleep(8)

    except DailyUploadLimitReached as d_err:
        print(f"\n[!] LIMIT DETECTED: {d_err}")
        # Close upload dialog if possible
        try:
            close_btn = page.locator('#close-button, [aria-label="Close"]').first
            if close_btn.is_visible():
                close_btn.click()
        except Exception:
            pass
        raise d_err

    except Exception as e:
        # Check if limit banner is visible before general exception
        if page and check_daily_limit(page):
            raise DailyUploadLimitReached("Daily upload limit reached on YouTube Studio!")
        print(f"[!] Schedule / Upload error: {e}")
        raise

    finally:
        chrome_session.close_page_safe(page)
        print("[*] YouTube Studio tab closed (clean).", flush=True)
