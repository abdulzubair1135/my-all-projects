import os
import sys
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')
asset_dir = "CycleCare_Presentation_Assets"

for f in sorted(os.listdir(asset_dir)):
    p = os.path.join(asset_dir, f)
    if os.path.isfile(p):
        im = Image.open(p)
        print(f"{f}: {im.size} (aspect ratio {im.size[0]/im.size[1]:.2f})")
