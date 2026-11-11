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
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
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
TEMP_DIR = os.path.join(OUTPUT_DIR, "temp")
os.makedirs(TEMP_DIR, exist_ok=True)

VOICE_POOL = {
    # 2 Distinct Male Voices
    "M1": {
        "name": "Kabir",
        "gender": "male",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+22%",
        "pitch": "+4Hz",
        "color": (57, 255, 20),      # Neon Green
        "description": "Young witty boy / energetic friend"
    },
    "M2": {
        "name": "Uncle/Papa",
        "gender": "male",
        "voice": "hi-IN-MadhurNeural",
        "rate": "+14%",
        "pitch": "-12Hz",
        "color": (255, 170, 0),      # Warm Orange
        "description": "Mature male / Papa / Uncle / authoritative taunter"
    },
    # 2 Distinct Female Voices
    "F1": {
        "name": "Ananya",
        "gender": "female",
        "voice": "hi-IN-SwaraNeural",
        "rate": "+24%",
        "pitch": "+8Hz",
        "color": (0, 235, 255),      # Cyan
        "description": "Young bubbly girl / sassy sarcastic girlfriend"
    },
    "F2": {
        "name": "Mummy Ji",
        "gender": "female",
        "voice": "hi-IN-SwaraNeural",
        "rate": "+15%",
        "pitch": "-6Hz",
        "color": (255, 105, 180),    # Hot Pink
        "description": "Mature female / dramatic mummy / serious narrator"
    }
}

def assign_character_voices(data):
    """
    Selects 2 distinct voices from the 4-voice pool (2 Male, 2 Female) based on AI character metadata,
    or picks random diverse male/female voices.
    """
    char_a = data.get("character_A", {})
    char_b = data.get("character_B", {})

    def resolve_key(meta, fallback_gender):
        gender = str(meta.get("gender", fallback_gender)).lower()
        ptype = str(meta.get("type", "young")).lower()
        name = str(meta.get("name", "")).lower()
        is_mature = any(w in ptype or w in name for w in ["mature", "old", "papa", "uncle", "dad", "father", "mummy", "mom", "mother", "boss", "suresh"])
        if "female" in gender or "woman" in gender or "girl" in gender:
            return "F2" if is_mature else "F1"
        else:
            return "M2" if is_mature else "M1"

    key_a = resolve_key(char_a, "male")
    key_b = resolve_key(char_b, "female" if key_a.startswith("M") else "male")

    # Ensure Character A and B have different voice presets
    if key_a == key_b:
        alternatives = [k for k in VOICE_POOL.keys() if k != key_a]
        key_b = alternatives[0]

    cfg_a = dict(VOICE_POOL[key_a])
    cfg_b = dict(VOICE_POOL[key_b])

    cfg_a["label"] = char_a.get("name") or cfg_a["name"]
    cfg_b["label"] = char_b.get("name") or cfg_b["name"]

    print(f"[*] Character A assigned: [{key_a}] {cfg_a['label']} ({cfg_a['gender'].upper()})")
    print(f"[*] Character B assigned: [{key_b}] {cfg_b['label']} ({cfg_b['gender'].upper()})")

    return {"A": cfg_a, "B": cfg_b}


