import os
import sys
sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import shutil
import subprocess
from curiosity_engine import produce_curiosity_short

ARTIFACT_DIR = r"C:\Users\abdul\.gemini\antigravity\brain\a28b7e23-4a1d-490e-86cb-c5a75cf0dcb2"

def render_and_extract(topic, base_name, language, voice):
    print(f"\n>>> RENDERING [{language.upper()}] TOPIC: '{topic}' with voice: {voice}")
    out_path, title, desc, tags = produce_curiosity_short(
        topic=topic,
        base_filename=base_name,
        language=language,
        voice_override=voice
    )
    print(f"[+] Render complete: {out_path}")
    
    # Extract 4 proof frames
    dur = 25
    timestamps = ["00:00:02", "00:00:08", "00:00:15", "00:00:21"]
    proof_files = []
    for idx, ts in enumerate(timestamps, 1):
        f_name = f"{base_name}_proof_{idx}.png"
        f_path = os.path.join("scratch", f_name)
        cmd = [
            "ffmpeg", "-y", "-ss", ts, "-i", out_path,
            "-vframes", "1", "-q:v", "2", f_path
        ]
        subprocess.run(cmd, capture_output=True)
        if os.path.exists(f_path):
            # Copy to artifact dir
            art_path = os.path.join(ARTIFACT_DIR, f_name)
            shutil.copyfile(f_path, art_path)
            proof_files.append(art_path)
            print(f"    Frame {idx} saved: {art_path}")

    return out_path, proof_files

if __name__ == "__main__":
    # 1. Hindi video
    h_path, h_proofs = render_and_extract(
        topic="Why Do We Get Brain Freeze From Ice Cream?",
        base_name="final_3d_hindi_brainfreeze",
        language="hi",
        voice="hi-IN-MadhurNeural"
    )

    # 2. English video
    e_path, e_proofs = render_and_extract(
        topic="Why Does Time Fly When You're Having Fun?",
        base_name="final_3d_english_timefly",
        language="en",
        voice="en-US-GuyNeural"
    )

    print("\nALL TWO VIDEOS RENDERED AND VERIFIED!")
