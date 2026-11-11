from PIL import Image
import os

def remove_white_bg(src_path, dst_path, tolerance=25):
    img = Image.open(src_path).convert("RGBA")
    datas = img.getdata()
    
    new_data = []
    for item in datas:
        r, g, b, a = item
        if r >= (255 - tolerance) and g >= (255 - tolerance) and b >= (255 - tolerance):
            new_data.append((255, 255, 255, 0))
        elif r >= 240 and g >= 240 and b >= 240:
            diff = min(r, g, b) - 240
            alpha = int(255 * (1.0 - (diff / 15.0)))
            new_data.append((r, g, b, max(0, min(255, alpha))))
        else:
            new_data.append(item)
            
    img.putdata(new_data)
    img.save(dst_path, "PNG")

target_dir = r"c:\Users\abdul\OneDrive\ドキュメント\arti astha\android\app\src\main\res\drawable"

assets = [
    (r"c:\Users\abdul\OneDrive\ドキュメント\arti astha\android\app\src\main\res\drawable\panda_idle.jpg", os.path.join(target_dir, "panda_idle.png")),
    (r"c:\Users\abdul\OneDrive\ドキュメント\arti astha\android\app\src\main\res\drawable\panda_blink.jpg", os.path.join(target_dir, "panda_blink.png")),
    (r"c:\Users\abdul\OneDrive\ドキュメント\arti astha\android\app\src\main\res\drawable\panda_shy.jpg", os.path.join(target_dir, "panda_shy.png")),
    (r"C:\Users\abdul\.gemini\antigravity\brain\b62ec233-9f93-4cef-a07e-c49ef9fb6ac5\panda_wave_hello_1791231623729.jpg", os.path.join(target_dir, "panda_wave.png"))
]

for src, dst in assets:
    if os.path.exists(src):
        remove_white_bg(src, dst)