def get_storyboard_and_metadata(topic):
    print(f"\n[*] Connecting to Chrome session on port 9222 for topic: '{topic}'...")
    prompt_text = (
        f"You are a professional YouTube Shorts creator. Create a funny, punchy 4 to 5 scene Hindi stickman conversation about: '{topic}'.\n"
        "Characters: Create two relatable Indian characters (e.g. Papa & Beta, Husband & Wife, Delivery Guy & Customer, or Friends).\n"
        "Identify them in 'character_A' and 'character_B' with their name, gender ('male' or 'female'), and type ('young' or 'mature').\n\n"
        "Crucial Dual-Text Requirement for Indian Voice and Subtitles:\n"
        "1. 'spoken_hindi': Write the dialogue in PURE HINDI DEVANAGARI SCRIPT (e.g. 'अरे भाई, मैं 20 मिनट से गेट पर खड़ा हूँ!'). The text-to-speech engine speaks Devanagari with authentic native Hindi pronunciation.\n"
        "2. 'dialogue': Write the EXACT SAME DIALOGUE in HINGLISH / Roman script (e.g. 'Arre bhai, main 20 minute se gate par khada hoon!'). This will be displayed on screen as captions for the audience.\n\n"
        "Guidelines for Visuals:\n"
        "- 'visual_prompt': Describe ONLY physical stickman action, posture, and facial expression (e.g. 'stickman tapping foot impatiently looking at watch', 'stickman riding scooter casually'). NEVER write single letters like 'A' or 'B', and NEVER write dialogue text or words in visual_prompt.\n\n"
        "Sound Effects (SFX):\n"
        "For each scene, choose the most fitting situational comedy sound effect from:\n"
        "['whoosh', 'pop', 'vine_boom', 'punch', 'laugh', 'cricket', 'boing', 'record_scratch', 'dramatic', 'none']\n"
        "- Use 'whoosh' or 'pop' for normal fast transitions\n"
        "- Use 'vine_boom' or 'dramatic' for sudden shock or twists\n"
        "- Use 'punch' for savage roasts\n"
        "- Use 'cricket' for awkward silence\n"
        "- Use 'record_scratch' for reality check\n"
        "- Use 'laugh' for the final punchline\n\n"
        "Strictly output a single raw valid JSON object without markdown formatting or intro:\n"
        "{\n"
        '  "title": "Short Catchy Clickbait Title 😂 #shorts #viral",\n'
        '  "description": "Engaging description with #comedy #stickman #animation",\n'
        '  "tags": ["shorts", "stickman", "funny", "hindi comedy", "animation", "relatable"],\n'
        '  "character_A": {"name": "Customer", "gender": "male", "type": "young"},\n'
        '  "character_B": {"name": "Delivery Guy", "gender": "male", "type": "mature"},\n'
        '  "scenes": [\n'
        '    {"scene": 1, "speaker": "A", "dialogue": "Arre bhai, main 20 minute se gate par khada hoon!", "spoken_hindi": "अरे भाई, मैं 20 मिनट से गेट पर खड़ा हूँ!", "visual_prompt": "stickman tapping foot impatiently looking at watch", "sfx": "whoosh"}\n'
        '  ]\n'
        "}"
    )

    page = None
    try:
        page = chrome_session.get_or_open_page("deepseek.com", "https://chat.deepseek.com", reuse=True)
        print("[*] Submitting prompt to DeepSeek...")
        textarea = page.wait_for_selector("textarea", timeout=15000)
        textarea.click()
        textarea.fill(prompt_text)
        textarea.press("Enter")

        print("[*] Generating script & SEO...")
        time.sleep(4)

        for _ in range(50):
            stop_btn = page.query_selector('div[aria-label="Stop"], button:has-text("Stop")')
            if not stop_btn:
                break
            time.sleep(1)

        time.sleep(2)
        elements = page.query_selector_all(".ds-markdown, .markdown")
        raw_text = elements[-1].inner_text() if elements else page.locator("body").inner_text()

        # Clean JSON extraction
        json_match = re.search(r'\{\s*"title".*\}\s*', raw_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except Exception:
                pass

        start = raw_text.find('{')
        end = raw_text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(raw_text[start:end])

        raise ValueError("JSON parse nahi ho saka.")

    except Exception as e:
        print(f"[!] DeepSeek extraction error: {e}")
        return None

async def make_audio_with_timestamps(text, voice_cfg, output_path):
    communicate = edge_tts.Communicate(
        text, 
        voice_cfg["voice"], 
        rate=voice_cfg["rate"], 
        pitch=voice_cfg["pitch"]
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

def generate_voice_and_timestamps(spoken_text, voice_cfg, output_path):
    """
    Takes pure spoken text (Hindi Devanagari) and voice configuration.
    Produces authentic native pronunciation audio with word timing.
    """
    if os.path.exists(output_path):
        os.remove(output_path)

    result_holder = []
    error_holder  = []

    def _run_tts_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            words = loop.run_until_complete(
                make_audio_with_timestamps(spoken_text, voice_cfg, output_path)
            )
            result_holder.append(words)
        except Exception as e:
            error_holder.append(e)
        finally:
            loop.close()

    tts_thread = threading.Thread(target=_run_tts_thread, daemon=True)
    tts_thread.start()
    tts_thread.join(timeout=120)

    if error_holder:
        raise RuntimeError(f"TTS generation failed: {error_holder[0]}")
    if not result_holder:
        raise RuntimeError("TTS thread timed out (120s exceeded)")

    audio_info = MP3(output_path)
    return audio_info.info.length, result_holder[0]

flux_client = None

def get_flux_client():
    global flux_client
    if flux_client is None:
        from gradio_client import Client
        print("[*] Connecting to FLUX.1 Cloud AI Image Engine (Zero Local GPU Load)...")
        flux_client = Client("black-forest-labs/FLUX.1-schnell")
    return flux_client

def generate_ai_stickman(visual_prompt, output_path, scene_id):
    print(f"[*] Generating High-Definition Stickman for Scene {scene_id} via Cloud AI (Bing)...")
    
    clean_visual = re.sub(r'\b(character\s*[ab]|speaker\s*[ab]|[ab])\b', '', visual_prompt, flags=re.I)
    clean_visual = clean_visual.replace('"', '').replace("'", '').strip()
    if not clean_visual:
        clean_visual = "stickman looking funny and expressive"

    prompt = (
        f"simple minimalist stick figure cartoon, {clean_visual}, "
        "bold black ink outlines, pure solid white background, xkcd meme webcomic style, "
        "funny expressive stickman doodle, minimal ink drawing, vector clipart, high contrast, zero clutter, "
        "no text, no letters, no typography, no speech bubbles, no watermark, masterpiece"
    )

    # 1. Primary: Cloud Generation via Microsoft Bing in persistent Chrome session (Zero local GPU load)
    try:
        page = chrome_session.get_or_open_page("bing.com/images/create", "https://www.bing.com/images/create", reuse=True)
        
        old_id = ""
        m = re.search(r'id=(1-[a-f0-9]+)', page.url)
        if m:
            old_id = m.group(1)

        textarea = page.wait_for_selector("textarea[name='gmc__textarea'], textarea[placeholder*='Describe']", timeout=8000)
        textarea.click()
        textarea.press("Control+A")
        textarea.press("Backspace")
        textarea.type(prompt, delay=5)
        time.sleep(0.5)

        gen_btn = page.wait_for_selector("button:has-text('Generate'), button.gmbtn__btn", timeout=5000)
        gen_btn.click()
        print(f"[*] Scene {scene_id}: Submitted prompt to Bing, waiting for new creation ID...")

        # Wait for new generation ID
        for _ in range(30):
            time.sleep(1)
            m = re.search(r'id=(1-[a-f0-9]+)', page.url)
            if m and m.group(1) != old_id:
                break

        # Wait for rendered image from Bing
        for _ in range(35):
            time.sleep(1.5)
            img_src = page.evaluate("""() => {
                let imgs = Array.from(document.querySelectorAll('img')).filter(i => 
                    i.src && 
                    i.src.includes('th.bing.com') && 
                    (i.src.includes('OIG') || i.src.includes('OIG1') || i.src.includes('OIG2') || i.src.includes('OIG3') || i.src.includes('OIG4') || i.src.includes('OIGP')) &&
                    (i.className.includes('aigc-') || i.naturalWidth > 150)
                );
                return imgs.length > 0 ? imgs[0].src : null;
            }""")
            if img_src:
                clean_url = img_src.split("?")[0] + "?pid=ImgGn"
                import urllib.request
                req = urllib.request.Request(clean_url, headers={"User-Agent": "Mozilla/5.0"})
                temp_raw = output_path + ".raw.png"
                with urllib.request.urlopen(req, timeout=15) as resp:
                    with open(temp_raw, "wb") as f:
                        f.write(resp.read())

                # Center and pad on pure white square 1024x1024 canvas
                with Image.open(temp_raw) as raw_im:
                    raw_im = raw_im.convert("RGB")
                    w, h = raw_im.size
                    scale = min(960 / w, 960 / h)
                    new_w, new_h = int(w * scale), int(h * scale)
                    resized = raw_im.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    square = Image.new("RGB", (1024, 1024), (255, 255, 255))
                    paste_x = (1024 - new_w) // 2
                    paste_y = (1024 - new_h) // 2
                    square.paste(resized, (paste_x, paste_y))
                    square.save(output_path, "PNG")

                if os.path.exists(temp_raw):
                    os.remove(temp_raw)
                print(f"-> Cloud Bing Frame {scene_id} ready (1024x1024 Square): {output_path}")
                return output_path
    except Exception as bing_e:
        print(f"[!] Bing cloud generator notice: {bing_e}. Trying FLUX / local failsafe...")

    # 2. Secondary Failsafe: FLUX Cloud
    try:
        from gradio_client import Client
        flux = Client("black-forest-labs/FLUX.1-schnell")
        res = flux.predict(
            prompt=prompt,
            seed=0,
            randomize_seed=True,
            width=1024,
            height=1024,
            num_inference_steps=4,
            api_name="/infer"
        )
        with Image.open(res[0]) as im:
            im.convert("RGB").save(output_path, "PNG")
        print(f"-> Cloud FLUX Frame {scene_id} ready: {output_path}")
        return output_path
    except Exception as flux_e:
        print(f"[!] FLUX failsafe notice: {flux_e}. Falling back to emergency vector doodle...")

    # 3. Guaranteed Emergency Fallback: Vector Stickman via PIL
    try:
        img = Image.new("RGB", (1024, 1024), (255, 255, 255))
        d = ImageDraw.Draw(img)
        # Head
        d.ellipse([412, 180, 612, 380], outline=(0, 0, 0), width=16)
        # Eyes & Smile
        d.ellipse([460, 240, 480, 260], fill=(0, 0, 0))
        d.ellipse([544, 240, 564, 260], fill=(0, 0, 0))
        d.arc([470, 270, 554, 330], start=20, end=160, fill=(0, 0, 0), width=12)
        # Body
        d.line([512, 380, 512, 680], fill=(0, 0, 0), width=18)
        # Arms
        d.line([512, 450, 320, 560], fill=(0, 0, 0), width=16)
        d.line([512, 450, 704, 560], fill=(0, 0, 0), width=16)
        # Legs
        d.line([512, 680, 360, 890], fill=(0, 0, 0), width=18)
        d.line([512, 680, 664, 890], fill=(0, 0, 0), width=18)
        img.save(output_path, "PNG")
        print(f"-> Emergency Stickman Frame {scene_id} generated: {output_path}")
        return output_path
    except Exception as em_err:
        print(f"[!] Emergency doodle failed: {em_err}")
        return output_path

def render_scene_frame(t, duration, raw_img, words_data, full_text, speaker_cfg, is_punchline=False):
    # 1. Base Slow Dramatic Cinematic Zoom
    zoom_rate = 0.08 if not is_punchline else 0.14
    zoom = 1.0 + zoom_rate * (t / duration)

    # 2. Snappy Comic Entrance Bounce (0s to 0.35s)
    if t < 0.35:
        p = t / 0.35
        # Overshoot spring curve
        pop_factor = 0.88 + 0.16 * np.sin(p * np.pi) + (0.12 * (p ** 2))
        pop_factor = min(pop_factor, 1.06)
    else:
        pop_factor = 1.0

    # 3. Conversational Talking Motion (Bobbing & Nodding with audio timing)
    is_speaking = False
    if words_data:
        for w_obj in words_data:
            if w_obj["start"] <= t <= w_obj["end"]:
                is_speaking = True
                break
    else:
        is_speaking = (t < duration - 0.25)

    if is_speaking:
        bob_y = int(7 * np.sin(t * 16))
        sway_x = int(3 * np.cos(t * 8))
    else:
        bob_y = int(2 * np.sin(t * 4))
        sway_x = 0

    # 4. Punchline Impact Camera Shake (on punchline climax)
    shake_x, shake_y = 0, 0
    if is_punchline and (t > max(0.5, duration - 1.8)):
        decay = max(0.0, 1.0 - (t - (duration - 1.8)) / 1.8)
        shake_mag = int(14 * decay)
        if shake_mag > 0:
            frame_seed = int(t * 24)
            rng = np.random.RandomState(frame_seed)
            shake_x = rng.randint(-shake_mag, shake_mag + 1)
            shake_y = rng.randint(-shake_mag, shake_mag + 1)

    # Apply transform
    eff_zoom = zoom * pop_factor
    base_w, base_h = 660, 660
    cur_w, cur_h = int(base_w * eff_zoom), int(base_h * eff_zoom)

    zoomed_img = raw_img.resize((cur_w, cur_h), Image.Resampling.BILINEAR)
    left = (cur_w - base_w) // 2
    top = (cur_h - base_h) // 2
    cropped_img = zoomed_img.crop((left, top, left + base_w, top + base_h))

    canvas = Image.new("RGB", (720, 1280), (248, 248, 250))
    draw = ImageDraw.Draw(canvas)

    # Dynamic animated container
    card_x1 = 25 + shake_x
    card_y1 = 145 + shake_y
    card_x2 = 695 + shake_x
    card_y2 = 815 + shake_y
    draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=24, fill=(255, 255, 255), outline=(225, 225, 230), width=3)
    
    # Paste animated stickman with conversational bob and sway
    canvas.paste(cropped_img, (30 + sway_x + shake_x, 150 + bob_y + shake_y))

    try:
        font = ImageFont.truetype("arialbd.ttf", 36)
        label_font = ImageFont.truetype("arialbd.ttf", 26)
    except:
        font = ImageFont.load_default()
        label_font = ImageFont.load_default()

    all_words = full_text.split()
    lines = []
    curr = []
    for w in all_words:
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
        progress = min(max(t / duration, 0.0), 1.0)
        active_idx = int(progress * len(all_words))

    total_text_h = len(lines) * 55
    box_y1 = 860 + shake_y
    box_y2 = box_y1 + total_text_h + 50
    draw.rounded_rectangle([35 + shake_x, box_y1, 685 + shake_x, box_y2], radius=20, fill=(18, 18, 22))

    if isinstance(speaker_cfg, dict):
        badge_label = speaker_cfg.get("label", "Speaker")
        active_color = speaker_cfg.get("color", (57, 255, 20))
    else:
        is_speaker_a = (str(speaker_cfg).upper() == "A")
        active_color = (57, 255, 20) if is_speaker_a else (0, 235, 255)
        badge_label = "Character A" if is_speaker_a else "Character B"
    draw.text((55 + shake_x, box_y1 + 10), badge_label, font=label_font, fill=active_color)

    text_y = box_y1 + 45
    w_counter = 0
    space_w = draw.textbbox((0, 0), " ", font=font)[2]

    for line in lines:
        line_w = sum(draw.textbbox((0, 0), word, font=font)[2] for word in line) + space_w * (len(line) - 1)
        cur_x = (720 - line_w) // 2 + shake_x

        for word in line:
            w_bbox = draw.textbbox((0, 0), word, font=font)
            word_w = w_bbox[2] - w_bbox[0]

            if w_counter == active_idx:
                color = active_color
            elif w_counter < active_idx:
                color = (255, 255, 255)
            else:
                color = (130, 130, 130)

            draw.text((cur_x + 2, text_y + 2), word, font=font, fill=(0, 0, 0))
            draw.text((cur_x, text_y), word, font=font, fill=color)

            cur_x += word_w + space_w
            w_counter += 1

        text_y += 55

    return np.array(canvas)

def create_shorts_thumbnail(best_image_path, title_text, output_thumb_path):
    canvas = Image.new("RGB", (720, 1280), (255, 255, 255))
    raw_img = Image.open(best_image_path).convert("RGB")
    raw_img = raw_img.resize((680, 680))
    canvas.paste(raw_img, (20, 290))
    
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arialbd.ttf", 46)
    except:
        font = ImageFont.load_default()

    hook_text = re.sub(r'#\S+', '', title_text).strip()
    words = hook_text.split()
    lines = []
    curr = []
    for w in words:
        curr.append(w)
        if len(" ".join(curr)) > 18:
            curr.pop()
            lines.append(" ".join(curr))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))

    banner_y1 = 60
    banner_y2 = banner_y1 + len(lines) * 65 + 30
    draw.rounded_rectangle([30, banner_y1, 690, banner_y2], radius=20, fill=(240, 20, 20))
    
    t_y = banner_y1 + 15
    for l in lines:
        bbox = draw.textbbox((0, 0), l, font=font)
        w = bbox[2] - bbox[0]
        tx = (720 - w) // 2
        draw.text((tx + 2, t_y + 2), l, font=font, fill=(0, 0, 0))
        draw.text((tx, t_y), l, font=font, fill=(255, 255, 255))
        t_y += 65

    canvas.save(output_thumb_path)
    return output_thumb_path


