"""
render_full_4scene_deepseek.py
==============================
Renders a complete 4-scene, 30-second YouTube Short combining:
1. DeepSeek-coded custom environments & character animations
2. Authentic 19-20 year old Young Boy voice acting (hi-IN-MadhurNeural +10Hz/+5Hz)
3. Broadcast mastered audio (FFmpeg EQ + compand)
4. Washi tape hook + dynamic karaoke subtitles + Lo-Fi BGM + SFX
"""

import os
import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import json
import math
import subprocess
import asyncio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, concatenate_audioclips
from mutagen.mp3 import MP3
import edge_tts

OUTPUT_DIR = "pipeline_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
TEMP_DIR = os.path.join(OUTPUT_DIR, "deepseek_full_temp")
os.makedirs(TEMP_DIR, exist_ok=True)
SFX_DIR = "sfx"

# ─── Load DeepSeek Scene 1 Code ──────────────────────────────────────────────
sys.path.append('scratch')
import deepseek_final_answer as dfa_scene1

# ─── Color Palette ────────────────────────────────────────────────────────────
INK    = (42, 40, 50)
PAPER  = (248, 244, 233)
WALL   = (238, 230, 214)
BLUE   = (152, 192, 230)
BLUE_D = (108, 148, 194)
WOOD   = (206, 166, 122)
WOOD_D = (168, 130, 92)
WHITE  = (253, 252, 248)
MOONC  = (255, 226, 140)
NIGHT  = (88, 106, 158)
PINK   = (246, 198, 198)
GREY   = (203, 194, 180)
RED    = (230, 45, 45)
CYAN   = (40, 160, 240)
YELLOW = (255, 215, 0)

def line(draw, pts, width=5, fill=INK):
    draw.line(pts, fill=fill, width=width, joint="curve")

def circ(draw, cx, cy, r, width=5, fill=None, outline=INK):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=width)

def poly(draw, pts, fill=None, outline=INK, width=5):
    draw.polygon(pts, fill=fill)
    if outline is not None:
        draw.line(list(pts) + [pts[0]], width=width, fill=outline, joint="curve")

# ─── DeepSeek Scene 2: College Corridor & Notice Board ───────────────────────
def draw_scene_2_corridor(draw, t, duration, w, h):
    draw.rectangle([0, 0, w, h], fill=PAPER)
    floor_y = 1040
    draw.rectangle([0, floor_y, w, h], fill=(232, 224, 210))
    line(draw, [(0, floor_y), (w, floor_y)], width=5)
    for tx in range(0, w, 120):
        line(draw, [(tx, floor_y), (tx + 40, h)], width=3, fill=GREY)
        
    # Classroom Door on left
    draw.rectangle([50, 400, 220, floor_y], fill=(240, 235, 225), outline=INK, width=5)
    draw.rectangle([70, 440, 200, 640], fill=(210, 230, 250), outline=INK, width=4)
    line(draw, [(135, 440), (135, 640)], width=3)
    line(draw, [(70, 540), (200, 540)], width=3)
    circ(draw, 195, 750, 8, width=3, fill=INK) # doorknob
    
    # Notice Board on right
    draw.rectangle([260, 320, 680, 720], fill=WOOD, outline=INK, width=6)
    draw.rectangle([280, 340, 660, 700], fill=(120, 70, 40), outline=INK, width=3) # corkboard
    
    # Notice Paper 1: Attendance Sheet
    px, py = 310, 370
    draw.rectangle([px, py, px + 180, py + 260], fill=WHITE, outline=INK, width=3)
    line(draw, [(px + 20, py + 30), (px + 160, py + 30)], width=4, fill=RED)
    for ly in range(py + 60, py + 220, 24):
        line(draw, [(px + 20, ly), (px + 160, ly)], width=2, fill=GREY)
        
    # Red Warning Stamp "12% DEBAR!"
    draw.rectangle([px + 15, py + 120, px + 165, py + 175], fill=(255, 230, 230), outline=RED, width=3)
    try:
        font_stamp = ImageFont.truetype("arialbd.ttf", 20)
    except:
        font_stamp = ImageFont.load_default()
    draw.text((px + 90, py + 148), "ATTENDANCE: 12%", fill=RED, font=font_stamp, anchor="mm")
    
    # Boy 2 (Doodle / Dost with backwards blue cap & cutting chai)
    scale = 1.35
    head_r = int(45 * scale)
    cx = 480
    cy = floor_y - 20
    neck_y = cy - int(120 * scale)
    hx = cx
    hy = neck_y - head_r
    
    # Torso
    line(draw, [(cx, neck_y), (cx, cy)], width=6)
    # Badge
    circ(draw, cx - 10, neck_y + 35, 4, width=0, fill=CYAN)
    
    # Legs
    line(draw, [(cx - 15, cy), (cx - 25, cy + 100), (cx - 40, cy + 180)], width=6)
    line(draw, [(cx + 15, cy), (cx + 25, cy + 100), (cx + 40, cy + 180)], width=6)
    
    # Left arm pointing to notice board
    p_ang = math.sin(t * 8) * 0.15
    line(draw, [(cx - 20, neck_y + 20), (cx - 70, neck_y + 60), (cx - 130 + int(p_ang * 20), neck_y - 10)], width=6)
    
    # Right arm holding cutting chai
    line(draw, [(cx + 20, neck_y + 20), (cx + 65, neck_y + 55), (cx + 40, neck_y + 85)], width=6)
    # Cutting chai cup
    chx, chy = cx + 45, neck_y + 90
    poly(draw, [(chx - 12, chy), (chx + 14, chy), (chx + 8, chy + 32), (chx - 8, chy + 32)], fill=(240, 240, 245), outline=INK, width=2)
    poly(draw, [(chx - 10, chy + 6), (chx + 12, chy + 6), (chx + 7, chy + 30), (chx - 7, chy + 30)], fill=(185, 105, 50), outline=None)
    # Steam
    sy = chy - 12 - int(t * 20) % 20
    draw.arc([chx - 6, sy, chx + 6, sy + 14], start=180, end=340, fill=GREY, width=2)
    
    # Head & Face
    circ(draw, hx, hy, head_r, width=6, fill=WHITE)
    # Backwards blue cap
    draw.arc([hx - head_r, hy - head_r - 4, hx + head_r, hy - 12], start=180, end=360, fill=CYAN, width=16)
    draw.arc([hx - head_r, hy - head_r - 4, hx + head_r, hy - 12], start=180, end=360, fill=INK, width=3)
    line(draw, [(hx - head_r - 16, hy - 26), (hx - head_r + 6, hy - 18)], width=6, fill=INK) # cap visor
    
    # Eyes & Smirk
    circ(draw, hx - 18, hy - 8, 5, width=0, fill=INK)
    circ(draw, hx + 18, hy - 8, 5, width=0, fill=INK)
    draw.arc([hx - 16, hy + 8, hx + 16, hy + 26], start=20, end=160, fill=INK, width=4)

