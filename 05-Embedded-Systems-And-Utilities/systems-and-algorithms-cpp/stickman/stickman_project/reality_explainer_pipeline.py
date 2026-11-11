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
    afx,
    ImageClip
)
import edge_tts
import chrome_session

OUTPUT_DIR = "pipeline_output"
TEMP_DIR = os.path.join(OUTPUT_DIR, "reality_temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# Single Premium Storyteller Voice Configuration - Snappy 1.45x YouTube Shorts Pacing
NARRATOR_VOICE = {
    "voice": "hi-IN-MadhurNeural",
    "rate": "+38%",
    "pitch": "+0Hz"
}

def get_reality_script(topic):
    print(f"[*] Generating Reality Infinite Storytelling Script for: '{topic}'...")
    page = chrome_session.get_or_open_page("chat.deepseek.com", "https://chat.deepseek.com", reuse=True)
    
    prompt = f"""You are a viral YouTube Shorts scriptwriter in the style of 'Reality Infinite' and 'Why We Do It' (2D stickman cartoon animation explainer).
Topic: '{topic}'

Write a captivating 4-scene video script with ONE narrator.
The tone must be curious, witty, educational, and funny.
The main character in every visual prompt must be a STICKMAN (round white head, minimalist stick figure body).

Format your reply strictly as a single JSON object with this exact structure:
{{
  "title": "Viral Clicky Hindi Title with 1 emoji #shorts #viral",
  "description": "Engaging description with #tags",
  "tags": ["tag1", "tag2", "tag3"],
  "scenes": [
    {{
      "scene": 1,
      "spoken_hindi": "शुद्ध हिंदी देवनागरी में जो आवाज़ बोलेगी (Fast, snappy storytelling narration)",
      "dialogue": "Exact same narration in stylized Hinglish for screen subtitles",
      "visual_prompt": "funny expressive stickman cartoon character with round white head and simple stick figure body doing something funny in a colorful environment",
      "sfx": "whoosh"
    }}
  ]
}}
Strictly return valid JSON only, without any markdown formatting or introductory text."""

    textarea = page.wait_for_selector("textarea, div[contenteditable='true']", timeout=15000)
    textarea.click()
    textarea.fill(prompt)
    textarea.press("Enter")

    time.sleep(4)
    last_len = 0
    for _ in range(50):
        stop_btn = page.query_selector('div[aria-label="Stop"], button:has-text("Stop")')
        elements = page.query_selector_all(".ds-markdown, .markdown")
        cur_text = elements[-1].inner_text() if elements else ""
        if not stop_btn and len(cur_text) > 200 and len(cur_text) == last_len:
            break
        last_len = len(cur_text)
        time.sleep(1)

    time.sleep(2)
    elements = page.query_selector_all(".ds-markdown, .markdown")
    raw_text = elements[-1].inner_text() if elements else page.locator("body").inner_text()
    
    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    start = raw_text.find('{')
    end = raw_text.rfind('}') + 1
    if start != -1 and end > start:
        return json.loads(raw_text[start:end])
    raise ValueError("DeepSeek JSON output parse nahi ho saka.")

async def _make_tts_audio(text, output_path):
    communicate = edge_tts.Communicate(
        text, 
        NARRATOR_VOICE["voice"], 
        rate=NARRATOR_VOICE["rate"], 
        pitch=NARRATOR_VOICE["pitch"]
    )
    words_data = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            with open(output_path, "ab") as f:
                f.write(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            start_sec = chunk["offset"] / 10_000_000
            dur_sec = chunk["duration"] / 10_000_000
            words_data.append({
                "word": chunk["text"],
                "start": start_sec,
                "end": start_sec + dur_sec
            })
    return words_data

def generate_reality_voice(spoken_text, output_path):
    if os.path.exists(output_path):
        os.remove(output_path)

    result_holder = []
    error_holder = []

    def _worker():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            words = loop.run_until_complete(_make_tts_audio(spoken_text, output_path))
            result_holder.append(words)
        except Exception as e:
            error_holder.append(e)
        finally:
            loop.close()

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    t.join(timeout=60)

    if error_holder:
        raise RuntimeError(f"TTS Error: {error_holder[0]}")
    if not result_holder:
        raise RuntimeError("TTS Timeout (60s exceeded)")

    audio_info = MP3(output_path)
    return audio_info.info.length, result_holder[0]

def generate_reality_image(visual_prompt, output_path, scene_id):
    print(f"[*] Generating Reality Infinite STICKMAN Scene {scene_id} via Bing Cloud AI...")
    
    clean_prompt = visual_prompt.replace('"', '').replace("'", '').strip()
    full_prompt = (
        f"2D colorful digital illustration, funny expressive stickman cartoon character with round white head and simple black ink stick figure body, "
        f"{clean_prompt}, storybook art style, clean bold outlines, vibrant colors, rich cinematic lighting, "
        "detailed colorful background, minimalist stick figure hero in a detailed world, no realistic human faces, pure stickman, no text, no watermark, masterpiece"
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
    print(f"[*] Scene {scene_id}: Submitted prompt to Bing, waiting for creation URL...")

    for _ in range(30):
        time.sleep(1)
        if page.url != old_url and ("/1-" in page.url or "FORM=GENCRE" in page.url):
            break

    for _ in range(35):
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
            print(f"-> Reality Stickman Scene {scene_id} ready: {output_path}")
            return output_path

    raise TimeoutError(f"Bing failed to render scene {scene_id} within timeout.")

def render_reality_frame(t, duration, raw_img, words_data, full_text, is_punchline=False):
    canvas_w, canvas_h = 720, 1280
    
    # 1. Ken Burns Slow Cinematic Zoom
    zoom = 1.0 + 0.08 * (t / duration)
    
    # 2. Punchline camera shake
    shake_x, shake_y = 0, 0
    if is_punchline and (t > max(0.5, duration - 1.5)):
        decay = max(0.0, 1.0 - (t - (duration - 1.5)) / 1.5)
        shake_mag = int(12 * decay)
        if shake_mag > 0:
            frame_seed = int(t * 24)
            rng = np.random.RandomState(frame_seed)
            shake_x = rng.randint(-shake_mag, shake_mag + 1)
            shake_y = rng.randint(-shake_mag, shake_mag + 1)

    # 3. Background: Blurred ambient fill
    bg = raw_img.resize((canvas_w, canvas_h)).filter(ImageFilter.GaussianBlur(radius=28))
    dark = Image.new("RGB", (canvas_w, canvas_h), (0, 0, 0))
    bg = Image.blend(bg, dark, 0.45)

    # 4. Foreground: Zoomed & sharp center
    fg_w = int(canvas_w * zoom)
    scale = fg_w / raw_img.width
    fg_h = int(raw_img.height * scale)
    zoomed_fg = raw_img.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
    
    crop_left = (fg_w - canvas_w) // 2
    crop_fg = zoomed_fg.crop((crop_left, 0, crop_left + canvas_w, fg_h))
    
    fg_y = (canvas_h - fg_h) // 2 - 80 + shake_y
    fg_x = shake_x
    bg.paste(crop_fg, (fg_x, fg_y))

    draw = ImageDraw.Draw(bg)
    draw.line([(0, fg_y), (canvas_w, fg_y)], fill=(40, 40, 45), width=2)
    draw.line([(0, fg_y + fg_h), (canvas_w, fg_y + fg_h)], fill=(40, 40, 45), width=2)

    # 5. Documentary Subtitles
    try:
        font = ImageFont.truetype("arialbd.ttf", 38)
    except:
        font = ImageFont.load_default()

    words = full_text.split()
    lines = []
    curr = []
    for w in words:
        curr.append(w)
        test_str = " ".join(curr)
        bbox = draw.textbbox((0, 0), test_str, font=font)
        if (bbox[2] - bbox[0]) > 600:
            curr.pop()
            lines.append(curr)
            curr = [w]
    if curr:
        lines.append(curr)

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

    total_text_h = len(lines) * 55
    sub_y1 = fg_y + fg_h + 35
    sub_y2 = sub_y1 + total_text_h + 40
    
    draw.rounded_rectangle(
        [30 + shake_x, sub_y1, 690 + shake_x, sub_y2], 
        radius=20, 
        fill=(14, 14, 18), 
        outline=(255, 215, 0), 
        width=2
    )

    t_y = sub_y1 + 20
    w_counter = 0
    space_w = draw.textbbox((0, 0), " ", font=font)[2]

    for line in lines:
        line_w = sum(draw.textbbox((0, 0), word, font=font)[2] for word in line) + space_w * (len(line) - 1)
        cur_x = (720 - line_w) // 2 + shake_x

        for word in line:
            w_bbox = draw.textbbox((0, 0), word, font=font)
            word_w = w_bbox[2] - w_bbox[0]

            if w_counter == active_idx:
                color = (255, 215, 0)      # Glowing Gold
            elif w_counter < active_idx:
                color = (255, 255, 255)      # Crisp White
            else:
                color = (135, 135, 140)      # Muted Gray

            draw.text((cur_x + 2, t_y + 2), word, font=font, fill=(0, 0, 0))
            draw.text((cur_x, t_y), word, font=font, fill=color)

            cur_x += word_w + space_w
            w_counter += 1

        t_y += 55

    return np.array(bg)

SFX_DIR = "sfx"
def get_sfx(name):
    if not name or name.lower() in ("none", "null", ""):
        return None
    candidates = [
        os.path.join(SFX_DIR, f"{name.lower()}.wav"),
        os.path.join(SFX_DIR, f"{name.lower()}.mp3"),
        f"{name.lower()}.wav",
        f"{name.lower()}.mp3"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def process_reality_production(topic=None, script_data=None):
    if script_data is None:
        script_data = get_reality_script(topic)
    
    title = script_data.get("title", "Curiosity Explainer")
    description = script_data.get("description", "")
    tags = script_data.get("tags", [])
    scenes = script_data.get("scenes", [])

    now_str = datetime.now().strftime("%Y-%m-%d_%I-%M-%p")
    slug = re.sub(r'[^a-zA-Z0-9]', '_', title)[:22].strip('_')
    session_dir = os.path.join(OUTPUT_DIR, f"Reality_{now_str}_{slug}")
    os.makedirs(session_dir, exist_ok=True)

    # Clean reality_temp for fresh run
    for f in os.listdir(TEMP_DIR):
        try:
            os.remove(os.path.join(TEMP_DIR, f))
        except Exception:
            pass

    print("\n" + "=" * 65)
    print(f"[*] REALITY STICKMAN PRODUCTION STARTED: {session_dir}")
    print(f"[*] TITLE: {title}")
    print(f"[*] VOICE SPEED: {NARRATOR_VOICE['rate']} (Snappy 1.45x Shorts Pacing)")
    print("=" * 65)

    clips = []
    total_scenes = len(scenes)

    for idx, sc in enumerate(scenes):
        scene_id = idx + 1
        spoken_text = sc.get("spoken_hindi") or sc["dialogue"]
        screen_text = sc["dialogue"]
        is_punchline = (scene_id == total_scenes)

        print(f"\n[Processing Scene {scene_id}/{total_scenes}]")
        print(f"-> Audio: {spoken_text}")
        print(f"-> Captions: {screen_text}")

        audio_file = os.path.join(TEMP_DIR, f"audio_{scene_id}.mp3")
        image_file = os.path.join(TEMP_DIR, f"scene_{scene_id}.png")

        duration, words_data = generate_reality_voice(spoken_text, audio_file)
        print(f"-> Voice Duration: {duration:.2f}s")

        generate_reality_image(sc["visual_prompt"], image_file, scene_id)
        raw_img = Image.open(image_file).convert("RGB")

        def make_frame(t, dur=duration, im=raw_img, w_data=words_data, txt=screen_text, punch=is_punchline):
            return render_reality_frame(t, dur, im, w_data, txt, punch)

        clip = VideoClip(make_frame, duration=duration)
        audio_clip = AudioFileClip(audio_file)
        audio_layers = [audio_clip]

        chosen_sfx = get_sfx(sc.get("sfx", "whoosh"))
        if chosen_sfx:
            try:
                sfx_audio = AudioFileClip(chosen_sfx).volumex(0.25)
                if sfx_audio.duration > duration:
                    sfx_audio = sfx_audio.subclip(0, duration)
                audio_layers.append(sfx_audio)
            except Exception:
                pass

        clip = clip.set_audio(CompositeAudioClip(audio_layers))
        clips.append(clip)

    print("\n[*] Concatenating scenes into complete film...")
    final_video = concatenate_videoclips(clips, method="compose")

    bgm_path = "bgm.mp3"
    if os.path.exists(bgm_path):
        print("[*] Mixing Ambient Curiosity BGM at 6% volume...")
        bgm_audio = (
            AudioFileClip(bgm_path)
            .fx(afx.audio_loop, duration=final_video.duration)
            .volumex(0.06)
        )
        final_audio = CompositeAudioClip([final_video.audio, bgm_audio])
        final_video = final_video.set_audio(final_audio)

    video_path = os.path.join(session_dir, "final_reality_short.mp4")
    print(f"\n[*] Exporting Reality Short MP4: {video_path}")
    final_video.write_videofile(
        video_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        logger="bar"
    )

    thumb_path = os.path.join(session_dir, "cover_thumbnail.png")
    best_image = os.path.join(TEMP_DIR, "scene_1.png")
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
    print(f"[SUCCESS] REALITY STICKMAN SHORT READY: {video_path}")
    print("=" * 65)
    return video_path, title, description, tags

if __name__ == "__main__":
    if os.path.exists("dreams_script.json"):
        with open("dreams_script.json", "r", encoding="utf-8") as f:
            script = json.load(f)
        process_reality_production(script_data=script)
    else:
        topic = "Hume sapne kyu aate hain? Aur dimaag sapno mein ajeeb kahaniyan kyu banata hai?"
        process_reality_production(topic=topic)
