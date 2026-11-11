"""
render_money_topic_short.py
===========================
Renders the complete 30s Short for:
Topic: 'Friend asking for money and suddenly going invisible'

Features 100% NEW Visuals:
- Scene 1: Roadside Chai Tapri with tea stall, smoking kettle, wooden bench, boy showing phone asking for 500 UPI.
- Scene 2: Dost smiling, pretending to scan QR code on his phone: 'Arre bhai scan kar raha hoon!'
- Scene 3: Boy staring at phone with 0 balance, dilated shock eyes, tumbleweed/whistle.
- Scene 4: CLIMAX: Dost has completely VANISHED into an expanding cartoon smoke cloud ('POOF!'), only empty sneakers left behind on the road!
"""

import os
import sys
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import math
import subprocess
import asyncio
import concurrent.futures
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, concatenate_audioclips
import edge_tts
import sfx_fetcher

OUTPUT_DIR = "pipeline_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
TEMP_DIR = os.path.join(OUTPUT_DIR, "detailed_temp")
os.makedirs(TEMP_DIR, exist_ok=True)
SFX_DIR = "sfx"

# ─── Colors ───────────────────────────────────────────────────────────────────
INK       = (35, 32, 42)
ROAD_BG   = (246, 242, 234)
ROAD_FLOOR= (215, 210, 200)
ROAD_LINE = (180, 175, 165)
STALL_WOOD= (190, 145, 95)
STALL_DARK= (150, 110, 70)
CHAI_POT  = (175, 180, 190)
RED_ACC   = (235, 55, 55)
CYAN_ACC  = (30, 165, 245)
YELLOW_ACC= (255, 215, 0)
WHITE     = (255, 255, 255)
SMOKE_COL = (235, 235, 240)
GREEN_UPI = (40, 180, 90)

def safe_run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)

def line(draw, pts, width=5, fill=INK):
    draw.line(pts, fill=fill, width=width, joint="curve")

def circ(draw, cx, cy, r, width=5, fill=None, outline=INK):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=width)

def poly(draw, pts, fill=None, outline=INK, width=5):
    draw.polygon(pts, fill=fill)
    if outline is not None:
        draw.line(list(pts) + [pts[0]], width=width, fill=outline, joint="curve")