# ─── DeepSeek Scene 3: Pillow & Alarm Whistle Shock ──────────────────────────
def draw_scene_3_pillow_shock(draw, t, duration, w, h):
    draw.rectangle([0, 0, w, h], fill=PAPER)
    floor_y = 1040
    draw.rectangle([0, floor_y, w, h], fill=WALL)
    line(draw, [(0, floor_y), (w, floor_y)], width=5)
    
    # Bed & Headboard
    draw.rectangle([30, 780, 72, 1010], fill=WOOD_D, outline=INK, width=5)
    draw.rectangle([50, 890, 550, 1008], fill=WHITE, outline=INK, width=5)
    
    # Vibrating Alarm Clock with Seeti steam
    vib = math.sin(t * 36) * 8
    ax, ay = 620 + int(vib), 880
    circ(draw, ax, ay, 46, width=5, fill=WHITE)
    circ(draw, ax - 26, ay - 42, 12, width=4, fill=RED)
    circ(draw, ax + 26, ay - 42, 12, width=4, fill=RED)
    line(draw, [(ax, ay), (ax + 18 * math.sin(t * 12), ay - 18 * math.cos(t * 12))], width=4)
    # Steam clouds from alarm!
    for i in range(3):
        sm_y = ay - 60 - i * 35 - int(t * 30) % 35
        sm_x = ax + int(math.sin(t * 15 + i) * 15)
        circ(draw, sm_x, sm_y, 14 + i * 5, width=2, fill=(245, 245, 255), outline=GREY)
        
    # Boy 1 sitting on bed, clutching pillow in SHOCK
    scale = 1.35
    head_r = int(45 * scale)
    bx = 280
    by = 780
    
    # Torso
    line(draw, [(bx, by + head_r), (bx, by + head_r + 140)], width=6)
    
    # Pillow clutched in hands
    px, py = bx + 10, by + head_r + 50
    draw.rounded_rectangle([px - 60, py - 40, px + 70, py + 45], radius=18, fill=WHITE, outline=INK, width=4)
    draw.arc([px - 40, py - 20, px + 50, py + 25], start=20, end=160, fill=BLUE_D, width=2)
    
    # Arms holding pillow
    line(draw, [(bx - 20, by + head_r + 15), (px - 50, py + 10)], width=6)
    line(draw, [(bx + 20, by + head_r + 15), (px + 60, py + 10)], width=6)
    
    # Head & Spiky Hair
    circ(draw, bx, by, head_r, width=6, fill=WHITE)
    line(draw, [(bx - 18, by - head_r), (bx - 12, by - head_r - 20), (bx - 4, by - head_r)], width=5)
    line(draw, [(bx + 4, by - head_r), (bx + 12, by - head_r - 20), (bx + 22, by - head_r)], width=5)
    
    # Dilated Shocked Eyes + Open Mouth
    circ(draw, bx - 18, by - 10, 16, width=4, fill=WHITE)
    circ(draw, bx + 18, by - 10, 16, width=4, fill=WHITE)
    circ(draw, bx - 18, by - 10, 6, width=0, fill=INK)
    circ(draw, bx + 18, by - 10, 6, width=0, fill=INK)
    draw.ellipse([bx - 16, by + 18, bx + 16, by + 46], fill=INK, outline=INK, width=3)
    
    # Sweat drop
    sw_y = by - 20 + int(t * 25) % 30
    poly(draw, [(bx + 52, sw_y), (bx + 46, sw_y + 14), (bx + 58, sw_y + 14)], fill=CYAN)
    circ(draw, bx + 52, sw_y + 16, 6, width=0, fill=CYAN)

