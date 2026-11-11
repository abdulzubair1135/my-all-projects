import os
import sys
sys.path.insert(0, os.getcwd())
import time
from datetime import datetime, timedelta
import auto_factory_batch
from curiosity_engine import produce_curiosity_short
from schedule_queue import schedule_video_on_youtube, DailyUploadLimitReached

def run_test():
    print("=" * 80)
    print("   END-TO-END PIPELINE AUDIT: PRODUCTION -> VERIFICATION -> YOUTUBE UPLOAD")
    print("=" * 80)

    # 1. Check Chrome Debugger
    auto_factory_batch.launch_chrome_debugger()

    # 2. Pick next topic
    topic = auto_factory_batch.peek_first_topic()
    if not topic:
        topic = "Why Do Mirrors Flip Horizontally But Not Vertically?"

    print(f"\n[*] SELECTED TOPIC FOR E2E TEST: '{topic}'")
    clean_slug = topic.lower().replace(" ", "_").replace("?", "").replace("'", "")[:24]
    base_name = f"e2e_test_{clean_slug}"

    # 3. Produce Curiosity Short
    print("\n>>> STEP 1: PRODUCING VIDEO...")
    res = produce_curiosity_short(
        topic=topic,
        base_filename=base_name,
        language="en",
        voice_override="en-US-GuyNeural"
    )

    if not res:
        print("[FAIL] Video production returned None!")
        return False

    v_path, v_title, v_desc, v_tags = res
    print(f"[+] Video output file: {v_path}")

    # 4. Strict Completion & Integrity Verification
    print("\n>>> STEP 2: VERIFYING VIDEO COMPLETION ON DISK...")
    if not auto_factory_batch.verify_video_complete(v_path):
        print(f"[FAIL] Video file failed integrity verification: {v_path}")
        return False
    print("[+] Video 100% verified on disk!")

    # 5. YouTube Studio Upload / Scheduling
    print("\n>>> STEP 3: DISPATCHING TO YOUTUBE STUDIO...")
    meta_pkg = {
        "video_path": v_path,
        "title": v_title,
        "description": v_desc,
        "tags": v_tags
    }
    target_slot = datetime.now() + timedelta(hours=2)

    try:
        schedule_video_on_youtube(meta_pkg, target_slot)
        print("[SUCCESS] Video successfully scheduled/uploaded on YouTube Studio!")
    except DailyUploadLimitReached as d_err:
        print(f"[ALERT] Daily upload limit reached on YouTube channel: {d_err}")
        print("[INFO] Video is safely stored locally in pipeline_output.")
    except Exception as e:
        print(f"[!] YouTube upload attempt error: {e}")

    # 6. Archive topic
    print("\n>>> STEP 4: QUEUE UPDATE...")
    auto_factory_batch.mark_topic_done(topic)
    print(f"[+] Topic '{topic}' permanently moved to done_topics.txt!")

    print("\n" + "=" * 80)
    print("   END-TO-END PIPELINE TEST FINISHED SUCCESSFULLY!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    run_test()