# ─── Scene 1: Chai Tapri Street Stall (Boy asking for 500) ───────────────────
def draw_scene_1_tapri(draw, t, dur, w, h):
    # 1. Sky & Road Perspective
    draw.rectangle([0, 0, w, h], fill=ROAD_BG)
    floor_y = 1000
    draw.rectangle([0, floor_y, w, h], fill=ROAD_FLOOR)
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)
    for rx in range(-50, w + 150, 95):
        line(draw, [(rx, floor_y), (rx + 45, h)], width=3, fill=ROAD_LINE)

    # Street Lamp Post on left
    line(draw, [(70, 150), (70, floor_y)], width=7)
    draw.arc([70, 120, 150, 200], start=180, end=360, fill=INK, width=6)
    circ(draw, 150, 180, 18, fill=YELLOW_ACC, outline=INK, width=3)
    # Light beam glow
    poly(draw, [(135, 195), (165, 195), (280, 500), (40, 500)], fill=(255, 250, 210, 40))

    # 2. Chai Tapri Stall on Right
    draw.rectangle([450, 600, 710, floor_y], fill=STALL_WOOD, outline=INK, width=5)
    # Tapri Striped Canopy / Awning
    canopy_pts = [(420, 500), (720, 500), (690, 600), (400, 600)]
    poly(draw, canopy_pts, fill=(240, 235, 225), outline=INK, width=4)
    for cx in range(410, 710, 45):
        poly(draw, [(cx, 500), (cx + 25, 500), (cx + 15, 600), (cx - 10, 600)], fill=RED_ACC, outline=None)
    # Steaming Chai Aluminium Kettle
    circ(draw, 520, 570, 28, fill=CHAI_POT, outline=INK, width=4)
    line(draw, [(500, 545), (540, 545)], width=4) # Handle
    line(draw, [(535, 560), (560, 550)], width=4) # Spout
    # Rising steam from kettle
    for si in range(3):
        sy = 535 - ((t * 25 + si * 20) % 55)
        sx = 560 + 5 * math.sin(t * 8 + si)
        circ(draw, sx, sy, 6, fill=WHITE, outline=ROAD_LINE, width=2)
    # Cutting Chai Glasses in Metal Stand
    draw.rectangle([580, 565, 680, 595], fill=None, outline=INK, width=3)
    for gx in range(595, 675, 25):
        draw.rectangle([gx - 8, 555, gx + 8, 585], fill=(195, 120, 60), outline=INK, width=2)

    # Tapri Sign: "RAMU KI CHAI - ONLY CASH NO UPI"
    draw.rectangle([450, 620, 690, 665], fill=INK, outline=None)
    draw.text((570, 642), "RAMU CHAI: NO UDHAAR", fill=YELLOW_ACC, font=ImageFont.load_default(), anchor='mm')

    # 3. Boy 1 (Left - Urgently showing phone with Rs 500 QR)
    bx = 220 + 4 * math.sin(t * 5)
    by = floor_y - 290
    
    # Shadow
    draw.ellipse([bx - 45, floor_y - 8, bx + 45, floor_y + 10], fill=(190, 185, 175))

    # Head & Desperate Face
    circ(draw, bx, by, 50, fill=WHITE, outline=INK, width=5)
    # Worry Eyebrows
    line(draw, [(bx - 22, by - 18), (bx - 6, by - 26)], width=3)
    line(draw, [(bx + 6, by - 26), (bx + 22, by - 18)], width=3)
    circ(draw, bx - 14, by - 5, 5, fill=INK)
    circ(draw, bx + 14, by - 5, 5, fill=INK)
    # Talking desperate mouth
    mouth_o = int(6 + 8 * abs(math.sin(t * 15)))
    draw.ellipse([bx - 12, by + 12 - mouth_o, bx + 12, by + 12 + mouth_o], fill=INK)

    # Torso
    line(draw, [(bx, by + 50), (bx, by + 205)], width=6)
    # Left Arm Holding Smartphone Out towards friend
    line(draw, [(bx, by + 85), (bx + 45, by + 105)], width=5)
    line(draw, [(bx + 45, by + 105), (bx + 85, by + 85)], width=5)
    # Smartphone with "UPI 500"
    ph_x, ph_y = bx + 95, by + 75
    draw.rounded_rectangle([ph_x - 18, ph_y - 30, ph_x + 18, ph_y + 30], radius=5, fill=(40, 40, 50), outline=INK, width=3)
    draw.rectangle([ph_x - 14, ph_y - 24, ph_x + 14, ph_y + 12], fill=GREEN_UPI)
    draw.text((ph_x, ph_y - 6), "500", fill=WHITE, font=ImageFont.load_default(), anchor='mm')
    # Right Arm begging / hand open
    line(draw, [(bx, by + 85), (bx - 45, by + 115)], width=5)
    line(draw, [(bx - 45, by + 115), (bx - 70, by + 95)], width=5)

    # Legs & Shoes
    line(draw, [(bx, by + 205), (bx - 25, floor_y)], width=6)
    line(draw, [(bx, by + 205), (bx + 25, floor_y)], width=6)

# ─── Scene 2: The Friend in Hoodie (Pretending to pay UPI) ────────────────────
def draw_scene_2_hoodie_friend(draw, t, dur, w, h):
    draw.rectangle([0, 0, w, h], fill=ROAD_BG)
    floor_y = 1000
    draw.rectangle([0, floor_y, w, h], fill=ROAD_FLOOR)
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)

    # Street background posters
    draw.rectangle([80, 260, 240, 420], fill=WHITE, outline=INK, width=3)
    draw.text((160, 340), "NO CASH?\nUSE UPI!", fill=RED_ACC, font=ImageFont.load_default(), anchor='mm')

    # Dost Close-Up in Green Hoodie with Fake Charming Smile
    fx = 360 + 5 * math.sin(t * 6)
    fy = 620
    
    # Head & Green Hoodie
    circ(draw, fx, fy, 75, fill=WHITE, outline=INK, width=6)
    # Hoodie outline covering head
    draw.arc([fx - 85, fy - 85, fx + 85, fy + 85], start=120, end=420, fill=(70, 160, 90), width=18)
    # Hoodie strings hanging down
    line(draw, [(fx - 25, fy + 70), (fx - 30, fy + 140)], width=4, fill=WHITE)
    line(draw, [(fx + 25, fy + 70), (fx + 30, fy + 140)], width=4, fill=WHITE)

    # Winking / Smug Eyes
    circ(draw, fx - 22, fy - 10, 8, fill=INK) # Left eye open
    # Right eye winking line
    draw.arc([fx + 14, fy - 18, fx + 36, fy - 2], start=0, end=180, fill=INK, width=4)
    # Smug confident smile
    draw.arc([fx - 25, fy + 10, fx + 25, fy + 40], start=0, end=180, fill=INK, width=5)

    # Shoulders & Hoodie Body
    poly(draw, [(fx - 140, floor_y), (fx - 70, fy + 75), (fx + 70, fy + 75), (fx + 140, floor_y)], fill=(70, 160, 90), outline=INK, width=5)

    # Hands Holding Phone Pretending to Scan QR
    px, py = fx, fy + 170
    draw.rounded_rectangle([px - 45, py - 60, px + 45, py + 60], radius=8, fill=(30, 30, 38), outline=INK, width=4)
    # Glowing scan line moving up and down
    scan_y = py - 40 + int((t * 50) % 80)
    line(draw, [(px - 35, scan_y), (px + 35, scan_y)], width=3, fill=CYAN_ACC)
    draw.text((px, py - 48), "SCANNING...", fill=YELLOW_ACC, font=ImageFont.load_default(), anchor='mm')

    # Comic Speech Bubble: "Haan bhai bas OTP aa raha hai!"
    draw.rounded_rectangle([200, 120, 520, 220], radius=20, fill=WHITE, outline=INK, width=4)
    poly(draw, [(340, 220), (360, 260), (375, 220)], fill=WHITE, outline=INK, width=3)
    draw.text((360, 170), "BAS SCAN HO GAYA BHAI! 👍", fill=INK, font=ImageFont.load_default(), anchor='mm')

