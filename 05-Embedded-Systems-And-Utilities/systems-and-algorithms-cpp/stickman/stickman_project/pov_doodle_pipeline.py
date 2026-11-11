"""
pov_doodle_pipeline.py
======================
Ultimate 2D Ink Doodle Animation Engine:
1. Pure Minimalist Black & White Ink Aesthetic with subtle comic color pops.
2. Natural Human Voice Acting:
   - Conversational pacing (+16% rate, natural pauses).
   - Studio Audio Mastering Chain (FFmpeg compression, 120Hz warmth, 3.5kHz vocal clarity).
3. Walking Kinematics & Dynamic Entrance:
   - 2-segment leg stride, knee bend, torso bounce, and arm swing.
4. Physical Cartoon Hits & Physics:
   - Flying Chappal spinning in from offscreen.
   - Impact burst with thwack sound effect.
   - Circling cartoon stars & spiral dizzy eyes.
5. Cute Cartoon Pet:
   - "Tommy" the Desi Dog with continuously wagging tail, floppy ear bounce, and shock reactions!
6. Living Animated Environments:
   - Spinning ceiling fan, ticking clock, steaming pots, gym lights.
7. Dynamic Camera Zoom & Punch-ins (Ken Burns on shock and punchlines).
8. Real-Time Lip-Sync via exact FFmpeg audio RMS volume.
"""

import os
import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import time
import json
import math
import random
import re
import subprocess
import threading
from datetime import datetime
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, concatenate_audioclips
from mutagen.mp3 import MP3
import edge_tts

OUTPUT_DIR = "pipeline_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
TEMP_DIR = os.path.join(OUTPUT_DIR, "pov_doodle_temp")
os.makedirs(TEMP_DIR, exist_ok=True)
SFX_DIR = "sfx"

VOICE_CONFIG = {
    "boy": {
        "name": "hi-IN-MadhurNeural",
        "rate": "+18%",
        "pitch": "+10Hz",
        "label": "BOY 1",
        "color": (255, 215, 0),
        "highlight": (255, 215, 0)
    },
    "boy2": {
        "name": "hi-IN-MadhurNeural",
        "rate": "+16%",
        "pitch": "+5Hz",
        "label": "DOST",
        "color": (40, 160, 240),
        "highlight": (40, 160, 240)
    },
    "girl": {
        "name": "hi-IN-SwaraNeural",
        "rate": "+16%",
        "pitch": "+0Hz",
        "label": "GIRL",
        "color": (255, 42, 133),
        "highlight": (255, 42, 133)
    },
    "mummy": {
        "name": "hi-IN-SwaraNeural",
        "rate": "+14%",
        "pitch": "-4Hz",
        "label": "MUMMY",
        "color": (230, 45, 45),
        "highlight": (230, 45, 45)
    },
    "boss": {
        "name": "hi-IN-MadhurNeural",
        "rate": "+12%",
        "pitch": "-8Hz",
        "label": "BOSS",
        "color": (120, 50, 210),
        "highlight": (120, 50, 210)
    },
    "dad": {
        "name": "hi-IN-MadhurNeural",
        "rate": "+10%",
        "pitch": "-6Hz",
        "label": "PAPA",
        "color": (50, 150, 60),
        "highlight": (50, 150, 60)
    }
}

