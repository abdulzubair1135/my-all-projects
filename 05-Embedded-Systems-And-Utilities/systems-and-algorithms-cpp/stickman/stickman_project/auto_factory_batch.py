import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

"""
auto_factory_batch.py
---------------------
Autonomous Queue & Memory Engine with YouTube Daily Upload Limit Handler.
"""

import os
import sys
import time
import json
import subprocess
import socket
import re
from datetime import datetime, timedelta
import chrome_session

TOPICS_FILE = "topics.txt"
DONE_TOPICS_FILE = "done_topics.txt"
STATE_FILE = "schedule_state.json"


def log(msg, symbol="[*]"):
    print(f"{symbol} [{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def get_done_topics():
    if not os.path.exists(DONE_TOPICS_FILE):
        return set()
    done = set()
    with open(DONE_TOPICS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "|" in line:
                done.add(line.split("|", 1)[1].strip().lower())
            elif line:
                done.add(line.lower())
    return done


def check_internet():
    dot_count = 0
    while True:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            log("INTERNET CONNECTED! Online access active.", "[OK]")
            return True
        except OSError:
            dot_count += 1
            print(f"\r[SEARCHING] Hotspot connect hone ka intezar hai ({dot_count}s)...", end="", flush=True)
            time.sleep(1)


def launch_chrome_debugger():
    log("Chrome Debugger launch check...", "[CHROME]")
    try:
        import urllib.request
        with urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=2) as r:
            tabs = json.loads(r.read())
        log("Chrome already active on port 9222!", "[OK]")

        # RULE: Agar DeepSeek tab pehle se open hai -> search ya reload bilkul mat karo!
        for t in tabs:
            if "deepseek.com" in t.get("url", ""):
                log(f"DeepSeek tab pehle se open hai ('{t.get('title')[:30]}...')! Koi nayi search nahi hogi.", "[OK]")
                return True

        # Agar DeepSeek tab nahi mila, tabhi navigate karo
        log("DeepSeek tab pehle se open nahi hai, chat.deepseek.com open kar rahe hain...", "[NAVIGATE]")
        urllib.request.urlopen("http://127.0.0.1:9222/json/new?https://chat.deepseek.com", timeout=5)
        time.sleep(3)
        return True
    except Exception:
        pass

    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        "chrome.exe"
    ]
    chosen_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    for cp in chrome_paths:
        if os.path.exists(cp):
            chosen_path = cp
            break

    cmd = (
        f'cmd.exe /c start "" "{chosen_path}" --remote-debugging-port=9222 '
        r'--user-data-dir="C:\chrome_dev" --no-first-run --no-default-browser-check '
        r'https://chat.deepseek.com https://studio.youtube.com'
    )
    subprocess.Popen(cmd, shell=True)
    
    for _ in range(8):
        time.sleep(1)
        try:
            import urllib.request
            urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=1)
            log("Chrome Debugger successfully launched on port 9222!", "[OK]")
            return True
        except Exception:
            pass
    return False


def verify_video_complete(v_path, min_size_bytes=1000000, max_wait_sec=30):
    """
    Guarantees the video file exists, is completely written, not in use,
    and passes full ffmpeg stream integrity check.
    If writing is still completing, waits in a loop up to max_wait_sec.
    """
    if not v_path:
        return False

    log(f"Video completion verification: checking '{v_path}'...", "[VERIFY]")
    start_t = time.time()
    while time.time() - start_t < max_wait_sec:
        if os.path.exists(v_path):
            current_size = os.path.getsize(v_path)
            if current_size >= min_size_bytes:
                try:
                    chk = subprocess.run(
                        ["ffmpeg", "-v", "error", "-i", v_path, "-f", "null", "-"],
                        capture_output=True,
                        timeout=15
                    )
                    if chk.returncode == 0:
                        log(f"VIDEO 100% COMPLETE & VERIFIED: {v_path} ({current_size // 1024} KB)!", "[COMPLETE]")
                        return True
                except Exception:
                    pass
            log("Video file abhi write/flush ho rahi hai, ruk rahe hain...", "[WAIT]")
        time.sleep(3)

    return False