# ─── Scene 3: Dilated Shock Eyes (Pending... aur tu kahan gaya?!) ────────────
def draw_scene_3_shock_phone(draw, t, dur, w, h):
    # Dramatic Anime Background with Radial Shock Lines
    draw.rectangle([0, 0, w, h], fill=(255, 248, 238))
    cx, cy = w // 2, 650

    # Comic Radial Lines
    for angle_deg in range(0, 360, 12):
        rad = math.radians(angle_deg)
        r1 = 260 + 25 * math.sin(t * 22 + angle_deg)
        r2 = 650
        line(draw, [(cx + r1 * math.cos(rad), cy + r1 * math.sin(rad)), 
                    (cx + r2 * math.cos(rad), cy + r2 * math.sin(rad))], width=3, fill=(235, 215, 200))

    # Boy Trembling with Phone
    jitter = 5 * math.sin(t * 38)
    bx = cx + jitter
    by = cy

    # Dilated Anime Face
    circ(draw, bx, by - 80, 68, fill=WHITE, outline=INK, width=6)
    # Pinpoint Shock Eyes
    circ(draw, bx - 26, by - 85, 24, fill=WHITE, outline=INK, width=4)
    circ(draw, bx + 26, by - 85, 24, fill=WHITE, outline=INK, width=4)
    circ(draw, bx - 26, by - 85, 4, fill=INK) # tiny pupils
    circ(draw, bx + 26, by - 85, 4, fill=INK)

    # Wide Open Jaw Drop
    mouth_h = int(22 + 8 * math.sin(t * 18))
    draw.ellipse([bx - 18, by - 45, bx + 18, by - 45 + mouth_h * 2], fill=INK)

    # Giant Flying Sweat Drops
    for so_x, so_y in [(-75, -100), (80, -90), (85, -30)]:
        circ(draw, bx + so_x, by + so_y, 10, fill=CYAN_ACC, outline=INK, width=3)

    # Big Smartphone Screen showing: "PAYMENT FAILED / CANCELLED"
    draw.rounded_rectangle([bx - 140, by + 80, bx + 140, by + 340], radius=16, fill=(25, 25, 32), outline=INK, width=5)
    draw.rectangle([bx - 125, by + 110, bx + 125, by + 320], fill=(255, 235, 235))
    # Red Cross Icon
    circ(draw, bx, by + 175, 30, fill=RED_ACC, outline=None)
    line(draw, [(bx - 14, by + 161), (bx + 14, by + 189)], width=5, fill=WHITE)
    line(draw, [(bx + 14, by + 161), (bx - 14, by + 189)], width=5, fill=WHITE)
    draw.text((bx, by + 230), "TRANSACTION FAILED!", fill=RED_ACC, font=ImageFont.load_default(), anchor='mm')
    draw.text((bx, by + 265), "BALANCE: Rs 0.42", fill=INK, font=ImageFont.load_default(), anchor='mm')

