import os
import sys
sys.path.insert(0, os.getcwd())
import time
import shutil
import subprocess
from PIL import Image
import auto_factory_batch
from curiosity_engine import produce_curiosity_short

ARTIFACT_DIR = r"C:\Users\abdul\.gemini\antigravity\brain\a28b7e23-4a1d-490e-86cb-c5a75cf0dcb2"

def main():
    print("=" * 80)
    print("   AUTONOMOUS 3-VIDEO PRODUCTION BATCH (ENGLISH 3D NEOMORPHISM)")
    print("=" * 80)

    BATCH_COUNT = 3
    results = []

    for idx in range(1, BATCH_COUNT + 1):
        topic = auto_factory_batch.peek_first_topic()
        if not topic:
            auto_factory_batch.refill_viral_topics_if_needed()
            topic = auto_factory_batch.peek_first_topic()

        print(f"\n" + "#" * 75)
        print(f"[*] BATCH [{idx}/{BATCH_COUNT}]: Topic: '{topic}'")
        print("#" * 75)

        clean_slug = topic.lower().replace(" ", "_").replace("?", "").replace("'", "")[:24]
        base_name = f"batch_{idx}_{clean_slug}"

        out_path, title, desc, tags = produce_curiosity_short(
            topic=topic,
            base_filename=base_name,
            language="en",
            voice_override="en-US-GuyNeural"
        )

        print(f"[+] Video {idx} Render Complete: {out_path}")

        # Extract 4 proof frames
        timestamps = ["00:00:02", "00:00:08", "00:00:14", "00:00:20"]
        proof_paths = []
        for s_idx, ts in enumerate(timestamps, 1):
            f_name = f"{base_name}_proof_{s_idx}.png"
            f_path = os.path.join("scratch", f_name)
            cmd = [
                "ffmpeg", "-y", "-ss", ts, "-i", out_path,
                "-vframes", "1", "-q:v", "2", f_path
            ]
            subprocess.run(cmd, capture_output=True)
            if os.path.exists(f_path):
                art_path = os.path.join(ARTIFACT_DIR, f_name)
                shutil.copyfile(f_path, art_path)
                proof_paths.append(art_path)
                print(f"    - Frame {s_idx} saved: {art_path}")

        # Permanently move topic to done_topics.txt
        auto_factory_batch.mark_topic_done(topic)
        print(f"[+] Topic '{topic}' permanently moved to done_topics.txt!")

        results.append({
            "topic": topic,
            "path": out_path,
            "proofs": proof_paths
        })

    print("\n" + "=" * 80)
    print("   ALL 3 VIDEOS SUCCESSFULLY PRODUCED & ARCHIVED!")
    print("=" * 80)

    # Launch all 3 videos on screen
    for r in results:
        p = r["path"]
        print(f"[LAUNCH] Opening {p} on screen...")
        subprocess.Popen(f'powershell -Command "Start-Process \'{p}\'"', shell=True)
        time.sleep(1)

if __name__ == "__main__":
    main()
