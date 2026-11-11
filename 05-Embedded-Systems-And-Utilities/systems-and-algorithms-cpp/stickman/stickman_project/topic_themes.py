"""
topic_themes.py
===============
Modular, hyper-detailed 2D visual scenes and animations for every viral topic.
Each theme provides:
- Custom backgrounds (Gym, Roadside Tapri, Corporate Office, Midnight Kitchen, Vanity Mirror, Living Room Sofa, etc.)
- Distinct character styling (gym headband, corporate tie & glasses, green hoodie, pajamas, messy hair, blankets)
- Comedic dynamic animations tailored to the topic (lifting dumbbells, vanishing poof, fridge light, spinning clocks, snack snatching)
"""

import math
from PIL import Image, ImageDraw, ImageFont

try:
    FONT_BADGE = ImageFont.truetype("arialbd.ttf", 28)
    FONT_SIGN  = ImageFont.truetype("arialbd.ttf", 22)
    FONT_SMALL = ImageFont.truetype("arialbd.ttf", 18)
except Exception:
    FONT_BADGE = ImageFont.load_default()
    FONT_SIGN  = ImageFont.load_default()
    FONT_SMALL = ImageFont.load_default()
INK        = (35, 32, 42)
INK_L      = (80, 75, 90)
WALL_BG    = (248, 243, 232)
WALL_STR   = (240, 234, 220)
FLOOR      = (225, 215, 198)
FLOOR_D    = (195, 182, 162)
WOOD       = (198, 154, 110)
WOOD_D     = (154, 112, 72)
RED_ACC    = (235, 55, 55)
CYAN_ACC   = (30, 165, 245)
YELLOW_ACC = (255, 215, 0)
WHITE      = (255, 255, 255)
SMOKE_COL  = (235, 235, 240)
GREEN_ACC  = (40, 180, 90)
DARK_ROOM  = (25, 28, 40)
FRIDGE_GLOW= (210, 245, 255)

def line(draw, pts, width=5, fill=INK):
    draw.line(pts, fill=fill, width=width, joint="curve")

def circ(draw, cx, cy, r, width=5, fill=None, outline=INK):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=width)

def poly(draw, pts, fill=None, outline=INK, width=5):
    draw.polygon(pts, fill=fill)
    if outline is not None:
        draw.line(list(pts) + [pts[0]], width=width, fill=outline, joint="curve")

# ──────────────────────────────────────────────────────────────────────────────
# THEME 1: GYM & FITNESS (Dumbbells, Bench, Shaking Muscles, Day 1 vs Day 3)
# ──────────────────────────────────────────────────────────────────────────────
def draw_gym_scene(draw, t, dur, w, h, scene_num, dialogue=""):
    floor_y = 1000
    # Gym Background: Industrial brick/concrete wall + rubber mats
    draw.rectangle([0, 0, w, h], fill=(235, 238, 242))
    # Gym wall mirror
    draw.rectangle([60, 200, 660, 800], fill=(215, 225, 235), outline=INK, width=5)
    line(draw, [(100, 220), (180, 780)], width=3, fill=(245, 250, 255))
    line(draw, [(140, 220), (220, 780)], width=2, fill=(245, 250, 255))
    # Motivational gym poster
    draw.rectangle([250, 240, 470, 340], fill=YELLOW_ACC, outline=INK, width=4)
    draw.text((360, 290), "NO PAIN\nNO GAIN 💀", fill=INK, anchor='mm')
    # Rubber mat floor
    draw.rectangle([0, floor_y, w, h], fill=(50, 52, 60))
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)

    # Dumbbell rack on right
    draw.rectangle([520, 700, 680, floor_y], fill=(160, 165, 175), outline=INK, width=4)
    # Weights on rack
    for dy in [750, 840, 930]:
        line(draw, [(540, dy), (660, dy)], width=14, fill=INK)
        circ(draw, 545, dy, 18, fill=(80, 85, 95), outline=INK, width=3)
        circ(draw, 655, dy, 18, fill=(80, 85, 95), outline=INK, width=3)

    if scene_num == 1:
        # Scene 1: Overly enthusiastic gym bro with red headband and shaker bottle
        bx, by = 280, 740
        # Red headband stickman
        circ(draw, bx, by - 120, 48, fill=WHITE, outline=INK, width=5)
        # Red Headband
        draw.rectangle([bx - 46, by - 138, bx + 46, by - 122], fill=RED_ACC, outline=INK, width=3)
        # Confident winking face
        line(draw, [(bx - 22, by - 122), (bx - 6, by - 122)], width=4)
        circ(draw, bx + 16, by - 122, 5, fill=INK)
        draw.arc([bx - 12, by - 110, bx + 18, by - 90], start=0, end=180, fill=INK, width=4)
        # Torso
        line(draw, [(bx, by - 72), (bx, by + 80)], width=6)
        # Legs
        line(draw, [(bx, by + 80), (bx - 40, floor_y)], width=6)
        line(draw, [(bx, by + 80), (bx + 40, floor_y)], width=6)
        # Arm flexing with 5kg dumbbell
        line(draw, [(bx, by - 40), (bx + 60, by - 70)], width=6)
        line(draw, [(bx + 60, by - 70), (bx + 40, by - 130)], width=6)
        # Dumbbell in hand
        line(draw, [(bx + 20, by - 130), (bx + 60, by - 130)], width=10, fill=(70, 70, 80))
        circ(draw, bx + 20, by - 130, 16, fill=(100, 100, 110), outline=INK, width=3)
        circ(draw, bx + 60, by - 130, 16, fill=(100, 100, 110), outline=INK, width=3)
        # Protein shaker bottle in left hand
        draw.rectangle([bx - 90, by - 30, bx - 60, by + 40], fill=CYAN_ACC, outline=INK, width=3)
        draw.text((360, 480), "DAY 1: FULL JOSH! 🔥", fill=RED_ACC, font=FONT_SIGN, anchor='mm')

    elif scene_num == 2:
        # Scene 2: Trainer / Dost laughing at the ultra-light 2.5kg dumbbell
        dx, dy = 400, 740
        # Friend laughing with backwards cap
        circ(draw, dx, dy - 120, 48, fill=WHITE, outline=INK, width=5)
        # Cap
        draw.arc([dx - 48, dy - 165, dx + 48, dy - 115], start=180, end=360, fill=CYAN_ACC, width=5)
        line(draw, [(dx - 48, dy - 135), (dx - 80, dy - 130)], width=6, fill=CYAN_ACC)
        # Laughing squint eyes
        line(draw, [(dx - 22, dy - 128), (dx - 8, dy - 122)], width=4)
        line(draw, [(dx - 22, dy - 116), (dx - 8, dy - 122)], width=4)
        line(draw, [(dx + 8, dy - 122), (dx + 22, dy - 128)], width=4)
        line(draw, [(dx + 8, dy - 122), (dx + 22, dy - 116)], width=4)
        # Open mouth
        draw.arc([dx - 16, dy - 115, dx + 16, dy - 92], start=0, end=180, fill=RED_ACC, width=4)
        # Body hands on hips
        line(draw, [(dx, dy - 72), (dx, dy + 80)], width=6)
        line(draw, [(dx, dy - 40), (dx - 50, dy - 10)], width=5)
        line(draw, [(dx - 50, dy - 10), (dx - 20, dy + 20)], width=5)
        line(draw, [(dx, dy - 40), (dx + 50, dy - 10)], width=5)
        line(draw, [(dx + 50, dy - 10), (dx + 20, dy + 20)], width=5)
        line(draw, [(dx, dy + 80), (dx - 40, floor_y)], width=6)
        line(draw, [(dx, dy + 80), (dx + 40, floor_y)], width=6)
        # Haha text
        draw.text((220, 520), "HAHAHA! 2.5 KG?! 😂", fill=INK, font=FONT_SIGN, anchor='mm')

    elif scene_num == 3:
        # Scene 3: Comic shock zoom - trying to bench press heavy weight, trembling violently!
        shake = int(math.sin(t * 35) * 8)
        bx = 360 + shake
        by = 650
        # Dramatic speed shock lines from corners
        for ang in range(0, 360, 20):
            rad = math.radians(ang)
            x1 = 360 + int(math.cos(rad) * 420)
            y1 = 640 + int(math.sin(rad) * 420)
            x2 = 360 + int(math.cos(rad) * 220)
            y2 = 640 + int(math.sin(rad) * 220)
            line(draw, [(x1, y1), (x2, y2)], width=4, fill=(220, 70, 70))
        # Giant Barbell crushing down
        line(draw, [(80, by - 60), (640, by - 60)], width=18, fill=INK)
        # Giant 20kg plates
        for px in [120, 140, 580, 600]:
            draw.rectangle([px - 15, by - 160, px + 15, by + 40], fill=(60, 65, 75), outline=INK, width=4)
            draw.text((px, by - 60), "20KG", fill=YELLOW_ACC, font=FONT_SIGN, anchor='mm')
        # Boy underneath struggling with bulging eyes & sweat drops
        circ(draw, bx, by + 40, 65, fill=WHITE, outline=INK, width=6)
        circ(draw, bx - 25, by + 30, 18, fill=WHITE, outline=INK, width=4)
        circ(draw, bx + 25, by + 30, 18, fill=WHITE, outline=INK, width=4)
        circ(draw, bx - 25, by + 30, 4, fill=INK)
        circ(draw, bx + 25, by + 30, 4, fill=INK)
        # Wavy scream mouth
        wavy = [(bx - 30 + i * 10, by + 70 + int(math.sin(i * 3 + t * 20) * 8)) for i in range(7)]
        line(draw, wavy, width=5, fill=RED_ACC)
        # Flying sweat drops
        for sw in [-80, -60, 60, 80]:
            circ(draw, bx + sw, by - 10 + int(math.sin(t * 15 + sw) * 20), 8, fill=CYAN_ACC, outline=INK, width=2)
        draw.text((360, 350), "BHAI UTHAAO! MAR GAYA!! 💀", fill=RED_ACC, font=FONT_SIGN, anchor='mm')

    else:
        # Scene 4: Climax - Day 3 Reality: Sleeping in bed covered in pain balm with crutches!
        draw.rectangle([0, 0, w, h], fill=WALL_BG)
        draw.rectangle([0, floor_y, w, h], fill=FLOOR)
        line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)
        # Bed
        draw.rectangle([120, 800, 600, floor_y], fill=WOOD, outline=INK, width=5)
        # Blanket covering sick stickman
        draw.rectangle([160, 820, 580, floor_y], fill=(130, 180, 225), outline=INK, width=5)
        # Head with ice pack
        circ(draw, 220, 780, 46, fill=WHITE, outline=INK, width=5)
        # Ice pack on head
        poly(draw, [(195, 740), (245, 740), (220, 710)], fill=CYAN_ACC, outline=INK, width=3)
        # Bandage on cheek
        draw.rectangle([230, 775, 255, 795], fill=(240, 215, 180), outline=INK, width=2)
        # Crossed X eyes (passed out)
        line(draw, [(205, 770), (219, 784)], width=4)
        line(draw, [(205, 784), (219, 770)], width=4)
        line(draw, [(230, 770), (244, 784)], width=4)
        line(draw, [(230, 784), (244, 770)], width=4)
        # Zzz floating
        draw.text((280, 680), "Zzz...", fill=INK, font=FONT_SIGN)
        # Gym shoes dumped in dustbin
        draw.rectangle([560, 880, 660, floor_y], fill=(170, 175, 185), outline=INK, width=4)
        draw.text((610, 850), "GYM SHOES 🗑️", fill=INK, font=FONT_SIGN, anchor='mm')
        # Big Punchline badge
        draw.rounded_rectangle([140, 440, 580, 530], radius=16, fill=RED_ACC, outline=WHITE, width=4)
        draw.text((360, 485), "DAY 3: ADMISSION CANCEL! 😭", fill=WHITE, font=FONT_BADGE, anchor='mm')