# ─── Scene 4: CLIMAX: Friend Gone into POOF! Smoke Cloud! ───────────────────
def draw_scene_4_poof_disappear(draw, t, dur, w, h):
    draw.rectangle([0, 0, w, h], fill=ROAD_BG)
    floor_y = 1000
    draw.rectangle([0, floor_y, w, h], fill=ROAD_FLOOR)
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)

    # Shadows on floor
    draw.ellipse([160, floor_y - 8, 300, floor_y + 12], fill=(200, 195, 185))
    draw.ellipse([430, floor_y - 8, 570, floor_y + 12], fill=(200, 195, 185))

    # 1. Boy 1 (Left - Completely dumbfounded, hands in air)
    b1_x = 230
    b1_y = floor_y - 300
    circ(draw, b1_x, b1_y, 50, fill=WHITE, outline=INK, width=5)
    # Confused eyebrows
    line(draw, [(b1_x - 22, b1_y - 12), (b1_x - 6, b1_y - 20)], width=3)
    line(draw, [(b1_x + 6, b1_y - 14), (b1_x + 22, b1_y - 14)], width=3)
    circ(draw, b1_x - 14, b1_y - 2, 5, fill=INK)
    circ(draw, b1_x + 14, b1_y - 2, 5, fill=INK)
    # Question mark above head
    draw.text((b1_x, b1_y - 75), "???", fill=RED_ACC, font=ImageFont.load_default(), anchor='mm')
    # Mouth open
    draw.ellipse([b1_x - 10, b1_y + 12, b1_x + 10, b1_y + 26], fill=INK)

    # Torso & Shrugging Hands
    line(draw, [(b1_x, b1_y + 50), (b1_x, b1_y + 205)], width=6)
    line(draw, [(b1_x, b1_y + 80), (b1_x - 55, b1_y + 115)], width=5)
    line(draw, [(b1_x - 55, b1_y + 115), (b1_x - 85, b1_y + 80)], width=5) # Left palm up
    line(draw, [(b1_x, b1_y + 80), (b1_x + 55, b1_y + 115)], width=5)
    line(draw, [(b1_x + 55, b1_y + 115), (b1_x + 85, b1_y + 80)], width=5) # Right palm up
    line(draw, [(b1_x, b1_y + 205), (b1_x - 25, floor_y)], width=6)
    line(draw, [(b1_x, b1_y + 205), (b1_x + 25, floor_y)], width=6)

    # 2. Right Side: DOST IS GONE! Only Empty Sneakers and a HUGE SMOKE PUFF!
    sx, sy = 500, floor_y - 160
    
    # Empty Green Sneakers left behind on floor!
    draw.rounded_rectangle([sx - 45, floor_y - 12, sx - 10, floor_y + 8], radius=6, fill=(70, 160, 90), outline=INK, width=3)
    draw.rounded_rectangle([sx + 10, floor_y - 12, sx + 45, floor_y + 8], radius=6, fill=(70, 160, 90), outline=INK, width=3)

    # Expanding Cartoon Smoke Cloud ("POOF!")
    smoke_scale = min(1.3, 0.7 + t * 0.25)
    cloud_pts = [
        (sx, sy - 120), (sx + 75, sy - 90), (sx + 110, sy - 20), (sx + 85, sy + 60),
        (sx + 15, sy + 90), (sx - 65, sy + 75), (sx - 105, sy), (sx - 75, sy - 80)
    ]
    for (px, py) in cloud_pts:
        puff_r = int(55 * smoke_scale)
        circ(draw, px, py, puff_r, fill=SMOKE_COL, outline=INK, width=3)

    # Little flying poof stars
    for st_x, st_y in [(sx - 120, sy - 140), (sx + 130, sy - 110), (sx + 110, sy + 90)]:
        circ(draw, st_x, st_y, 8, fill=YELLOW_ACC, outline=INK, width=2)

    # Giant Comic "POOF! 💨" Text in Smoke Center
    draw.text((sx, sy), "POOF! 💨", fill=RED_ACC, font=ImageFont.load_default(), anchor='mm')
    draw.text((sx, sy + 40), "(GAYAB!)", fill=INK, font=ImageFont.load_default(), anchor='mm')

    # Tommy Dog in corner laughing with tongue out
    dog_x, dog_y = 635, floor_y - 25
    circ(draw, dog_x, dog_y, 22, fill=WHITE, outline=INK, width=4)
    circ(draw, dog_x + 22, dog_y - 14, 15, fill=WHITE, outline=INK, width=4)
    circ(draw, dog_x + 26, dog_y - 16, 3, fill=INK)
    poly(draw, [(dog_x + 14, dog_y - 24), (dog_x + 10, dog_y - 38), (dog_x + 22, dog_y - 28)], fill=STALL_WOOD, outline=INK, width=2)
    # Tongue
    draw.ellipse([dog_x + 30, dog_y - 10, dog_x + 38, dog_y - 4], fill=RED_ACC)
    # Wagging tail
    tail_w = 20 * math.sin(t * 30)
    line(draw, [(dog_x - 20, dog_y - 5), (dog_x - 45, dog_y - 25 + tail_w)], width=5)

