import os
import shutil
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

src_dir = os.path.join(os.getcwd(), "CYCLECARE_COMPLETE_DOCUMENTATION", "assets")
dst_dir = os.path.join(os.getcwd(), "CycleCare_Presentation_Assets")

os.makedirs(dst_dir, exist_ok=True)

files = os.listdir(src_dir)
copied = []
for f in files:
    src_file = os.path.join(src_dir, f)
    if os.path.isfile(src_file):
        dst_file = os.path.join(dst_dir, f)
        shutil.copy2(src_file, dst_file)
        copied.append(f)

print(f"Copied {len(copied)} files successfully:")
for c in sorted(copied):
    print(f" - {c}")