# ──────────────────────────────────────────────────────────────────────────────
# THEME 2: JOB INTERVIEW / VIVA PANIC (Tie, CV, Sweating, Professor / HR Boss)
# ──────────────────────────────────────────────────────────────────────────────
def draw_interview_scene(draw, t, dur, w, h, scene_num, dialogue=""):
    floor_y = 1000
    # Corporate Office / Viva Cabin
    draw.rectangle([0, 0, w, h], fill=(242, 238, 230))
    # Wall clock
    circ(draw, 360, 220, 45, fill=WHITE, outline=INK, width=4)
    line(draw, [(360, 220), (360, 190)], width=4)
    line(draw, [(360, 220), (385, 220)], width=3)
    # Mahogany Desk
    draw.rectangle([100, 720, 620, floor_y], fill=(140, 90, 55), outline=INK, width=6)
    draw.rectangle([0, floor_y, w, h], fill=(195, 185, 170))
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)
    # Boss Nameplate
    draw.rectangle([140, 700, 310, 740], fill=YELLOW_ACC, outline=INK, width=3)
    draw.text((225, 720), "HR / PROFESSOR", fill=INK, font=FONT_SIGN, anchor='mm')
    # Resume / CV Paper
    draw.rectangle([340, 690, 430, 750], fill=WHITE, outline=INK, width=3)
    for ly in range(700, 745, 8):
        line(draw, [(350, ly), (420, ly)], width=2, fill=(180, 180, 190))

    if scene_num == 1:
        # Scene 1: Boy outside room boasting confidence: "Bhai full prepared hoon, aag laga dunga!"
        bx, by = 360, 720
        # Stickman with nerdy glasses and tie
        circ(draw, bx, by - 120, 48, fill=WHITE, outline=INK, width=5)
        # Glasses
        circ(draw, bx - 18, by - 122, 14, fill=WHITE, outline=INK, width=3)
        circ(draw, bx + 18, by - 122, 14, fill=WHITE, outline=INK, width=3)
        line(draw, [(bx - 4, by - 122), (bx + 4, by - 122)], width=3)
        # Overconfident grin
        draw.arc([bx - 14, by - 108, bx + 18, by - 90], start=0, end=180, fill=INK, width=4)
        # Torso & Tie
        line(draw, [(bx, by - 72), (bx, by + 80)], width=6)
        poly(draw, [(bx - 8, by - 55), (bx + 8, by - 55), (bx + 12, by - 10), (bx, by + 20), (bx - 12, by - 10)], fill=RED_ACC, outline=INK, width=3)
        # Thumbs up gesture
        line(draw, [(bx, by - 40), (bx + 60, by - 60)], width=5)
        line(draw, [(bx + 60, by - 60), (bx + 80, by - 90)], width=5)
        draw.rectangle([bx + 75, by - 105, bx + 90, by - 90], fill=WHITE, outline=INK, width=3)
        line(draw, [(bx, by + 80), (bx - 35, floor_y)], width=6)
        line(draw, [(bx, by + 80), (bx + 35, floor_y)], width=6)
        draw.text((360, 480), "CONFIDENCE: 1000% 😎", fill=INK, font=FONT_SIGN, anchor='mm')

    elif scene_num == 2:
        # Scene 2: HR / Interviewer asking a terrifying question
        hx, hy = 480, 680
        # Angry interviewer with mustache
        circ(draw, hx, hy - 110, 46, fill=WHITE, outline=INK, width=5)
        # Serious eyes
        line(draw, [(hx - 22, hy - 120), (hx - 8, hy - 114)], width=5)
        line(draw, [(hx + 8, hy - 114), (hx + 22, hy - 120)], width=5)
        circ(draw, hx - 14, hy - 110, 5, fill=INK)
        circ(draw, hx + 14, hy - 110, 5, fill=INK)
        # Thick mustache
        poly(draw, [(hx - 22, hy - 96), (hx + 22, hy - 96), (hx, hy - 84)], fill=INK)
        # Pointer stick in hand
        line(draw, [(hx - 30, hy - 40), (hx - 120, hy - 80)], width=6, fill=(180, 50, 50))
        # Question speech bubble
        draw.rounded_rectangle([120, 360, 440, 460], radius=14, fill=WHITE, outline=INK, width=4)
        draw.text((280, 410), "TELL ME SOMETHING NOT\nIN YOUR RESUME! 🤨", fill=RED_ACC, font=FONT_SIGN, anchor='mm')

    elif scene_num == 3:
        # Scene 3: Comic Panic - Boy shivering, brain loading icon, sweating a river!
        shake = int(math.sin(t * 40) * 9)
        bx = 360 + shake
        by = 680
        circ(draw, bx, by - 110, 54, fill=WHITE, outline=INK, width=6)
        # Shaky spiral shock eyes
        for ex in [bx - 20, bx + 20]:
            circ(draw, ex, by - 110, 14, fill=WHITE, outline=INK, width=3)
            circ(draw, ex, by - 110, 5, fill=RED_ACC)
        # Shaking open jaw
        circ(draw, bx, by - 70, 18, fill=INK)
        # Flying sweat fountain
        for sx in [-70, -45, 45, 70]:
            circ(draw, bx + sx, by - 110 + int(math.sin(t * 18 + sx) * 25), 8, fill=CYAN_ACC, outline=INK, width=2)
        # Comic 404 Brain Not Found pop-up
        draw.rounded_rectangle([bx - 150, 380, bx + 150, 460], radius=12, fill=YELLOW_ACC, outline=INK, width=4)
        draw.text((bx, 420), "BRAIN.EXE HAS STOPPED! 💀", fill=INK, font=FONT_SIGN, anchor='mm')

    else:
        # Scene 4: Climax - Rejected stamp + Boy running out through the door!
        draw.rectangle([0, 0, w, h], fill=WALL_BG)
        draw.rectangle([0, floor_y, w, h], fill=FLOOR)
        line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)
        # Giant Red REJECTED / FAIL Stamp across screen
        poly(draw, [(120, 420), (600, 370), (620, 520), (140, 570)], fill=(255, 235, 235), outline=RED_ACC, width=8)
        draw.text((370, 470), "REJECTED! ❌\n(OVERCONFIDENCE)", fill=RED_ACC, font=FONT_SIGN, anchor='mm')
        # Stickman running away fast
        rx = min(650, int(200 + t * 180))
        circ(draw, rx, 850, 38, fill=WHITE, outline=INK, width=5)
        line(draw, [(rx, 888), (rx, 960)], width=6)
        line(draw, [(rx, 960), (rx + 40, floor_y)], width=6)
        line(draw, [(rx, 960), (rx - 40, floor_y)], width=6)
        # Smoke puffs behind feet
        circ(draw, rx - 60, floor_y - 20, 20, fill=SMOKE_COL, outline=INK, width=3)


