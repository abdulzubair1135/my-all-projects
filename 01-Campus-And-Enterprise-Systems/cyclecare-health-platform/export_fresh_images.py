import os
import sys
import win32com.client

sys.stdout.reconfigure(encoding='utf-8')

pptx_path = os.path.abspath("CycleCare_Project_Presentation.pptx")
out_dir = os.path.abspath("CycleCare_Slide_Images")
os.makedirs(out_dir, exist_ok=True)

powerpoint = win32com.client.Dispatch("PowerPoint.Application")
try:
    pres = powerpoint.Presentations.Open(pptx_path, WithWindow=False)
    for i in range(1, pres.Slides.Count + 1):
        slide_file = os.path.join(out_dir, f"slide_{i:02d}.png")
        pres.Slides(i).Export(slide_file, "PNG", 1920, 1080)
    print(f"Exported {pres.Slides.Count} slide images to {out_dir}")
    pres.Close()
finally:
    powerpoint.Quit()