def extract_rms_per_frame(mp3_path, fps=24):
    """
    Extract exact RMS audio amplitude per 24fps frame via direct FFmpeg PCM 16kHz pipe.
    """
    cmd = [
        'ffmpeg', '-y', '-i', mp3_path,
        '-ac', '1', '-ar', '16000', '-f', 's16le', 'pipe:1'
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    raw_audio, _ = proc.communicate()
    samples = np.frombuffer(raw_audio, dtype=np.int16).astype(np.float32)
    
    samples_per_frame = int(16000 / fps)
    total_frames = int(len(samples) / samples_per_frame)
    rms_list = []
    
    for i in range(total_frames):
        chunk = samples[i * samples_per_frame : (i + 1) * samples_per_frame]
        val = np.sqrt(np.mean(chunk**2)) if len(chunk) > 0 else 0.0
        rms_list.append(val)
        
    rms_arr = np.array(rms_list)
    max_val = np.max(rms_arr) if len(rms_arr) > 0 else 1.0
    norm = rms_arr / (max_val + 1e-5)
    return norm

def get_word_timings_from_rms(norm_rms, text, fps=24):
    """
    Align words to active audio speech segments extracted from RMS.
    """
    words = text.split()
    n_frames = len(norm_rms)
    if n_frames == 0 or len(words) == 0:
        return []
        
    is_speech = norm_rms > 0.10
    clusters = []
    in_cluster = False
    start = 0
    for i, spk in enumerate(is_speech):
        if spk and not in_cluster:
            in_cluster = True
            start = i
        elif not spk and in_cluster:
            in_cluster = False
            clusters.append((start, i))
    if in_cluster:
        clusters.append((start, n_frames - 1))
        
    if not clusters:
        total_dur = n_frames / fps
        w_dur = total_dur / len(words)
        return [{"word": w, "start": i * w_dur, "end": (i + 1) * w_dur} for i, w in enumerate(words)]
        
    speech_frames = []
    for s, e in clusters:
        speech_frames.extend(range(s, e + 1))
        
    words_data = []
    n_speech = len(speech_frames)
    for i, w in enumerate(words):
        f_start_idx = int(i * (n_speech / len(words)))
        f_end_idx = int((i + 1) * (n_speech / len(words))) - 1
        f_end_idx = max(f_start_idx, min(n_speech - 1, f_end_idx))
        
        t_start = speech_frames[f_start_idx] / fps
        t_end = (speech_frames[f_end_idx] + 1) / fps
        words_data.append({
            "word": w,
            "start": round(t_start, 2),
            "end": round(t_end, 2)
        })
        
    return words_data

def master_voice_audio(raw_mp3, output_mp3):
    """
    Master raw TTS into broadcast podcast quality via FFmpeg:
    - Dynamic compressor / limiter (flattens jumps, tightens punch)
    - Warm bass boost at 120Hz
    - Vocal clarity boost at 3500Hz
    """
    cmd = [
        'ffmpeg', '-y', '-i', raw_mp3,
        '-af', 'compand=0|0:1|1:-60/-60|-40/-30|-20/-10|0/-3:6:0:-90:0.2,equalizer=f=120:width_type=o:width=2:g=3.5,equalizer=f=3500:width_type=o:width=1.5:g=3.5',
        output_mp3
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not os.path.exists(output_mp3) or os.path.getsize(output_mp3) == 0:
        import shutil
        shutil.copy2(raw_mp3, output_mp3)

def synthesize_audio(text, speaker, output_path):
    spk_key = speaker.lower() if speaker.lower() in VOICE_CONFIG else "boy"
    cfg = VOICE_CONFIG[spk_key]
    clean_text = re.sub(r'[\*\_#\"\'\(\)]', '', text).strip()
    
    raw_temp = output_path.replace(".mp3", "_raw.mp3")
    
    def run_coro():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async def main():
            communicate = edge_tts.Communicate(
                clean_text, 
                cfg["name"], 
                rate=cfg["rate"], 
                pitch=cfg["pitch"]
            )
            with open(raw_temp, "wb") as f:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
        loop.run_until_complete(main())
        loop.close()

    t = threading.Thread(target=run_coro)
    t.start()
    t.join(timeout=30)

    # Master audio into crisp studio podcast sound!
    master_voice_audio(raw_temp, output_path)

    audio_info = MP3(output_path)
    duration = audio_info.info.length
    
    norm_rms = extract_rms_per_frame(output_path, fps=24)
    words_data = get_word_timings_from_rms(norm_rms, clean_text, fps=24)
    
    return duration, norm_rms, words_data

def get_line_jitter(seed, amount=1.2):
    rng = np.random.RandomState(int(seed))
    return rng.uniform(-amount, amount)

def draw_doodle_star(draw, cx, cy, r=12, fill=(255, 215, 0), outline=(22, 22, 28)):
    pts = []
    for i in range(10):
        ang = i * math.pi / 5 - math.pi / 2
        radius = r if i % 2 == 0 else r * 0.45
        pts.append((cx + int(radius * math.cos(ang)), cy + int(radius * math.sin(ang))))
    draw.polygon(pts, fill=fill, outline=outline, width=2)

def draw_doodle_dog(draw, x, y, scale=1.0, t=0.0, emotion='idle'):
    """
    Cute Desi cartoon doggy 'Tommy' with wagging tail and floppy ears!
    """
    ink = (22, 22, 28)
    line_w = max(3, int(4 * scale))
    
    # Wagging tail
    tail_ang = math.sin(t * 18) * 30
    tx = x - int(35 * scale)
    ty = y - int(15 * scale)
    t_end_x = tx - int(25 * math.cos(math.radians(45 + tail_ang)) * scale)
    t_end_y = ty - int(25 * math.sin(math.radians(45 + tail_ang)) * scale)
    draw.line([(tx, ty), (t_end_x, t_end_y)], fill=ink, width=line_w)
    
    # Dog body
    draw.ellipse([x - int(35 * scale), y - int(25 * scale), x + int(25 * scale), y + int(10 * scale)], fill=(250, 245, 235), outline=ink, width=line_w)
    
    # Legs
    for lx in [-25, -10, 10, 20]:
        draw.line([(x + int(lx * scale), y + int(5 * scale)), (x + int(lx * scale), y + int(25 * scale))], fill=ink, width=line_w)
        draw.line([(x + int(lx * scale), y + int(25 * scale)), (x + int((lx + 6) * scale), y + int(25 * scale))], fill=ink, width=line_w)
        
    # Head
    hx = x + int(28 * scale)
    hy = y - int(30 * scale)
    hr = int(18 * scale)
    draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(250, 245, 235), outline=ink, width=line_w)
    
    # Floppy ear
    ear_bounce = math.sin(t * 12) * 3
    draw.ellipse([hx - hr + 2, hy - hr + int(ear_bounce), hx - 2, hy + int(ear_bounce)], fill=(22, 22, 28))
    
    # Snout & Nose
    draw.ellipse([hx + hr - 4, hy - 4, hx + hr + 12, hy + 8], fill=(250, 245, 235), outline=ink, width=line_w)
    draw.ellipse([hx + hr + 6, hy - 2, hx + hr + 12, hy + 4], fill=ink)
    
    # Eye
    if emotion == 'shock':
        draw.ellipse([hx + 2, hy - 8, hx + 10, hy], fill=(255, 255, 255), outline=ink, width=2)
        draw.ellipse([hx + 5, hy - 5, hx + 8, hy - 2], fill=ink)
    else:
        draw.ellipse([hx + 4, hy - 6, hx + 8, hy - 2], fill=ink)
        
    # Red collar with gold bell
    draw.line([(hx - 10, hy + hr - 2), (hx + 6, hy + hr + 2)], fill=(220, 40, 40), width=int(3 * scale))
    draw.ellipse([hx - 2, hy + hr + 2, hx + 4, hy + hr + 8], fill=(255, 215, 0), outline=ink, width=1)

def draw_ceiling_fan(draw, cx, cy, t=0.0):
    ink = (60, 60, 70)
    draw.line([(cx, cy - 70), (cx, cy)], fill=(150, 150, 160), width=3)
    draw.ellipse([cx - 16, cy - 8, cx + 16, cy + 8], fill=(220, 220, 225), outline=ink, width=2)
    angle_base = (t * 720) % 360
    for i in range(3):
        rad = math.radians(angle_base + i * 120)
        bx = int(cx + 85 * math.cos(rad))
        by = int(cy + 25 * math.sin(rad))
        draw.line([(cx, cy), (bx, by)], fill=(170, 175, 185), width=6)

def get_chappal_image(angle_deg, scale=1.0):
    sw, sh = int(45 * scale), int(100 * scale)
    surf = Image.new('RGBA', (sw + 40, sh + 40), (0, 0, 0, 0))
    sd = ImageDraw.Draw(surf)
    ox, oy = 20, 20
    # Blue Hawai Chappal Sole
    sd.rounded_rectangle([ox, oy, ox + sw, oy + sh], radius=int(16 * scale), fill=(100, 180, 240), outline=(22, 22, 28), width=3)
    sd.rounded_rectangle([ox + 4, oy + 4, ox + sw - 4, oy + sh - 4], radius=int(12 * scale), outline=(255, 255, 255), width=2)
    # V-strap
    v_top = (ox + sw // 2, oy + int(28 * scale))
    v_l = (ox + 6, oy + int(55 * scale))
    v_r = (ox + sw - 6, oy + int(55 * scale))
    sd.line([v_top, v_l], fill=(22, 22, 28), width=int(5 * scale))
    sd.line([v_top, v_r], fill=(22, 22, 28), width=int(5 * scale))
    sd.ellipse([v_top[0]-4, v_top[1]-4, v_top[0]+4, v_top[1]+4], fill=(220, 40, 40))
    
    rotated = surf.rotate(angle_deg, resample=Image.Resampling.BICUBIC, expand=True)
    return rotated

def draw_spiral_eye(draw, cx, cy, r=12, fill=(22, 22, 28)):
    pts = []
    for a in range(0, 720, 20):
        rad = math.radians(a)
        cur_r = (a / 720.0) * r
        pts.append((cx + int(cur_r * math.cos(rad)), cy + int(cur_r * math.sin(rad))))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=fill, width=2)

def draw_prop(draw, prop_type, hand_pos, scale=1.0, t=0.0):
    hx, hy = hand_pos
    ink_color = (22, 22, 28)
    
    try:
        font_tiny = ImageFont.truetype("arialbd.ttf", int(14 * scale))
        font_price = ImageFont.truetype("arialbd.ttf", int(26 * scale))
    except:
        font_tiny = ImageFont.load_default()
        font_price = ImageFont.load_default()

    if prop_type == "bill":
        vib = int(math.sin(t * 25) * 3)
        rx, ry = hx + 10 + vib, hy - int(90 * scale)
        rw, rh = int(140 * scale), int(200 * scale)
        draw.rectangle([rx, ry, rx + rw, ry + rh], fill=(255, 255, 255), outline=ink_color, width=3)
        for bx in range(rx + 15, rx + rw - 15, int(7 * scale)):
            draw.line([(bx, ry + int(20 * scale)), (bx, ry + int(38 * scale))], fill=ink_color, width=2)
        draw.text((rx + rw // 2, ry + int(56 * scale)), "ZARA BILL", fill=(110, 110, 120), font=font_tiny, anchor="mm")
        draw.text((rx + rw // 2, ry + int(85 * scale)), "TOTAL DUE:", fill=ink_color, font=font_tiny, anchor="mm")
        draw.text((rx + rw // 2, ry + int(125 * scale)), "₹18,000", fill=(225, 30, 30), font=font_price, anchor="mm")
        for vx in [-10, rw + 10]:
            draw.line([(rx + vx, ry + int(110 * scale)), (rx + vx + (6 if vx>0 else -6), ry + int(98 * scale))], fill=(225, 30, 30), width=3)
            draw.line([(rx + vx, ry + int(125 * scale)), (rx + vx + (8 if vx>0 else -8), ry + int(125 * scale))], fill=(225, 30, 30), width=3)
            draw.line([(rx + vx, ry + int(140 * scale)), (rx + vx + (6 if vx>0 else -6), ry + int(152 * scale))], fill=(225, 30, 30), width=3)
            
    elif prop_type == "dumbbell":
        vib = int(math.sin(t * 30) * 3)
        dx, dy = hx + vib, hy - int(10 * scale)
        draw.line([(dx - int(35 * scale), dy), (dx + int(35 * scale), dy)], fill=ink_color, width=int(8 * scale))
        draw.rectangle([dx - int(45 * scale), dy - int(25 * scale), dx - int(32 * scale), dy + int(25 * scale)], fill=(40, 40, 50), outline=ink_color, width=3)
        draw.rectangle([dx + int(32 * scale), dy - int(25 * scale), dx + int(45 * scale), dy + int(25 * scale)], fill=(40, 40, 50), outline=ink_color, width=3)
        draw.text((dx, dy - int(25 * scale)), "2.5 KG", fill=(220, 40, 40), font=font_tiny, anchor="mm")
        
    elif prop_type == "shaker":
        sx, sy = hx - int(12 * scale), hy - int(40 * scale)
        draw.polygon([(sx, sy), (sx + int(26 * scale), sy), (sx + int(22 * scale), sy + int(50 * scale)), (sx + int(4 * scale), sy + int(50 * scale))], fill=(245, 245, 250), outline=ink_color)
        draw.rectangle([sx + int(4 * scale), sy - int(12 * scale), sx + int(22 * scale), sy], fill=(40, 160, 220), outline=ink_color, width=2)
        draw.text((sx + int(13 * scale), sy + int(25 * scale)), "FIT", fill=(40, 160, 220), font=font_tiny, anchor="mm")
        
    elif prop_type == "laptop":
        lx, ly = hx - int(40 * scale), hy - int(20 * scale)
        draw.polygon([(lx, ly), (lx + int(75 * scale), ly), (lx + int(65 * scale), ly + int(22 * scale)), (lx - int(10 * scale), ly + int(22 * scale))], fill=(220, 225, 230), outline=ink_color, width=2)
        draw.polygon([(lx + int(5 * scale), ly - int(40 * scale)), (lx + int(70 * scale), ly - int(40 * scale)), (lx + int(75 * scale), ly), (lx, ly)], fill=(240, 248, 255), outline=ink_color, width=2)
        draw.line([(lx + int(18 * scale), ly - int(25 * scale)), (lx + int(55 * scale), ly - int(25 * scale))], fill=(40, 180, 80), width=2)
        draw.line([(lx + int(18 * scale), ly - int(15 * scale)), (lx + int(45 * scale), ly - int(15 * scale))], fill=(40, 180, 80), width=2)

    elif prop_type == "pillow":
        px, py = hx - int(40 * scale), hy - int(35 * scale)
        draw.rounded_rectangle([px, py, px + int(80 * scale), py + int(55 * scale)], radius=int(14 * scale), fill=(245, 250, 255), outline=ink_color, width=3)
        draw.arc([px + int(15 * scale), py + int(15 * scale), px + int(65 * scale), py + int(40 * scale)], start=20, end=160, fill=(180, 200, 220), width=2)

    elif prop_type == "broom":
        bx, by = hx - int(10 * scale), hy - int(60 * scale)
        draw.line([(bx, by), (bx - int(25 * scale), by + int(110 * scale))], fill=(180, 130, 70), width=int(5 * scale))
        pts = [
            (bx - int(25 * scale), by + int(100 * scale)),
            (bx - int(45 * scale), by + int(140 * scale)),
            (bx - int(10 * scale), by + int(140 * scale))
        ]
        draw.polygon(pts, fill=(220, 180, 100), outline=ink_color)
        draw.line([(bx - int(28 * scale), by + int(112 * scale)), (bx - int(18 * scale), by + int(112 * scale))], fill=(220, 40, 40), width=3)

    elif prop_type == "phone":
        ph_w = int(22 * scale)
        ph_h = int(38 * scale)
        px = hx - ph_w // 2
        py = hy - int(25 * scale)
        draw.rounded_rectangle([px, py, px + ph_w, py + ph_h], radius=int(4 * scale), fill=(30, 32, 40), outline=ink_color, width=2)
        draw.rectangle([px + 2, py + 4, px + ph_w - 2, py + ph_h - 6], fill=(220, 245, 255))
        draw.line([(px + 6, py + ph_h - 3), (px + ph_w - 6, py + ph_h - 3)], fill=(120, 120, 130), width=1)
        draw.ellipse([px + ph_w // 2 - 2, py + 1, px + ph_w // 2 + 2, py + 3], fill=(10, 10, 15))

    elif prop_type == "chai_cup":
        cx = hx - int(10 * scale)
        cy = hy - int(15 * scale)
        draw.polygon([(cx, cy), (cx + int(24 * scale), cy), (cx + int(18 * scale), cy + int(32 * scale)), (cx + int(6 * scale), cy + int(32 * scale))], fill=(240, 240, 245), outline=ink_color, width=2)
        draw.polygon([(cx + 2, cy + 8), (cx + int(22 * scale), cy + 8), (cx + int(17 * scale), cy + int(30 * scale)), (cx + int(7 * scale), cy + int(30 * scale))], fill=(185, 105, 50))
        steam_y = cy - int(10 * scale) - int(t * 15) % 15
        draw.arc([cx + 4, steam_y, cx + 14, steam_y + 12], start=200, end=340, fill=(150, 150, 160), width=2)
        draw.arc([cx + 12, steam_y - 6, cx + 22, steam_y + 6], start=180, end=320, fill=(150, 150, 160), width=2)

    elif prop_type == "samosa":
        sx = hx - int(15 * scale)
        sy = hy - int(20 * scale)
        draw.polygon([(sx, sy + int(30 * scale)), (sx + int(16 * scale), sy), (sx + int(32 * scale), sy + int(30 * scale))], fill=(235, 180, 85), outline=ink_color, width=2)

    elif prop_type == "newspaper":
        nx = hx - int(25 * scale)
        ny = hy - int(30 * scale)
        nw, nh = int(60 * scale), int(75 * scale)
        draw.rectangle([nx, ny, nx + nw, ny + nh], fill=(245, 245, 240), outline=ink_color, width=2)
        draw.line([(nx + nw//2, ny), (nx + nw//2, ny + nh)], fill=(180, 180, 190), width=1)
        draw.text((nx + nw//4, ny + 8), "DAINIK", fill=ink_color, font=font_tiny, anchor="mm")
        for ly in range(ny + 18, ny + nh - 6, 6):
            draw.line([(nx + 4, ly), (nx + nw - 4, ly)], fill=(120, 120, 130), width=1)

    elif prop_type == "pen":
        draw.line([(hx - 10, hy - 25), (hx + 5, hy + 5)], fill=(40, 120, 220), width=3)
        draw.polygon([(hx + 5, hy + 5), (hx + 8, hy + 9), (hx + 3, hy + 7)], fill=ink_color)

def draw_doodle_stickman(draw, x, y, scale=1.0, is_girl=False, is_boy2=False, character_type="boy", pose='idle', is_speaking=False, mouth_open=0.0, is_blink=False, emotion='none', prop='none', t=0.0, boil_seed=0, look_dx=0, look_dy=0, eyebrow='normal', is_walking=False, walk_cycle=0.0):
    char_type = character_type
    if is_girl:
        char_type = "girl"
    elif is_boy2:
        char_type = "boy2"

    head_r = int(45 * scale)
    torso_len = int(120 * scale)
    limb_len = int(75 * scale)
    
    if is_walking:
        bounce_y = int(abs(math.sin(walk_cycle * 2)) * 8)
    else:
        bounce_amp = 4 if is_speaking else 2
        bounce_y = int(math.sin(t * 8) * bounce_amp)
        
    cy = y - bounce_y if is_walking else y + bounce_y
    
    jx = int(get_line_jitter(boil_seed + (10 if char_type in ["girl", "mummy"] else 1), 1.2))
    jy = int(get_line_jitter(boil_seed + (20 if char_type in ["girl", "mummy"] else 2), 1.2))
    
    head_center = (x + jx, cy - torso_len - head_r + jy)
    neck = (x + jx, cy - torso_len + jy)
    pelvis = (x + jx, cy + jy)
    
    ink_color = (22, 22, 28)
    line_w = max(4, int(5 * scale))
    
    # Torso
    draw.line([neck, pelvis], fill=ink_color, width=line_w)
    
    # Clothing / Torso specifics
    if char_type == "girl":
        d_top_w = int(10 * scale)
        d_bot_w = int(38 * scale)
        dress_pts = [
            (neck[0] - d_top_w, neck[1] + int(30 * scale)),
            (neck[0] + d_top_w, neck[1] + int(30 * scale)),
            (pelvis[0] + d_bot_w, pelvis[1] + int(10 * scale)),
            (pelvis[0] - d_bot_w, pelvis[1] + int(10 * scale))
        ]
        draw.polygon(dress_pts, fill=(253, 253, 250), outline=ink_color)
        draw.line([(pelvis[0] - d_bot_w, pelvis[1] + int(10 * scale)), (pelvis[0] + d_bot_w, pelvis[1] + int(10 * scale))], fill=ink_color, width=line_w)
    elif char_type == "mummy":
        d_top_w = int(12 * scale)
        d_bot_w = int(42 * scale)
        saree_pts = [
            (neck[0] - d_top_w, neck[1] + int(25 * scale)),
            (neck[0] + d_top_w, neck[1] + int(25 * scale)),
            (pelvis[0] + d_bot_w, pelvis[1] + int(12 * scale)),
            (pelvis[0] - d_bot_w, pelvis[1] + int(12 * scale))
        ]
        draw.polygon(saree_pts, fill=(255, 250, 245), outline=ink_color)
        draw.line([(neck[0] - int(10 * scale), neck[1] + int(15 * scale)), (pelvis[0] + int(32 * scale), pelvis[1] - int(5 * scale))], fill=(225, 40, 40), width=int(5 * scale))
        draw.line([(pelvis[0] - d_bot_w, pelvis[1] + int(12 * scale)), (pelvis[0] + d_bot_w, pelvis[1] + int(12 * scale))], fill=(225, 40, 40), width=int(4 * scale))
    elif char_type == "boss":
        tie_pts = [
            (neck[0] - int(4 * scale), neck[1] + int(6 * scale)),
            (neck[0] + int(4 * scale), neck[1] + int(6 * scale)),
            (neck[0] + int(6 * scale), neck[1] + int(40 * scale)),
            (neck[0], neck[1] + int(52 * scale)),
            (neck[0] - int(6 * scale), neck[1] + int(40 * scale))
        ]
        draw.polygon(tie_pts, fill=(40, 100, 220), outline=ink_color)
    elif char_type == "dad":
        pk_x = neck[0] + int(8 * scale)
        pk_y = neck[1] + int(25 * scale)
        draw.rectangle([pk_x, pk_y, pk_x + int(14 * scale), pk_y + int(18 * scale)], outline=ink_color, width=2)
        draw.line([(pk_x + int(4 * scale), pk_y - int(4 * scale)), (pk_x + int(4 * scale), pk_y + int(6 * scale))], fill=(220, 40, 40), width=2)
    elif char_type == "boy":
        bx_x = neck[0] - int(8 * scale)
        bx_y = neck[1] + int(25 * scale)
        draw.ellipse([bx_x - 3, bx_y - 3, bx_x + 3, bx_y + 3], fill=(255, 215, 0))
    elif char_type == "boy2":
        bx_x = neck[0] - int(8 * scale)
        bx_y = neck[1] + int(25 * scale)
        draw.ellipse([bx_x - 3, bx_y - 3, bx_x + 3, bx_y + 3], fill=(40, 160, 240))
    
    # Legs (Standing vs Walking)
    hip_w = int(12 * scale) if is_girl else int(10 * scale)
    l_hip = (pelvis[0] - hip_w, pelvis[1] + (int(10 * scale) if is_girl else 0))
    r_hip = (pelvis[0] + hip_w, pelvis[1] + (int(10 * scale) if is_girl else 0))
    
    if is_walking:
        thigh_len = int(limb_len * 0.9)
        shin_len = int(limb_len * 0.9)
        a1_l = math.sin(walk_cycle) * 0.55
        k_bend_l = max(0.0, -math.cos(walk_cycle)) * 0.75
        l_knee = (int(l_hip[0] + thigh_len * math.sin(a1_l)), int(l_hip[1] + thigh_len * math.cos(a1_l)))
        l_foot = (int(l_knee[0] + shin_len * math.sin(a1_l - k_bend_l)), int(l_knee[1] + shin_len * math.cos(a1_l - k_bend_l)))
        
        a1_r = -math.sin(walk_cycle) * 0.55
        k_bend_r = max(0.0, math.cos(walk_cycle)) * 0.75
        r_knee = (int(r_hip[0] + thigh_len * math.sin(a1_r)), int(r_hip[1] + thigh_len * math.cos(a1_r)))
        r_foot = (int(r_knee[0] + shin_len * math.sin(a1_r - k_bend_r)), int(r_knee[1] + shin_len * math.cos(a1_r - k_bend_r)))
    else:
        l_knee = (l_hip[0] - int(8 * scale), l_hip[1] + limb_len)
        l_foot = (l_knee[0] - int(14 * scale), l_knee[1] + limb_len)
        r_knee = (r_hip[0] + int(8 * scale), r_hip[1] + limb_len)
        r_foot = (r_knee[0] + int(14 * scale), r_knee[1] + limb_len)
    
    draw.line([l_hip, l_knee, l_foot], fill=ink_color, width=line_w)
    draw.line([r_hip, r_knee, r_foot], fill=ink_color, width=line_w)
    
    # Arms & Poses
    sh_y = neck[1] + int(12 * scale)
    l_sh = (neck[0] - int(14 * scale), sh_y)
    r_sh = (neck[0] + int(14 * scale), sh_y)
    
    if is_walking:
        arm_len = int(75 * scale)
        arm_ang_l = -math.sin(walk_cycle) * 0.5
        arm_ang_r = math.sin(walk_cycle) * 0.5
        l_hand = (int(l_sh[0] + arm_len * math.sin(arm_ang_l)), int(l_sh[1] + arm_len * math.cos(arm_ang_l)))
        r_hand = (int(r_sh[0] + arm_len * math.sin(arm_ang_r)), int(r_sh[1] + arm_len * math.cos(arm_ang_r)))
    elif pose == 'dizzy_hit':
        # Hands clutching head after hit!
        l_el = (l_sh[0] - int(35 * scale), l_sh[1] - int(30 * scale))
        l_hand = (head_center[0] - head_r + 6, head_center[1] - int(10 * scale))
        r_el = (r_sh[0] + int(35 * scale), r_sh[1] - int(30 * scale))
        r_hand = (head_center[0] + head_r - 6, head_center[1] - int(10 * scale))
    elif pose == 'shock':
        l_el = (l_sh[0] - int(40 * scale), l_sh[1] - int(45 * scale))
        l_hand = (head_center[0] - head_r + 4, head_center[1] - int(10 * scale))
        r_el = (r_sh[0] + int(40 * scale), r_sh[1] - int(45 * scale))
        r_hand = (head_center[0] + head_r - 4, head_center[1] - int(10 * scale))
    elif pose == 'hands_on_hips':
        l_el = (l_sh[0] - int(40 * scale), l_sh[1] + int(35 * scale))
        l_hand = (l_hip[0] - int(8 * scale), l_hip[1] - int(10 * scale))
        r_el = (r_sh[0] + int(40 * scale), r_sh[1] + int(35 * scale))
        r_hand = (r_hip[0] + int(8 * scale), r_hip[1] - int(10 * scale))
    elif pose == 'shrug':
        l_el = (l_sh[0] - int(45 * scale), l_sh[1] + int(20 * scale))
        l_hand = (l_el[0] - int(20 * scale), l_el[1] - int(25 * scale))
        r_el = (r_sh[0] + int(45 * scale), r_sh[1] + int(20 * scale))
        r_hand = (r_el[0] + int(20 * scale), r_el[1] - int(25 * scale))
    else: # talk_gesture
        g_wave = math.sin(t * 7) * 8 if is_speaking else 0
        l_el = (l_sh[0] - int(30 * scale), l_sh[1] + int(35 * scale))
        l_hand = (l_el[0] - int(15 * scale), l_el[1] + int(35 * scale))
        r_el = (r_sh[0] + int(32 * scale), r_sh[1] + int(22 * scale))
        r_hand = (r_el[0] + int(25 * scale), r_el[1] - int(28 * scale) + int(g_wave))
        
    draw.line([l_sh, l_hand] if is_walking else [l_sh, l_el, l_hand], fill=ink_color, width=line_w)
    draw.line([r_sh, r_hand] if is_walking else [r_sh, r_el, r_hand], fill=ink_color, width=line_w)
    
    # Handheld Prop
    if prop != "none" and prop != "flying_chappal":
        p_hand = r_hand if pose != 'shock' else (r_sh[0] + int(60 * scale), r_sh[1])
        draw_prop(draw, prop, p_hand, scale=scale, t=t)
        
    # Head
    hx, hy = head_center
    draw.ellipse([hx - head_r, hy - head_r, hx + head_r, hy + head_r], fill=(253, 253, 250), outline=ink_color, width=line_w)
    eye_y = hy - int(6 * scale)
    mouth_y = hy + int(18 * scale)
    
    # Hair / Cap / Accessories
    if char_type == "girl":
        draw.arc([hx - head_r - 2, hy - head_r - 4, hx + head_r + 2, hy + 2], start=170, end=360, fill=ink_color, width=int(6 * scale))
        draw.line([(hx + int(32 * scale), hy - int(15 * scale)), (hx + int(52 * scale), hy + int(25 * scale))], fill=ink_color, width=int(6 * scale))
        draw.ellipse([hx + int(32 * scale), hy - int(18 * scale), hx + int(42 * scale), hy - int(8 * scale)], fill=(255, 42, 133))
    elif char_type == "mummy":
        draw.arc([hx - head_r - 2, hy - head_r - 4, hx + head_r + 2, hy + 2], start=170, end=360, fill=ink_color, width=int(6 * scale))
        bun_x, bun_y = hx + head_r + int(6 * scale), hy - int(18 * scale)
        draw.ellipse([bun_x - int(13 * scale), bun_y - int(13 * scale), bun_x + int(13 * scale), bun_y + int(13 * scale)], fill=ink_color)
        draw.ellipse([hx - int(3 * scale), hy - int(14 * scale) - int(3 * scale), hx + int(3 * scale), hy - int(14 * scale) + int(3 * scale)], fill=(225, 30, 30))
    elif char_type == "boss":
        draw.arc([hx - head_r, hy - head_r - int(2 * scale), hx + head_r, hy - int(12 * scale)], start=180, end=360, fill=ink_color, width=int(5 * scale))
        draw.rectangle([hx - int(24 * scale), eye_y - int(10 * scale), hx - int(8 * scale), eye_y + int(6 * scale)], outline=ink_color, width=2)
        draw.rectangle([hx + int(8 * scale), eye_y - int(10 * scale), hx + int(24 * scale), eye_y + int(6 * scale)], outline=ink_color, width=2)
        draw.line([(hx - int(8 * scale), eye_y - int(2 * scale)), (hx + int(8 * scale), eye_y - int(2 * scale))], fill=ink_color, width=2)
    elif char_type == "dad":
        draw.arc([hx - head_r, hy - head_r - int(2 * scale), hx + head_r, hy - int(12 * scale)], start=180, end=360, fill=ink_color, width=int(4 * scale))
        draw.ellipse([hx - int(24 * scale), eye_y - int(10 * scale), hx - int(8 * scale), eye_y + int(6 * scale)], outline=ink_color, width=2)
        draw.ellipse([hx + int(8 * scale), eye_y - int(10 * scale), hx + int(24 * scale), eye_y + int(6 * scale)], outline=ink_color, width=2)
        draw.line([(hx - int(8 * scale), eye_y - int(2 * scale)), (hx + int(8 * scale), eye_y - int(2 * scale))], fill=ink_color, width=2)
        draw.arc([hx - int(16 * scale), mouth_y - int(18 * scale), hx, mouth_y - int(4 * scale)], start=0, end=180, fill=ink_color, width=int(4 * scale))
        draw.arc([hx, mouth_y - int(18 * scale), hx + int(16 * scale), mouth_y - int(4 * scale)], start=0, end=180, fill=ink_color, width=int(4 * scale))
    elif char_type == "boy2":
        draw.arc([hx - head_r, hy - head_r - int(4 * scale), hx + head_r, hy - int(10 * scale)], start=180, end=360, fill=(40, 140, 220), width=int(14 * scale))
        draw.arc([hx - head_r, hy - head_r - int(4 * scale), hx + head_r, hy - int(10 * scale)], start=180, end=360, fill=ink_color, width=int(3 * scale))
        bx1 = hx - head_r - int(14 * scale)
        by1 = hy - int(24 * scale)
        bx2 = hx - head_r + int(6 * scale)
        by2 = hy - int(16 * scale)
        draw.line([(bx1, by1), (bx2, by2)], fill=ink_color, width=int(6 * scale))
    else: # boy
        draw.line([(hx - 15, hy - head_r), (hx - 10, hy - head_r - int(14 * scale)), (hx - 2, hy - head_r)], fill=ink_color, width=int(4 * scale))
        draw.line([(hx + 5, hy - head_r), (hx + 10, hy - head_r - int(14 * scale)), (hx + 20, hy - head_r)], fill=ink_color, width=int(4 * scale))
        
    # Eyebrows
    eye_y = hy - int(6 * scale)
    brow_y = eye_y - int(10 * scale)
    if eyebrow == 'angry':
        draw.line([(hx - int(24 * scale), brow_y - int(4 * scale)), (hx - int(8 * scale), brow_y + int(4 * scale))], fill=ink_color, width=int(3 * scale))
        draw.line([(hx + int(24 * scale), brow_y - int(4 * scale)), (hx + int(8 * scale), brow_y + int(4 * scale))], fill=ink_color, width=int(3 * scale))
    elif eyebrow == 'shock':
        draw.arc([hx - int(26 * scale), brow_y - int(10 * scale), hx - int(8 * scale), brow_y + int(4 * scale)], start=180, end=360, fill=ink_color, width=int(3 * scale))
        draw.arc([hx + int(8 * scale), brow_y - int(10 * scale), hx + int(26 * scale), brow_y + int(4 * scale)], start=180, end=360, fill=ink_color, width=int(3 * scale))
    elif eyebrow == 'smirk':
        draw.arc([hx - int(24 * scale), brow_y - int(8 * scale), hx - int(8 * scale), brow_y + int(4 * scale)], start=180, end=360, fill=ink_color, width=int(3 * scale))
        draw.line([(hx + int(8 * scale), brow_y), (hx + int(24 * scale), brow_y)], fill=ink_color, width=int(3 * scale))
    else:
        draw.arc([hx - int(22 * scale), brow_y - int(4 * scale), hx - int(10 * scale), brow_y + int(4 * scale)], start=180, end=360, fill=ink_color, width=int(2 * scale))
        draw.arc([hx + int(10 * scale), brow_y - int(4 * scale), hx + int(22 * scale), brow_y + int(4 * scale)], start=180, end=360, fill=ink_color, width=int(2 * scale))

    # Eyes (Spiral dizzy vs Blinking vs Normal)
    if pose == 'dizzy_hit' and t > 0.8:
        draw_spiral_eye(draw, hx - int(16 * scale), eye_y, r=int(12 * scale))
        draw_spiral_eye(draw, hx + int(16 * scale), eye_y, r=int(12 * scale))
    elif is_blink:
        draw.line([(hx - int(24 * scale), eye_y), (hx - int(10 * scale), eye_y)], fill=ink_color, width=line_w)
        draw.line([(hx + int(10 * scale), eye_y), (hx + int(24 * scale), eye_y)], fill=ink_color, width=line_w)
    elif pose == 'shock':
        draw.ellipse([hx - int(28 * scale), eye_y - int(16 * scale), hx - int(6 * scale), eye_y + int(10 * scale)], fill=(255, 255, 255), outline=ink_color, width=3)
        draw.ellipse([hx + int(6 * scale), eye_y - int(16 * scale), hx + int(28 * scale), eye_y + int(10 * scale)], fill=(255, 255, 255), outline=ink_color, width=3)
        draw.ellipse([hx - int(19 * scale) + look_dx, eye_y - int(5 * scale) + look_dy, hx - int(13 * scale) + look_dx, eye_y + int(3 * scale) + look_dy], fill=ink_color)
        draw.ellipse([hx + int(13 * scale) + look_dx, eye_y - int(5 * scale) + look_dy, hx + int(19 * scale) + look_dx, eye_y + int(3 * scale) + look_dy], fill=ink_color)
    else:
        draw.ellipse([hx - int(22 * scale) + look_dx, eye_y - int(14 * scale) + look_dy, hx - int(10 * scale) + look_dx, eye_y + int(4 * scale) + look_dy], fill=ink_color)
        draw.ellipse([hx + int(10 * scale) + look_dx, eye_y - int(14 * scale) + look_dy, hx + int(22 * scale) + look_dx, eye_y + int(4 * scale) + look_dy], fill=ink_color)
        
    # Mouth (RMS Lip Sync)
    mouth_y = hy + int(18 * scale)
    if is_speaking and mouth_open > 0.08:
        m_h = int(24 * mouth_open * scale)
        m_w = int((12 + 6 * mouth_open) * scale)
        draw.ellipse([hx - m_w, mouth_y - m_h, hx + m_w, mouth_y + m_h], fill=(30, 20, 25), outline=ink_color, width=3)
        if m_h > 5:
            draw.ellipse([hx - int(m_w * 0.6), mouth_y, hx + int(m_w * 0.6), mouth_y + m_h - 2], fill=(255, 100, 130))
    elif is_girl and not is_speaking:
        draw.arc([hx - int(12 * scale), mouth_y - int(5 * scale), hx + int(12 * scale), mouth_y + int(12 * scale)], start=20, end=160, fill=ink_color, width=int(3 * scale))
    else:
        draw.arc([hx - int(12 * scale), mouth_y - int(10 * scale), hx + int(12 * scale), mouth_y + int(8 * scale)], start=20, end=160, fill=ink_color, width=int(3 * scale))
        
    if emotion == 'sweat':
        sw_y = hy - int(35 * scale) + int(t * 20) % 25
        sw_x = hx + int(52 * scale)
        draw.polygon([(sw_x, sw_y), (sw_x - 7, sw_y + 16), (sw_x + 7, sw_y + 16)], fill=(70, 180, 255))
        draw.ellipse([sw_x - 7, sw_y + 8, sw_x + 7, sw_y + 22], fill=(70, 180, 255))

    # Circling stars after chappal hit!
    if pose == 'dizzy_hit' and t > 0.8:
        for i in range(3):
            star_ang = (t * 8) + (i * 2 * math.pi / 3)
            sx = hx + int(math.cos(star_ang) * 48 * scale)
            sy = hy - int(55 * scale) + int(math.sin(star_ang) * 16 * scale)
            draw_doodle_star(draw, sx, sy, r=int(12 * scale))

def draw_doodle_environment(draw, w, h, floor_y, theme="shopping", t=0.0):
    ink_color = (60, 60, 70)
    
    # 1. Living Ceiling Fan
    draw_ceiling_fan(draw, 360, 190, t=t)
    
    if theme == "home_mummy":
        # Bed Headboard on Left
        draw.rectangle([50, 500, 180, floor_y], fill=(245, 240, 230), outline=ink_color, width=3)
        draw.line([(50, 540), (180, 540)], fill=ink_color, width=2)
        draw.line([(50, 600), (180, 600)], fill=ink_color, width=2)
        
        # Vibrating Alarm Clock on Right
        ax, ay = 600, 320
        vib = int(math.sin(t * 30) * 3)
        draw.ellipse([ax - 35 + vib, ay - 35, ax + 35 + vib, ay + 35], fill=(255, 255, 255), outline=ink_color, width=3)
        draw.ellipse([ax - 38 + vib, ay - 42, ax - 18 + vib, ay - 22], fill=(220, 40, 40), outline=ink_color, width=2)
        draw.ellipse([ax + 18 + vib, ay - 42, ax + 38 + vib, ay - 22], fill=(220, 40, 40), outline=ink_color, width=2)
        draw.arc([ax - 50 + vib, ay - 50, ax + 50 + vib, ay + 50], start=200, end=250, fill=ink_color, width=2)
        draw.arc([ax - 50 + vib, ay - 50, ax + 50 + vib, ay + 50], start=290, end=340, fill=ink_color, width=2)
    else:
        # Default store/room background
        draw.rectangle([60, 460, 180, floor_y], fill=(255, 255, 255), outline=ink_color, width=3)
        draw.line([(60, 550), (180, 550)], fill=ink_color, width=2)
        draw.line([(60, 640), (180, 640)], fill=ink_color, width=2)
        draw.rounded_rectangle([80, 500, 110, 545], radius=4, fill=(255, 230, 240), outline=ink_color, width=2)
        draw.rounded_rectangle([130, 490, 160, 545], radius=4, fill=(230, 245, 255), outline=ink_color, width=2)

    # Floor Line & Contact Shadow
    draw.line([(30, floor_y), (690, floor_y)], fill=(185, 185, 195), width=3)
    draw.ellipse([300, floor_y - 5, 420, floor_y + 12], fill=(232, 232, 238))

def render_pov_frame(t, duration, hook_text, dialogue_text, words_data, norm_rms, speaker="boy", shot_type="two_shot", pose="talk_gesture", emotion="none", prop="none", is_punchline=False, theme="home_mummy", action="none", duo_type="boy_and_girl"):
    w, h = 720, 1280
    boil_seed = int(t * 12)
    
    canvas = Image.new("RGB", (w, h), (252, 252, 248))
    draw = ImageDraw.Draw(canvas)
    
    # Notebook paper lines
    draw.line([(32, 0), (32, h)], fill=(255, 210, 210), width=2)
    for y_line in range(160, 1020, 48):
        draw.line([(0, y_line), (w, y_line)], fill=(238, 242, 250), width=1)
        
    shake_x, shake_y = 0, 0
    # Dramatic screen shake on chappal hit or punchline
    if (action == "chappal_impact" and 0.8 <= t <= 1.5) or (is_punchline and t > max(0.5, duration - 1.2)):
        decay = max(0.0, 1.0 - (t - 0.8) / 0.7) if action == "chappal_impact" else 1.0
        shake_mag = int(16 * decay)
        if shake_mag > 0:
            rng = np.random.RandomState(int(t * 30))
            shake_x = rng.randint(-shake_mag, shake_mag + 1)
            shake_y = rng.randint(-shake_mag, shake_mag + 1)
            
    try:
        font_hook = ImageFont.truetype("arialbd.ttf", 28)
        font_badge = ImageFont.truetype("arialbd.ttf", 24)
        font_sub = ImageFont.truetype("arialbd.ttf", 34)
    except:
        font_hook = ImageFont.load_default()
        font_badge = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    floor_y = 750 + shake_y
    draw_doodle_environment(draw, w, h, floor_y, theme=theme, t=t)
    
    # Cute pet Tommy on the floor!
    dog_emotion = 'shock' if (action in ['chappal_impact', 'whistle_shock'] or pose == 'shock') else 'idle'
    draw_doodle_dog(draw, 610 + shake_x, floor_y - 25, scale=1.1, t=t, emotion=dog_emotion)
    
    # Top POV Hook Pill with Washi Tape Effect (Clean text without missing emoji glyphs)
    clean_hook = re.sub(r'[^\w\s\.,!\?\'\"\:\-₹]', '', hook_text).strip()
    h_box_w = min(640, draw.textbbox((0, 0), clean_hook, font=font_hook)[2] + 60)
    h_box_x1 = (w - h_box_w) // 2 + shake_x
    draw.rounded_rectangle([h_box_x1, 55, h_box_x1 + h_box_w, 125], radius=16, fill=(248, 248, 252), outline=(22, 22, 28), width=3)
    draw.polygon([(h_box_x1 - 12, 50), (h_box_x1 + 35, 45), (h_box_x1 + 25, 75), (h_box_x1 - 22, 80)], fill=(255, 225, 105))
    draw.polygon([(h_box_x1 + h_box_w - 25, 45), (h_box_x1 + h_box_w + 22, 50), (h_box_x1 + h_box_w + 12, 80), (h_box_x1 + h_box_w - 35, 75)], fill=(255, 225, 105))
    draw.text((w // 2 + shake_x, 90), clean_hook, fill=(22, 22, 28), font=font_hook, anchor="mm")
    
    # Real-Time Mouth Opening
    fps = 24
    frame_idx = min(int(t * fps), len(norm_rms) - 1) if len(norm_rms) > 0 else 0
    vol = norm_rms[frame_idx] if len(norm_rms) > 0 else 0.0
    mouth_open = min(1.0, vol * 1.5)
    
    # Blinking
    blink_cycle = t % 2.8
    is_blink = (2.5 <= blink_cycle <= 2.68)
    
    eyebrow_type = 'angry' if emotion == 'angry' else ('shock' if pose in ['shock', 'dizzy_hit'] else ('smirk' if speaker in ['girl', 'boy2'] else 'normal'))
    
    # Dynamic Walking into Scene (Entrance)
    is_walking = (action == "walk_in" and t < 1.8)
    walk_cycle = t * 9.0
    if is_walking:
        prog = min(1.0, t / 1.8)
        char_x = int(-80 + (360 - (-80)) * prog)
    else:
        char_x = 360 + shake_x
        
    # Close-up vs Two-Shot
    if shot_type.endswith("_close"):
        target_role = shot_type.replace("_close", "")
        if target_role not in ["boy", "boy2", "girl", "mummy", "boss", "dad"]:
            target_role = speaker
        elif target_role == "boy" and speaker in ["boy2", "mummy", "boss", "dad", "girl"]:
            target_role = speaker
            
        scale = 1.45
        draw_doodle_stickman(
            draw, x=char_x, y=floor_y - 10, scale=scale, 
            character_type=target_role, pose=pose, is_speaking=True, 
            mouth_open=mouth_open, is_blink=is_blink, emotion=emotion, prop=prop,
            t=t, boil_seed=boil_seed, look_dx=0, look_dy=0, eyebrow=eyebrow_type,
            is_walking=is_walking, walk_cycle=walk_cycle
        )
    else: # two_shot
        scale = 1.15
        if duo_type == "mummy_and_boy":
            left_char, right_char = "mummy", "boy"
        elif duo_type == "boss_and_employee":
            left_char, right_char = "boss", "boy"
        elif duo_type == "dad_and_boy":
            left_char, right_char = "dad", "boy"
        elif duo_type == "boy_and_boy2" or speaker == "boy2":
            left_char, right_char = "boy", "boy2"
        else: # boy_and_girl
            left_char, right_char = "boy", "girl"
            
        left_active = (speaker == left_char)
        right_active = (speaker == right_char)
        
        left_pose = pose if left_active else ("idle" if not is_punchline else "shrug")
        right_pose = pose if right_active else ("idle" if not is_punchline else "pleading")
        
        left_emotion = emotion if left_active else ("sweat" if (is_punchline and not left_active) else "none")
        right_emotion = emotion if right_active else "none"
        
        left_prop = prop if left_active else "none"
        right_prop = prop if right_active else "none"
        
        # Left Character
        draw_doodle_stickman(
            draw, x=220 + shake_x, y=floor_y - 5, scale=scale, 
            character_type=left_char, pose=left_pose, is_speaking=left_active, 
            mouth_open=(mouth_open if left_active else 0.0), 
            is_blink=is_blink, emotion=left_emotion, prop=left_prop,
            t=t, boil_seed=boil_seed, look_dx=int(5 * scale), look_dy=0, 
            eyebrow=('shock' if (is_punchline and not left_active) else eyebrow_type)
        )
        
        # Right Character
        draw_doodle_stickman(
            draw, x=500 + shake_x, y=floor_y - 5, scale=scale, 
            character_type=right_char, pose=right_pose, is_speaking=right_active, 
            mouth_open=(mouth_open if right_active else 0.0), 
            is_blink=is_blink, emotion=right_emotion, prop=right_prop,
            t=t, boil_seed=boil_seed, look_dx=-int(5 * scale), look_dy=0, 
            eyebrow=('smirk' if right_active else 'normal')
        )

    # Flying Chappal Physics & Impact Animation
    if action == "chappal_impact":
        target_head = (char_x, floor_y - int(120 * 1.45) - int(45 * 1.45) - 10)
        if t < 0.8:
            prog = t / 0.8
            # Trajectory curve from top-left (-50, 150) to head
            cur_cx = int(-50 + (target_head[0] - (-50)) * prog)
            cur_cy = int(120 + (target_head[1] - 120) * prog - math.sin(prog * math.pi) * 80)
            spin_ang = int(t * 1440)
            chappal_img = get_chappal_image(spin_ang, scale=1.1)
            canvas.paste(chappal_img, (cur_cx - chappal_img.width // 2, cur_cy - chappal_img.height // 2), chappal_img)
        elif 0.8 <= t <= 1.4:
            # Comic impact explosion lines at head
            for i in range(8):
                ang = i * math.pi / 4
                x1 = target_head[0] + int(20 * math.cos(ang))
                y1 = target_head[1] + int(20 * math.sin(ang))
                x2 = target_head[0] + int(50 * math.cos(ang))
                y2 = target_head[1] + int(50 * math.sin(ang))
                draw.line([(x1, y1), (x2, y2)], fill=(220, 40, 40), width=3)
            # Chappal falls down bouncing
            fall_prog = min(1.0, (t - 0.8) / 0.6)
            fall_x = int(target_head[0] + 40 + fall_prog * 80)
            fall_y = int(target_head[1] + fall_prog * (floor_y - target_head[1]))
            chappal_img = get_chappal_image(int(fall_prog * 180), scale=0.9)
            canvas.paste(chappal_img, (fall_x, fall_y - 20), chappal_img)
    elif action == "whistle_shock" and 0.4 <= t <= 2.0:
        wx, wy = char_x + 50, floor_y - 240
        for i, r in enumerate([16, 24, 32]):
            draw.ellipse([wx - r + i*14, wy - r - i*16, wx + r + i*14, wy + r - i*16], fill=(245, 248, 255), outline=(22, 22, 28), width=2)
        draw.text((wx + 65, wy - 55), "SEETI!!", fill=(220, 40, 40), font=font_badge, anchor="mm")
        
    spk_cfg = VOICE_CONFIG.get(speaker, VOICE_CONFIG["boy"])
    badge_label = f"●  {spk_cfg['label']}  ●"
    badge_w = 200
    badge_h = 42
    badge_x = (w - badge_w) // 2 + shake_x
    badge_y = floor_y + 110
    
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=21, fill=(20, 20, 26), outline=spk_cfg["color"], width=2)
    draw.text((w // 2 + shake_x, badge_y + badge_h // 2), badge_label, fill=spk_cfg["color"], font=font_badge, anchor="mm")
    
    words = dialogue_text.split()
    lines = []
    cur_line = []
    for wd in words:
        test_line = cur_line + [wd]
        w_px = sum(draw.textbbox((0, 0), x, font=font_sub)[2] for x in test_line) + (len(test_line) - 1) * 10
        if w_px > 600 and cur_line:
            lines.append(cur_line)
            cur_line = [wd]
        else:
            cur_line.append(wd)
    if cur_line:
        lines.append(cur_line)
        
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
        
    line_height = 50
    total_text_h = len(lines) * line_height
    sub_y1 = badge_y + badge_h + 20
    sub_y2 = sub_y1 + total_text_h + 38
    
    draw.rounded_rectangle([36 + shake_x, sub_y1, 684 + shake_x, sub_y2], radius=20, fill=(18, 18, 24), outline=spk_cfg["color"], width=2)
    
    t_y = sub_y1 + 19
    w_counter = 0
    space_w = draw.textbbox((0, 0), " ", font=font_sub)[2]
    
    for line in lines:
        line_w = sum(draw.textbbox((0, 0), word, font=font_sub)[2] for word in line) + space_w * (len(line) - 1)
        cur_x = (w - line_w) // 2 + shake_x
        
        for word in line:
            w_bbox = draw.textbbox((0, 0), word, font=font_sub)
            word_w = w_bbox[2] - w_bbox[0]
            
            if w_counter == active_idx:
                color = spk_cfg["color"]
            elif w_counter < active_idx:
                color = (255, 255, 255)
            else:
                color = (130, 130, 138)
                
            draw.text((cur_x + 2, t_y + 2), word, font=font_sub, fill=(0, 0, 0))
            draw.text((cur_x, t_y), word, font=font_sub, fill=color)
            
            cur_x += word_w + space_w
            w_counter += 1
            
        t_y += line_height

    # Dynamic Camera Zoom & Punch-in
    zoom = 1.0
    if action == "chappal_impact" and t >= 0.8:
        zoom = 1.15
    elif is_punchline and t > 0.4:
        zoom = 1.0 + 0.12 * min(1.0, (t - 0.4) / 1.5)
    elif pose == 'shock':
        zoom = 1.0 + 0.10 * min(1.0, t / 0.8)

    if zoom > 1.005:
        crop_w = int(w / zoom)
        crop_h = int(h / zoom)
        focus_x = char_x if shot_type != "two_shot" else (220 if speaker == "boy" else 500)
        focus_y = floor_y - 180
        left = max(0, min(w - crop_w, int(focus_x - crop_w / 2)))
        top = max(0, min(h - crop_h, int(focus_y - crop_h / 2)))
        canvas = canvas.crop((left, top, left + crop_w, top + crop_h)).resize((w, h), Image.Resampling.BILINEAR)
        
    return np.array(canvas)

def generate_pov_script(topic):
    print(f"[*] Generating Viral POV Doodle Script for topic: '{topic}' via DeepSeek...")
    try:
        import urllib.request
        import websockets
        import asyncio

        def _get_deepseek_ws():
            with urllib.request.urlopen("http://127.0.0.1:9222/json", timeout=3) as r:
                tabs = json.loads(r.read())
            for t in tabs:
                if "chat.deepseek.com" in t.get("url", ""):
                    return t["webSocketDebuggerUrl"]
            return None

        ws_url = _get_deepseek_ws()
        if not ws_url:
            raise RuntimeError("DeepSeek tab not found on port 9222")

        prompt = f"""You are the Master Director of viral 2D Stickman POV Shorts.
Topic: '{topic}'

Analyze the topic and choose the best matching characters, theme, props, emotions, and visual gags!
Available Director Options:
1. duo_type:
   - "boy_and_boy2" (Best for: college friends, roommate fights, lazy boys, phone excuses)
   - "mummy_and_boy" (Best for: waking up late, cleaning room, food, exam tension, flying chappal)
   - "boss_and_employee" (Best for: office work, appraisal, asking for leave, salary)
   - "boy_and_girl" (Best for: shopping, restaurant bill, late replies, relationship)
   - "dad_and_boy" (Best for: marks, pocket money, career advice)
2. theme:
   - "home_mummy", "bedroom_morning", "office_desk", "street_food", "exam_hall"
3. speaker per scene: "boy", "boy2", "girl", "mummy", "boss", "dad"
4. shot_type per scene: "boy_close", "girl_close", "mummy_close", "boss_close", "dad_close", "two_shot"
5. prop per scene: "phone", "chai_cup", "samosa", "newspaper", "pillow", "laptop", "dumbbell", "broom", "pen", "none"
6. action per scene: "walk_in", "chappal_impact", "whistle_shock", "none"
7. pose per scene: "talk_gesture", "hands_on_hips", "shock", "pleading", "shrug", "dizzy_hit"
8. emotion per scene: "none", "shock", "sweat", "angry"

Write a hilarious, fast-paced 4-scene dialogue banter tailored specifically to this topic.
Format your reply strictly as a single JSON object with this exact structure:
{{
  "title": "Viral Clicky Hindi Title with 1 emoji #shorts #viral",
  "hook": "POV: Relatable Hook in Hinglish",
  "duo_type": "boy_and_boy2",
  "theme": "bedroom_morning",
  "description": "Short funny description with tags #shorts #comedy #doodle #animation",
  "tags": ["shorts", "comedy", "funny", "relatable", "stickman", "doodle"],
  "scenes": [
    {{
      "scene": 1,
      "speaker": "boy",
      "shot_type": "boy_close",
      "spoken_hindi": "शुद्ध हिंदी देवनागरी में जो आवाज़ बोलेगी (Natural, punchy spoken Hindi)",
      "dialogue": "Exact dialogue in clean Hinglish for subtitles",
      "pose": "talk_gesture",
      "prop": "phone",
      "action": "walk_in",
      "emotion": "none",
      "is_punchline": false
    }},
    {{
      "scene": 2,
      "speaker": "boy2",
      "shot_type": "boy_close",
      "spoken_hindi": "शुद्ध हिंदी में दूसरा कैरेक्टर बोलेगा",
      "dialogue": "Exact dialogue in clean Hinglish",
      "pose": "hands_on_hips",
      "prop": "phone",
      "action": "none",
      "emotion": "none",
      "is_punchline": false
    }},
    {{
      "scene": 3,
      "speaker": "boy",
      "shot_type": "boy_close",
      "spoken_hindi": "शुद्ध हिंदी में रिएक्शन/शॉक",
      "dialogue": "Reaction in Hinglish",
      "pose": "shock",
      "prop": "none",
      "action": "whistle_shock",
      "emotion": "shock",
      "is_punchline": false
    }},
    {{
      "scene": 4,
      "speaker": "boy2",
      "shot_type": "two_shot",
      "spoken_hindi": "शुद्ध हिंदी में फाइनल फनी पंचलाइन",
      "dialogue": "Punchline dialogue in Hinglish",
      "pose": "pleading",
      "prop": "none",
      "action": "none",
      "emotion": "none",
      "is_punchline": true
    }}
  ]
}}
Strictly return valid JSON only."""

        async def _call_deepseek():
            async with websockets.connect(ws_url) as ws:
                escaped_prompt = json.dumps(prompt)
                fill_js = f"""
                (() => {{
                    const ta = document.querySelector('textarea, div[contenteditable="true"]');
                    if (!ta) return false;
                    ta.focus();
                    const proto = Object.getPrototypeOf(ta);
                    const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set || Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value')?.set;
                    setter.call(ta, {escaped_prompt});
                    ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    ta.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    
                    setTimeout(() => {{
                        const sendBtn = document.querySelector('div.ds-button--circle, button.ds-button--circle, div[aria-label="Send"], button[aria-label="Send"]');
                        if (sendBtn) sendBtn.click();
                    }}, 300);
                    return true;
                }})()
                """
                await ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate", "params": {"expression": fill_js, "returnByValue": True}}))
                await ws.recv()
                print("[*] Prompt sent to DeepSeek directly! Waiting for response...")
                
                last_body = ""
                stable_count = 0
                for i in range(45):
                    await asyncio.sleep(1.5)
                    await ws.send(json.dumps({"id": 10 + i, "method": "Runtime.evaluate", "params": {"expression": "document.body.innerText", "returnByValue": True}}))
                    res = json.loads(await ws.recv())
                    body_text = res.get("result", {}).get("result", {}).get("value", "")
                    
                    if "{" in body_text and "scenes" in body_text:
                        if len(body_text) == len(last_body):
                            stable_count += 1
                            if stable_count >= 2:
                                break
                        else:
                            stable_count = 0
                    last_body = body_text

                # Extract JSON block
                match = re.search(r'\{[\s\S]*"title"[\s\S]*"scenes"[\s\S]*\}', last_body)
                if match:
                    raw_json = match.group(0)
                    brace_count = 0
                    end_idx = -1
                    for idx, ch in enumerate(raw_json):
                        if ch == '{':
                            brace_count += 1
                        elif ch == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = idx + 1
                                break
                    if end_idx != -1:
                        data = json.loads(raw_json[:end_idx])
                        return data
            return None

        script_data = asyncio.run(_call_deepseek())
        if script_data:
            print(f"[OK] DeepSeek generated script directly: '{script_data.get('title')}'")
            return script_data
        raise RuntimeError("Could not parse JSON from DeepSeek stream")

    except Exception as e:
        print(f"[WARN] Direct DeepSeek auto-generate skipped ({e}). Using robust procedural fallback script for '{topic}'...")
        clean_top = str(topic).strip()
        return {
            "title": f"POV: {clean_top} 😂 #shorts #viral",
            "hook": f"POV: {clean_top[:30]}",
            "duo_type": "boy_and_boy2",
            "theme": "home_mummy",
            "description": f"When {clean_top} gets out of hand! 😂 Stickman POV animation #shorts #comedy",
            "tags": ["shorts", "comedy", "funny", "relatable", "stickman", "doodle"],
            "scenes": [
                {
                    "scene": 1,
                    "speaker": "boy",
                    "shot_type": "boy_close",
                    "spoken_hindi": f"भाई सच बता रहा हूँ, {clean_top} का ड्रामा हर रोज़ का सिरदर्द बन चुका है!",
                    "dialogue": f"Bhai sach bata raha hoon, {clean_top} ka drama har roz ka sir-dard hai!",
                    "pose": "talk_gesture",
                    "prop": "phone",
                    "action": "walk_in",
                    "emotion": "none",
                    "is_punchline": False
                },
                {
                    "scene": 2,
                    "speaker": "boy2",
                    "shot_type": "boy_close",
                    "spoken_hindi": "अरे तू शांत रह भाई! तेरे से ज़्यादा टेंशन में तो मैं यहाँ जी रहा हूँ!",
                    "dialogue": "Arre tu shant reh bhai! Tere se zyada tension mein toh main jee raha hoon!",
                    "pose": "hands_on_hips",
                    "prop": "phone",
                    "action": "none",
                    "emotion": "none",
                    "is_punchline": False
                },
                {
                    "scene": 3,
                    "speaker": "boy",
                    "shot_type": "boy_close",
                    "spoken_hindi": "तू और टेंशन? भाई तूने ज़िंदगी में बस दो ही काम किए हैं—बहाने और सोना!",
                    "dialogue": "Tu aur tension? Bhai tune zindagi mein bas do hi kaam kiye hain—bahane aur sona!",
                    "pose": "shock",
                    "prop": "none",
                    "action": "whistle_shock",
                    "emotion": "shock",
                    "is_punchline": False
                },
                {
                    "scene": 4,
                    "speaker": "boy2",
                    "shot_type": "two_shot",
                    "spoken_hindi": "तीसरा काम भूल गया भाई! तेरी बेइज़्ज़ती करने का मज़ा ही अलग है!",
                    "dialogue": "Teesra kaam bhool gaya bhai! Teri beizzati karne ka maza hi alag hai!",
                    "pose": "pleading",
                    "prop": "none",
                    "action": "none",
                    "emotion": "none",
                    "is_punchline": True
                }
            ]
        }

def process_pov_doodle_production(topic=None, script_data=None, base_filename=None, theme=None):
    if script_data is None:
        if topic:
            script_data = generate_pov_script(topic)
        else:
            with open("sample_pov_script.json", "r", encoding="utf-8") as f:
                script_data = json.load(f)
        
    hook = script_data.get("hook", "POV: Relatable Moment 😂")
    title = script_data.get("title", "POV Comedy")
    description = script_data.get("description", "")
    tags = script_data.get("tags", [])
    scenes = script_data.get("scenes", [])
    env_theme = theme or script_data.get("theme", "home_mummy")
    
    now_str = datetime.now().strftime("%Y-%m-%d_%I-%M-%p")
    safe_topic = re.sub(r'[^a-zA-Z0-9_]', '_', title)[:25]
    session_dir = os.path.join(OUTPUT_DIR, f"POV_{now_str}_{safe_topic}")
    os.makedirs(session_dir, exist_ok=True)
    
    clips = []
    print("\n" + "=" * 65)
    print(f"[*] PRODUCING ULTIMATE ANIMATED POV DOODLE SHORT ({len(scenes)} SCENES)")
    print(f"[*] Theme: '{env_theme}' | Hook: '{hook}'")
    print(f"[*] Title: '{title}'")
    print("=" * 65)
    
    for sc in scenes:
        s_num = sc["scene"]
        speaker = sc.get("speaker", "boy")
        shot_type = sc.get("shot_type", "two_shot")
        spoken_hindi = sc.get("spoken_hindi", "")
        dialogue = sc.get("dialogue", spoken_hindi)
        pose = sc.get("pose", "talk_gesture")
        emotion = sc.get("emotion", "none")
        prop = sc.get("prop", "none")
        action = sc.get("action", "none")
        is_last = (s_num == len(scenes)) or sc.get("is_punchline", False)
        
        print(f"\n--- Scene {s_num}/{len(scenes)}: [{speaker.upper()}] ({shot_type}) ---")
        print(f"Dialogue: '{dialogue}'")
        
        # 1. Synthesize & Master Voice Audio with RMS Extraction
        audio_path = os.path.join(TEMP_DIR, f"scene_{s_num}_audio.mp3")
        duration, norm_rms, words_data = synthesize_audio(spoken_hindi, speaker, audio_path)
        a_clip = AudioFileClip(audio_path)
        
        # 2. Sound Effects (Whoosh, Thwack, Pop, Boom, Gasp)
        sfx_clips = [a_clip]
        
        whoosh_file = os.path.join(SFX_DIR, "whoosh.wav")
        if os.path.exists(whoosh_file):
            sfx_clips.append(AudioFileClip(whoosh_file).set_start(0.0).volumex(0.35))
            
        if action == "chappal_impact":
            thwack_file = os.path.join(SFX_DIR, "thwack.wav")
            if os.path.exists(thwack_file):
                sfx_clips.append(AudioFileClip(thwack_file).set_start(0.8).volumex(0.85))
            gasp_file = os.path.join(SFX_DIR, "gasp.wav")
            if os.path.exists(gasp_file):
                sfx_clips.append(AudioFileClip(gasp_file).set_start(0.85).volumex(0.50))
        elif action == "whistle_shock":
            whistle_file = os.path.join(SFX_DIR, "whistle.wav")
            if os.path.exists(whistle_file):
                sfx_clips.append(AudioFileClip(whistle_file).set_start(0.4).volumex(0.85))
            vine_file = os.path.join(SFX_DIR, "vine_boom.wav")
            if os.path.exists(vine_file):
                sfx_clips.append(AudioFileClip(vine_file).set_start(1.2).volumex(0.65))
                
        if pose == "shock" and action != "whistle_shock":
            gasp_file = os.path.join(SFX_DIR, "gasp.wav")
            if os.path.exists(gasp_file):
                sfx_clips.append(AudioFileClip(gasp_file).set_start(0.1).volumex(0.35))
                
        if is_last:
            boom_file = os.path.join(SFX_DIR, "boom.wav")
            if os.path.exists(boom_file):
                sfx_clips.append(AudioFileClip(boom_file).set_start(max(0.0, duration - 1.2)).volumex(0.45))
            laugh_file = os.path.join(SFX_DIR, "laugh.wav")
            if os.path.exists(laugh_file):
                sfx_clips.append(AudioFileClip(laugh_file).set_start(max(0.0, duration - 1.0)).volumex(0.35))
                
        scene_audio = CompositeAudioClip(sfx_clips)
        
        # 3. Create Video Frame Generator
        duo_type = script_data.get("duo_type", "boy_and_girl")
        def make_frame(t, dur=duration, h_txt=hook, d_txt=dialogue, w_data=words_data, 
                       rms=norm_rms, spk=speaker, s_type=shot_type, p=pose, emo=emotion, 
                       prp=prop, punch=is_last, thm=env_theme, act=action, d_type=duo_type):
            return render_pov_frame(t, dur, h_txt, d_txt, w_data, rms, spk, s_type, p, emo, prp, punch, theme=thm, action=act, duo_type=d_type)
            
        v_clip = VideoClip(make_frame, duration=duration).set_fps(24)
        v_clip = v_clip.set_audio(scene_audio)
        clips.append(v_clip)
        
    print("\n[*] Concatenating scenes into complete POV Doodle Short...")
    final_video = concatenate_videoclips(clips, method="compose")
    
    # 4. Mix Playful Comedy Lo-Fi BGM at 6% volume
    bgm_path = os.path.join(SFX_DIR, "comedy_bgm.wav")
    if os.path.exists(bgm_path):
        print("[*] Mixing Playful Comedy Lo-Fi BGM at 6% volume...")
        bgm_clip = AudioFileClip(bgm_path)
        if bgm_clip.duration < final_video.duration:
            n_loops = int(final_video.duration / bgm_clip.duration) + 1
            bgm_clip = concatenate_audioclips([bgm_clip] * n_loops)
        bgm_clip = bgm_clip.subclip(0, final_video.duration).volumex(0.06)
        final_audio = CompositeAudioClip([final_video.audio, bgm_clip])
        final_video = final_video.set_audio(final_audio)
        
    out_mp4 = os.path.join(session_dir, "final_pov_short.mp4")
    print(f"\n[*] Exporting Ultimate POV Doodle MP4: {out_mp4}")
    try:
        final_video.write_videofile(
            out_mp4,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            ffmpeg_params=["-pix_fmt", "yuv420p"],
            threads=4
        )
    except Exception as w_err:
        if os.path.exists(out_mp4) and os.path.getsize(out_mp4) > 10000:
            print(f"[*] Note: write_videofile completed with cleanup warning ({w_err}), video file is intact!")
        else:
            raise w_err
    
    thumb_path = os.path.join(session_dir, "cover_thumbnail.png")
    final_video.save_frame(thumb_path, t=min(1.5, final_video.duration * 0.5))
    
    metadata = {
        "title": title,
        "description": f"{description}\n\n#shorts #comedy #pov #doodle #animation",
        "tags": tags + ["shorts", "comedy", "doodle", "pov"],
        "video_path": os.path.abspath(out_mp4),
        "thumbnail_path": os.path.abspath(thumb_path),
        "produced_at": datetime.now().isoformat()
    }
    with open(os.path.join(session_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
        
    print("\n" + "=" * 65)
    print(f"[SUCCESS] ULTIMATE ANIMATED POV DOODLE READY: {out_mp4}")
    print("=" * 65)
    return out_mp4, title, description, tags

if __name__ == "__main__":
    process_pov_doodle_production()