# ──────────────────────────────────────────────────────────────────────────────
# THEME 3: LATE NIGHT HUNGER / MIDNIGHT FRIDGE RAID
# ──────────────────────────────────────────────────────────────────────────────
def draw_kitchen_scene(draw, t, dur, w, h, scene_num, dialogue=""):
    floor_y = 1000
    # Dark Midnight Kitchen Room
    draw.rectangle([0, 0, w, h], fill=DARK_ROOM)
    # Moon in kitchen window
    draw.rectangle([100, 180, 280, 420], fill=(40, 45, 65), outline=INK, width=5)
    circ(draw, 220, 250, 35, fill=(255, 245, 180))
    # Kitchen tile floor
    draw.rectangle([0, floor_y, w, h], fill=(30, 32, 45))
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)

    # Giant Refrigerator on right
    fridge_open = (scene_num >= 2)
    fx = 480
    if not fridge_open:
        # Closed fridge
        draw.rectangle([fx, 380, 680, floor_y], fill=(220, 225, 235), outline=INK, width=6)
        line(draw, [(fx, 640), (680, 640)], width=4, fill=INK)
        # Handles
        draw.rectangle([fx + 20, 520, fx + 35, 600], fill=(120, 125, 135), outline=INK, width=2)
        draw.rectangle([fx + 20, 680, fx + 35, 780], fill=(120, 125, 135), outline=INK, width=2)
    else:
        # Open fridge with divine glowing light beam!
        # Light cone
        poly(draw, [(fx, 380), (fx + 200, 380), (fx + 200, floor_y), (fx, floor_y), (100, floor_y), (200, 380)], fill=(230, 250, 255, 60))
        draw.rectangle([fx, 380, 680, floor_y], fill=FRIDGE_GLOW, outline=INK, width=6)
        # Shelves inside fridge
        for sy in [500, 640, 780, 900]:
            line(draw, [(fx, sy), (680, sy)], width=5, fill=(150, 180, 200))
        # Empty bottle & cobweb inside fridge (EMPTY FRIDGE TRAGEDY)
        # Milk bottle tipped over
        line(draw, [(fx + 40, 630), (fx + 100, 630)], width=14, fill=WHITE)
        # Cobweb on top shelf
        draw.text((fx + 50, 420), "🕸️ (KHAALI!)", fill=INK, font=FONT_SIGN)

    if scene_num == 1:
        # Sneaky ninja crawl towards fridge
        cx = int(140 + t * 45)
        circ(draw, cx, 840, 42, fill=WHITE, outline=INK, width=5)
        # Thief mask / headband
        draw.rectangle([cx - 40, 825, cx + 40, 845], fill=INK)
        circ(draw, cx - 12, 835, 5, fill=WHITE)
        circ(draw, cx + 12, 835, 5, fill=WHITE)
        # Tiptoe body
        line(draw, [(cx, 882), (cx, 940)], width=6)
        line(draw, [(cx, 940), (cx + 30, floor_y)], width=5)
        line(draw, [(cx, 940), (cx - 20, floor_y)], width=5)
        draw.text((280, 500), "MISSION: LATE NIGHT MAGGIE 🕵️‍♂️", fill=YELLOW_ACC, font=FONT_SIGN, anchor='mm')

    elif scene_num == 2:
        # Opening fridge and discovering it's completely empty!
        bx = 360
        circ(draw, bx, 780, 48, fill=WHITE, outline=INK, width=5)
        # Shock wide eyes
        circ(draw, bx - 16, 775, 14, fill=WHITE, outline=INK, width=3)
        circ(draw, bx + 16, 775, 14, fill=WHITE, outline=INK, width=3)
        circ(draw, bx - 16, 775, 4, fill=INK)
        circ(draw, bx + 16, 775, 4, fill=INK)
        # Dropped jaw
        circ(draw, bx, 810, 12, fill=INK)
        draw.text((280, 500), "KISI NE AAKHRI SLICE BHI KHAA LI?! 😱", fill=RED_ACC, font=FONT_SIGN, anchor='mm')

    elif scene_num == 3:
        # Blaming roommate: dost appears with crumbs on his mouth!
        dx = 240
        circ(draw, dx, 760, 48, fill=WHITE, outline=INK, width=5)
        # Innocent looking whistle face
        circ(draw, dx - 14, 755, 6, fill=INK)
        circ(draw, dx + 14, 755, 6, fill=INK)
        circ(draw, dx + 20, 775, 5, fill=INK) # whistling mouth
        # Crumbs on face
        for cxy in [(dx - 10, 770), (dx + 5, 782), (dx - 20, 780)]:
            circ(draw, cxy[0], cxy[1], 3, fill=YELLOW_ACC)
        # Hidden empty plate behind back
        line(draw, [(dx, 808), (dx, 890)], width=6)
        circ(draw, dx - 40, 850, 16, fill=WHITE, outline=INK, width=3)
        draw.text((360, 460), "BRO MAINE NAHI KHAYA, SACH MEIN! 🤥", fill=WHITE, font=FONT_SIGN, anchor='mm')

    else:
        # Scene 4: Pillow fight / Utensil clash in the dark!
        draw.rounded_rectangle([140, 420, 580, 520], radius=16, fill=RED_ACC, outline=WHITE, width=4)
        draw.text((360, 470), "MIDNIGHT HUNGER WAR DECLARED! ⚔️🍕", fill=WHITE, font=FONT_SIGN, anchor='mm')


