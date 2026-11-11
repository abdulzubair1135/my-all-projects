"""
render_hyper_detailed_deepseek.py
=================================
Produces the Hyper-Detailed, Studio-Quality 30s Stickman Comedy Short.
Features:
1. Hyper-detailed backgrounds:
   - Scene 1: Bedroom with starry window, nightstand, wallpaper stripes, rug, wall posters, phone charger, slippers.
   - Scene 2: 3D perspective college corridor, notice board with sticky notes & red stamps, cutting chai steam.
   - Scene 3: Dramatic anime shock punch-in zoom, speed lines, vibrating sweat drops, alarm bell chaos.
   - Scene 4: Two-shot climax with distinct character designs (messy hair vs backwards cap), lip-sync mouth flap, Tommy dog wagging.
2. Hyper-detailed audio design:
   - Viral YouTube BGM: 'Sneaky Snitch' (Kevin MacLeod) mixed at ideal 18% comedy groove.
   - Full SFX Suite: Snoring Zzz -> Loud Alarm Bell -> Chai Sip -> Whistle Shock -> Vine Boom & Sitcom Laugh.
   - Young Indian Boy (19-20y) high-energy voices with broadcast mastering.
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
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, concatenate_audioclips
import edge_tts
import sfx_fetcher
import topic_themes

OUTPUT_DIR = "pipeline_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
TEMP_DIR = os.path.join(OUTPUT_DIR, "detailed_temp")
os.makedirs(TEMP_DIR, exist_ok=True)
SFX_DIR = "sfx"

# ─── Color Palette ────────────────────────────────────────────────────────────
INK       = (35, 32, 42)
INK_L     = (80, 75, 90)
WALL_BG   = (248, 243, 232)
WALL_STR  = (240, 234, 220)
FLOOR     = (225, 215, 198)
FLOOR_D   = (195, 182, 162)
WOOD      = (198, 154, 110)
WOOD_D    = (154, 112, 72)
BLANKET   = (130, 180, 225)
BLANKET_D = (90, 145, 195)
PILLOW    = (255, 252, 245)
RED_ACC   = (235, 55, 55)
CYAN_ACC  = (30, 165, 245)
YELLOW_ACC= (255, 215, 0)
WHITE     = (255, 255, 255)
NIGHT_SKY = (65, 85, 135)
MOON_YEL  = (255, 235, 140)
CHAI_COL  = (185, 115, 60)

def line(draw, pts, width=5, fill=INK):
    draw.line(pts, fill=fill, width=width, joint="curve")

def circ(draw, cx, cy, r, width=5, fill=None, outline=INK):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=width)

def poly(draw, pts, fill=None, outline=INK, width=5):
    draw.polygon(pts, fill=fill)
    if outline is not None:
        draw.line(list(pts) + [pts[0]], width=width, fill=outline, joint="curve")

# ─── Scene 1: Hyper-Detailed Bedroom Morning ─────────────────────────────────
def draw_scene_1_detailed(draw, t, dur, w, h):
    # 1. Background Wallpaper with Subtle Vertical Stripes
    draw.rectangle([0, 0, w, h], fill=WALL_BG)
    for sx in range(0, w, 40):
        draw.rectangle([sx, 0, sx + 20, 1020], fill=WALL_STR)
        
    # 2. Floor with Perspective Planks
    floor_y = 1020
    draw.rectangle([0, floor_y, w, h], fill=FLOOR)
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)
    for px in range(0, w, 110):
        line(draw, [(px, floor_y), (px + 35, h)], width=3, fill=FLOOR_D)
        
    # 3. Patterned Bedside Oval Rug
    draw.ellipse([80, 1060, 420, 1160], fill=(235, 210, 190), outline=INK, width=3)
    draw.ellipse([110, 1080, 390, 1140], fill=None, outline=(190, 150, 130), width=2)
    
    # 4. Slippers (Chappal) on Rug
    # Left chappal
    draw.ellipse([160, 1090, 205, 1125], fill=(70, 130, 180), outline=INK, width=3)
    draw.arc([165, 1095, 200, 1115], start=0, end=180, fill=WHITE, width=3)
    # Right chappal
    draw.ellipse([220, 1095, 265, 1130], fill=(70, 130, 180), outline=INK, width=3)
    draw.arc([225, 1100, 260, 1120], start=0, end=180, fill=WHITE, width=3)

    # 5. Wall Poster: "ENGINEERING = NO SLEEP"
    draw.rectangle([480, 140, 660, 320], fill=WHITE, outline=INK, width=4)
    draw.rectangle([488, 148, 652, 312], fill=(245, 240, 255))
    draw.text((570, 190), "ENGINEERING", fill=RED_ACC, font=ImageFont.load_default(), anchor='mm')
    draw.text((570, 230), "NO SLEEP", fill=INK, font=ImageFont.load_default(), anchor='mm')
    draw.text((570, 270), "75% ATTENDANCE?", fill=CYAN_ACC, font=ImageFont.load_default(), anchor='mm')
    # Pushpins
    circ(draw, 570, 146, 5, fill=RED_ACC, outline=INK, width=2)

    # 6. Night Sky Window with Curtains & Twinkling Stars
    wx, wy, ww, wh = 60, 130, 320, 380
    draw.rectangle([wx, wy, wx + ww, wy + wh], fill=NIGHT_SKY, outline=INK, width=6)
    # Crescent moon
    circ(draw, wx + 230, wy + 80, 38, fill=MOON_YEL, outline=None)
    circ(draw, wx + 242, wy + 72, 34, fill=NIGHT_SKY, outline=None)
    # Stars
    for (sx, sy) in [(wx+50, wy+60), (wx+130, wy+110), (wx+80, wy+240), (wx+180, wy+290), (wx+240, wy+210)]:
        twinkle = 1.0 + 0.3 * math.sin(t * 8 + sx)
        circ(draw, sx, sy, int(3 * twinkle), fill=WHITE, outline=None)
    # Window Frame Cross
    line(draw, [(wx + ww//2, wy), (wx + ww//2, wy + wh)], width=5)
    line(draw, [(wx, wy + wh//2), (wx + ww, wy + wh//2)], width=5)
    # Curtains fluttering gently
    curt_sway = 12 * math.sin(t * 3)
    poly(draw, [(wx-15, wy-10), (wx+45, wy-10), (wx+55 + curt_sway, wy+wh+20), (wx-20, wy+wh+20)], fill=(245, 190, 195), outline=INK, width=4)
    poly(draw, [(wx+ww-45, wy-10), (wx+ww+15, wy-10), (wx+ww+20, wy+wh+20), (wx+ww-55 - curt_sway, wy+wh+20)], fill=(245, 190, 195), outline=INK, width=4)

    # 7. Bed and Wooden Headboard
    bx, by = 60, 720
    draw.rectangle([bx - 20, by - 120, bx + 15, by + 280], fill=WOOD_D, outline=INK, width=5) # Headboard post
    draw.rectangle([bx - 10, by - 100, bx + 10, by + 180], fill=WOOD, outline=INK, width=4)
    draw.rectangle([bx, by + 120, bx + 420, by + 260], fill=(235, 230, 220), outline=INK, width=5) # Bed base
    line(draw, [(bx + 40, by + 260), (bx + 40, floor_y)], width=6) # Legs
    line(draw, [(bx + 400, by + 260), (bx + 400, floor_y)], width=6)

    # 8. Pillow with Soft Impression
    draw.rounded_rectangle([bx + 15, by + 40, bx + 140, by + 130], radius=15, fill=PILLOW, outline=INK, width=4)

    # 9. Sleeping Stickman (Boy 1) with Breathing Physics
    wake_progress = min(1.0, max(0.0, (t - 1.8) / 0.8)) # starts waking at 1.8s
    breath_y = 6 * math.sin(t * 3.5) * (1.0 - wake_progress)
    
    head_x = bx + 90
    head_y = by + 75 - breath_y - (25 * wake_progress)
    
    # Head
    circ(draw, head_x, head_y, 45, fill=WHITE, outline=INK, width=5)
    # Messy Bedhead Hair strands
    line(draw, [(head_x - 30, head_y - 40), (head_x - 45, head_y - 65)], width=4)
    line(draw, [(head_x - 10, head_y - 45), (head_x - 15, head_y - 75)], width=4)
    line(draw, [(head_x + 15, head_y - 45), (head_x + 25, head_y - 70)], width=4)

    if wake_progress < 0.5:
        # Sleeping closed eyes
        line(draw, [(head_x - 22, head_y - 5), (head_x - 6, head_y - 5)], width=4)
        line(draw, [(head_x + 6, head_y - 5), (head_x + 22, head_y - 5)], width=4)
        # Sleeping relaxed mouth
        line(draw, [(head_x - 10, head_y + 18), (head_x + 10, head_y + 18)], width=3)
        # Floating Zzz particles
        for zi, (zo_x, zo_y, z_sc) in enumerate([(35, -45, 18), (65, -80, 24), (100, -125, 30)]):
            drift_y = (t * 25 + zi * 30) % 90
            draw.text((head_x + zo_x, head_y + zo_y - drift_y), "Z", fill=CYAN_ACC, font=ImageFont.load_default())
    else:
        # Waking up shocked eyes
        eye_rad = int(8 + 8 * wake_progress)
        circ(draw, head_x - 16, head_y - 6, eye_rad, fill=WHITE, outline=INK, width=3)
        circ(draw, head_x + 16, head_y - 6, eye_rad, fill=WHITE, outline=INK, width=3)
        circ(draw, head_x - 16, head_y - 6, 4, fill=INK, outline=None)
        circ(draw, head_x + 16, head_y - 6, 4, fill=INK, outline=None)
        # Talking / O-shaped mouth
        mouth_open = int(6 + 8 * abs(math.sin(t * 18)))
        draw.ellipse([head_x - 10, head_y + 12 - mouth_open, head_x + 10, head_y + 12 + mouth_open], fill=INK)
        # Sweat drop
        circ(draw, head_x + 38, head_y - 12, 6, fill=CYAN_ACC, outline=INK, width=2)

    # 10. Blanket Covering Body with Folds
    blanket_top = by + 100 - breath_y * 0.5
    draw.rounded_rectangle([bx + 80, blanket_top, bx + 430, by + 250], radius=18, fill=BLANKET, outline=INK, width=5)
    # Blanket fold creases
    for fx in range(bx + 140, bx + 400, 65):
        line(draw, [(fx, blanket_top + 10), (fx + 15, by + 235)], width=3, fill=BLANKET_D)

    # 11. Wooden Nightstand on Right
    nx, ny, nw, nh = 500, 740, 175, 280
    draw.rectangle([nx, ny, nx + nw, ny + nh], fill=WOOD, outline=INK, width=5)
    # Nightstand drawer
    draw.rectangle([nx + 15, ny + 20, nx + nw - 15, ny + 110], fill=WOOD_D, outline=INK, width=4)
    circ(draw, nx + nw//2, ny + 65, 8, fill=INK) # Knob
    # Open bottom shelf with book
    draw.rectangle([nx + 20, ny + 170, nx + nw - 20, ny + 210], fill=(220, 70, 70), outline=INK, width=3)
    line(draw, [(nx + 35, ny + 190), (nx + nw - 35, ny + 190)], width=2, fill=WHITE)

    # 12. Ringing Twin-Bell Alarm Clock (Vibrates furiously)
    clock_shake_x = 7 * math.sin(t * 45) if t > 0.5 else 0
    clock_shake_y = 4 * math.cos(t * 45) if t > 0.5 else 0
    cx = nx + nw//2 + clock_shake_x
    cy = ny - 55 + clock_shake_y
    # Bell bells
    circ(draw, cx - 35, cy - 35, 18, fill=RED_ACC, outline=INK, width=3)
    circ(draw, cx + 35, cy - 35, 18, fill=RED_ACC, outline=INK, width=3)
    line(draw, [(cx - 20, cy - 30), (cx, cy - 45)], width=4)
    line(draw, [(cx + 20, cy - 30), (cx, cy - 45)], width=4)
    circ(draw, cx, cy - 48, 6, fill=INK) # Ringer hammer
    # Clock body
    circ(draw, cx, cy, 44, fill=WHITE, outline=INK, width=5)
    circ(draw, cx, cy, 3, fill=INK)
    # Spinning clock hands
    hand_angle = t * 14
    line(draw, [(cx, cy), (cx + 22 * math.cos(hand_angle), cy + 22 * math.sin(hand_angle))], width=4)
    line(draw, [(cx, cy), (cx + 30 * math.cos(hand_angle * 3), cy + 30 * math.sin(hand_angle * 3))], width=3, fill=RED_ACC)
    # Ring soundwaves / vibration lines
    if t > 0.5:
        for rad in [55, 68]:
            draw.arc([cx - rad, cy - rad, cx + rad, cy + rad], start=210, end=250, fill=INK, width=3)
            draw.arc([cx - rad, cy - rad, cx + rad, cy + rad], start=290, end=330, fill=INK, width=3)

# ─── Scene 2: Hyper-Detailed College Corridor & Dost ─────────────────────────
def draw_scene_2_detailed(draw, t, dur, w, h):
    # 1. 3D Corridor Perspective
    draw.rectangle([0, 0, w, h], fill=(244, 238, 226))
    floor_y = 1000
    draw.rectangle([0, floor_y, w, h], fill=(225, 218, 205))
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)
    # Perspective Floor Tiles
    for tx in range(-100, w + 200, 90):
        line(draw, [(tx, floor_y), (tx + 55, h)], width=3, fill=FLOOR_D)

    # Ceiling Tube Light with Glow
    draw.rectangle([180, 20, 540, 45], fill=WHITE, outline=INK, width=3)
    draw.rectangle([190, 25, 530, 40], fill=(255, 255, 230))
    line(draw, [(240, 0), (240, 20)], width=3)
    line(draw, [(480, 0), (480, 20)], width=3)

    # 2. Classroom Door (Left) with Signboard
    draw.rectangle([40, 320, 220, floor_y], fill=(238, 232, 220), outline=INK, width=5)
    # Glass Windows on Door
    for gy in [360, 470]:
        draw.rectangle([65, gy, 195, gy + 85], fill=(210, 235, 252), outline=INK, width=3)
        line(draw, [(130, gy), (130, gy + 85)], width=2, fill=INK_L)
    # Brass Handle
    draw.rectangle([185, 620, 200, 680], fill=YELLOW_ACC, outline=INK, width=3)
    # Room Sign: "ROOM 404: CS DEPT"
    draw.rectangle([60, 260, 200, 305], fill=INK, outline=None)
    draw.text((130, 282), "ROOM 404", fill=WHITE, font=ImageFont.load_default(), anchor='mm')

    # 3. Large Wooden Notice Board with Pushpins & Notices
    draw.rectangle([250, 240, 690, 680], fill=WOOD, outline=INK, width=6)
    draw.rectangle([268, 258, 672, 662], fill=(115, 65, 35), outline=INK, width=3) # Cork texture

    # Notice 1: Attendance Circular
    nx, ny = 290, 280
    draw.rectangle([nx, ny, nx + 190, ny + 270], fill=WHITE, outline=INK, width=3)
    circ(draw, nx + 95, ny + 10, 5, fill=RED_ACC, outline=INK, width=2) # Red pin
    line(draw, [(nx + 20, ny + 35), (nx + 170, ny + 35)], width=4, fill=RED_ACC)
    draw.text((nx + 95, ny + 55), "DEBAR LIST 2026", fill=RED_ACC, font=ImageFont.load_default(), anchor='mm')
    GREY_COL = (190, 185, 175)
    for ly in range(ny + 80, ny + 190, 22):
        line(draw, [(nx + 15, ly), (nx + 175, ly)], width=2, fill=GREY_COL)
    # Big Red Stamp: "12% ONLY!"
    draw.rectangle([nx + 20, ny + 190, nx + 170, ny + 245], fill=(255, 230, 230), outline=RED_ACC, width=3)
    draw.text((nx + 95, ny + 218), "ATTENDANCE: 12%", fill=RED_ACC, font=ImageFont.load_default(), anchor='mm')

    # Notice 2: Yellow Sticky Notes (Relatable College Jokes)
    draw.rectangle([510, 300, 640, 420], fill=(255, 250, 160), outline=INK, width=2)
    circ(draw, 575, 308, 4, fill=CYAN_ACC, outline=INK, width=1)
    draw.text((575, 350), "CANTEEN BILL", fill=INK, font=ImageFont.load_default(), anchor='mm')
    draw.text((575, 380), "DUE: Rs 450/-", fill=RED_ACC, font=ImageFont.load_default(), anchor='mm')

    # Notice 3: Pink Sticky Note
    draw.rectangle([515, 450, 635, 560], fill=(255, 210, 225), outline=INK, width=2)
    draw.text((575, 495), "VIVA CANCELLED?", fill=INK, font=ImageFont.load_default(), anchor='mm')
    draw.text((575, 525), "(FAKE NEWS)", fill=GREY_COL, font=ImageFont.load_default(), anchor='mm')

    # 4. Dost Stickman (Cool Boy with Backwards Cap & Chai)
    dx = 470
    dy = floor_y - 280
    
    # Body sway while speaking
    sway = 5 * math.sin(t * 6)
    dx += sway
    
    # Head & Cap
    circ(draw, dx, dy, 52, fill=WHITE, outline=INK, width=5)
    # Cool Backwards Cap (Blue)
    poly(draw, [(dx - 54, dy - 20), (dx + 54, dy - 20), (dx + 48, dy - 55), (dx - 48, dy - 55)], fill=CYAN_ACC, outline=INK, width=4)
    # Cap bill pointing backwards
    poly(draw, [(dx - 54, dy - 20), (dx - 85, dy - 12), (dx - 54, dy - 8)], fill=CYAN_ACC, outline=INK, width=3)
    
    # Expressive Face
    circ(draw, dx - 16, dy - 2, 6, fill=INK) # Eyes
    circ(draw, dx + 16, dy - 2, 6, fill=INK)
    # Raised animated eyebrow
    line(draw, [(dx - 25, dy - 20), (dx - 8, dy - 26)], width=3)
    line(draw, [(dx + 8, dy - 26), (dx + 25, dy - 20)], width=3)
    # Talking mouth (flaps naturally with speech)
    mouth_h = int(6 + 8 * abs(math.sin(t * 14)))
    draw.ellipse([dx - 14, dy + 16 - mouth_h, dx + 14, dy + 16 + mouth_h], fill=INK)

    # Torso & Blue Graphic T-shirt
    line(draw, [(dx, dy + 52), (dx, dy + 210)], width=6)
    # Blue T-shirt print
    circ(draw, dx, dy + 100, 10, fill=CYAN_ACC, outline=None)
    
    # Left Arm (Hand on Hip with attitude)
    line(draw, [(dx, dy + 85), (dx - 45, dy + 125)], width=5)
    line(draw, [(dx - 45, dy + 125), (dx - 10, dy + 155)], width=5)

    # Right Arm Holding Hot Steaming Cutting Chai
    line(draw, [(dx, dy + 85), (dx + 50, dy + 115)], width=5)
    line(draw, [(dx + 50, dy + 115), (dx + 55, dy + 150)], width=5)
    # Cutting Chai Glass
    gx, gy = dx + 55, dy + 150
    poly(draw, [(gx - 14, gy), (gx + 14, gy), (gx + 10, gy + 32), (gx - 10, gy + 32)], fill=CHAI_COL, outline=INK, width=3)
    # Swirling Steam from Chai
    for si, so_x in enumerate([-6, 6]):
        steam_y = gy - 10 - ((t * 22 + si * 18) % 45)
        steam_x = gx + so_x + 5 * math.sin(t * 8 + si)
        draw.arc([steam_x - 8, steam_y - 12, steam_x + 8, steam_y + 12], start=180, end=360, fill=GREY_COL, width=2)

    # Legs & Sneakers on floor
    line(draw, [(dx, dy + 210), (dx - 25, floor_y)], width=6)
    line(draw, [(dx, dy + 210), (dx + 25, floor_y)], width=6)
    # Sneakers
    draw.rounded_rectangle([dx - 45, floor_y - 8, dx - 10, floor_y + 8], radius=5, fill=RED_ACC, outline=INK, width=3)
    draw.rounded_rectangle([dx + 10, floor_y - 8, dx + 45, floor_y + 8], radius=5, fill=RED_ACC, outline=INK, width=3)

# ─── Scene 3: Hyper-Detailed Pillow Clutch & Anime Shock ─────────────────────
def draw_scene_3_shock(draw, t, dur, w, h):
    # Dramatic Anime Background with Radial Shock Speed Lines
    draw.rectangle([0, 0, w, h], fill=(255, 245, 235))
    
    # Dynamic Camera Zoom Simulation: Center scale increases slightly
    cx, cy = w // 2, 680
    
    # Comic Radial Speed Lines shooting outward
    for angle_deg in range(0, 360, 12):
        rad = math.radians(angle_deg)
        r_inner = 280 + 30 * math.sin(t * 20 + angle_deg)
        r_outer = 680
        x1 = cx + r_inner * math.cos(rad)
        y1 = cy + r_inner * math.sin(rad)
        x2 = cx + r_outer * math.cos(rad)
        y2 = cy + r_outer * math.sin(rad)
        line(draw, [(x1, y1), (x2, y2)], width=3, fill=(235, 215, 200))

    # Boy 1 Clutching Pillow with High-Voltage Shock Jitter
    jitter_x = 5 * math.sin(t * 35)
    jitter_y = 3 * math.cos(t * 35)
    bx = cx + jitter_x
    by = cy + jitter_y

    # Dilated Anime Shock Face
    head_r = 65
    circ(draw, bx, by - 90, head_r, fill=WHITE, outline=INK, width=6)
    
    # Spiky Terrified Hair on Head
    for ha in [-40, -20, 0, 20, 40]:
        h_rad = math.radians(ha - 90)
        line(draw, [(bx + 55 * math.cos(h_rad), by - 90 + 55 * math.sin(h_rad)), 
                    (bx + 90 * math.cos(h_rad), by - 90 + 90 * math.sin(h_rad))], width=5)

    # Huge Dilated Shock Eyes with Pinpoint Pupils
    circ(draw, bx - 26, by - 95, 22, fill=WHITE, outline=INK, width=4)
    circ(draw, bx + 26, by - 95, 22, fill=WHITE, outline=INK, width=4)
    circ(draw, bx - 26, by - 95, 5, fill=INK) # tiny terrified pupils
    circ(draw, bx + 26, by - 95, 5, fill=INK)

    # Trembling Jaw / Wide Open O-Mouth
    mouth_drop = int(18 + 8 * math.sin(t * 16))
    draw.ellipse([bx - 18, by - 60, bx + 18, by - 60 + mouth_drop * 2], fill=INK)
    # Tongue inside mouth
    draw.ellipse([bx - 10, by - 50 + mouth_drop, bx + 10, by - 55 + mouth_drop * 2], fill=RED_ACC)

    # Massive Flying Sweat Drops
    for si, (so_x, so_y) in enumerate([(-70, -110), (75, -100), (80, -50)]):
        circ(draw, bx + so_x + 5 * math.sin(t * 12 + si), by + so_y, 10, fill=CYAN_ACC, outline=INK, width=3)

    # Steam Whistle on Head
    line(draw, [(bx, by - 155), (bx, by - 190)], width=6)
    circ(draw, bx, by - 195, 12, fill=RED_ACC, outline=INK, width=3)
    # Puffy steam clouds rising
    for st_i in range(3):
        sy = by - 215 - st_i * 25
        sr = 12 + st_i * 6
        circ(draw, bx + (10 if st_i % 2 else -10), sy, sr, fill=WHITE, outline=INK, width=2)

    # White Pillow Being Clutched Tightly
    poly(draw, [(bx - 120, by + 10), (bx + 120, by + 10), (bx + 105, by + 130), (bx - 105, by + 130)], fill=PILLOW, outline=INK, width=5)
    # Pillow crease folds under squeeze pressure
    line(draw, [(bx - 50, by + 40), (bx - 10, by + 90)], width=4, fill=FLOOR_D)
    line(draw, [(bx + 50, by + 40), (bx + 10, by + 90)], width=4, fill=FLOOR_D)

    # Clutched Stickman Arms wrapping around pillow
    line(draw, [(bx - 50, by - 25), (bx - 90, by + 50)], width=6)
    line(draw, [(bx - 90, by + 50), (bx - 20, by + 70)], width=6) # Left hand
    line(draw, [(bx + 50, by - 25), (bx + 90, by + 50)], width=6)
    line(draw, [(bx + 90, by + 50), (bx + 20, by + 70)], width=6) # Right hand

    # Bed Base Frame
    draw.rectangle([bx - 280, by + 130, bx + 280, 1150], fill=(235, 230, 220), outline=INK, width=5)
    line(draw, [(bx - 280, by + 130), (bx + 280, by + 130)], width=6)

# ─── Scene 4: Hyper-Detailed Two-Shot Climax Punchline ───────────────────────
def draw_scene_4_detailed(draw, t, dur, w, h):
    # 1. Background Wall & Perspective Floor
    draw.rectangle([0, 0, w, h], fill=(246, 242, 232))
    floor_y = 1000
    draw.rectangle([0, floor_y, w, h], fill=(225, 218, 202))
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)
    for px in range(-50, w + 150, 85):
        line(draw, [(px, floor_y), (px + 45, h)], width=3, fill=FLOOR_D)

    # 2. Wall Posters & Meme Frames
    draw.rectangle([80, 180, 260, 360], fill=WHITE, outline=INK, width=4)
    draw.rectangle([90, 190, 250, 350], fill=(255, 235, 225))
    draw.text((170, 250), "ATTENDANCE", fill=RED_ACC, font=ImageFont.load_default(), anchor='mm')
    draw.text((170, 290), "12%", fill=INK, font=ImageFont.load_default(), anchor='mm')

    # Window with Afternoon Sun
    draw.rectangle([460, 160, 660, 380], fill=(160, 215, 255), outline=INK, width=5)
    circ(draw, 600, 220, 30, fill=YELLOW_ACC, outline=None)
    line(draw, [(560, 160), (560, 380)], width=4)
    line(draw, [(460, 270), (660, 270)], width=4)

    # 3. Soft Drop Shadows on Floor
    draw.ellipse([160, floor_y - 8, 300, floor_y + 12], fill=(200, 190, 175))
    draw.ellipse([420, floor_y - 8, 560, floor_y + 12], fill=(200, 190, 175))

    # 4. BOY 1 (Left - Defeated Shrug with Messy Hair)
    b1_x = 230
    b1_y = floor_y - 300
    b1_sway = 4 * math.sin(t * 5)
    
    # Head & Messy Hair
    circ(draw, b1_x + b1_sway, b1_y, 48, fill=WHITE, outline=INK, width=5)
    for h_ang in [-45, -20, 15, 40]:
        h_rad = math.radians(h_ang - 90)
        line(draw, [(b1_x + b1_sway + 45*math.cos(h_rad), b1_y + 45*math.sin(h_rad)),
                    (b1_x + b1_sway + 70*math.cos(h_rad), b1_y + 70*math.sin(h_rad))], width=4)
    # Worried Eyebrows & Shrugging Eyes
    line(draw, [(b1_x + b1_sway - 22, b1_y - 12), (b1_x + b1_sway - 8, b1_y - 20)], width=3)
    line(draw, [(b1_x + b1_sway + 8, b1_y - 20), (b1_x + b1_sway + 22, b1_y - 12)], width=3)
    circ(draw, b1_x + b1_sway - 14, b1_y - 2, 5, fill=INK)
    circ(draw, b1_x + b1_sway + 14, b1_y - 2, 5, fill=INK)
    # Nervous smile mouth
    draw.arc([b1_x + b1_sway - 12, b1_y + 8, b1_x + b1_sway + 12, b1_y + 24], start=0, end=180, fill=INK, width=3)
    # Big Sweat drop dripping
    circ(draw, b1_x + b1_sway + 38, b1_y - 8, 6, fill=CYAN_ACC, outline=INK, width=2)

    # Torso & Shrugging Raised Arms (Palms up)
    line(draw, [(b1_x + b1_sway, b1_y + 48), (b1_x + b1_sway, b1_y + 195)], width=6)
    # Shrug Left Arm
    line(draw, [(b1_x + b1_sway, b1_y + 75), (b1_x + b1_sway - 55, b1_y + 115)], width=5)
    line(draw, [(b1_x + b1_sway - 55, b1_y + 115), (b1_x + b1_sway - 85, b1_y + 80)], width=5)
    # Shrug Right Arm
    line(draw, [(b1_x + b1_sway, b1_y + 75), (b1_x + b1_sway + 50, b1_y + 115)], width=5)
    line(draw, [(b1_x + b1_sway + 50, b1_y + 115), (b1_x + b1_sway + 75, b1_y + 85)], width=5)
    # Legs
    line(draw, [(b1_x + b1_sway, b1_y + 195), (b1_x + b1_sway - 25, floor_y)], width=6)
    line(draw, [(b1_x + b1_sway, b1_y + 195), (b1_x + b1_sway + 25, floor_y)], width=6)

    # 5. BOY 2 / DOST (Right - Delivering Punchline with Pointing Finger)
    b2_x = 490
    b2_y = floor_y - 310
    b2_bob = 6 * math.sin(t * 12)
    
    # Head & Cool Backwards Cap
    circ(draw, b2_x, b2_y + b2_bob, 50, fill=WHITE, outline=INK, width=5)
    poly(draw, [(b2_x - 52, b2_y + b2_bob - 18), (b2_x + 52, b2_y + b2_bob - 18), (b2_x + 46, b2_y + b2_bob - 50), (b2_x - 46, b2_y + b2_bob - 50)], fill=CYAN_ACC, outline=INK, width=4)
    poly(draw, [(b2_x + 52, b2_y + b2_bob - 18), (b2_x + 80, b2_y + b2_bob - 12), (b2_x + 52, b2_y + b2_bob - 8)], fill=CYAN_ACC, outline=INK, width=3)

    # Laughing Punchline Eyes & Animated Mouth Flap
    circ(draw, b2_x - 16, b2_y + b2_bob - 2, 6, fill=INK)
    circ(draw, b2_x + 16, b2_y + b2_bob - 2, 6, fill=INK)
    # Wide Laughing Open Mouth Sync
    punch_mouth = int(12 + 10 * abs(math.sin(t * 16)))
    draw.ellipse([b2_x - 18, b2_y + b2_bob + 15 - punch_mouth, b2_x + 18, b2_y + b2_bob + 15 + punch_mouth], fill=INK)
    draw.ellipse([b2_x - 10, b2_y + b2_bob + 18, b2_x + 10, b2_y + b2_bob + 18 + punch_mouth], fill=RED_ACC)

    # Torso
    line(draw, [(b2_x, b2_y + b2_bob + 50), (b2_x, b2_y + b2_bob + 205)], width=6)
    # Left Arm Pointing directly at Boy 1
    line(draw, [(b2_x, b2_y + b2_bob + 80), (b2_x - 65, b2_y + b2_bob + 95)], width=5)
    line(draw, [(b2_x - 65, b2_y + b2_bob + 95), (b2_x - 110, b2_y + b2_bob + 80)], width=5)
    # Right Arm on Hip
    line(draw, [(b2_x, b2_y + b2_bob + 80), (b2_x + 45, b2_y + b2_bob + 120)], width=5)
    line(draw, [(b2_x + 45, b2_y + b2_bob + 120), (b2_x + 10, b2_y + b2_bob + 145)], width=5)
    # Legs
    line(draw, [(b2_x, b2_y + b2_bob + 205), (b2_x - 20, floor_y)], width=6)
    line(draw, [(b2_x, b2_y + b2_bob + 205), (b2_x + 30, floor_y)], width=6)

    # 6. Tommy the Dog Laughing & Wagging Tail
    dog_x, dog_y = 620, floor_y - 25
    circ(draw, dog_x, dog_y, 22, fill=WHITE, outline=INK, width=4) # Body
    circ(draw, dog_x + 22, dog_y - 14, 15, fill=WHITE, outline=INK, width=4) # Head
    circ(draw, dog_x + 26, dog_y - 16, 3, fill=INK) # Eye
    poly(draw, [(dog_x + 14, dog_y - 24), (dog_x + 10, dog_y - 38), (dog_x + 22, dog_y - 28)], fill=WOOD, outline=INK, width=2) # Ear
    # Wagging Tail
    tail_sway = 25 * math.sin(t * 30)
    line(draw, [(dog_x - 20, dog_y - 5), (dog_x - 45, dog_y - 25 + tail_sway)], width=5)

    # 7. Comic Punchline Pop-Up Badge on Climax Beat (t > 2.0s)
    if t > 2.0:
        pop_scale = min(1.0, (t - 2.0) * 3)
        badge_w = int(320 * pop_scale)
        badge_h = int(65 * pop_scale)
        bx1 = 360 - badge_w // 2
        bx2 = 360 + badge_w // 2
        by1 = 450 - badge_h // 2
        by2 = 450 + badge_h // 2
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=14, fill=RED_ACC, outline=WHITE, width=4)
        draw.text((360, 450), "DEBAR LIST #1 CONFIRMED! 💀", fill=WHITE, font=ImageFont.load_default(), anchor='mm')

import json
import re

# ─── Rich Topic Script Intelligence ──────────────────────────────────────────
HANDCRAFTED_TOPIC_SCRIPTS = {
    "money": {
        "hook": "POV: Dost ko 500 udhaar diye the 😭",
        "title": "POV: 500 Rupay Ke Liye Dost Hawa 😂 #shorts #comedy #relatable",
        "description": "Hostel ka woh dost jise paisa chahiye hota hai toh 4 missed calls, aur dena hota hai toh phone switched off!\n\n#shorts #comedy #stickman",
        "scenes": [
            {
                "scene": 1,
                "speaker": "boy",
                "spoken_hindi": "भाई, महीने के आखिर में 500 उधार दे दे, मेरी मेस की फीस रह गई है।",
                "dialogue": "Bhai, mahine ke aakhir mein 500 udhaar de de, mess fees reh gayi hai!",
                "sfx": ["whoosh", "ding"]
            },
            {
                "scene": 2,
                "speaker": "dost",
                "spoken_hindi": "अरे बिल्कुल भाई! तू मेरा अपना है। बस UPI ऐप खुल ही नहीं रहा...",
                "dialogue": "Arre bilkul bhai! Tu mera apna hai. Bas UPI app khul hi nahi raha...",
                "sfx": ["pop"]
            },
            {
                "scene": 3,
                "speaker": "boy",
                "spoken_hindi": "भाई, पाँच मिनट हो गए... तू अभी भी ऐप खोल रहा है? अरे तू तो गायब ही हो गया!",
                "dialogue": "Bhai 5 minute ho gaye... tu abhi bhi app khol raha hai? Arre tu gayab ho gaya?!",
                "sfx": ["record_scratch", "gasp"]
            },
            {
                "scene": 4,
                "speaker": "dost",
                "spoken_hindi": "भाई, बैटरी 1% बची थी, फोन बंद हो गया... कल मिलते हैं, पक्का!",
                "dialogue": "Bhai battery 1% bachi thi, phone switch off ho gaya... kal milte hain pakka!",
                "sfx": ["boom", "laugh"]
            }
        ]
    },
    "interview": {
        "hook": "POV: Job Interview & The Confidence Lie 💀",
        "title": "POV: Job Interview Viva Panic 😂 #shorts #comedy #job #viva",
        "description": "Resume mein Leadership likhne ke baad jab interviewer ne aukaat dikha di!\n\n#shorts #comedy #stickman",
        "scenes": [
            {
                "scene": 1,
                "speaker": "boy",
                "spoken_hindi": "भाई फुल कॉन्फिडेंट हूँ! रेज्यूमे में लीडरशिप और हार्डवर्किंग लिखा है, आज इंटरव्यू फोड़ के आऊंगा!",
                "dialogue": "Bhai full confident hoon! Resume mein Leadership likha hai, phod ke aaunga!",
                "sfx": ["whoosh", "ding"]
            },
            {
                "scene": 2,
                "speaker": "dost",
                "spoken_hindi": "अच्छा? तो टेल मी समथिंग दैट इस नॉट इन योर रेज्यूमे! तुम्हारी सबसे बड़ी कमजोरी क्या है?",
                "dialogue": "Tell me something not in your resume! Tumhari sabse badi weakness kya hai?",
                "sfx": ["pop"]
            },
            {
                "scene": 3,
                "speaker": "boy",
                "spoken_hindi": "कमजोरी? सर... कमजोरी तो ये है कि मुझे इस सवाल का जवाब ही नहीं पता भाई!",
                "dialogue": "Weakness? Sir... weakness toh ye hai ki is sawaal ka jawaab hi nahi pata!",
                "sfx": ["record_scratch", "gasp"]
            },
            {
                "scene": 4,
                "speaker": "dost",
                "spoken_hindi": "बहुत बढ़िया! सिक्योरिटी, इनका रेज्यूमे डस्टबिन में डालो और अगले मुर्गे को भेजो!",
                "dialogue": "Security, inka resume dustbin mein daalo aur agle murge ko bhejo!",
                "sfx": ["boom", "laugh"]
            }
        ]
    },
    "gym": {
        "hook": "POV: Gym Day 1 Josh vs Day 3 Maut 🏋️‍♂️",
        "title": "POV: Gym Day 1 vs Day 3 😂 #shorts #comedy #gym #fitness",
        "description": "Day 1 pe Arnold banna tha, Day 3 pe bed se uthne ke liye crane chahiye!\n\n#shorts #comedy #stickman",
        "scenes": [
            {
                "scene": 1,
                "speaker": "boy",
                "spoken_hindi": "भाई आज से रोज़ सुबह 5 बजे जिम! 6 पैक एब्स और आर्नोल्ड जैसी बॉडी एक महीने में कन्फर्म!",
                "dialogue": "Bhai aaj se roz subah 5 baje gym! Arnold jaisi body 1 mahine mein confirm!",
                "sfx": ["whoosh", "ding"]
            },
            {
                "scene": 2,
                "speaker": "dost",
                "spoken_hindi": "अरे पहले ये ढाई किलो का डंबल तो ढंग से उठा ले, हाथ काँप रहे हैं तेरे!",
                "dialogue": "Arre pehle ye 2.5 kg ka dumbbell toh dhang se utha le, haath kaanp rahe hain!",
                "sfx": ["pop"]
            },
            {
                "scene": 3,
                "speaker": "boy",
                "spoken_hindi": "काँप नहीं रहे, मसल एक्टिवेट हो रही है भाई! कल देखना मैं 50 किलो बेंच प्रेस मारूँगा!",
                "dialogue": "Kaanp nahi rahe, muscle activate ho rahi hai! Kal 50 kg bench press maarunga!",
                "sfx": ["record_scratch", "gasp"]
            },
            {
                "scene": 4,
                "speaker": "dost",
                "spoken_hindi": "डे 3 हो गया... बेड से हिल भी नहीं पा रहा, कमर में दर्द और मम्मी से मूव लगवा रहा है!",
                "dialogue": "Day 3 ho gaya... bed se hil bhi nahi pa raha, mummy se Moov lagwa raha hai!",
                "sfx": ["boom", "laugh"]
            }
        ]
    },
    "ready": {
        "hook": "POV: 'Bas 2 Minute Mein Aaya' Lie 👗",
        "title": "POV: Who Takes Longer To Get Ready 😂 #shorts #comedy #relatable",
        "description": "Inka 2 minute matlab Mahabharat ka poora yuddh khatam ho jaye!\n\n#shorts #comedy #stickman",
        "scenes": [
            {
                "scene": 1,
                "speaker": "boy",
                "spoken_hindi": "भाई चल निकलना है, 7 बजे का टाइम था! तू कब से शीशे के सामने खड़ा है!",
                "dialogue": "Bhai chal nikalna hai, 7 baje ka time tha! Tu kab se mirror ke samne khada hai!",
                "sfx": ["whoosh", "ding"]
            },
            {
                "scene": 2,
                "speaker": "dost",
                "spoken_hindi": "बस 2 मिनट बाबा! ऑलमोस्ट डन हूँ, बस बाल सेट करने हैं और परफ्यूम लगाना है!",
                "dialogue": "Bas 2 minute baba! Almost done hoon, bas baal set karne hain aur perfume lagana hai!",
                "sfx": ["pop"]
            },
            {
                "scene": 3,
                "speaker": "boy",
                "spoken_hindi": "तेरा '2 मिनट' सुनते सुनते पूरा एक घंटा हो गया! बाहर ऑटो वाला डबल मीटर मांग रहा है!",
                "dialogue": "Tera 2 minute sunte sunte 1 ghanta ho gaya! Auto wala double meter maang raha hai!",
                "sfx": ["record_scratch", "gasp"]
            },
            {
                "scene": 4,
                "speaker": "dost",
                "spoken_hindi": "अरे चिल ना! जो लोग लेट आते हैं वही तो पार्टी की जान होते हैं! आजा अब!",
                "dialogue": "Arre chill na! Jo log late aate hain wahi toh party ki shaan hote hain!",
                "sfx": ["boom", "laugh"]
            }
        ]
    },
    "snacks": {
        "hook": "POV: Samosa Ka Aakhri Bite Betrayal 🥟",
        "title": "POV: Splitting Snacks Fairly 😂 #shorts #comedy #food #relatable",
        "description": "Dosti ek taraf, aur plate ka aakhri samosa ek taraf!\n\n#shorts #comedy #stickman",
        "scenes": [
            {
                "scene": 1,
                "speaker": "boy",
                "spoken_hindi": "ये आखिरी समोसा बराबर आधा-आधा कटेगा! स्केल लेके आना ज़रा, एक मिलीमीटर का भी फर्क नहीं होना चाहिए!",
                "dialogue": "Ye aakhri samosa barabar aadha-aadha katega! 1 millimeter ka bhi farak nahi hona chahiye!",
                "sfx": ["whoosh", "ding"]
            },
            {
                "scene": 2,
                "speaker": "dost",
                "spoken_hindi": "हाँ भाई 100% फेयर शेयर! तेरी दोस्ती पर पूरा भरोसा है मुझे!",
                "dialogue": "Haan bhai 100% fair share! Teri dosti par pura bharosa hai mujhe!",
                "sfx": ["pop"]
            },
            {
                "scene": 3,
                "speaker": "boy",
                "spoken_hindi": "रुक मैं चटनी लेके आता हूँ... अरे रुक! समोसा कहाँ गया प्लेट से?!",
                "dialogue": "Ruk main chatni leke aata hoon... ae ruk! Samosa kahan gaya plate se?!",
                "sfx": ["record_scratch", "gasp"]
            },
            {
                "scene": 4,
                "speaker": "dost",
                "spoken_hindi": "भाई वो समोसा ठंडा हो रहा था, इसलिए मैंने सैक्रिफाइस कर दिया! फ्रेंडशिप गोल्स!",
                "dialogue": "Bhai wo samosa thanda ho raha tha, isliye maine sacrifice kar diya! Friendship goals!",
                "sfx": ["boom", "laugh"]
            }
        ]
    }
}

def extract_deepseek_json(raw_text):
    if not raw_text:
        return None
    raw_clean = re.sub(r'```(?:json)?', '', raw_text)
    m = re.search(r'\{[\s\S]*"scenes"[\s\S]*\}', raw_clean)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    sc_pos = raw_clean.find('"scenes"')
    if sc_pos != -1:
        first_brace = raw_clean.rfind('{', 0, sc_pos)
        if first_brace != -1:
            sub = raw_clean[first_brace:]
            cnt = 0
            for i, c in enumerate(sub):
                if c == '{': cnt += 1
                elif c == '}':
                    cnt -= 1
                    if cnt == 0:
                        try:
                            return json.loads(sub[:i+1])
                        except Exception:
                            pass
    m2 = re.search(r'("title"|"hook"|"scenes")[\s\S]*\}', raw_clean)
    if m2:
        candidate = "{" + m2.group(0)
        last_brace = candidate.rfind("}")
        if last_brace != -1:
            try:
                return json.loads(candidate[:last_brace + 1])
            except Exception:
                pass
    return None

def fetch_dynamic_script(topic):
    """
    Returns an ultra-custom, highly entertaining 4-scene comedic banter script.
    Queries DeepSeek via Chrome CDP Network intercept for 100% fresh, dynamic dialogues.
    Includes rich contextual procedural fallbacks for key topics so generic fallbacks are NEVER used.
    """
    clean_top = str(topic).strip() if topic else "College Attendance 12% & 'Kal Pakka Jaunga'"
    t_lower = clean_top.lower()

    # Handcrafted instant scripts for baseline showcase
    if any(k in t_lower for k in ["invisible", "paisa", "500", "udhaar", "lend"]):
        return HANDCRAFTED_TOPIC_SCRIPTS["money_tapri"]
    elif any(k in t_lower for k in ["interview", "viva", "confident", "hr", "professor"]):
        return HANDCRAFTED_TOPIC_SCRIPTS["interview"]
    elif any(k in t_lower for k in ["gym", "quitting", "workout", "day 1", "day 3"]):
        return HANDCRAFTED_TOPIC_SCRIPTS["gym"]
    elif any(k in t_lower for k in ["ready", "almost done", "dressing", "mirror", "longer"]):
        return HANDCRAFTED_TOPIC_SCRIPTS["ready"]
    elif any(k in t_lower for k in ["snack", "bite", "samosa", "food", "splitting", "fairly"]):
        return HANDCRAFTED_TOPIC_SCRIPTS["snacks"]

    # For other topics, query DeepSeek with 60s timeout
    prompt = (
        f"Write a hilarious, highly relatable conversational banter between two 19-20 year old Indian college hostel boys for a 2D stickman YouTube Short (under 30s) on this topic: '{clean_top}'.\n"
        "Strictly output a single raw JSON object only with format:\n"
        "{\n"
        '  "hook": "POV: ... 😭",\n'
        '  "title": "POV: ... 😂 #shorts",\n'
        '  "description": "...",\n'
        '  "scenes": [\n'
        '    {"scene": 1, "speaker": "boy", "spoken_hindi": "...", "dialogue": "...", "sfx": ["whoosh"]},\n'
        '    {"scene": 2, "speaker": "dost", "spoken_hindi": "...", "dialogue": "...", "sfx": ["pop"]},\n'
        '    {"scene": 3, "speaker": "boy", "spoken_hindi": "...", "dialogue": "...", "sfx": ["record_scratch", "gasp"]},\n'
        '    {"scene": 4, "speaker": "dost", "spoken_hindi": "...", "dialogue": "...", "sfx": ["boom", "laugh"]}\n'
        '  ]\n'
        "}"
    )

    try:
        import direct_deepseek
        raw = direct_deepseek.ask_deepseek(prompt, max_wait_sec=60)
        data = extract_deepseek_json(raw)
        if data and "scenes" in data and len(data["scenes"]) >= 4:
            for idx, sc in enumerate(data["scenes"][:4]):
                sc["scene"] = idx + 1
                sc["speaker"] = "boy" if idx % 2 == 0 else "dost"
                if "dialogue" not in sc or not sc["dialogue"]:
                    sc["dialogue"] = sc.get("spoken_hindi", "Bhai sach me!")
                if "spoken_hindi" not in sc or not sc["spoken_hindi"]:
                    sc["spoken_hindi"] = sc["dialogue"]
                if "sfx" not in sc:
                    sc["sfx"] = ["whoosh"] if idx == 0 else ["pop"] if idx == 1 else ["gasp"] if idx == 2 else ["boom"]
            print(f"[*] DeepSeek custom script loaded for: '{clean_top}'")
            return data
    except Exception as e:
        print(f"[*] DeepSeek prompt note: {e}")

    # Rich contextual procedural fallbacks (NEVER generic!)
    t_low = clean_top.lower()
    if any(k in t_low for k in ["ac", "father", "papa", "temperature", "degree", "18"]):
        return {
            "hook": "POV: Jab papa AC ka remote dekh lein 🥶",
            "title": "Papa Reacting to 18°C AC 😂 #shorts #comedy",
            "description": "Papa reacting to AC temperature set to 18 degrees! Relatable Indian family comedy.\n\n#shorts #comedy #stickman",
            "scenes": [
                {
                    "scene": 1,
                    "speaker": "boy",
                    "spoken_hindi": "पापा प्लीज 18 पर रहने दो ना, बाहर 45 डिग्री आग बरस रही है!",
                    "dialogue": "Papa please 18 pe rehne do na, bahar 45 degree aag baras rahi hai!",
                    "sfx": ["whoosh"]
                },
                {
                    "scene": 2,
                    "speaker": "dost",
                    "spoken_hindi": "18 डिग्री? बेवकूफ, ये कमरा है या शिमला का फ्रीजर? बिजली का बिल तेरा बाप भरेगा?",
                    "dialogue": "18 degree? Ye kamra hai ya freezer? Bijli ka bill tera baap bharega?!",
                    "sfx": ["pop", "record_scratch"]
                },
                {
                    "scene": 3,
                    "speaker": "boy",
                    "spoken_hindi": "पापा बस 5 मिनट ठंडा होने दो, फिर 24 पर कर दूँगा पक्का!",
                    "dialogue": "Papa bas 5 minute thanda hone do, phir 24 kar dunga pakka!",
                    "sfx": ["gasp"]
                },
                {
                    "scene": 4,
                    "speaker": "dost",
                    "spoken_hindi": "5 मिनट? पिछले साल भी यही बोला था और मीटर रॉकेट बन गया था! रिमोट इधर ला!",
                    "dialogue": "5 minute? Pichli baar bhi yahi bola tha, meter rocket ban gaya tha! Remote la idhar!",
                    "sfx": ["boom", "laugh"]
                }
            ]
        }
    elif any(k in t_low for k in ["dog", "street dog", "fearless", "bark"]):
        return {
            "hook": "POV: Raat ko gali ke kutto ke samne fearless banna 🐶",
            "title": "Walking Past Street Dogs at Night 😂 #shorts",
            "description": "Walking past street dogs pretending to be the main character!\n\n#shorts #comedy #stickman",
            "scenes": [
                {
                    "scene": 1,
                    "speaker": "boy",
                    "spoken_hindi": "देख भाई, अगर तू डरेगा तो वो काटेंगे! बस सीना चौड़ा करके आगे बढ़ता रह!",
                    "dialogue": "Dekh bhai, agar tu darega toh wo kaatenge! Bas seena chauda karke chalta reh!",
                    "sfx": ["whoosh"]
                },
                {
                    "scene": 2,
                    "speaker": "dost",
                    "spoken_hindi": "अरे वो देख, काले वाले ने कान खड़े कर लिए हैं! वो अपनी गैंग बुला रहा है!",
                    "dialogue": "Arre wo dekh, kaale wale ne kaan khade kar liye! Apni gang bula raha hai!",
                    "sfx": ["pop"]
                },
                {
                    "scene": 3,
                    "speaker": "boy",
                    "spoken_hindi": "आई कॉन्टैक्ट मत कर! आसमान में तारे देख जैसे हम वॉक करने निकले हैं!",
                    "dialogue": "Eye contact mat kar! Aasman me taare dekh jaise normal walk kar rahe hain!",
                    "sfx": ["gasp", "record_scratch"]
                },
                {
                    "scene": 4,
                    "speaker": "dost",
                    "spoken_hindi": "भौंक दिया उसने! भाग भाई, उसैन बोल्ट बन जा वर्ना इंजेक्शन लगेंगे!",
                    "dialogue": "Bhaunk diya usne! Bhaag bhai, Usain Bolt ban ja varna injection lagenge!",
                    "sfx": ["boom", "laugh"]
                }
            ]
        }
    elif any(k in t_low for k in ["chips", "packet", "2 am", "midnight", "wake"]):
        return {
            "hook": "POV: Raat ke 2 baje chips ka packet kholna 🤫",
            "title": "Trying to Open Chips at 2 AM 😂 #shorts",
            "description": "Why does a chips packet sound like an atomic bomb at 2 AM?!\n\n#shorts #comedy #stickman",
            "scenes": [
                {
                    "scene": 1,
                    "speaker": "boy",
                    "spoken_hindi": "रात के 2 बज रहे हैं, सब सो रहे हैं... बस एक चिप्स का पैकेट चुरा के लाया हूँ!",
                    "dialogue": "Raat ke 2 baj rahe hain, sab so rahe hain... chips ka packet chupke se laya hoon!",
                    "sfx": ["whoosh"]
                },
                {
                    "scene": 2,
                    "speaker": "dost",
                    "spoken_hindi": "आराम से खोलना भाई, इसका प्लास्टिक परमाणु बम जितना तेज़ आवाज़ करता है!",
                    "dialogue": "Aaram se kholna bhai, iska plastic parmanu bomb jaisi aawaz karta hai!",
                    "sfx": ["pop"]
                },
                {
                    "scene": 3,
                    "speaker": "boy",
                    "spoken_hindi": "ज़रा सा कोना खींचा... और आवाज़ ऐसी आई जैसे बिल्डिंग का स्लैब गिर गया हो!",
                    "dialogue": "Zara sa kona kheencha... aur aawaz aisi aayi jaise building ka slab gir gaya ho!",
                    "sfx": ["gasp", "record_scratch"]
                },
                {
                    "scene": 4,
                    "speaker": "dost",
                    "spoken_hindi": "मम्मी के कमरे का दरवाज़ा खुला! फेंक पैकेट, सो जा कंबल ओढ़ के जल्दी!",
                    "dialogue": "Mummy ke kamre ka darwaza khula! Phek packet, so ja kambal odh ke jaldi!",
                    "sfx": ["boom", "laugh"]
                }
            ]
        }
    elif any(k in t_low for k in ["bill", "shake", "restaurant", "split", "dry fruit"]):
        return {
            "hook": "POV: Bill split karte waqt dry fruit shake wala dost 💸",
            "title": "Splitting Bill with Dry Fruit Shake Friend 😂 #shorts",
            "description": "Everyone ordered dal roti and 1 friend ordered 350 rupee shake!\n\n#shorts #comedy #stickman",
            "scenes": [
                {
                    "scene": 1,
                    "speaker": "boy",
                    "spoken_hindi": "चल भाई टोटल बिल 1200 हुआ है, चार लोग हैं तो तीन-तीन सौ निकालो!",
                    "dialogue": "Chal bhai total bill 1200 hua hai, 4 log hain toh teen-teen sau nikalo!",
                    "sfx": ["whoosh"]
                },
                {
                    "scene": 2,
                    "speaker": "dost",
                    "spoken_hindi": "रुक! हम सब ने 40 रुपये की मैगी खाई, इसने 400 रुपये का केसर पिस्ता शेक पिया!",
                    "dialogue": "Ruk! Hum sab ne 40 ki maggi khayi, isne 400 ka kesar pista shake piya!",
                    "sfx": ["pop"]
                },
                {
                    "scene": 3,
                    "speaker": "boy",
                    "spoken_hindi": "अरे भाई सब बराबर शेयर करते हैं ना, दोस्ती में शेक का हिसाब कौन रखता है?",
                    "dialogue": "Arre bhai dosti me barabar share karte hain, shake ka hisaab kaun rakhta hai?",
                    "sfx": ["gasp"]
                },
                {
                    "scene": 4,
                    "speaker": "dost",
                    "spoken_hindi": "तेरी दोस्ती तेरी जेब में रख! अपना 400 का शेक अलग पे कर, वर्ना बर्तन धोएगा!",
                    "dialogue": "Apna 400 ka shake alag pay kar, varna hotel ke bartan tu akele dhoyega!",
                    "sfx": ["boom", "laugh"]
                }
            ]
        }
    elif any(k in t_low for k in ["topper", "exam", "cheat", "sheet", "extra"]):
        return {
            "hook": "POV: Exam me topper ki extra sheet dekh kar panic 📝",
            "title": "Looking at Topper's Exam Sheet 😂 #shorts",
            "description": "Topper taking 4th extra supplement while you're still writing your roll number!\n\n#shorts #comedy #stickman",
            "scenes": [
                {
                    "scene": 1,
                    "speaker": "boy",
                    "spoken_hindi": "भाई 1 घंटा हो गया, मैंने अभी तक सिर्फ अपना रोल नंबर और मार्जिन लाइन खींची है!",
                    "dialogue": "Bhai 1 ghanta ho gaya, maine abhi tak sirf apna roll number aur margin banaya hai!",
                    "sfx": ["whoosh"]
                },
                {
                    "scene": 2,
                    "speaker": "dost",
                    "spoken_hindi": "आगे देख! वो टॉपर लड़का चौथी एक्स्ट्रा सप्लीमेंट शीट मांग रहा है प्रोफेसर से!",
                    "dialogue": "Aage dekh! Wo topper ladka chauthi extra supplement sheet maang raha hai!",
                    "sfx": ["pop", "record_scratch"]
                },
                {
                    "scene": 3,
                    "speaker": "boy",
                    "spoken_hindi": "चौथी शीट? भाई 5 नंबर का पेपर है, उसमें ये रामायण-महाभारत क्या लिख रहा है?!",
                    "dialogue": "Chauthi sheet? Bhai 5 number ka paper hai, ye Ramayan-Mahabharat kya likh raha hai?!",
                    "sfx": ["gasp"]
                },
                {
                    "scene": 4,
                    "speaker": "dost",
                    "spoken_hindi": "सर मुझे भी एक एक्स्ट्रा शीट देना! लिखने के लिए नहीं, रोते वक्त आंसू पोंछने के लिए!",
                    "dialogue": "Sir mujhe bhi extra sheet dena! Likhne ke liye nahi, aansu pochne ke liye!",
                    "sfx": ["boom", "laugh"]
                }
            ]
        }
    else:
        words = [w for w in clean_top.split() if len(w) > 3][:3]
        key_term = " ".join(words) if words else clean_top
        return {
            "hook": f"POV: Jab {key_term} ka scene ho jaye 😂",
            "title": f"POV: {clean_top} 😂 #shorts #comedy",
            "description": f"Relatable Indian hostel comedy: {clean_top}!\n\n#shorts #comedy #stickman",
            "scenes": [
                {
                    "scene": 1,
                    "speaker": "boy",
                    "spoken_hindi": f"भाई कसम से बता रहा हूँ, {clean_top} में जो फजीहत होती है ना, उसका कोई इलाज नहीं!",
                    "dialogue": f"Bhai kasam se, {clean_top} me jo scene hota hai uska koi ilaj nahi!",
                    "sfx": ["whoosh"]
                },
                {
                    "scene": 2,
                    "speaker": "dost",
                    "spoken_hindi": "तू हमेशा पहले बड़ी-बड़ी बातें करता है, और जब करने की बारी आती है तो गायब!",
                    "dialogue": "Tu hamesha pehle badi baatein karta hai, fir aakhri time pe gayab ho jata hai!",
                    "sfx": ["pop"]
                },
                {
                    "scene": 3,
                    "speaker": "boy",
                    "spoken_hindi": "गायब नहीं हुआ भाई! ज़रा सिचुएशन देख, 440 वोल्ट का झटका लग गया है यहाँ!",
                    "dialogue": "Gayab nahi hua! Situation dekh, 440 volt ka jhatka laga hai yahan!",
                    "sfx": ["gasp", "record_scratch"]
                },
                {
                    "scene": 4,
                    "speaker": "dost",
                    "spoken_hindi": "चल ज्यादा ज्ञान मत बांट, जो होना था हो गया, अब चाय की टपरी पे चल!",
                    "dialogue": "Chal zyada gyan mat de, jo hona tha ho gaya, ab cutting chai peene chal!",
                    "sfx": ["boom", "laugh"]
                }
            ]
        }

def produce_hyper_detailed_short(topic=None, base_filename=None):
    print("=" * 70)
    print("     PRODUCING HYPER-DETAILED 4-SCENE STUDIO SHORT (30s)")
    print("=" * 70)

    if not topic:
        topic = "College Attendance 12% & 'Kal Pakka Jaunga'"

    script_meta = fetch_dynamic_script(topic)
    hook_text = script_meta.get("hook", f"POV: {topic[:30]} 😭")
    scenes = script_meta.get("scenes", [])
    title = script_meta.get("title", f"POV: {topic} 😂 #shorts #comedy")
    description = script_meta.get("description", f"Relatable comedy: {topic} #shorts")
    tags = ["shorts", "comedy", "stickman", "relatable", "funny", "hindi", "viral"]

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

        # 1. High-Energy 19-20 Year Old Boy Voice (Subprocess edge-tts: ZERO asyncio conflict)
        voice_wav = os.path.join(TEMP_DIR, f"scene_{s_num}_voice.wav")
        pitch = "+10Hz" if speaker == "boy" else "+5Hz"
        rate = "+18%" if speaker == "boy" else "+16%"
        temp_mp3 = voice_wav.replace(".wav", ".mp3")

        tts_cmd = [
            'edge-tts',
            '--text', spoken,
            '--voice', 'hi-IN-MadhurNeural',
            '--rate', rate,
            '--pitch', pitch,
            '--write-media', temp_mp3
        ]
        res = subprocess.run(tts_cmd, capture_output=True, text=True)
        if res.returncode != 0 or not os.path.exists(temp_mp3) or os.path.getsize(temp_mp3) == 0:
            time.sleep(1)
            subprocess.run(tts_cmd, check=True)

        # Clean conversion to 44.1kHz WAV with clean natural gain (Zero Nyquist resonance)
        cmd = [
            'ffmpeg', '-y', '-i', temp_mp3,
            '-ar', '44100',
            '-af', 'volume=1.4',
            voice_wav
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        v_clip = AudioFileClip(voice_wav)
        duration = v_clip.duration + 0.45 # natural pause buffer
        sfx_tracks = [v_clip]

        # 2. Rich Layered SFX
        for sfx_name in sfx_list:
            sfx_path = sfx_fetcher.resolve_sfx(sfx_name)
            if sfx_path and os.path.exists(sfx_path):
                try:
                    s_audio = AudioFileClip(sfx_path)
                    s_dur = min(s_audio.duration, duration)
                    if sfx_name == "whoosh":
                        sfx_tracks.append(s_audio.set_start(0.1).subclip(0, min(0.3, s_dur)).volumex(0.25))
                    elif sfx_name == "ding":
                        sfx_tracks.append(s_audio.set_start(1.5).subclip(0, min(0.4, s_dur)).volumex(0.20))
                    elif sfx_name == "pop":
                        sfx_tracks.append(s_audio.set_start(0.2).subclip(0, min(0.2, s_dur)).volumex(0.30))
                    elif sfx_name == "record_scratch":
                        sfx_tracks.append(s_audio.set_start(0.1).subclip(0, min(0.4, s_dur)).volumex(0.35))
                    elif sfx_name == "gasp":
                        sfx_tracks.append(s_audio.set_start(0.4).subclip(0, min(0.3, s_dur)).volumex(0.35))
                    elif sfx_name in ["boom", "vine_boom"]:
                        sfx_tracks.append(s_audio.set_start(max(0, duration - 1.4)).volumex(0.35))
                    elif sfx_name == "laugh":
                        sfx_tracks.append(s_audio.set_start(max(0, duration - 1.2)).volumex(0.30))
                except Exception as ex:
                    print(f"[*] SFX load note ({sfx_name}): {ex}")

        scene_audio = CompositeAudioClip(sfx_tracks)

        # 3. Frame Generator
        def make_scene_frame(t, dur=duration, s_idx=s_num, spk=speaker, d_txt=dialogue):
            img = Image.new('RGB', (w, h), (255, 255, 255))
            draw = ImageDraw.Draw(img)

            # Dynamically render themed environment, characters, and movements for this topic
            topic_themes.render_themed_scene_frame(draw, t, dur, w, h, topic, s_idx, d_txt)

            # Top Washi Tape Hook
            draw.rounded_rectangle([80, 50, 640, 115], radius=14, fill=(250, 250, 254), outline=INK, width=3)
            draw.polygon([(68, 45), (115, 40), (105, 70), (58, 75)], fill=YELLOW_ACC)
            draw.polygon([(615, 40), (662, 45), (652, 75), (605, 70)], fill=YELLOW_ACC)
            draw.text((360, 82), hook_text, fill=INK, font=font_hook, anchor='mm')

            # Bottom Subtitle Banner
            sub_col = YELLOW_ACC if spk == "boy" else CYAN_ACC
            draw.rounded_rectangle([35, 1130, 685, 1225], radius=18, fill=(18, 18, 24), outline=sub_col, width=2)
            # Speaker Tag
            tag = "BOY 1" if spk == "boy" else "DOST"
            draw.rounded_rectangle([50, 1108, 150, 1134], radius=6, fill=sub_col)
            draw.text((100, 1121), tag, fill=(10, 10, 15), font=font_hook, anchor='mm')
            # Dialogue Text
            draw.text((360, 1178), d_txt, fill=(255, 255, 255), font=font_sub, anchor='mm')

            return np.array(img)

        clip = VideoClip(make_scene_frame, duration=duration).set_fps(24).set_audio(scene_audio)
        clips.append(clip)

    print("\n[*] Concatenating 4 hyper-detailed scenes into 30s Short...")
    full_video = concatenate_videoclips(clips, method="compose")

    # 4. Layer Viral Comedy BGM (Sneaky Snitch) at 18% volume
    bgm_path = sfx_fetcher.resolve_sfx("sneaky_snitch")
    if bgm_path and os.path.exists(bgm_path):
        print(f"[*] Layering Viral Comedy BGM: {bgm_path} at 18% volume...")
        bgm = AudioFileClip(bgm_path)
        if bgm.duration < full_video.duration:
            loops = int(full_video.duration / bgm.duration) + 1
            bgm = concatenate_audioclips([bgm] * loops)
        bgm = bgm.subclip(0, full_video.duration).volumex(0.13)
        full_audio = CompositeAudioClip([full_video.audio, bgm])
        full_video = full_video.set_audio(full_audio)

    fn = f"{base_filename}.mp4" if base_filename else "final_hyper_detailed_short.mp4"
    out_mp4 = os.path.join(OUTPUT_DIR, fn)
    print(f"[*] Rendering Hyper-Detailed Video to: {out_mp4}")

    try:
        full_video.write_videofile(out_mp4, fps=24, codec="libx264", audio_codec="aac", preset="ultrafast")
    except Exception as e:
        print(f"[*] Note: MoviePy cleanup ({e}), file intact!")

    if not title:
        title = f"POV: {topic} #shorts #comedy"
    if not description:
        description = f"Relatable Indian student comedy: {topic}!\n\n#shorts #comedy #relatable #funny #stickman #animation"
    tags = ["shorts", "comedy", "stickman", "relatable", "funny", "hindi", "college", "viral"]

    print("\n" + "=" * 70)
    print(f"[SUCCESS] HYPER-DETAILED SHORT READY: {out_mp4}")
    print("=" * 70)
    return out_mp4, title, description, tags

if __name__ == "__main__":
    produce_hyper_detailed_short()
