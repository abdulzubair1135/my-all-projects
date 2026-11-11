import os
import sys
sys.path.insert(0, os.getcwd())
import shutil
import subprocess
from PIL import Image
from curiosity_engine import produce_curiosity_short

ARTIFACT_DIR = r"C:\Users\abdul\.gemini\antigravity\brain\a28b7e23-4a1d-490e-86cb-c5a75cf0dcb2"

def main():
    topic = "Can You Hear In Space?"
    base_name = "final_english_unique_scenes_space"
    
    print(f"\n=======================================================")
    print(f"[*] RENDERING SHORT WITH GUARANTEED DISTINCT SCENE IMAGES")
    print(f"[*] Topic: {topic}")
    print(f"=======================================================\n")
    
    out_path, title, desc, tags = produce_curiosity_short(
        topic=topic,
        base_filename=base_name,
        language="en",
        voice_override="en-US-GuyNeural"
    )
    
    print(f"\n[+] Render finished: {out_path}")
    
    # Extract 1 proof frame from each scene
    timestamps = ["00:00:02", "00:00:08", "00:00:14", "00:00:20"]
    crops = []
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
            # Crop diagram box to inspect difference
            im = Image.open(f_path)
            diag_crop = im.crop((64, 214, 656, 606))
            crop_path = os.path.join("scratch", f"diag_crop_sc_{idx}.png")
            diag_crop.save(crop_path)
            crops.append(crop_path)
            print(f"[+] Scene {idx} frame extracted & copied to: {art_path}")

    # Mark topic done in queue
    import auto_factory_batch
    auto_factory_batch.mark_topic_done(topic)
    print(f"[+] Topic '{topic}' permanently moved to done_topics.txt!")

    # Launch video
    subprocess.Popen(f'powershell -Command "Start-Process \'{out_path}\'"', shell=True)
    print(f"[+] Video launched on screen: {out_path}")

if __name__ == "__main__":
    main()