# ──────────────────────────────────────────────────────────────────────────────
# THEME 4: PHONE BATTERY 1% / WORST TIMING
# ──────────────────────────────────────────────────────────────────────────────
def draw_battery_scene(draw, t, dur, w, h, scene_num, dialogue=""):
    floor_y = 1000
    draw.rectangle([0, 0, w, h], fill=(245, 240, 235))
    draw.rectangle([0, floor_y, w, h], fill=FLOOR)
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)

    # Wall electrical socket across room on left
    draw.rectangle([60, 840, 130, 930], fill=(225, 225, 230), outline=INK, width=4)
    circ(draw, 85, 875, 6, fill=INK)
    circ(draw, 105, 875, 6, fill=INK)
    circ(draw, 95, 905, 8, fill=INK)

    if scene_num in [1, 2]:
        # Giant Mobile Screen showing 1% Red Battery Flashing
        draw.rectangle([180, 300, 540, 820], fill=(25, 25, 30), outline=INK, width=8)
        # Battery icon
        blink = (int(t * 4) % 2 == 0)
        bat_color = RED_ACC if blink else (120, 30, 30)
        draw.rectangle([280, 420, 440, 500], fill=None, outline=WHITE, width=5)
        draw.rectangle([440, 445, 455, 475], fill=WHITE)
        # 1% sliver
        draw.rectangle([285, 425, 305, 495], fill=bat_color)
        draw.text((360, 550), "1% REMAINING ⚠️", fill=bat_color, font=FONT_SIGN, anchor='mm')
        draw.text((360, 620), "IMPORTANT OTP INCOMING...", fill=WHITE, font=FONT_SIGN, anchor='mm')

    elif scene_num == 3:
        # Cinematic Slow Motion Dive towards Charger Socket!
        dx = int(500 - t * 90)
        dy = int(720 + t * 30)
        circ(draw, dx - 80, dy - 20, 42, fill=WHITE, outline=INK, width=5)
        # Desperate reaching arm
        line(draw, [(dx - 40, dy), (dx - 140, dy + 20)], width=6)
        # Charger pin in hand
        line(draw, [(dx - 140, dy + 20), (dx - 180, dy + 20)], width=6, fill=CYAN_ACC)
        # Slow-mo text
        draw.text((360, 400), "NOOOOO! JUST 2 SECONDS! ⚡😭", fill=RED_ACC, font=FONT_SIGN, anchor='mm')

    else:
        # Scene 4: Screen Blackout / Phone Died!
        draw.rectangle([0, 0, w, h], fill=(15, 15, 20))
        draw.rounded_rectangle([160, 440, 560, 540], radius=16, fill=RED_ACC, outline=WHITE, width=4)
        draw.text((360, 490), "PHONE DIED ON LAST DIGIT! 💀", fill=WHITE, font=FONT_SIGN, anchor='mm')