def get_next_schedule_slot():
    now = datetime.now()
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                last_time_str = data.get("last_scheduled_time")
                if last_time_str:
                    last_time = datetime.fromisoformat(last_time_str)
                    if last_time > now:
                        return last_time + timedelta(hours=2)
        except Exception:
            pass
    return now + timedelta(hours=1)


def save_last_schedule_slot(slot_time):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_scheduled_time": slot_time.isoformat()}, f, indent=2)


def get_remaining_topics():
    if not os.path.exists(TOPICS_FILE):
        return []
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def peek_first_topic():
    topics = get_remaining_topics()
    return topics[0] if topics else None


def mark_topic_done(topic):
    topics = get_remaining_topics()
    clean_topic = topic.strip()
    if clean_topic in topics:
        topics.remove(clean_topic)
        with open(TOPICS_FILE, "w", encoding="utf-8") as f:
            for t in topics:
                f.write(f"{t}\n")
    
    # Save permanently into done_topics.txt so it's NEVER repeated!
    with open(DONE_TOPICS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {clean_topic}\n")
    log(f"Topic permanently recorded in '{DONE_TOPICS_FILE}' & removed from queue: '{clean_topic}'", "[DONE_LOG]")


def return_topic_to_queue(topic):
    existing = get_remaining_topics()
    if topic not in existing:
        all_topics = [topic] + existing
        with open(TOPICS_FILE, "w", encoding="utf-8") as f:
            for t in all_topics:
                f.write(f"{t}\n")
        log(f"Topic RETURNED to top of queue: '{topic}'", "[RECOVER]")
    else:
        log(f"Topic already in queue: '{topic}'", "[INFO]")


CURIOSITY_TOPICS_RESERVOIR = [
    "Why Do We Hear Sounds Through Our Ears?",
    "Why Can't We Tickle Ourselves?",
    "Why Does Ice Float On Water When Solids Sink?",
    "What Actually Happens Inside A Black Hole?",
    "Why Does Your Brain Freeze When Drinking Slushie?",
    "Why Do Onions Make Us Cry?",
    "How Do Whales Sleep Underwater Without Drowning?",
    "Why Does The Moon Change Shape Every Night?",
    "Why Can't We Remember Being A Baby?",
    "Why Do Flamingos Stand On One Leg?",
    "How Does Soap Actually Kill Bacteria?",
    "Why Is The Sky Blue During Day But Black At Night?",
    "Why Do Your Fingers Wrinkle In Water?",
    "Why Do We Get Goosebumps When Scared Or Cold?",
    "Why Does Helium Make Your Voice Squeaky?",
    "What Is Lightning Really Made Of?",
    "Why Do Stars Twinkle In The Sky?",
    "Why Do We Yawn When We See Someone Else Yawn?",
    "Why Is Ocean Water Salty But Rain Is Fresh?",
    "Why Do Cats Always Land On Their Feet?",
    "Why Do Mirages Happen In Hot Deserts?",
    "What Actually Triggers An Earthquake?",
    "Why Can Birds Sit On High Voltage Power Lines Safely?",
    "Why Does Hot Water Freeze Faster Than Cold Water?",
    "Why Does Shivering Keep Your Body Warm?",
    "How Does Glass Look Transparent While Sand Is Opaque?",
    "Why Do Chameleons Really Change Colors?",
    "How Do Airplanes Stay In The Air Despite Heavy Weight?",
    "Why Do We Dream When We Sleep?",
    "Why Is Honey The Only Food That Never Spoils?",
    "How Do Magnets Pull Things Through Air?",
    "Why Does Salt Melt Ice On Frozen Roads?",
    "Why Do Fireflies Glow In Total Darkness?",
    "Why Do Autumn Leaves Change Color?",
    "Why Does A Sliced Apple Turn Brown?",
    "How Do Bats Hunt And Fly In Pure Darkness?",
    "Why Can Camels Go Weeks Without Water?",
    "Why Does Your Stomach Growl When Hungry?",
    "Why Do We Blink Without Realizing It?",
    "Why Do Tears Taste Salty?"
]


def refill_viral_topics_if_needed():
    topics = get_remaining_topics()
    if len(topics) >= 4:
        return

    log("Topics queue low! Fetching fresh curiosity science topics...", "[REFILL]")
    done_set = get_done_topics()
    existing_set = {t.lower() for t in topics}

    prompt = (
        "Give me 10 mind-blowing, highly viral 'Did you know?' science curiosity topics for 30-second YouTube shorts (e.g. why ice floats, why onions make us cry, how bats see in dark). "
        'Strictly output a single raw JSON array of strings only. Example: ["topic 1", "topic 2"]'
    )

    added = False
    try:
        import direct_deepseek
        raw_text = direct_deepseek.ask_deepseek(prompt, max_wait_sec=45)
        match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if match:
            new_topics = json.loads(match.group(0))
            count_added = 0
            with open(TOPICS_FILE, "a", encoding="utf-8") as f:
                for item in new_topics:
                    clean_item = re.sub(r'^\d+[\.\-\s]+', '', str(item)).strip()
                    if clean_item and clean_item.lower() not in existing_set and clean_item.lower() not in done_set:
                        f.write(f"{clean_item}\n")
                        existing_set.add(clean_item.lower())
                        count_added += 1
            if count_added > 0:
                log(f"{count_added} fresh curiosity topics added from DeepSeek!", "[SUCCESS]")
                added = True
    except Exception as e:
        log(f"DeepSeek online refill note ({e}) - using reservoir pool", "[INFO]")

    if not added:
        import random
        pool = [t for t in CURIOSITY_TOPICS_RESERVOIR if t.lower() not in existing_set and t.lower() not in done_set]
        selected = random.sample(pool, min(10, len(pool)))
        with open(TOPICS_FILE, "a", encoding="utf-8") as f:
            for item in selected:
                f.write(f"{item}\n")
        log(f"{len(selected)} curiosity topics added from reservoir pool! Queue never empty!", "[SUCCESS]")


def main():
    os.system("cls")
    print("=" * 80)
    print("        STICKMAN FACTORY: AUTONOMOUS QUEUE & MEMORY ENGINE")
    print("=" * 80)

    check_internet()
    launch_chrome_debugger()

    from curiosity_engine import produce_curiosity_short as process_full_production
    from schedule_queue import schedule_video_on_youtube, DailyUploadLimitReached

    refill_viral_topics_if_needed()

    BATCH_COUNT = 5
    processed_count = 0
    failed_count = 0

    for i in range(BATCH_COUNT):
        topic = peek_first_topic()
        if not topic:
            refill_viral_topics_if_needed()
            topic = peek_first_topic()
            if not topic:
                log("Koi topic bacha nahi!", "[STOP]")
                break

        clean_topic = re.sub(r'^\d+[\.\-\s]+', '', topic).strip()
        target_slot = get_next_schedule_slot()

        print("\n" + "#" * 80)
        log(f"PROCESSING TOPIC [{i+1}/{BATCH_COUNT}]: '{clean_topic}'", "[BATCH]")
        log(f"Assigned Slot: {target_slot.strftime('%b %d, %Y - %I:%M %p')}", "[CLOCK]")
        print("#" * 80)

        clean_name = f"auto_{int(time.time())}_{i+1}"

        # --- RENDER PHASE WITH SAFE COMPLETION CHECK & PAUSE ---
        MAX_RETRIES = 3
        res = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                log(f"Rendering Hindi topic (Attempt {attempt}/{MAX_RETRIES}): '{clean_topic}'...", "[RENDER]")
                res = process_full_production(clean_topic, base_filename=clean_name, language="hi")
            except Exception as render_err:
                log(f"Render error on attempt {attempt}: {render_err}", "[ERROR]")

            # Check if video is 100% complete and verified
            if res:
                v_path, v_title, v_desc, v_tags = res
                if verify_video_complete(v_path):
                    break
                else:
                    log(f"Video file abhi complete nahi hui ya disk par valid nahi hai: '{v_path}'", "[WARN]")
                    res = None

            if attempt < MAX_RETRIES:
                log("Video complete nahi hui! Engine thodi der ruk raha hai (waiting 30 seconds before retry)...", "[PAUSE]")
                for wait_s in range(30, 0, -5):
                    time.sleep(5)
            else:
                log(f"Topic '{clean_topic}' par 3 attempts ke baad bhi video ready nahi hui.", "[HALT]")

        # AGAR VIDEO COMPLETE NAHI HUI -> RUK JAO! (Queue aage nahi badhegi, topic safe rahega)
        if not res:
            log(f"Video complete na hone ki wajah se engine 60 seconds pause kar raha hai... Topic queue me RAHEGA.", "[PAUSE]")
            time.sleep(60)
            failed_count += 1
            continue

        # JAB VIDEO 100% COMPLETE HO JAYE -> TAB HI AAGE BADHO!
        v_path, v_title, v_desc, v_tags = res
        mark_topic_done(topic)
        log(f"Topic '{clean_topic}' video 100% complete ho chuka hai! Ab hi queue se done_topics.txt me move kiya.", "[QUEUE]")

        meta_pkg = {
            "video_path": v_path,
            "title": v_title,
            "description": v_desc,
            "tags": v_tags
        }

        # --- UPLOAD PHASE ---
        upload_success = False
        daily_limit_hit = False

        try:
            log("Uploading to YouTube Studio...", "[QUEUE]")
            schedule_video_on_youtube(meta_pkg, target_slot)
            upload_success = True
        except DailyUploadLimitReached as d_err:
            log("=================================================================", "[ALERT]")
            log("YOUTUBE DAILY UPLOAD LIMIT REACHED!", "[LIMIT]")
            log("YouTube channels par bina 1-time verification ke 24 ghante me 5-10 videos ki limit hoti hai.", "[INFO]")
            log("Rendered video save ho chuki hai pipeline_output folder me.", "[SAVED]")
            log("Script ab gracefully yahan pause ho rahi hai taaki Chrome hang na ho.", "[PAUSE]")
            log("24 ghante baad ya verification ke baad dubara run karein!", "[ACTION]")
            log("=================================================================", "[ALERT]")
            daily_limit_hit = True
            break
        except Exception as upload_err:
            log(f"Upload FAILED (video saved locally in pipeline_output): {upload_err}", "[WARN]")

        if upload_success:
            save_last_schedule_slot(target_slot)
            log(f"Topic '{clean_topic}' successfully scheduled on YouTube!", "[SUCCESS]")
            processed_count += 1
        else:
            log(f"Video saved in pipeline_output for topic: '{clean_topic}'", "[SAVED]")
            processed_count += 1

        chrome_session.close_all_extra_tabs(
            keep_url_keywords=("deepseek.com", "studio.youtube.com", "bing.com")
        )

        # Graceful cooling pause before starting next topic
        log("Video production finished successfully! Graceful cooling pause (10 seconds) before next topic...", "[COOLDOWN]")
        time.sleep(10)

    chrome_session.close_all_extra_tabs(
        keep_url_keywords=("deepseek.com", "studio.youtube.com", "bing.com")
    )

    if not daily_limit_hit:
        log(f"Batch complete! {processed_count} videos published, {failed_count} failed/skipped.", "[DONE]")


if __name__ == "__main__":
    main()