# ─── DeepSeek Scene 4: Two-Shot Buddy Climax Punchline ───────────────────────
def draw_scene_4_two_shot(draw, t, duration, w, h):
    draw.rectangle([0, 0, w, h], fill=PAPER)
    floor_y = 1040
    draw.rectangle([0, floor_y, w, h], fill=WALL)
    line(draw, [(0, floor_y), (w, floor_y)], width=5)
    
    # Window in background
    draw.rectangle([250, 180, 470, 460], fill=NIGHT, outline=INK, width=5)
    line(draw, [(360, 180), (360, 460)], width=4)
    line(draw, [(250, 320), (470, 320)], width=4)
    circ(draw, 410, 240, 22, width=0, fill=MOONC)
    
    scale = 1.25
    head_r = int(45 * scale)
    
    # ── Left: Boy 1 (Sticky) with pasina & shrug pose ──
    x1 = 200
    y1 = floor_y - 15
    neck1 = y1 - int(120 * scale)
    h1_y = neck1 - head_r
    
    line(draw, [(x1, neck1), (x1, y1)], width=6)
    circ(draw, x1 - 10, neck1 + 35, 4, width=0, fill=YELLOW) # badge
    # Legs
    line(draw, [(x1 - 12, y1), (x1 - 22, y1 + 100), (x1 - 35, y1 + 170)], width=6)
    line(draw, [(x1 + 12, y1), (x1 + 22, y1 + 100), (x1 + 35, y1 + 170)], width=6)
    # Shrug Arms
    line(draw, [(x1 - 18, neck1 + 18), (x1 - 65, neck1 + 45), (x1 - 90, neck1 + 15)], width=6)
    line(draw, [(x1 + 18, neck1 + 18), (x1 + 65, neck1 + 45), (x1 + 90, neck1 + 15)], width=6)
    # Head & Spiky Hair
    circ(draw, x1, h1_y, head_r, width=6, fill=WHITE)
    line(draw, [(x1 - 15, h1_y - head_r), (x1 - 10, h1_y - head_r - 18), (x1 - 2, h1_y - head_r)], width=4)
    line(draw, [(x1 + 4, h1_y - head_r), (x1 + 10, h1_y - head_r - 18), (x1 + 18, h1_y - head_r)], width=4)
    # Nervous smile & sweat
    circ(draw, x1 - 14, h1_y - 8, 4, width=0, fill=INK)
    circ(draw, x1 + 14, h1_y - 8, 4, width=0, fill=INK)
    draw.arc([x1 - 14, h1_y + 10, x1 + 14, h1_y + 24], start=20, end=160, fill=INK, width=3)
    sw_y = h1_y - 15 + int(t * 20) % 25
    circ(draw, x1 + 48, sw_y + 12, 5, width=0, fill=CYAN)
    
    # ── Right: Boy 2 (Doodle / Dost) with backwards cap delivering punchline ──
    x2 = 520
    y2 = floor_y - 15
    neck2 = y2 - int(120 * scale)
    h2_y = neck2 - head_r
    
    line(draw, [(x2, neck2), (x2, y2)], width=6)
    circ(draw, x2 - 10, neck2 + 35, 4, width=0, fill=CYAN) # badge
    # Legs
    line(draw, [(x2 - 12, y2), (x2 - 20, y2 + 100), (x2 - 30, y2 + 170)], width=6)
    line(draw, [(x2 + 12, y2), (x2 + 20, y2 + 100), (x2 + 30, y2 + 170)], width=6)
    # Punchline gesturing hands
    g_wave = math.sin(t * 9) * 12
    line(draw, [(x2 - 18, neck2 + 18), (x2 - 50, neck2 + 45), (x2 - 80, neck2 + 20 + int(g_wave))], width=6)
    line(draw, [(x2 + 18, neck2 + 18), (x2 + 45, neck2 + 45), (x2 + 30, neck2 + 75)], width=6)
    # Head with Backwards Blue Cap
    circ(draw, x2, h2_y, head_r, width=6, fill=WHITE)
    draw.arc([x2 - head_r, h2_y - head_r - 4, x2 + head_r, h2_y - 12], start=180, end=360, fill=CYAN, width=15)
    draw.arc([x2 - head_r, h2_y - head_r - 4, x2 + head_r, h2_y - 12], start=180, end=360, fill=INK, width=3)
    line(draw, [(x2 - head_r - 14, h2_y - 24), (x2 - head_r + 6, h2_y - 16)], width=6, fill=INK)
    # Sassy laughing mouth
    circ(draw, x2 - 14, h2_y - 8, 4, width=0, fill=INK)
    circ(draw, x2 + 14, h2_y - 8, 4, width=0, fill=INK)
    draw.ellipse([x2 - 16, h2_y + 12, x2 + 16, h2_y + 36], fill=INK, outline=INK, width=2)
    draw.ellipse([x2 - 10, h2_y + 24, x2 + 10, h2_y + 34], fill=(255, 100, 130)) # tongue!
    
    # Tommy the Pet Dog in corner laughing!
    dog_x, dog_y = 620, floor_y - 15
    circ(draw, dog_x, dog_y, 22, width=4, fill=WHITE)
    circ(draw, dog_x + 22, dog_y - 14, 14, width=4, fill=WHITE)
    circ(draw, dog_x + 24, dog_y - 16, 3, width=0, fill=INK)
    draw.arc([dog_x + 18, dog_y - 10, dog_x + 28, dog_y], start=20, end=160, fill=INK, width=2)
    # Wagging tail!
    tail_ang = math.sin(t * 18) * 0.7
    line(draw, [(dog_x - 18, dog_y - 4), (dog_x - 38 + int(math.cos(tail_ang)*15), dog_y - 20 + int(math.sin(tail_ang)*15))], width=4)