# ──────────────────────────────────────────────────────────────────────────────
# THEME 5: CHAI TAPRI / MONEY / UPI / VANISHING FRIEND (From Proven Short)
# ──────────────────────────────────────────────────────────────────────────────
def draw_tapri_money_scene(draw, t, dur, w, h, scene_num, dialogue=""):
    ROAD_BG   = (246, 242, 234)
    ROAD_FLOOR= (215, 210, 200)
    ROAD_LINE = (180, 175, 165)
    STALL_WOOD= (190, 145, 95)
    CHAI_POT  = (175, 180, 190)
    GREEN_UPI = (40, 180, 90)
    floor_y = 1000

    draw.rectangle([0, 0, w, h], fill=ROAD_BG)
    draw.rectangle([0, floor_y, w, h], fill=ROAD_FLOOR)
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)
    for rx in range(-50, w + 150, 95):
        line(draw, [(rx, floor_y), (rx + 45, h)], width=3, fill=ROAD_LINE)

    # Street Lamp Post
    line(draw, [(70, 150), (70, floor_y)], width=7)
    draw.arc([70, 120, 150, 200], start=180, end=360, fill=INK, width=6)
    circ(draw, 150, 180, 18, fill=YELLOW_ACC, outline=INK, width=3)
    # Chai Tapri Stall on Right
    draw.rectangle([450, 600, 710, floor_y], fill=STALL_WOOD, outline=INK, width=5)
    poly(draw, [(420, 500), (720, 500), (690, 600), (400, 600)], fill=(240, 235, 225), outline=INK, width=4)
    draw.text((560, 550), "RAMU CHAI ☕", fill=INK, font=FONT_SIGN, anchor='mm')

    if scene_num == 1:
        # Boy holding phone asking for 500 UPI
        bx, by = 260, 720
        circ(draw, bx, by - 120, 48, fill=WHITE, outline=INK, width=5)
        line(draw, [(bx - 18, by - 122), (bx - 8, by - 122)], width=4)
        line(draw, [(bx + 8, by - 122), (bx + 18, by - 122)], width=4)
        draw.arc([bx - 12, by - 105, bx + 12, by - 85], start=0, end=180, fill=INK, width=4)
        line(draw, [(bx, by - 72), (bx, by + 80)], width=6)
        line(draw, [(bx, by + 80), (bx - 40, floor_y)], width=6)
        line(draw, [(bx, by + 80), (bx + 40, floor_y)], width=6)
        # Phone
        draw.rectangle([bx + 50, by - 80, bx + 110, by + 20], fill=GREEN_UPI, outline=INK, width=4)
        draw.text((bx + 80, by - 30), "500", fill=WHITE, font=FONT_SIGN, anchor='mm')
        draw.text((260, 480), "BHAI 500 UPI KAREGA? 📱", fill=INK, font=FONT_SIGN, anchor='mm')

    elif scene_num == 2:
        # Dost smiling in green hoodie pretending to scan QR code
        dx, dy = 380, 720
        circ(draw, dx, dy - 120, 48, fill=WHITE, outline=INK, width=5)
        # Hoodie
        draw.arc([dx - 54, dy - 170, dx + 54, dy - 65], start=160, end=380, fill=GREEN_UPI, width=7)
        # Sly smile
        draw.arc([dx - 15, dy - 105, dx + 15, dy - 85], start=0, end=180, fill=INK, width=4)
        # Phone scanning QR
        draw.rectangle([dx - 120, dy - 60, dx - 60, dy + 40], fill=(30, 30, 35), outline=INK, width=4)
        # Blue laser scan line moving
        laser_y = int(dy - 50 + ((t * 80) % 80))
        line(draw, [(dx - 115, laser_y), (dx - 65, laser_y)], width=3, fill=CYAN_ACC)
        draw.text((380, 480), "HAAN HAAN SCAN HO RAHA HAI... 😉", fill=GREEN_UPI, font=FONT_SIGN, anchor='mm')

    elif scene_num == 3:
        # Boy staring at balance: Rs 0.42! Dilated eyes!
        draw.rounded_rectangle([160, 360, 560, 780], radius=20, fill=(25, 28, 35), outline=INK, width=6)
        circ(draw, 360, 480, 50, fill=RED_ACC, outline=WHITE, width=4)
        line(draw, [(335, 455), (385, 505)], width=8, fill=WHITE)
        line(draw, [(335, 505), (385, 455)], width=8, fill=WHITE)
        draw.text((360, 580), "PAYMENT NOT RECEIVED!", fill=WHITE, font=FONT_SIGN, anchor='mm')
        draw.text((360, 660), "BALANCE: Rs 0.42 💀", fill=RED_ACC, font=FONT_SIGN, anchor='mm')

    else:
        # Climax: Dost has completely vanished! Only empty sneakers + Poof smoke cloud!
        sx, sy = 400, 750
        # Expanding smoke cloud
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            cx = sx + int(math.cos(rad) * 90)
            cy = sy + int(math.sin(rad) * 70)
            circ(draw, cx, cy, 55, fill=SMOKE_COL, outline=INK, width=4)
        circ(draw, sx, sy, 70, fill=WHITE, outline=INK, width=5)
        draw.text((sx, sy), "POOF! 💨\n(GAYAB!)", fill=INK, font=FONT_SIGN, anchor='mm')
        # Empty green sneakers left on ground
        draw.rectangle([sx - 50, floor_y - 25, sx - 10, floor_y], fill=GREEN_UPI, outline=INK, width=3)
        draw.rectangle([sx + 10, floor_y - 25, sx + 50, floor_y], fill=GREEN_UPI, outline=INK, width=3)
        # Punchline badge
        draw.rounded_rectangle([150, 420, 570, 510], radius=16, fill=RED_ACC, outline=WHITE, width=4)
        draw.text((360, 465), "UDHAAR DETE HI INVISIBLE! 👻", fill=WHITE, font=FONT_SIGN, anchor='mm')


# ──────────────────────────────────────────────────────────────────────────────
# THEME 6: GETTING READY / DRESSING MIRROR / ALMOST DONE LIE
# ──────────────────────────────────────────────────────────────────────────────
def draw_ready_scene(draw, t, dur, w, h, scene_num, dialogue=''):
    floor_y = 1000
    draw.rectangle([0, 0, w, h], fill=(245, 238, 230))
    draw.rectangle([0, floor_y, w, h], fill=FLOOR)
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)

    # Giant Vanity Dressing Mirror on left
    draw.rectangle([60, 240, 320, 800], fill=(225, 235, 245), outline=INK, width=6)
    line(draw, [(80, 260), (140, 780)], width=3, fill=WHITE)
    draw.rectangle([40, 800, 340, 840], fill=WOOD, outline=INK, width=4)
    draw.rectangle([80, 760, 110, 800], fill=CYAN_ACC, outline=INK, width=3)
    draw.rectangle([130, 770, 155, 800], fill=RED_ACC, outline=INK, width=2)

    # Giant Ticking Clock on wall
    circ(draw, 520, 300, 55, fill=WHITE, outline=INK, width=5)
    angle = (t * 180) % 360
    rad = math.radians(angle)
    line(draw, [(520, 300), (520 + int(math.cos(rad) * 40), 300 + int(math.sin(rad) * 40))], width=4, fill=RED_ACC)
    draw.text((520, 375), '1 HOUR LATER... ⏰', fill=RED_ACC, font=FONT_SIGN, anchor='mm')

    if scene_num == 1:
        bx = 520
        circ(draw, bx, 640, 48, fill=WHITE, outline=INK, width=5)
        line(draw, [(bx - 20, 625), (bx - 5, 635)], width=4)
        line(draw, [(bx + 5, 635), (bx + 20, 625)], width=4)
        circ(draw, bx - 12, 642, 5, fill=INK)
        circ(draw, bx + 12, 642, 5, fill=INK)
        draw.arc([bx - 12, 655, bx + 12, 675], start=180, end=360, fill=INK, width=4)
        line(draw, [(bx, 688), (bx, 780)], width=6)
        line(draw, [(bx - 35, 720), (bx + 35, 720)], width=8)
        foot_y = floor_y - abs(int(math.sin(t * 15) * 12))
        line(draw, [(bx, 780), (bx - 35, floor_y)], width=6)
        line(draw, [(bx, 780), (bx + 35, foot_y)], width=6)
        draw.text((520, 520), '7:00 PM TIME THA!! 🤬', fill=RED_ACC, font=FONT_BADGE, anchor='mm')

    elif scene_num == 2:
        dx = 240
        circ(draw, dx, 620, 48, fill=WHITE, outline=INK, width=5)
        draw.arc([dx - 45, 580, dx + 45, 640], start=180, end=360, fill=INK, width=6)
        line(draw, [(dx - 18, 622), (dx - 6, 622)], width=4)
        circ(draw, dx + 12, 622, 5, fill=INK)
        draw.arc([dx - 10, 632, dx + 14, 652], start=0, end=180, fill=INK, width=4)
        line(draw, [(dx + 25, 640), (dx + 50, 600)], width=5)
        draw.rectangle([dx + 40, 580, dx + 65, 600], fill=YELLOW_ACC, outline=INK, width=2)
        draw.text((240, 520), 'BAS 2 MINUTE! 😉', fill=GREEN_ACC, font=FONT_BADGE, anchor='mm')

    elif scene_num == 3:
        draw.rounded_rectangle([180, 480, 540, 620], radius=16, fill=(25, 28, 35), outline=RED_ACC, width=6)
        draw.text((360, 530), 'AUTO WAITING: RS 250! 🚕', fill=YELLOW_ACC, font=FONT_SIGN, anchor='mm')
        draw.text((360, 580), 'METER DOUBLE CHAL RAHA HAI! 💀', fill=WHITE, font=FONT_SIGN, anchor='mm')

    else:
        draw.rounded_rectangle([140, 440, 580, 540], radius=16, fill=RED_ACC, outline=WHITE, width=4)
        draw.text((360, 490), 'POHANCHTE POHANCHTE\nPARTY KHATAM! 😭🎉', fill=WHITE, font=FONT_BADGE, anchor='mm')