SFX_DIR = "sfx"
SFX_VOLUME_MAP = {
    "vine_boom": 0.40,
    "laugh": 0.35,
    "punch": 0.30,
    "record_scratch": 0.30,
    "dramatic": 0.30,
    "cricket": 0.25,
    "boing": 0.25,
    "whoosh": 0.20,
    "pop": 0.20
}

def get_sfx_path(sfx_name):
    if not sfx_name or sfx_name.lower() in ("none", "null", ""):
        return None
    name = sfx_name.lower().strip().replace(" ", "_")
    # Check sfx/ directory first (.wav or .mp3)
    candidates = [
        os.path.join(SFX_DIR, f"{name}.wav"),
        os.path.join(SFX_DIR, f"{name}.mp3"),
        f"{name}.mp3",
        f"{name}.wav"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def assemble_video(scenes, cover_path, target_video_path, assigned_voices=None):
    if assigned_voices is None:
        assigned_voices = {
            "A": VOICE_POOL["M1"],
            "B": VOICE_POOL["F1"]
        }
    clips = []
    print("\n--- Starting Rendering Queue with Comedy SFX & Dual Hindi/Hinglish Engine ---")

    total_scenes = len(scenes)
    for idx, sc in enumerate(scenes):
        scene_id = idx + 1
        speaker_key = sc.get("speaker", "A").upper()
        if speaker_key not in assigned_voices:
            speaker_key = "A" if idx % 2 == 0 else "B"
        
        voice_cfg = assigned_voices[speaker_key]
        is_punchline = (scene_id == total_scenes)

        spoken_text = sc.get("spoken_hindi") or sc["dialogue"]
        screen_text = sc["dialogue"]

        print(f"\n[Processing Scene {scene_id}/{total_scenes} - {voice_cfg['label']}]")
        print(f"-> Spoken (Hindi Audio): {spoken_text}")
        print(f"-> Captions (Hinglish Screen): {screen_text}")

        audio_file = os.path.join(TEMP_DIR, f"audio_{scene_id}.mp3")
        image_file = os.path.join(TEMP_DIR, f"image_{scene_id}.png")

        duration, words_data = generate_voice_and_timestamps(spoken_text, voice_cfg, audio_file)
        print(f"-> Voice Duration: {duration:.2f}s")

        if not (scene_id == 1 and os.path.exists(image_file)):
            generate_ai_stickman(sc["visual_prompt"], image_file, scene_id)
        raw_img = Image.open(image_file).convert("RGB")

        def make_frame(t, dur=duration, img=raw_img, w_data=words_data, txt=screen_text, spk_cfg=voice_cfg, punch=is_punchline):
            return render_scene_frame(t, dur, img, w_data, txt, spk_cfg, punch)

        clip = VideoClip(make_frame, duration=duration)
        audio_clip = AudioFileClip(audio_file)

        audio_layers = [audio_clip]

        scene_sfx_name = sc.get("sfx", "whoosh" if idx == 0 else ("laugh" if is_punchline else "none"))
        chosen_sfx_path = get_sfx_path(scene_sfx_name)

        if is_punchline and not chosen_sfx_path:
            chosen_sfx_path = get_sfx_path("laugh")

        if chosen_sfx_path:
            clean_sfx_key = scene_sfx_name.lower().strip()
            vol = SFX_VOLUME_MAP.get(clean_sfx_key, 0.25)
            print(f"[*] Triggering AI SFX: [{clean_sfx_key.upper()}] from {chosen_sfx_path} at volume {vol:.2f}")
            try:
                sfx_audio = AudioFileClip(chosen_sfx_path).volumex(vol)
                if clean_sfx_key in ("laugh", "cricket"):
                    start_pos = min(max(duration - 1.5, 0.5), duration)
                    sfx_audio = sfx_audio.set_start(start_pos)
                else:
                    if sfx_audio.duration > duration:
                        sfx_audio = sfx_audio.subclip(0, duration)
                audio_layers.append(sfx_audio)
            except Exception as sfx_err:
                print(f"[!] Warning: Could not mix SFX {clean_sfx_key}: {sfx_err}")

        clip = clip.set_audio(CompositeAudioClip(audio_layers))
        clips.append(clip)

    print("\n[*] Concatenating scenes...")
    concatenated_video = concatenate_videoclips(clips, method="compose")

    if os.path.exists(cover_path):
        cover_clip = ImageClip(cover_path).set_duration(0.08)
        concatenated_video = concatenate_videoclips([cover_clip, concatenated_video], method="compose")

    bgm_path = "bgm.mp3"
    if os.path.exists(bgm_path):
        print("[*] Mixing Background Music at 8% volume...")
        bgm_audio = (
            AudioFileClip(bgm_path)
            .fx(afx.audio_loop, duration=concatenated_video.duration)
            .volumex(0.08)
        )
        final_audio = CompositeAudioClip([concatenated_video.audio, bgm_audio])
        final_video = concatenated_video.set_audio(final_audio)
    else:
        final_video = concatenated_video

    print(f"\n[*] Exporting MP4: {target_video_path}")
    final_video.write_videofile(
        target_video_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        logger="bar"
    )
    return target_video_path

def process_full_production(topic, base_filename=None):
    print(f"\n[*] Topic process kiya ja raha hai: '{topic}'")
    
    data = None
    for attempt in range(3):
        try:
            data = get_storyboard_and_metadata(topic)
            if data and "scenes" in data and len(data["scenes"]) > 0:
                break
        except Exception as e:
            print(f"[!] DeepSeek fetch attempt {attempt+1} fail hua: {e}")
            time.sleep(3)

    if not data or "scenes" not in data or len(data["scenes"]) == 0:
        print(f"[!] '{topic}' ke liye script generate nahi ho saki. Skip kar rahe hain.")
        return None

    now_str = datetime.now().strftime("%Y-%m-%d_%I-%M-%p")
    clean_topic_slug = re.sub(r'[^a-zA-Z0-9]', '_', topic)[:22].strip('_')
    
    folder_name = f"{now_str}_{clean_topic_slug}"
    video_session_dir = os.path.join(OUTPUT_DIR, folder_name)
    os.makedirs(video_session_dir, exist_ok=True)
    for f in os.listdir(TEMP_DIR):
        try:
            os.remove(os.path.join(TEMP_DIR, f))
        except Exception:
            pass

    print(f"\n" + "=" * 60)
    print(f"[*] DEDICATED FOLDER CREATED: {video_session_dir}")
    print("=" * 60)

    scenes = data.get("scenes", [])
    title = data.get("title", topic)
    description = data.get("description", "")
    tags = data.get("tags", [])

    print(f"[*] TITLE: {title}")
    print(f"[*] DESCRIPTION: {description}")
    print(f"[*] TAGS: {', '.join(tags)}")

    thumb_path = os.path.join(video_session_dir, "cover_thumbnail.png")
    best_image = os.path.join(TEMP_DIR, "image_1.png")
    generate_ai_stickman(scenes[0]["visual_prompt"], best_image, 1)
    create_shorts_thumbnail(best_image, title, thumb_path)

    video_path = os.path.join(video_session_dir, "final_short.mp4")
    assigned_voices = assign_character_voices(data)
    assemble_video(scenes, thumb_path, video_path, assigned_voices)

    meta_path = os.path.join(video_session_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "title": title,
            "description": description,
            "tags": tags,
            "topic": topic,
            "created_at": now_str,
            "video_path": os.path.abspath(video_path),
            "thumbnail_path": os.path.abspath(thumb_path)
        }, f, indent=2, ensure_ascii=False)

    return video_path, title, description, tags