import os
import json
import asyncio
import re
import time
import torch
from mutagen.mp3 import MP3
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
import edge_tts
from playwright.sync_api import sync_playwright

OUTPUT_DIR = "pipeline_output"
TEMP_DIR = os.path.join(OUTPUT_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# ---------------------------------------------------------
# 1. BRAIN: CHROME BROWSER AUTOMATION (DEEPSEEK WEB)
# ---------------------------------------------------------
def get_storyboard_from_deepseek_web(topic):
    print("\n[*] Connecting to running Chrome session on port 9222...")
    prompt_text = (
        f"You are a short stickman video creator. Create a funny 3-scene story about: '{topic}'. "
        "Return ONLY a raw valid JSON array like this format, no markdown formatting, no other text:\n"
        "[\n"
        '  {"scene": 1, "visual_prompt": "stickman shocked looking at computer screen", "dialogue": "Arre bhai yeh kya ho gaya!"},\n'
        '  {"scene": 2, "visual_prompt": "stickman thinking deeply scratching head", "dialogue": "Poora din nikal gaya par logic samajh nahi aaya."},\n'
        '  {"scene": 3, "visual_prompt": "stickman jumping with joy celebration", "dialogue": "Lekin aakhir me code chal hi gaya!"}\n'
        "]"
    )

    with sync_playwright() as p:
        try:
            # Connect to existing open Chrome
            browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            default_context = browser.contexts[0]
            
            # Find or open DeepSeek tab
            page = None
            for p_tab in default_context.pages:
                if "deepseek.com" in p_tab.url:
                    page = p_tab
                    break
            if not page:
                page = default_context.new_page()
                page.goto("https://chat.deepseek.com")
                page.wait_for_load_state("networkidle")

            print("[*] Typing prompt into DeepSeek chat input...")
            # Target textarea
            textarea = page.wait_for_selector("textarea", timeout=15000)
            textarea.fill(prompt_text)
            textarea.press("Enter")

            print("[*] Waiting for DeepSeek response and live generation...")
            # Wait for response generation to complete
            time.sleep(5)
            
            # Polling until send button becomes active again (generation stops)
            while True:
                # Check if stop button exists
                stop_btn = page.query_selector('div[aria-label="Stop"], button:has-text("Stop")')
                if not stop_btn:
                    break
                time.sleep(2)

            print("[*] Reading generated text from browser...")
            messages = page.query_selector_all(".ds-markdown, .markdown, .chat-message")
            if messages:
                raw_text = messages[-1].inner_text()
            else:
                raw_text = page.locator("body").inner_text()

            # Clean JSON extraction
            json_match = re.search(r'\[\s*\{.*\}\s*\]', raw_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                start = raw_text.find('[')
                end = raw_text.rfind(']') + 1
                if start != -1 and end != 0:
                    return json.loads(raw_text[start:end])
                raise ValueError("JSON parse nahi ho paya. Dobara try karein.")

        except Exception as e:
            print(f"[!] Browser automation error: {e}")
            print("[!] Make sure start_deepseek_chrome.bat chalu hai aur Chrome खुला हुआ hai.")
            raise e

# ---------------------------------------------------------
# 2. AUDIO: EDGE-TTS
# ---------------------------------------------------------
async def make_audio(text, output_path):
    communicate = edge_tts.Communicate(text, "hi-IN-MadhurNeural")
    await communicate.save(output_path)

def generate_voice(text, output_path):
    asyncio.run(make_audio(text, output_path))
    audio_info = MP3(output_path)
    return audio_info.info.length

# ---------------------------------------------------------
# 3. ARTIST: LOCAL AI DIFFUSERS (GPU 4GB Optimized)
# ---------------------------------------------------------
pipe = None
def load_image_model():
    global pipe
    if pipe is None:
        print("[*] Loading AI Image Model on GPU (RTX 2050)...")
        from diffusers import AutoPipelineForText2Image
        pipe = AutoPipelineForText2Image.from_pretrained(
            "runwayml/stable-diffusion-v1-5", 
            torch_dtype=torch.float16,
            safety_checker=None
        )
        pipe.enable_attention_slicing()
        pipe.to("cuda")

def generate_ai_stickman(visual_prompt, output_path, scene_id):
    load_image_model()
    print(f"[*] AI drawing frame for Scene {scene_id} on GPU...")
    
    prompt = (
        f"{visual_prompt}, stick figure, minimalist 2d black ink line art, "
        "pure solid white background, high contrast, clean vector outline, simple doodle"
    )
    neg_prompt = (
        "colors, 3d, realistic, photographic, gradients, shading, shadows, "
        "complex background, dirty lines, blur, watermark, text"
    )

    image = pipe(
        prompt=prompt,
        negative_prompt=neg_prompt,
        num_inference_steps=20,
        height=512,
        width=512,
        guidance_scale=7.5
    ).images[0]

    image.save(output_path)

# ---------------------------------------------------------
# 4. DIRECTOR: ASSEMBLE VIDEO (FCFS)
# ---------------------------------------------------------
def assemble_video(scenes):
    clips = []
    print("\n--- Starting Rendering Queue ---")

    for idx, sc in enumerate(scenes):
        scene_id = idx + 1
        print(f"\n[Processing Scene {scene_id}/{len(scenes)}]")

        audio_file = os.path.join(TEMP_DIR, f"audio_{scene_id}.mp3")
        image_file = os.path.join(TEMP_DIR, f"image_{scene_id}.png")

        # 1. Voice
        duration = generate_voice(sc["dialogue"], audio_file)
        print(f"-> Voice rendered: {duration:.2f}s")

        # 2. AI Drawing
        generate_ai_stickman(sc["visual_prompt"], image_file, scene_id)

        # 3. Match frame with audio length
        audio_clip = AudioFileClip(audio_file)
        img_clip = ImageClip(image_file).set_duration(audio_clip.duration).set_audio(audio_clip)
        clips.append(img_clip)

    print("\n[*] Assembling and rendering final MP4...")
    final_video = concatenate_videoclips(clips, method="compose")
    final_path = os.path.join(OUTPUT_DIR, "final_ai_stickman_video.mp4")
    
    final_video.write_videofile(
        final_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        logger="bar"
    )
    return final_path

# ---------------------------------------------------------
# 5. CONTROLLER & APPROVAL GATE
# ---------------------------------------------------------
def main():
    print("=" * 60)
    print("   DEEPSEEK CHROME WEB + LOCAL AI VIDEO PIPELINE   ")
    print("=" * 60)

    topic = input("\n[?] Video topic daliye (e.g., dream vs reality): ").strip()
    if not topic:
        topic = "Sapne aur reality ka fasla"

    try:
        scenes = get_storyboard_from_deepseek_web(topic)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        return

    print("\n" + "=" * 50)
    print("   DEEPSEEK GENERATED STORYBOARD (REVIEW & APPROVE)")
    print("=" * 50)
    for sc in scenes:
        print(f"[Scene {sc['scene']}]")
        print(f"  Visual   : {sc['visual_prompt']}")
        print(f"  Dialogue : {sc['dialogue']}")
    print("-" * 50)

    choice = input("\n[?] Kya aapko script pasand aayi? Video render karein? (y/n): ").strip().lower()

    if choice == 'y':
        output_file = assemble_video(scenes)
        print("\n" + "=" * 60)
        print(f"[SUCCESS] AI Video completely ready!")
        print(f"Location: {os.path.abspath(output_file)}")
        print("=" * 60)
    else:
        print("[!] Script reject kar di gayi.")

if __name__ == "__main__":
    main()