# ──────────────────────────────────────────────────────────────────────────────
# THEME 7: SNACKS FAIR SPLIT / LAST SAMOSA BETRAYAL
# ──────────────────────────────────────────────────────────────────────────────
def draw_snacks_scene(draw, t, dur, w, h, scene_num, dialogue=''):
    floor_y = 1000
    draw.rectangle([0, 0, w, h], fill=(245, 242, 235))
    draw.rectangle([0, floor_y, w, h], fill=FLOOR)
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)

    # Coffee table in living room
    draw.rectangle([160, 720, 560, 760], fill=WOOD, outline=INK, width=5)
    line(draw, [(200, 760), (180, floor_y)], width=6)
    line(draw, [(520, 760), (540, floor_y)], width=6)
    draw.ellipse([260, 700, 460, 735], fill=WHITE, outline=INK, width=4)

    samosa_eaten = (scene_num >= 3)
    if not samosa_eaten:
        poly(draw, [(360, 640), (310, 715), (410, 715)], fill=(235, 175, 70), outline=INK, width=4)
        line(draw, [(360, 620), (365, 590)], width=3, fill=(180, 180, 190))
    else:
        circ(draw, 360, 718, 4, fill=(210, 150, 50))
        draw.text((360, 670), '🍽️ (KHAALI!)', fill=RED_ACC, font=FONT_SIGN, anchor='mm')

    if scene_num == 1:
        line(draw, [(280, 660), (440, 660)], width=8, fill=YELLOW_ACC)
        for rx in range(290, 440, 15):
            line(draw, [(rx, 656), (rx, 664)], width=2, fill=INK)
        draw.text((360, 520), 'EXACT 50% SHARE ONLY! 📏', fill=INK, font=FONT_BADGE, anchor='mm')

    elif scene_num == 2:
        bx, by = 260, 640
        circ(draw, bx, by - 60, 44, fill=WHITE, outline=INK, width=4)
        draw.arc([bx - 12, by - 55, bx + 12, by - 35], start=0, end=180, fill=INK, width=3)
        draw.text((360, 520), 'FRIENDSHIP PROMISE! 🤝', fill=GREEN_ACC, font=FONT_BADGE, anchor='mm')

    elif scene_num == 3:
        bx = 360
        circ(draw, bx, 560, 54, fill=WHITE, outline=INK, width=6)
        circ(draw, bx - 18, 550, 14, fill=WHITE, outline=INK, width=3)
        circ(draw, bx + 18, 550, 14, fill=WHITE, outline=INK, width=3)
        circ(draw, bx - 18, 550, 4, fill=INK)
        circ(draw, bx + 18, 550, 4, fill=INK)
        circ(draw, bx, 595, 18, fill=INK)
        draw.text((360, 440), 'SAMOSA KAHAN GAYA?! 😱', fill=RED_ACC, font=FONT_BADGE, anchor='mm')

    else:
        dx = 360
        circ(draw, dx, 560, 56, fill=WHITE, outline=INK, width=6)
        circ(draw, dx - 35, 570, 22, fill=(255, 220, 220), outline=INK, width=3)
        circ(draw, dx + 35, 570, 22, fill=(255, 220, 220), outline=INK, width=3)
        draw.arc([dx - 15, 575, dx + 15, 595], start=0, end=180, fill=INK, width=4)
        draw.rounded_rectangle([120, 410, 600, 500], radius=16, fill=RED_ACC, outline=WHITE, width=4)
        draw.text((360, 455), 'AAKHRI BITE BETRAYAL! 🥟💀', fill=WHITE, font=FONT_BADGE, anchor='mm')

# ──────────────────────────────────────────────────────────────────────────────
# THEME 8: FATHER & AC TEMPERATURE (18°C Freeze vs ₹5000 Bijli Bill)
# ──────────────────────────────────────────────────────────────────────────────
def draw_ac_father_scene(draw, t, dur, w, h, scene_num, dialogue=""):
    floor_y = 1000
    wall_col = (230, 242, 252) if scene_num in [1, 3] else (250, 240, 235)
    draw.rectangle([0, 0, w, h], fill=wall_col)
    
    draw.rectangle([0, floor_y, w, h], fill=WOOD)
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)
    for px in range(0, w, 120):
        line(draw, [(px, floor_y), (px + 40, h)], width=3, fill=WOOD_D)

    ac_x, ac_y, ac_w, ac_h = 160, 160, 400, 120
    draw.rounded_rectangle([ac_x, ac_y, ac_x + ac_w, ac_y + ac_h], radius=16, fill=WHITE, outline=INK, width=5)
    line(draw, [(ac_x + 20, ac_y + ac_h - 20), (ac_x + ac_w - 20, ac_y + ac_h - 20)], width=4, fill=(180, 190, 205))
    
    draw.rounded_rectangle([ac_x + ac_w - 110, ac_y + 35, ac_x + ac_w - 20, ac_y + 85], radius=8, fill=(30, 35, 45), outline=INK, width=2)
    disp_temp = "18°C" if scene_num < 4 else "26°C"
    disp_col = CYAN_ACC if scene_num < 4 else YELLOW_ACC
    draw.text((ac_x + ac_w - 65, ac_y + 60), disp_temp, fill=disp_col, font=FONT_SIGN, anchor='mm')
    
    vent_open = 15 * math.sin(t * 4)
    line(draw, [(ac_x + 40, ac_y + ac_h), (ac_x + ac_w - 40, ac_y + ac_h + 10 + vent_open)], width=5, fill=INK)
    
    for i, lx in enumerate(range(ac_x + 60, ac_x + ac_w - 60, 50)):
        wave_y = (t * 200 + i * 40) % 300
        line(draw, [(lx, ac_y + ac_h + 20 + wave_y), (lx - 20, ac_y + ac_h + 70 + wave_y)], width=3, fill=CYAN_ACC)

    if scene_num in [1, 3]:
        shiver_x = math.sin(t * 40) * 4
        bx, by = 360 + shiver_x, 700
        circ(draw, bx, by - 120, 50, fill=WHITE, outline=INK, width=5)
        line(draw, [(bx - 16, by - 105), (bx + 16, by - 105)], width=3)
        for tx in range(int(bx - 14), int(bx + 15), 6):
            line(draw, [(tx, by - 110), (tx, by - 100)], width=2)
        circ(draw, bx, by - 120, 8, fill=CYAN_ACC, outline=None)
        line(draw, [(bx, by - 70), (bx, by + 90)], width=6)
        line(draw, [(bx, by + 90), (bx - 35, floor_y)], width=6)
        line(draw, [(bx, by + 90), (bx + 35, floor_y)], width=6)
        line(draw, [(bx, by - 30), (bx + 50, by - 50)], width=6)
        draw.rectangle([bx + 45, by - 70, bx + 70, by - 25], fill=(50, 50, 60), outline=INK, width=2)
        draw.text((360, 480), "ARCTIC FREEZE! 🥶❄️", fill=CYAN_ACC, font=FONT_BADGE, anchor='mm')
    else:
        fx, fy = 360, 680
        circ(draw, fx, fy - 120, 54, fill=WHITE, outline=INK, width=5)
        draw.rectangle([fx - 38, fy - 140, fx - 8, fy - 118], fill=None, outline=INK, width=3)
        draw.rectangle([fx + 8, fy - 140, fx + 38, fy - 118], fill=None, outline=INK, width=3)
        line(draw, [(fx - 8, fy - 128), (fx + 8, fy - 128)], width=3)
        draw.arc([fx - 24, fy - 114, fx, fy - 98], start=0, end=180, fill=INK, width=5)
        draw.arc([fx, fy - 114, fx + 24, fy - 98], start=0, end=180, fill=INK, width=5)
        line(draw, [(fx - 36, fy - 150), (fx - 10, fy - 142)], width=4)
        line(draw, [(fx + 36, fy - 150), (fx + 10, fy - 142)], width=4)
        draw.text((fx - 70, fy - 155), "♨️", fill=RED_ACC, font=FONT_SIGN, anchor='mm')
        draw.text((fx + 70, fy - 155), "♨️", fill=RED_ACC, font=FONT_SIGN, anchor='mm')
        line(draw, [(fx, fy - 66), (fx, fy + 90)], width=6)
        line(draw, [(fx, fy + 90), (fx - 40, floor_y)], width=6)
        line(draw, [(fx, fy + 90), (fx + 40, floor_y)], width=6)
        line(draw, [(fx, fy - 20), (fx - 70, fy - 10)], width=6)
        draw.rectangle([fx - 170, fy - 80, fx - 65, fy + 60], fill=WHITE, outline=RED_ACC, width=3)
        draw.text((fx - 118, fy - 40), "BIJLI BILL", fill=RED_ACC, font=FONT_SMALL, anchor='mm')
        draw.text((fx - 118, fy - 10), "₹5,480/-", fill=INK, font=FONT_SIGN, anchor='mm')
        draw.text((fx - 118, fy + 25), "DUE: TODAY!", fill=RED_ACC, font=FONT_SMALL, anchor='mm')
        line(draw, [(fx, fy - 20), (fx + 65, fy - 50)], width=6)
        draw.rectangle([fx + 55, fy - 70, fx + 80, fy - 25], fill=INK, outline=YELLOW_ACC, width=2)
        draw.text((360, 480), "KASHMIR BANA RAKHA HAI?! 😡🔥", fill=RED_ACC, font=FONT_BADGE, anchor='mm')


