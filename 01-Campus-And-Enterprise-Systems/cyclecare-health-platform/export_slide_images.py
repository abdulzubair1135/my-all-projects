import os
import sys
import win32com.client

sys.stdout.reconfigure(encoding='utf-8')

pptx_path = os.path.abspath("CycleCare_Project_Presentation.pptx")
out_dir = os.path.abspath("CycleCare_Slide_Images")
os.makedirs(out_dir, exist_ok=True)

powerpoint = win32com.client.Dispatch("PowerPoint.Application")
presentation = powerpoint.Presentations.Open(pptx_path, WithWindow=False)

# Export slides
for i in range(1, presentation.Slides.Count + 1):
    slide_file = os.path.join(out_dir, f"slide_{i:02d}.png")
    presentation.Slides(i).Export(slide_file, "PNG", 1920, 1080)

slide_count = presentation.Slides.Count
presentation.Close()
powerpoint.Quit()

print(f"Successfully exported {slide_count} slides to {out_dir}")
