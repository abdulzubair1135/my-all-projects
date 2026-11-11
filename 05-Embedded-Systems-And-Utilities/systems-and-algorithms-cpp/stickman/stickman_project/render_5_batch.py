"""
render_5_batch.py
-----------------
Batch renders 5 ultra-polished POV Doodle videos locally without YouTube uploading.
"""

import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import os
import json
import pov_doodle_pipeline

def main():
    with open("batch_5_scripts.json", "r", encoding="utf-8") as f:
        scripts = json.load(f)
        
    print(f"[*] Starting local render of {len(scripts)} polished POV Doodle shorts...", flush=True)
    results = []
    
    for i, script in enumerate(scripts):
        hook_clean = script['hook'].encode('ascii', errors='ignore').decode('ascii')
        print(f"\n=======================================================", flush=True)
        print(f"[*] RENDERING VIDEO {i+1}/{len(scripts)}: {hook_clean}", flush=True)
        print(f"=======================================================", flush=True)
        
        theme = script.get("theme", "shopping")
        out_path = pov_doodle_pipeline.process_pov_doodle_production(
            script_data=script,
            theme=theme
        )
        results.append(out_path)
        print(f"[OK] Video {i+1} completed: {out_path}", flush=True)
        
    print("\n" + "=" * 65, flush=True)
    print("[ALL DONE] ALL 5 VIDEOS RENDERED LOCALLY FOR REVIEW:", flush=True)
    for i, r in enumerate(results):
        print(f"Video {i+1}: {r}", flush=True)
    print("=" * 65, flush=True)

if __name__ == "__main__":
    main()