# ──────────────────────────────────────────────────────────────────────────────
# THEME 9: STREET DOGS AT NIGHT (Fearless Walk vs Sprint)
# ──────────────────────────────────────────────────────────────────────────────
def draw_street_dog_scene(draw, t, dur, w, h, scene_num, dialogue=""):
    floor_y = 1000
    draw.rectangle([0, 0, w, h], fill=(20, 24, 38))
    draw.rectangle([0, floor_y, w, h], fill=(45, 48, 55))
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)
    for rx in range(0, w, 80):
        line(draw, [(rx, floor_y + 120), (rx + 45, floor_y + 120)], width=6, fill=YELLOW_ACC)

    draw.rectangle([60, 200, 78, floor_y], fill=(120, 130, 145), outline=INK, width=3)
    line(draw, [(70, 200), (140, 150)], width=8, fill=(120, 130, 145))
    poly(draw, [(140, 150), (20, floor_y), (380, floor_y)], fill=(255, 245, 180, 40))
    circ(draw, 140, 150, 18, fill=YELLOW_ACC, outline=INK, width=2)

    dog_x = 520
    dog_y = floor_y - 20
    draw.ellipse([dog_x - 60, dog_y - 50, dog_x + 40, dog_y], fill=(160, 120, 80), outline=INK, width=4)
    circ(draw, dog_x - 70, dog_y - 65, 24, fill=(160, 120, 80), outline=INK, width=4)
    poly(draw, [(dog_x - 85, dog_y - 85), (dog_x - 75, dog_y - 65), (dog_x - 90, dog_y - 65)], fill=(130, 90, 50), outline=INK, width=3)
    tail_ang = math.sin(t * 15) * 20
    line(draw, [(dog_x + 35, dog_y - 35), (dog_x + 70, dog_y - 65 + tail_ang)], width=5, fill=INK)
    line(draw, [(dog_x - 40, dog_y), (dog_x - 45, floor_y)], width=5)
    line(draw, [(dog_x - 20, dog_y), (dog_x - 20, floor_y)], width=5)
    line(draw, [(dog_x + 10, dog_y), (dog_x + 15, floor_y)], width=5)
    line(draw, [(dog_x + 30, dog_y), (dog_x + 35, floor_y)], width=5)

    if scene_num in [1, 2]:
        circ(draw, dog_x - 78, dog_y - 68, 4, fill=WHITE)
        circ(draw, dog_x - 78, dog_y - 68, 2, fill=INK)
        bx, by = 240, 720
        circ(draw, bx, by - 120, 48, fill=WHITE, outline=INK, width=5)
        circ(draw, bx - 5, by - 132, 5, fill=INK)
        circ(draw, bx + 15, by - 132, 5, fill=INK)
        circ(draw, bx + 8, by - 105, 5, fill=INK)
        circ(draw, bx - 38, by - 115, 6, fill=CYAN_ACC, outline=INK, width=2)
        line(draw, [(bx, by - 72), (bx, by + 80)], width=6)
        line(draw, [(bx, by + 80), (bx - 30, floor_y)], width=6)
        line(draw, [(bx, by + 80), (bx + 30, floor_y)], width=6)
        line(draw, [(bx, by - 30), (bx - 20, by + 30)], width=5)
        line(draw, [(bx, by - 30), (bx + 20, by + 30)], width=5)
        draw.text((360, 480), "ACTING CONFIDENT... 🕶️", fill=WHITE, font=FONT_BADGE, anchor='mm')
    else:
        draw.text((dog_x - 120, dog_y - 120), "BHO-BHO! 🐶🔥", fill=RED_ACC, font=FONT_BADGE, anchor='mm')
        sprint_x = (t * 300) % 250
        bx, by = 180 + sprint_x, 720
        circ(draw, bx, by - 120, 52, fill=WHITE, outline=INK, width=5)
        circ(draw, bx, by - 98, 16, fill=INK)
        circ(draw, bx - 16, by - 130, 14, fill=WHITE, outline=INK, width=2)
        circ(draw, bx + 16, by - 130, 14, fill=WHITE, outline=INK, width=2)
        circ(draw, bx - 16, by - 130, 4, fill=INK)
        circ(draw, bx + 16, by - 130, 4, fill=INK)
        leg_rot = math.sin(t * 30) * 45
        line(draw, [(bx, by + 80), (bx - 60 + leg_rot, floor_y)], width=7)
        line(draw, [(bx, by + 80), (bx + 60 - leg_rot, floor_y)], width=7)
        line(draw, [(bx, by - 30), (bx - 60, by - 90)], width=6)
        line(draw, [(bx, by - 30), (bx + 60, by - 90)], width=6)
        for sx, sy in [(bx - 80, floor_y - 20), (bx - 120, floor_y - 30), (bx - 100, floor_y - 50)]:
            circ(draw, sx, sy, 18, fill=SMOKE_COL, outline=INK, width=2)
        draw.text((360, 480), "FULL 100M SPRINT! 💨💀", fill=YELLOW_ACC, font=FONT_BADGE, anchor='mm')


