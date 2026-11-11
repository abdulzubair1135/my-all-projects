import os
import sys
sys.path.insert(0, os.getcwd())
import shutil
import subprocess
from curiosity_engine import produce_curiosity_short
import auto_factory_batch

ARTIFACT_DIR = r"C:\Users\abdul\.gemini\antigravity\brain\a28b7e23-4a1d-490e-86cb-c5a75cf0dcb2"

def main():
    topic = "How Do Whales Sleep Without Drowning?"
    base_name = "bot_verified_whales_sleep"

    print("=" * 80)
    print(f"[*] 3-BOT REVIEWED EXPANDED SHORT PRODUCTION: '{topic}'")
    print("=" * 80)

    out_path, title, desc, tags = produce_curiosity_short(
        topic=topic,
        base_filename=base_name,
        language="en",
        voice_override="en-US-GuyNeural"
    )

    print(f"\n[+] Render Complete: {out_path}")

    # Extract 4 proof frames
    timestamps = ["00:00:03", "00:00:12", "00:00:23", "00:00:34"]
    for idx, ts in enumerate(timestamps, 1):
        f_name = f"{base_name}_proof_{idx}.png"
        f_path = os.path.join("scratch", f_name)
        cmd = [
            "ffmpeg", "-y", "-ss", ts, "-i", out_path,
            "-vframes", "1", "-q:v", "2", f_path
        ]
        subprocess.run(cmd, capture_output=True)
        if os.path.exists(f_path):
            art_path = os.path.join(ARTIFACT_DIR, f_name)
            shutil.copyfile(f_path, art_path)
            print(f"    - Frame {idx} saved: {art_path}")

    # Mark topic done
    auto_factory_batch.mark_topic_done(topic)
    print(f"[+] Topic '{topic}' permanently logged to done_topics.txt!")

    # Launch video
    subprocess.Popen(f'powershell -Command "Start-Process \'{out_path}\'"', shell=True)
    print(f"[+] Video launched on screen: {out_path}")

if __name__ == "__main__":
    main()