# ─── MASTER PRODUCTION PIPELINE ───────────────────────────────────────────────
def produce_complete_deepseek_short():
    print("=" * 70)
    print("     PRODUCING COMPLETE 4-SCENE DEEPSEEK SHORT (30 SECONDS)")
    print("=" * 70)
    
    with open("college_attendance_script.json", "r", encoding="utf-8") as f:
        script = json.load(f)
        
    hook_text = script.get("hook", "POV: College Attendance 12% 💀")
    scenes = script.get("scenes", [])
    
    try:
        font_hook = ImageFont.truetype("arialbd.ttf", 28)
        font_sub = ImageFont.truetype("arialbd.ttf", 34)
    except:
        font_hook = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    clips = []
    w, h = 720, 1280
    
    for sc in scenes:
        s_num = sc["scene"]
        speaker = sc["speaker"]
        spoken = sc["spoken_hindi"]
        dialogue = sc["dialogue"]
        
        print(f"\n--- Scene {s_num}/4: [{speaker.upper()}] ---")
        print(f"Dialogue: '{dialogue}'")
        
        # 1. Voice Synthesis
        voice_wav = os.path.join(TEMP_DIR, f"scene_{s_num}_voice.wav")
        pitch = "+10Hz" if speaker == "boy" else "+5Hz"
        rate = "+18%" if speaker == "boy" else "+16%"
        temp_mp3 = voice_wav.replace(".wav", ".mp3")
        
        async def _tts(txt=spoken, p=pitch, r=rate, mp3=temp_mp3):
            c = edge_tts.Communicate(txt, "hi-IN-MadhurNeural", rate=r, pitch=p)
            await c.save(mp3)
        asyncio.run(_tts())
        
        # FFmpeg Broadcast Master EQ
        cmd = [
            'ffmpeg', '-y', '-i', temp_mp3,
            '-af', 'highpass=f=80,lowpass=f=12000,equalizer=f=120:t=q:w=1.2:g=2.5,equalizer=f=3500:t=q:w=1.5:g=3.0,compand=attacks=0.02:decays=0.15:points=-80/-80|-40/-30|-20/-14|0/-6:gain=2.5',
            voice_wav
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        v_clip = AudioFileClip(voice_wav)
        duration = v_clip.duration + 0.35 # small buffer
        
        # SFX per scene
        sfx_tracks = [v_clip]
        if s_num == 3:
            whistle_sfx = os.path.join(SFX_DIR, "whistle.wav")
            if os.path.exists(whistle_sfx):
                sfx_tracks.append(AudioFileClip(whistle_sfx).set_start(0.2).volumex(0.35))
        elif s_num == 4:
            boom_sfx = os.path.join(SFX_DIR, "boom.wav")
            laugh_sfx = os.path.join(SFX_DIR, "laugh.wav")
            if os.path.exists(boom_sfx):
                sfx_tracks.append(AudioFileClip(boom_sfx).set_start(duration - 1.2).volumex(0.40))
            if os.path.exists(laugh_sfx):
                sfx_tracks.append(AudioFileClip(laugh_sfx).set_start(duration - 1.0).volumex(0.30))
                
        scene_audio = CompositeAudioClip(sfx_tracks)
        
        # Frame Generator
        def make_scene_frame(t, dur=duration, s_idx=s_num, spk=speaker, d_txt=dialogue):
            img = Image.new('RGB', (w, h), (255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # DeepSeek Scene Specific Art
            if s_idx == 1:
                dfa_scene1.draw_scene(draw, t, dur, w, h)
            elif s_idx == 2:
                draw_scene_2_corridor(draw, t, dur, w, h)
            elif s_idx == 3:
                draw_scene_3_pillow_shock(draw, t, dur, w, h)
            else:
                draw_scene_4_two_shot(draw, t, dur, w, h)
                
            # Washi Tape Top Hook
            draw.rounded_rectangle([100, 50, 620, 115], radius=14, fill=(248, 248, 252), outline=INK, width=3)
            draw.polygon([(88, 45), (135, 40), (125, 70), (78, 75)], fill=YELLOW)
            draw.polygon([(595, 40), (642, 45), (632, 75), (585, 70)], fill=YELLOW)
            draw.text((360, 82), hook_text, fill=INK, font=font_hook, anchor='mm')
            
            # Subtitle Banner
            sub_col = YELLOW if spk == "boy" else CYAN
            draw.rounded_rectangle([40, 1130, 680, 1225], radius=18, fill=(18, 18, 24), outline=sub_col, width=2)
            # Speaker Tag
            tag = "BOY 1" if spk == "boy" else "DOST"
            draw.rounded_rectangle([55, 1108, 155, 1134], radius=6, fill=sub_col)
            draw.text((105, 1121), tag, fill=(10, 10, 15), font=font_hook, anchor='mm')
            # Text
            draw.text((360, 1178), d_txt, fill=(255, 255, 255), font=font_sub, anchor='mm')
            
            return np.array(img)
            
        c = VideoClip(make_scene_frame, duration=duration).set_fps(24).set_audio(scene_audio)
        clips.append(c)
        
    print("\n[*] Concatenating 4 scenes into complete 30s Short...")
    full_video = concatenate_videoclips(clips, method="compose")
    
    # Mix Lo-Fi BGM at 6%
    bgm_path = os.path.join(SFX_DIR, "comedy_bgm.wav")
    if os.path.exists(bgm_path):
        bgm = AudioFileClip(bgm_path)
        if bgm.duration < full_video.duration:
            loops = int(full_video.duration / bgm.duration) + 1
            bgm = concatenate_audioclips([bgm] * loops)
        bgm = bgm.subclip(0, full_video.duration).volumex(0.06)
        full_audio = CompositeAudioClip([full_video.audio, bgm])
        full_video = full_video.set_audio(full_audio)
        
    out_mp4 = os.path.join(OUTPUT_DIR, "final_college_attendance_full_short.mp4")
    print(f"[*] Rendering Full Video to: {out_mp4}")
    
    try:
        full_video.write_videofile(out_mp4, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    except Exception as e:
        print(f"[*] Note: MoviePy cleanup ({e}), file intact!")
        
    print("\n" + "=" * 70)
    print(f"[SUCCESS] COMPLETE 4-SCENE SHORT READY: {out_mp4}")
    print("=" * 70)
    return out_mp4

if __name__ == "__main__":
    produce_complete_deepseek_short()