# ──────────────────────────────────────────────────────────────────────────────
# THEME 10: TOPPER EXAM SHEET & CHEATING
# ──────────────────────────────────────────────────────────────────────────────
def draw_classroom_topper_scene(draw, t, dur, w, h, scene_num, dialogue=""):
    floor_y = 1000
    draw.rectangle([0, 0, w, h], fill=(245, 245, 238))
    draw.rectangle([80, 140, 640, 420], fill=(42, 68, 52), outline=WOOD, width=8)
    draw.text((360, 200), "FINAL SEMESTER EXAM 📝", fill=WHITE, font=FONT_SIGN, anchor='mm')
    draw.text((360, 260), "TIME REMAINING: 10 MINS ⏳", fill=YELLOW_ACC, font=FONT_SIGN, anchor='mm')
    draw.text((360, 320), "NO TALKING! - PROF. SHARMA", fill=(210, 230, 220), font=FONT_SMALL, anchor='mm')

    draw.rectangle([0, floor_y, w, h], fill=FLOOR)
    line(draw, [(0, floor_y), (w, floor_y)], width=6, fill=INK)

    desk_y = 800
    draw.rectangle([60, desk_y, 660, desk_y + 60], fill=WOOD, outline=INK, width=5)
    line(draw, [(120, desk_y + 60), (120, floor_y)], width=8, fill=WOOD_D)
    line(draw, [(600, desk_y + 60), (600, floor_y)], width=8, fill=WOOD_D)

    tx, ty = 220, 680
    circ(draw, tx, ty - 100, 44, fill=WHITE, outline=INK, width=4)
    draw.rectangle([tx - 28, ty - 115, tx - 6, ty - 98], fill=None, outline=INK, width=2)
    draw.rectangle([tx + 6, ty - 115, tx + 28, ty - 98], fill=None, outline=INK, width=2)
    line(draw, [(tx - 6, ty - 106), (tx + 6, ty - 106)], width=2)
    line(draw, [(tx, ty - 56), (tx, desk_y)], width=6)
    pen_vib = math.sin(t * 35) * 8
    line(draw, [(tx, ty - 20), (tx + 30 + pen_vib, desk_y - 10)], width=5)
    for sy in range(desk_y - 45, desk_y - 10, 8):
        draw.rectangle([tx - 10, sy, tx + 60, sy + 30], fill=WHITE, outline=INK, width=2)
    draw.text((tx + 25, desk_y - 60), "SHEET #4! 📑", fill=RED_ACC, font=FONT_SMALL, anchor='mm')

    sx, sy = 500, 680
    circ(draw, sx, sy - 100, 48, fill=WHITE, outline=INK, width=5)
    eye_look = -14
    circ(draw, sx - 16 + eye_look, sy - 105, 5, fill=INK)
    circ(draw, sx + 16 + eye_look, sy - 105, 5, fill=INK)
    line(draw, [(sx - 10, sy - 85), (sx + 10, sy - 85)], width=4)
    line(draw, [(sx, sy - 85), (sx + 35, sy - 115)], width=4, fill=YELLOW_ACC)
    for dw in [(-30, -110), (35, -110)]:
        circ(draw, sx + dw[0], sy + dw[1], 6, fill=CYAN_ACC, outline=INK, width=2)
    draw.rectangle([sx - 40, desk_y - 25, sx + 40, desk_y + 10], fill=WHITE, outline=INK, width=2)
    draw.text((sx, desk_y - 10), "BLANK 😭", fill=RED_ACC, font=FONT_SMALL, anchor='mm')

    if scene_num in [1, 2]:
        draw.text((360, 480), "BHAI BAS QUESTION 1 DIKHA DE! 🙏", fill=INK, font=FONT_BADGE, anchor='mm')
    else:
        draw.text((360, 480), "TOPPER: 'AUR EK EXTRA SHEET SIR!' 💀", fill=RED_ACC, font=FONT_BADGE, anchor='mm')


# ──────────────────────────────────────────────────────────────────────────────
# MASTER THEME DISPATCHER
# ──────────────────────────────────────────────────────────────────────────────
def get_theme_for_topic(topic_str):
    t = str(topic_str).lower()
    if any(k in t for k in ["ac", "temperature", "father", "papa", "degree", "freeze", "cooler"]):
        return "ac_father"
    elif any(k in t for k in ["dog", "street dog", "fearless", "bark", "night walk"]):
        return "street_dog"
    elif any(k in t for k in ["topper", "exam", "cheat", "sheet", "supplement", "paper"]):
        return "classroom_topper"
    elif any(k in t for k in ["gym", "workout", "dumbbell", "fitness", "exercise", "biceps"]):
        return "gym"
    elif any(k in t for k in ["interview", "viva", "job", "hr", "professor", "resume"]):
        return "interview"
    elif any(k in t for k in ["hunger", "fridge", "midnight", "food", "maggie", "kitchen", "chips"]):
        return "kitchen"
    elif any(k in t for k in ["battery", "phone", "charge", "dying", "switch off"]):
        return "battery"
    elif any(k in t for k in ["ready", "dressing", "longer", "almost done", "mirror"]):
        return "ready"
    elif any(k in t for k in ["snack", "bite", "samosa", "splitting", "fairly"]):
        return "snacks"
    elif any(k in t for k in ["money", "paisa", "upi", "invisible", "udhaar", "lend", "borrow", "bill", "shake", "restaurant"]):
        return "tapri_money"
    else:
        return "tapri_money"


def render_themed_scene_frame(draw, t, dur, w, h, topic, scene_num, dialogue=""):
    theme = get_theme_for_topic(topic)
    if theme == "ac_father":
        draw_ac_father_scene(draw, t, dur, w, h, scene_num, dialogue)
    elif theme == "street_dog":
        draw_street_dog_scene(draw, t, dur, w, h, scene_num, dialogue)
    elif theme == "classroom_topper":
        draw_classroom_topper_scene(draw, t, dur, w, h, scene_num, dialogue)
    elif theme == "gym":
        draw_gym_scene(draw, t, dur, w, h, scene_num, dialogue)
    elif theme == "interview":
        draw_interview_scene(draw, t, dur, w, h, scene_num, dialogue)
    elif theme == "kitchen":
        draw_kitchen_scene(draw, t, dur, w, h, scene_num, dialogue)
    elif theme == "battery":
        draw_battery_scene(draw, t, dur, w, h, scene_num, dialogue)
    elif theme == "ready":
        draw_ready_scene(draw, t, dur, w, h, scene_num, dialogue)
    elif theme == "snacks":
        draw_snacks_scene(draw, t, dur, w, h, scene_num, dialogue)
    else:
        draw_tapri_money_scene(draw, t, dur, w, h, scene_num, dialogue)