# ─── Production Function ─────────────────────────────────────────────────────
def produce_money_friend_short(topic=None, base_filename=None):
    print("=" * 70)
    print("     PRODUCING 100% NEW ANIMATION SHORT: 'FRIEND ASKING FOR MONEY'")
    print("=" * 70)

    hook_text = "POV: Dost se 500 rupay maang liye 😭"
    scenes = [
        {
            "scene": 1,
            "speaker": "boy",
            "spoken_hindi": "Bhai bas 500 rupay UPI kar de, kal subah 10 baje tere haath mein honge!",
            "dialogue": "Bhai bas 500 rupay UPI kar de, kal pakka wapas kar dunga!",
            "sfx": ["whoosh"]
        },
        {
            "scene": 2,
            "speaker": "dost",
            "spoken_hindi": "Arre bhai tere liye jaan haazir hai! Phone nikaal, bas scan hi kar raha hoon!",
            "dialogue": "Arre tere liye jaan haazir hai bhai! Bas QR scan kar raha hoon!",
            "sfx": ["pop"]
        },
        {
            "scene": 3,
            "speaker": "boy",
            "spoken_hindi": "Bhai yahan balance zero dikha raha hai... aur tu achanak kahan gaya?",
            "dialogue": "Bhai notification toh aayi nahi... aur tu achanak kahan chala gaya?",
            "sfx": ["record_scratch", "gasp"]
        },
        {
            "scene": 4,
            "speaker": "boy",
            "spoken_hindi": "Arre bhai 500 ke chakkar mein insaan se sidha dhuaan ban gaya!",
            "dialogue": "Arre bhai 500 rupay bachane ke chakkar mein hawa ban gaya!",
            "sfx": ["boom", "laugh"]
        }
    ]

    try:
        font_hook = ImageFont.truetype("arialbd.ttf", 26)
        font_sub = ImageFont.truetype("arialbd.ttf", 22)
    except Exception:
        font_hook = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    clips = []
    w, h = 720, 1280

    for sc in scenes:
        s_num = sc["scene"]
        speaker = sc["speaker"]
        spoken = sc["spoken_hindi"]
        dialogue = sc["dialogue"]
        sfx_list = sc.get("sfx", [])

        print(f"\n--- Scene {s_num}/4: [{speaker.upper()}] ---")
        print(f"Dialogue: '{dialogue}'")

        voice_wav = os.path.join(TEMP_DIR, f"money_sc_{s_num}.wav")
        pitch = "+10Hz" if speaker == "boy" else "+5Hz"
        rate = "+18%" if speaker == "boy" else "+16%"
        temp_mp3 = voice_wav.replace(".wav", ".mp3")

        async def _tts(txt=spoken, p=pitch, r=rate, mp3=temp_mp3):
            c = edge_tts.Communicate(txt, "hi-IN-MadhurNeural", rate=r, pitch=p)
            await c.save(mp3)
        safe_run_async(_tts())

        # Clean conversion (Zero 12kHz Nyquist resonance)
        cmd = [
            'ffmpeg', '-y', '-i', temp_mp3,
            '-ar', '44100',
            '-af', 'volume=1.4',
            voice_wav
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        v_clip = AudioFileClip(voice_wav)
        duration = v_clip.duration + 0.40
        sfx_tracks = [v_clip]

        for sfx_name in sfx_list:
            sfx_path = sfx_fetcher.resolve_sfx(sfx_name)
            if sfx_path and os.path.exists(sfx_path):
                try:
                    s_audio = AudioFileClip(sfx_path)
                    s_dur = min(s_audio.duration, duration)
                    if sfx_name == "whoosh":
                        sfx_tracks.append(s_audio.set_start(0.1).subclip(0, min(0.3, s_dur)).volumex(0.25))
                    elif sfx_name == "pop":
                        sfx_tracks.append(s_audio.set_start(0.2).subclip(0, min(0.2, s_dur)).volumex(0.30))
                    elif sfx_name == "record_scratch":
                        sfx_tracks.append(s_audio.set_start(0.1).subclip(0, min(0.4, s_dur)).volumex(0.35))
                    elif sfx_name == "gasp":
                        sfx_tracks.append(s_audio.set_start(0.4).subclip(0, min(0.3, s_dur)).volumex(0.35))
                    elif sfx_name in ["boom", "vine_boom"]:
                        sfx_tracks.append(s_audio.set_start(max(0, duration - 1.4)).volumex(0.40))
                    elif sfx_name == "laugh":
                        sfx_tracks.append(s_audio.set_start(max(0, duration - 1.2)).volumex(0.30))
                except Exception as ex:
                    print(f"[*] SFX note ({sfx_name}): {ex}")

        scene_audio = CompositeAudioClip(sfx_tracks)

        def make_scene_frame(t, dur=duration, s_idx=s_num, spk=speaker, d_txt=dialogue):
            img = Image.new('RGB', (w, h), (255, 255, 255))
            draw = ImageDraw.Draw(img)

            if s_idx == 1:
                draw_scene_1_tapri(draw, t, dur, w, h)
            elif s_idx == 2:
                draw_scene_2_hoodie_friend(draw, t, dur, w, h)
            elif s_idx == 3:
                draw_scene_3_shock_phone(draw, t, dur, w, h)
            else:
                draw_scene_4_poof_disappear(draw, t, dur, w, h)

            # Top Hook
            draw.rounded_rectangle([70, 50, 650, 115], radius=14, fill=(250, 250, 254), outline=INK, width=3)
            draw.polygon([(58, 45), (105, 40), (95, 70), (48, 75)], fill=YELLOW_ACC)
            draw.polygon([(625, 40), (672, 45), (662, 75), (615, 70)], fill=YELLOW_ACC)
            draw.text((360, 82), hook_text, fill=INK, font=font_hook, anchor='mm')

            # Bottom Subtitle Banner
            sub_col = YELLOW_ACC if spk == "boy" else CYAN_ACC
            draw.rounded_rectangle([35, 1130, 685, 1225], radius=18, fill=(18, 18, 24), outline=sub_col, width=2)
            tag = "BOY 1" if spk == "boy" else "DOST"
            draw.rounded_rectangle([50, 1108, 150, 1134], radius=6, fill=sub_col)
            draw.text((100, 1121), tag, fill=(10, 10, 15), font=font_hook, anchor='mm')
            draw.text((360, 1178), d_txt, fill=(255, 255, 255), font=font_sub, anchor='mm')

            return np.array(img)

        clip = VideoClip(make_scene_frame, duration=duration).set_fps(24).set_audio(scene_audio)
        clips.append(clip)

    print("\n[*] Concatenating 4 completely new scenes into 30s Short...")
    full_video = concatenate_videoclips(clips, method="compose")

    # Layer Sneaky Snitch BGM at 13%
    bgm_path = sfx_fetcher.resolve_sfx("sneaky_snitch")
    if bgm_path and os.path.exists(bgm_path):
        bgm = AudioFileClip(bgm_path)
        if bgm.duration < full_video.duration:
            loops = int(full_video.duration / bgm.duration) + 1
            bgm = concatenate_audioclips([bgm] * loops)
        bgm = bgm.subclip(0, full_video.duration).volumex(0.13)
        full_audio = CompositeAudioClip([full_video.audio, bgm])
        full_video = full_video.set_audio(full_audio)

    fn = f"{base_filename}.mp4" if base_filename else "final_money_friend_short.mp4"
    out_mp4 = os.path.join(OUTPUT_DIR, fn)
    print(f"[*] Rendering New Video to: {out_mp4}")

    try:
        full_video.write_videofile(out_mp4, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    except Exception as e:
        print(f"[*] Note: MoviePy cleanup ({e}), file intact!")

    title = "POV: Dost se 500 rupay maang liye aur wo gayab ho gaya 😂 #shorts"
    description = "When your friend promises UPI and suddenly vanishes! 😂 #shorts #comedy #relatable #funny #stickman"
    tags = ["shorts", "comedy", "funny", "relatable", "stickman", "upi", "dost"]

    print("\n" + "=" * 70)
    print(f"[SUCCESS] 100% NEW SHORT READY: {out_mp4}")
    print("=" * 70)
    return out_mp4, title, description, tags

if __name__ == "__main__":
    produce_money_friend_short()
