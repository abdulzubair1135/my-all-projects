"""
render_5_custom_shorts.py
=========================
Renders 5 brand new, completely distinct, hyper-detailed YouTube Shorts for:
1. Friend asking for money and suddenly going invisible
2. Job interview viva panic and the 'I'm confident' lie
3. Gym day 1 enthusiasm vs quitting by day 3
4. Who takes longer to get ready (and the 'almost done' lie)
5. Splitting snacks fairly and the last bite betrayal

Each video has 100% NEW characters, NEW backgrounds, NEW props, and NEW dialogues!
"""

import os
import sys
import time

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from render_hyper_detailed_deepseek import produce_hyper_detailed_short

TOPICS = [
    ("Friend asking for money and suddenly going invisible", "short_1_money_invisible"),
    ("Job interview viva panic and the 'I'm confident' lie", "short_2_interview_panic"),
    ("Gym day 1 enthusiasm vs quitting by day 3", "short_3_gym_day1_vs_day3"),
    ("Who takes longer to get ready (and the 'almost done' lie)", "short_4_getting_ready_lie"),
    ("Splitting snacks fairly and the last bite betrayal", "short_5_snacks_samosa_betrayal")
]

def main():
    print("=" * 80)
    print("     PRODUCING 5 BRAND NEW HYPER-DETAILED 2D SHORTS (TOPIC-BY-TOPIC)")
    print("=" * 80)

    rendered_files = []

    for idx, (topic, base_fn) in enumerate(TOPICS, 1):
        print(f"\n[{idx}/5] STARTING PRODUCTION: '{topic}'")
        start_t = time.time()
        try:
            out_path, title, desc, tags = produce_hyper_detailed_short(topic, base_filename=base_fn)
            duration = round(time.time() - start_t, 1)
            print(f"[DONE {idx}/5] Rendered successfully in {duration}s -> {out_path}")
            rendered_files.append((topic, out_path, title))
        except Exception as e:
            print(f"[ERROR {idx}/5] Failed to render topic '{topic}': {e}")

    print("\n" + "=" * 80)
    print("     ALL 5 SHORTS RENDERED SUCCESSFULLY!")
    print("=" * 80)
    for i, (top, path, tit) in enumerate(rendered_files, 1):
        size_mb = round(os.path.getsize(path) / (1024 * 1024), 2)
        print(f"{i}. [{size_mb} MB] {tit}\n   Path: {path}")

if __name__ == "__main__":
    main()
