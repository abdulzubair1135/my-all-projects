import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
import os
import json
import asyncio
import threading
import re
import time
import urllib.request
import numpy as np
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from mutagen.mp3 import MP3
from moviepy.editor import (
    VideoClip, 
    AudioFileClip, 
    CompositeAudioClip, 
    concatenate_videoclips, 
    afx
)
import edge_tts
import chrome_session

OUTPUT_DIR = "pipeline_output"
TEMP_DIR = os.path.join(OUTPUT_DIR, "duo_temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# Boy & Girl Voice Configurations - Natural High-Pacing Edge-TTS
VOICES = {
    "boy": {
        "name": "hi-IN-MadhurNeural",
        "rate": "+35%",
        "pitch": "+0Hz",
        "display_name": "BOY",
        "color": (255, 215, 0),        # Golden Yellow
        "border_color": (255, 215, 0)
    },
    "girl": {
        "name": "hi-IN-SwaraNeural",
        "rate": "+35%",
        "pitch": "+0Hz",
        "display_name": "GIRL",
        "color": (255, 42, 133),       # Neon Pink
        "border_color": (255, 42, 133)
    }
}

def get_duo_script(topic):
    print(f"[*] Generating Boy & Girl Stickman Comedy Script for: '{topic}'...")
    page = chrome_session.get_or_open_page("chat.deepseek.com", "https://chat.deepseek.com", reuse=True)
    
    prompt = f"""You are a viral YouTube Shorts comedy scriptwriter specializing in funny, relatable conversational banter between a Boy and a Girl (Stickman cartoon characters).
Topic: '{topic}'

Write a hilarious, fast-paced 4 to 5 scene dialogue banter between Boy and Girl.
The humor must be sharp, funny, highly relatable (college, relationship, shopping, food, late replies, money).
Characters:
- Boy ('boy'): Witty, slightly sarcastic, relatable guy.
- Girl ('girl'): Smart, dramatic, savage comeback girl.

Format your reply strictly as a single JSON object with this exact structure:
{{
  "title": "Viral Clicky Hindi Title with 1 emoji #shorts #viral",
  "description": "Short funny description with tags #comedy #relatable #animation #stickman #shorts",
  "tags": ["shorts", "comedy", "funny", "relatable", "stickman", "animation"],
  "scenes": [
    {{
      "scene": 1,
      "speaker": "boy",
      "spoken_hindi": "शुद्ध हिंदी देवनागरी में जो आवाज़ बोलेगी (Natural, punchy spoken Hindi)",
      "dialogue": "Exact same dialogue in clean Hinglish for on-screen subtitles",
      "visual_prompt": "boy stickman asking question curiously while girl stickman looks annoyed",
      "is_punchline": false
    }},
    {{
      "scene": 2,
      "speaker": "girl",
      "spoken_hindi": "शुद्ध हिंदी में लड़की का जवाब",
      "dialogue": "Exact dialogue in Hinglish",
      "visual_prompt": "girl stickman with cute ponytail giving sassy comeback, boy stickman shocked",
      "is_punchline": false
    }}
  ]
}}
Strictly return valid JSON only, without any markdown formatting or commentary."""

    textarea = page.wait_for_selector("textarea, div[contenteditable='true']", timeout=15000)
    textarea.click()
    textarea.fill(prompt)
    textarea.press("Enter")
    print("[*] Prompt sent to DeepSeek. Waiting for script completion...")

    time.sleep(5)
    last_len = 0
    stable_count = 0
    for _ in range(70):
        time.sleep(1.5)
        stop_btn = page.query_selector('div[aria-label="Stop"], button:has-text("Stop")')
        elements = page.query_selector_all(".ds-markdown, .markdown")
        cur_text = elements[-1].inner_text() if elements else ""
        
        if not stop_btn:
            if len(cur_text) == last_len and len(cur_text) > 100:
                stable_count += 1
                if stable_count >= 2:
                    break
            else:
                stable_count = 0
        last_len = len(cur_text)

    elements = page.query_selector_all(".ds-markdown, .markdown")
    if not elements:
        raise RuntimeError("No response elements found in DeepSeek")

    raw_text = elements[-1].inner_text()
    cleaned = re.sub(r'```json\s*', '', raw_text)
    cleaned = re.sub(r'```\s*$', '', cleaned).strip()

    match = re.search(r'\{.*\}', cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)

    try:
        script_data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("[!] JSON decode failed, raw text snippet:", raw_text[:300])
        raise e

    print(f"[OK] Script successfully generated: '{script_data.get('title')}' ({len(script_data.get('scenes', []))} scenes)")
    return script_data

def synthesize_voice(text, speaker, output_path):
    spk_key = speaker.lower() if speaker.lower() in VOICES else "boy"
    cfg = VOICES[spk_key]
    
    clean_text = re.sub(r'[\*\_#\"\'\(\)]', '', text).strip()
    
    result_holder = [[]]
    loop = asyncio.new_event_loop()
    
    def run_coro():
        asyncio.set_event_loop(loop)
        async def main():
            communicate = edge_tts.Communicate(
                clean_text, 
                cfg["name"], 
                rate=cfg["rate"], 
                pitch=cfg["pitch"]
            )
            words = []
            with open(output_path, "wb") as f:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        words.append({
                            "word": chunk["text"],
                            "start": chunk["offset"] / 10000000.0,
                            "end": (chunk["offset"] + chunk["duration"]) / 10000000.0
                        })
            result_holder[0] = words
        loop.run_until_complete(main())
        loop.close()

    t = threading.Thread(target=run_coro)
    t.start()
    t.join(timeout=30)

    audio_info = MP3(output_path)
    return audio_info.info.length, result_holder[0]

def generate_bw_image(visual_prompt, output_path, scene_id):
    print(f"[*] Generating B&W Minimal Stickman Scene {scene_id} via Bing Cloud AI...")
    
    clean_prompt = visual_prompt.replace('"', '').replace("'", '').strip()
    full_prompt = (
        f"minimalist black and white comic art, plain white background, two funny stickman characters: "
        f"a boy stickman on the left and a girl stickman with simple cute ponytail on the right, "
        f"{clean_prompt}, simple clean black ink line art, comic strip doodle style, minimalist stick figures, "
        f"very minimal subtle color accent only, no realistic human faces, pure stick figures, high resolution"
    )

    page = chrome_session.get_or_open_page("bing.com/images/create", "https://www.bing.com/images/create", reuse=True)
    old_url = page.url

    textarea = page.wait_for_selector("textarea[name='gmc__textarea'], textarea[placeholder*='Describe']", timeout=8000)
    textarea.click()
    textarea.press("Control+A")
    textarea.press("Backspace")
    textarea.type(full_prompt, delay=5)
    time.sleep(0.5)

    gen_btn = page.wait_for_selector("button:has-text('Generate'), button.gmbtn__btn", timeout=5000)
    gen_btn.click()
    print(f"[*] Scene {scene_id}: Prompt submitted, waiting for creation URL...")

    for _ in range(30):
        time.sleep(1)
        if page.url != old_url and ("/1-" in page.url or "FORM=GENCRE" in page.url):
            break

    for _ in range(40):
        time.sleep(1.5)
        img_src = page.evaluate("""() => {
            let display = document.querySelector('img.aigc-display__img');
            if (display && display.src && display.naturalWidth > 150) return display.src;
            let thumb = document.querySelector('img.aigc-batch__thumb');
            if (thumb && thumb.src && thumb.naturalWidth > 100) return thumb.src;
            let any_oig = Array.from(document.querySelectorAll('img')).find(i => 
                i.src && i.src.includes('th.bing.com') && i.src.includes('OIG') && i.naturalWidth > 150
            );
            return any_oig ? any_oig.src : null;
        }""")
        if img_src:
            clean_url = img_src.split("?")[0] + "?pid=ImgGn"
            req = urllib.request.Request(clean_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                with open(output_path, "wb") as f:
                    f.write(resp.read())
            print(f"-> B&W Stickman Scene {scene_id} ready: {output_path}")
            return output_path

    raise TimeoutError(f"Bing failed to render scene {scene_id} within timeout.")

def render_duo_frame(t, duration, raw_img, words_data, full_text, speaker="boy", is_punchline=False):
    canvas_w, canvas_h = 720, 1280
    spk_key = speaker.lower() if speaker.lower() in VOICES else "boy"
    cfg = VOICES[spk_key]

    # Clean off-white background
    bg = Image.new("RGB", (canvas_w, canvas_h), (252, 252, 252))

    # 1. Ken Burns Subtle Zoom
    zoom = 1.0 + 0.05 * (t / duration)
    
    # 2. Punchline camera shake on last scene
    shake_x, shake_y = 0, 0
    if is_punchline and (t > max(0.5, duration - 1.2)):
        decay = max(0.0, 1.0 - (t - (duration - 1.2)) / 1.2)
        shake_mag = int(14 * decay)
        if shake_mag > 0:
            frame_seed = int(t * 24)
            rng = np.random.RandomState(frame_seed)
            shake_x = rng.randint(-shake_mag, shake_mag + 1)
            shake_y = rng.randint(-shake_mag, shake_mag + 1)

    # 3. Center Illustration
    base_w = 660
    fg_w = int(base_w * zoom)
    scale = fg_w / raw_img.width
    fg_h = int(raw_img.height * scale)
    zoomed_img = raw_img.resize((fg_w, fg_h), Image.Resampling.LANCZOS)

    # Crop to stay centered
    crop_x = (fg_w - base_w) // 2
    cropped = zoomed_img.crop((crop_x, 0, crop_x + base_w, fg_h))

    img_x = (canvas_w - base_w) // 2 + shake_x
    img_y = 120 + shake_y
    bg.paste(cropped, (img_x, img_y))

    draw = ImageDraw.Draw(bg)

    # Clean minimalist card border around illustration
    draw.rounded_rectangle(
        [img_x - 4, img_y - 4, img_x + base_w + 4, img_y + fg_h + 4],
        radius=16,
        outline=(220, 222, 228),
        width=2
    )

    # 4. Fonts
    try:
        font_badge = ImageFont.truetype("arialbd.ttf", 26)
        font_sub = ImageFont.truetype("arialbd.ttf", 36)
    except:
        font_badge = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # 5. Speaker Badge Pill
    badge_label = f"●  {cfg['display_name']}  ●"
    badge_w = 220
    badge_h = 44
    badge_x = (canvas_w - badge_w) // 2 + shake_x
    badge_y = img_y + fg_h + 30

    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_w, badge_y + badge_h],
        radius=22,
        fill=(22, 22, 28),
        outline=cfg["border_color"],
        width=2
    )
    draw.text((canvas_w // 2 + shake_x, badge_y + badge_h // 2), badge_label, fill=cfg["color"], font=font_badge, anchor="mm")

    # 6. Word-wrapped Subtitles
    words = full_text.split()
    lines = []
    cur_line = []
    for w in words:
        test_line = cur_line + [w]
        w_px = sum(draw.textbbox((0, 0), x, font=font_sub)[2] for x in test_line) + (len(test_line) - 1) * 12
        if w_px > 600 and cur_line:
            lines.append(cur_line)
            cur_line = [w]
        else:
            cur_line.append(w)
    if cur_line:
        lines.append(cur_line)

    # Karaoke Word Tracking
    active_idx = -1
    if words_data:
        for i, w_obj in enumerate(words_data):
            if w_obj["start"] <= t <= w_obj["end"]:
                active_idx = i
                break
            elif t > w_obj["end"]:
                active_idx = i
    else:
        prog = min(max(t / duration, 0.0), 1.0)
        active_idx = int(prog * len(words))

    line_height = 54
    total_text_h = len(lines) * line_height
    sub_y1 = badge_y + badge_h + 25
    sub_y2 = sub_y1 + total_text_h + 40

    # Subtitle Card Box
    draw.rounded_rectangle(
        [36 + shake_x, sub_y1, 684 + shake_x, sub_y2],
        radius=22,
        fill=(18, 18, 22),
        outline=cfg["border_color"],
        width=2
    )

    t_y = sub_y1 + 22
    w_counter = 0
    space_w = draw.textbbox((0, 0), " ", font=font_sub)[2]

    for line in lines:
        line_w = sum(draw.textbbox((0, 0), word, font=font_sub)[2] for word in line) + space_w * (len(line) - 1)
        cur_x = (canvas_w - line_w) // 2 + shake_x

        for word in line:
            w_bbox = draw.textbbox((0, 0), word, font=font_sub)
            word_w = w_bbox[2] - w_bbox[0]

            if w_counter == active_idx:
                color = cfg["color"]           # Speaker Highlight Color
            elif w_counter < active_idx:
                color = (255, 255, 255)         # Crisp White
            else:
                color = (130, 130, 138)         # Muted Light Gray

            draw.text((cur_x + 2, t_y + 2), word, font=font_sub, fill=(0, 0, 0))
            draw.text((cur_x, t_y), word, font=font_sub, fill=color)

            cur_x += word_w + space_w
            w_counter += 1

        t_y += line_height

    return np.array(bg)

def process_duo_production(topic=None, script_data=None, base_filename=None):
    if script_data is None:
        script_data = get_duo_script(topic)
    
    title = script_data.get("title", "Stickman Comedy")
    description = script_data.get("description", "")
    tags = script_data.get("tags", [])
    scenes = script_data.get("scenes", [])

    now_str = datetime.now().strftime("%Y-%m-%d_%I-%M-%p")
    safe_topic = re.sub(r'[^a-zA-Z0-9_]', '_', title)[:25]
    session_dir = os.path.join(OUTPUT_DIR, f"Duo_{now_str}_{safe_topic}")
    os.makedirs(session_dir, exist_ok=True)

    clips = []
    print("\n" + "=" * 65)
    print(f"[*] PRODUCING B&W BOY & GIRL STICKMAN EPISODE ({len(scenes)} SCENES)")
    print(f"[*] Title: '{title}'")
    print("=" * 65)

    for sc in scenes:
        s_num = sc["scene"]
        speaker = sc.get("speaker", "boy")
        spoken_hindi = sc.get("spoken_hindi", "")
        dialogue = sc.get("dialogue", spoken_hindi)
        v_prompt = sc.get("visual_prompt", "")
        is_last = (s_num == len(scenes)) or sc.get("is_punchline", False)

        print(f"\n--- Scene {s_num}/{len(scenes)}: [{speaker.upper()}] ---")
        print(f"Dialogue: '{dialogue}'")

        # 1. Synthesize Voice
        audio_path = os.path.join(TEMP_DIR, f"scene_{s_num}_audio.mp3")
        duration, words_data = synthesize_voice(spoken_hindi, speaker, audio_path)
        print(f"Audio ready: {duration:.2f}s, words: {len(words_data)}")

        # 2. Generate B&W Minimal Image
        img_path = os.path.join(TEMP_DIR, f"scene_{s_num}_img.png")
        generate_bw_image(v_prompt, img_path, s_num)
        raw_img = Image.open(img_path).convert("RGB")

        # 3. Create VideoClip
        def make_frame_func(r_img, w_data, txt, spk, punch):
            return lambda t: render_duo_frame(t, duration, r_img, w_data, txt, speaker=spk, is_punchline=punch)

        frame_gen = make_frame_func(raw_img, words_data, dialogue, speaker, is_last)
        clip = VideoClip(frame_gen, duration=duration)
        clip = clip.set_audio(AudioFileClip(audio_path))
        clips.append(clip)

    print("\n[*] Concatenating scenes into complete Short...")
    final_video = concatenate_videoclips(clips, method="compose")

    video_path = os.path.join(session_dir, "final_duo_short.mp4")
    print(f"\n[*] Exporting B&W Stickman Short MP4: {video_path}")
    final_video.write_videofile(
        video_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        logger="bar"
    )

    thumb_path = os.path.join(session_dir, "cover_thumbnail.png")
    best_image = os.path.join(TEMP_DIR, "scene_1_img.png")
    if os.path.exists(best_image):
        import shutil
        shutil.copy(best_image, thumb_path)

    meta_path = os.path.join(session_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "title": title,
            "description": description,
            "tags": tags,
            "topic": topic or title,
            "created_at": now_str,
            "video_path": os.path.abspath(video_path),
            "thumbnail_path": os.path.abspath(thumb_path)
        }, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 65)
    print(f"[SUCCESS] B&W BOY & GIRL STICKMAN SHORT READY: {video_path}")
    print("=" * 65)
    return video_path, title, description, tags

if __name__ == "__main__":
    test_topic = "Ladkiyon ki shopping vs Ladko ki shopping"
    process_duo_production(topic=test_topic)
