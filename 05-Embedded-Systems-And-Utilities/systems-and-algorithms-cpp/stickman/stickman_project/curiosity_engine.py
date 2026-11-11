"""
curiosity_engine.py
===================
Ultra-Fast 3D Neomorphism Science Curiosity Engine.
- Pre-baked Static Neomorphic Backdrop: Top-Left Specular Glow + Bottom-Right Soft Diffuse Shadow.
- 60+ FPS Rendering speed.
- Clean Light Palette: Soft warm whites, clinical light slate (#ECEFF8), with crisp ink-black outlines.
- 3D Capsule Stickman Character (Jointed limb segments, capsule torso, spherical joints, blinking eyes, expressive gestures).
- Guaranteed Scientific Photo/Diagram in upper Neomorphic frame (smart multi-pass Wikimedia search + guaranteed fallback).
- Kinetic Typography in lower 3D Neomorphic Card with vibrant accent highlights.
- Bilingual Neural Voice:
  * Hindi: hi-IN-MadhurNeural
  * English: en-US-GuyNeural (or custom override)
"""

import os
import sys
import re
import math
import textwrap
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import numpy as np
import moviepy.editor as mp

import curiosity_director

OUTPUT_DIR = "pipeline_output"
TEMP_DIR = os.path.join(OUTPUT_DIR, "curiosity_temp")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
SFX_DIR = "sfx"

# 3D Neomorphism Palette
BG_COLOR = (236, 240, 248)       # Soft modern slate base
SHADOW_DARK = (188, 196, 212)    # Bottom-right diffuse shadow
SHADOW_LIGHT = (255, 255, 255)   # Top-left specular highlight
CARD_FACE = (246, 249, 255)      # Card surface
LINE_COLOR = (24, 28, 36)        # Crisp ink-black border
ACCENT_BLUE = (66, 133, 244)
ACCENT_YELLOW = (255, 179, 0)
ACCENT_RED = (234, 67, 53)
ACCENT_GREEN = (52, 168, 83)

def get_font(size, bold=True, language="en"):
    if language == "hi" and os.path.exists(r"C:\Windows\Fonts\Nirmala.ttc"):
        try:
            return ImageFont.truetype(r"C:\Windows\Fonts\Nirmala.ttc", size)
        except Exception:
            pass
    font_name = "arialbd.ttf" if bold else "arial.ttf"
    try:
        return ImageFont.truetype(font_name, size)
    except Exception:
        return ImageFont.load_default()


def bake_static_neomorphic_backdrop(w=720, h=1280):
    """
    Pre-renders the high-resolution 3D Neomorphic static background with dual Gaussian shadows.
    Runs ONCE per video to give instant 30-60 FPS render speed!
    """
    base = Image.new("RGBA", (w, h), BG_COLOR)

    cards = [
        (50, 50, 620, 125, 24, 7),     # Top Hook Card
        (50, 200, 620, 420, 28, 9),    # Middle Diagram Card
        (200, 645, 320, 50, 25, 5),    # Scene Pill
        (50, 1055, 620, 175, 26, 7),   # Bottom Subtitles Card
    ]

    # 1. Dark diffuse shadow layer
    s_dark = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_draw = ImageDraw.Draw(s_dark)
    for x, y, cw, ch, rad, dep in cards:
        d_draw.rounded_rectangle([x + dep, y + dep, x + cw + dep, y + ch + dep], radius=rad, fill=SHADOW_DARK)
    s_dark = s_dark.filter(ImageFilter.GaussianBlur(8))

    # 2. Light specular highlight layer
    s_light = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    l_draw = ImageDraw.Draw(s_light)
    for x, y, cw, ch, rad, dep in cards:
        l_draw.rounded_rectangle([x - dep, y - dep, x + cw - dep, y + ch - dep], radius=rad, fill=SHADOW_LIGHT)
    s_light = s_light.filter(ImageFilter.GaussianBlur(8))

    base.paste(s_light, (0, 0), s_light)
    base.paste(s_dark, (0, 0), s_dark)

    # 3. Card Faces
    b_draw = ImageDraw.Draw(base)
    for x, y, cw, ch, rad, dep in cards:
        b_draw.rounded_rectangle([x, y, x + cw, y + ch], radius=rad, fill=CARD_FACE, outline=LINE_COLOR, width=3)

    # Pre-render floor shadow for stickman
    floor_sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(floor_sh).ellipse([240 - 70, 1040 - 14, 240 + 70, 1040 + 14], fill=(180, 190, 208, 190))
    floor_sh = floor_sh.filter(ImageFilter.GaussianBlur(6))
    base.paste(floor_sh, (0, 0), floor_sh)

    return base


def prepare_diagram_image(img_path):
    """
    Loads any image, composites transparent PNG/LA alpha onto pure clean white background,
    and returns a crisp RGB PIL Image.
    """
    if not img_path or not os.path.exists(img_path):
        return None
    try:
        raw = Image.open(img_path)
        # Convert LA or RGBA with transparent alpha onto pure clean white background
        if raw.mode in ("RGBA", "LA") or (raw.mode == "P" and "transparency" in raw.info):
            raw_rgba = raw.convert("RGBA")
            bg = Image.new("RGBA", raw_rgba.size, (255, 255, 255, 255))
            flattened = Image.alpha_composite(bg, raw_rgba).convert("RGB")
        else:
            flattened = raw.convert("RGB")
        return flattened
    except Exception as e:
        print(f"[!] Diagram prep error for {img_path}: {e}")
        return None


def create_fallback_science_diagram(topic, heading="SCIENCE FACT", scene_num=1, iw=592, ih=392, language="en"):
    """
    Guarantees a sleek 3D Neomorphic science laboratory infographic card
    with a UNIQUE icon and layout for every scene! Zero blank or repeating diagrams.
    """
    card = Image.new("RGB", (iw, ih), CARD_FACE)
    d = ImageDraw.Draw(card)

    # Subtle modern grid background
    for gx in range(0, iw, 40):
        d.line([(gx, 0), (gx, ih)], fill=(234, 239, 248), width=1)
    for gy in range(0, ih, 40):
        d.line([(0, gy), (iw, gy)], fill=(234, 239, 248), width=1)

    cx, cy = iw // 2, ih // 2 - 25

    if scene_num == 1:
        # Precision Chronometer / Dial Clock
        d.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], outline=ACCENT_BLUE, width=4)
        for ang in range(0, 360, 30):
            rad = math.radians(ang)
            x1 = cx + int(math.cos(rad) * 55)
            y1 = cy + int(math.sin(rad) * 55)
            x2 = cx + int(math.cos(rad) * 65)
            y2 = cy + int(math.sin(rad) * 65)
            d.line([(x1, y1), (x2, y2)], fill=LINE_COLOR, width=2)
        d.line([(cx, cy), (cx, cy - 40)], fill=ACCENT_RED, width=3)
        d.line([(cx, cy), (cx + 30, cy + 10)], fill=LINE_COLOR, width=3)
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=LINE_COLOR)

    elif scene_num == 2:
        # Molecular Bond & Atoms
        nodes = [(cx - 60, cy - 35), (cx + 50, cy - 40), (cx, cy + 45)]
        for p1, p2 in [(nodes[0], nodes[1]), (nodes[1], nodes[2]), (nodes[2], nodes[0])]:
            d.line([p1, p2], fill=LINE_COLOR, width=5)
            d.line([p1, p2], fill=(255, 255, 255), width=2)
        for idx, (nx, ny) in enumerate(nodes):
            col = [ACCENT_RED, ACCENT_BLUE, ACCENT_YELLOW][idx % 3]
            d.ellipse([nx - 22, ny - 22, nx + 22, ny + 22], fill=col, outline=LINE_COLOR, width=3)
            d.ellipse([nx - 14, ny - 14, nx - 4, ny - 4], fill=(255, 255, 255))

    elif scene_num == 3:
        # Brain Synapse / Neural Waves
        for r in [25, 55, 85]:
            d.arc([cx - r, cy - r, cx + r, cy + r], start=200, end=340, fill=ACCENT_BLUE, width=3)
            d.arc([cx - r, cy - r, cx + r, cy + r], start=20, end=160, fill=ACCENT_YELLOW, width=3)
        d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=ACCENT_RED, outline=LINE_COLOR, width=3)
        d.ellipse([cx - 12, cy - 12, cx - 4, cy - 4], fill=(255, 255, 255))

    else:
        # Orbital Rings / Galaxy Spacetime
        d.ellipse([cx - 100, cy - 40, cx + 100, cy + 40], outline=ACCENT_BLUE, width=3)
        d.ellipse([cx - 40, cy - 100, cx + 40, cy + 100], outline=ACCENT_GREEN, width=3)
        d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=ACCENT_RED, outline=LINE_COLOR, width=3)
        d.ellipse([cx - 16, cy - 16, cx - 6, cy - 6], fill=(255, 255, 255))

    # Topic label inside diagram
    t_font = get_font(22, bold=True, language=language)
    clean_t = re.sub(r'[^\x20-\x7E\u0900-\u097F]', '', topic).strip()
    d.text((cx, ih - 75), clean_t[:36], fill=LINE_COLOR, font=t_font, anchor="mm")

    sub_font = get_font(15, bold=True, language=language)
    d.text((cx, ih - 45), f"• {heading.upper()} •", fill=ACCENT_BLUE, font=sub_font, anchor="mm")

    return card


def draw_3d_stickman(draw, cx, cy, t, action="pointing"):
    """
    Renders an expressive 3D Neomorphic Capsule character with:
    - 3D Pill Torso
    - Segmented capsule limbs with spherical joints
    - Eye blinking and speaking mouth
    - Action-specific expressive poses
    - Crisp black outlines
    """
    bob = math.sin(t * 8) * 6
    floor_y = 1040

    # Torso Pill Body
    torso_top = cy - 40 + bob
    torso_bot = cy + 105 + bob
    torso_w = 44

    # Legs (Capsule limbs)
    hip_l = (cx - 15, torso_bot - 15)
    hip_r = (cx + 15, torso_bot - 15)
    knee_l = (cx - 28, torso_bot + 65)
    knee_r = (cx + 28, torso_bot + 65)
    foot_l = (cx - 36, floor_y)
    foot_r = (cx + 36, floor_y)

    for p1, p2 in [(hip_l, knee_l), (knee_l, foot_l), (hip_r, knee_r), (knee_r, foot_r)]:
        draw.line([p1, p2], fill=LINE_COLOR, width=12)
        draw.line([p1, p2], fill=(255, 255, 255), width=6)

    # Knee Spheres
    draw.ellipse([knee_l[0] - 8, knee_l[1] - 8, knee_l[0] + 8, knee_l[1] + 8], fill=CARD_FACE, outline=LINE_COLOR, width=3)
    draw.ellipse([knee_r[0] - 8, knee_r[1] - 8, knee_r[0] + 8, knee_r[1] + 8], fill=CARD_FACE, outline=LINE_COLOR, width=3)

    # Shoes (Neomorphic 3D oval caps)
    draw.rounded_rectangle([foot_l[0] - 16, foot_l[1] - 10, foot_l[0] + 12, foot_l[1] + 6], radius=8, fill=(240, 244, 252), outline=LINE_COLOR, width=3)
    draw.rounded_rectangle([foot_r[0] - 12, foot_r[1] - 10, foot_r[0] + 16, foot_r[1] + 6], radius=8, fill=(240, 244, 252), outline=LINE_COLOR, width=3)

    # Torso Pill Body with clean black border
    draw.rounded_rectangle([cx - torso_w // 2, torso_top, cx + torso_w // 2, torso_bot], radius=torso_w // 2, fill=(252, 254, 255), outline=LINE_COLOR, width=4)
    # Tie / Badge Detail
    draw.line([(cx, torso_top + 16), (cx, torso_top + 65)], fill=LINE_COLOR, width=3)
    draw.polygon([(cx, torso_top + 65), (cx - 8, torso_top + 54), (cx + 8, torso_top + 54)], fill=ACCENT_BLUE)

    # Arms & Poses
    sh_l = (cx - torso_w // 2 + 4, torso_top + 18)
    sh_r = (cx + torso_w // 2 - 4, torso_top + 18)

    if "scratch" in action:
        # Scratching head
        arm_wave = math.sin(t * 12) * 10
        el_l = (cx - 48, torso_top - 12)
        h_l = (cx - 24 + arm_wave, cy - 110 + bob)
        el_r = (cx + 36, torso_top + 45)
        h_r = (cx + 20, torso_top + 80)
    elif "celebrat" in action or "thumbs" in action:
        # Celebration double thumbs-up
        el_l = (cx - 52, torso_top - 30)
        h_l = (cx - 68, torso_top - 80)
        el_r = (cx + 52, torso_top - 30)
        h_r = (cx + 68, torso_top - 80)
    elif "spark" in action or "brain" in action:
        # Hands on cheeks / mind blown
        el_l = (cx - 55, torso_top - 15)
        h_l = (cx - 44, cy - 85 + bob)
        el_r = (cx + 55, torso_top - 15)
        h_r = (cx + 44, cy - 85 + bob)
    else:
        # Pointing to upper diagram
        el_l = (cx - 36, torso_top + 45)
        h_l = (cx - 20, torso_top + 80)
        el_r = (cx + 55, torso_top - 20)
        h_r = (cx + 105, torso_top - 70)

    for p1, p2 in [(sh_l, el_l), (el_l, h_l), (sh_r, el_r), (el_r, h_r)]:
        draw.line([p1, p2], fill=LINE_COLOR, width=12)
        draw.line([p1, p2], fill=(255, 255, 255), width=6)

    # Hand Spheres
    draw.ellipse([h_l[0] - 9, h_l[1] - 9, h_l[0] + 9, h_l[1] + 9], fill=CARD_FACE, outline=LINE_COLOR, width=3)
    draw.ellipse([h_r[0] - 9, h_r[1] - 9, h_r[0] + 9, h_r[1] + 9], fill=CARD_FACE, outline=LINE_COLOR, width=3)

    # Extra visuals based on action
    if "point" in action or action == "pointing":
        # Laser pointer line to diagram box
        target_pt = (360, 410)
        draw.line([h_r, target_pt], fill=ACCENT_RED, width=3)
        pulse_r = int(14 + math.sin(t * 16) * 4)
        draw.ellipse([target_pt[0] - pulse_r, target_pt[1] - pulse_r, target_pt[0] + pulse_r, target_pt[1] + pulse_r], outline=ACCENT_RED, width=3)
    elif "scratch" in action:
        # Floating 3D Question Mark
        q_y = int(cy - 160 + bob - (t * 25 % 40))
        q_font = get_font(36, bold=True, language="en")
        draw.text((cx + 65, q_y), "?", fill=ACCENT_BLUE, font=q_font, anchor="mm")
    elif "spark" in action or "brain" in action:
        # Radiating Energy Spark lines
        for spk in range(8):
            ang = spk * (math.pi / 4) + t * 7
            ex = cx + int(math.cos(ang) * 85)
            ey = cy - 90 + bob + int(math.sin(ang) * 85)
            draw.line([(cx, cy - 90 + bob), (ex, ey)], fill=ACCENT_YELLOW, width=4)

    # Head (3D Neomorphic Sphere)
    head_y = cy - 90 + bob
    head_r = 50
    # Base head sphere
    draw.ellipse([cx - head_r, head_y - head_r, cx + head_r, head_y + head_r], fill=(255, 255, 255), outline=LINE_COLOR, width=4)
    # Specular gloss highlight on top-left of sphere
    draw.ellipse([cx - head_r + 10, head_y - head_r + 8, cx - head_r + 32, head_y - head_r + 26], fill=(242, 246, 255))
    # Soft shaded arc on bottom-right
    draw.arc([cx - head_r + 4, head_y - head_r + 4, cx + head_r - 4, head_y + head_r - 4], start=25, end=115, fill=(210, 220, 235), width=6)

    # Glasses
    gx1, gx2 = cx - 38, cx - 8
    gx3, gx4 = cx + 8, cx + 38
    gy1, gy2 = head_y - 12, head_y + 14
    draw.rounded_rectangle([gx1, gy1, gx2, gy2], radius=6, fill=(255, 255, 255), outline=LINE_COLOR, width=3)
    draw.rounded_rectangle([gx3, gy1, gx4, gy2], radius=6, fill=(255, 255, 255), outline=LINE_COLOR, width=3)
    draw.line([(gx2, head_y + 1), (gx3, head_y + 1)], fill=LINE_COLOR, width=4)
    # Glasses Glare
    draw.line([(gx1 + 6, gy2 - 4), (gx2 - 6, gy1 + 4)], fill=(180, 215, 255), width=2)
    draw.line([(gx3 + 6, gy2 - 4), (gx4 - 6, gy1 + 4)], fill=(180, 215, 255), width=2)

    # Eyes & Eyebrows (Blinking)
    is_blink = (math.sin(t * 3.5) > 0.93)
    if is_blink:
        draw.line([(cx - 26, head_y - 1), (cx - 18, head_y - 1)], fill=LINE_COLOR, width=3)
        draw.line([(cx + 18, head_y - 1), (cx + 26, head_y - 1)], fill=LINE_COLOR, width=3)
    else:
        draw.ellipse([cx - 26, head_y - 3, cx - 20, head_y + 3], fill=LINE_COLOR)
        draw.ellipse([cx + 20, head_y - 3, cx + 26, head_y + 3], fill=LINE_COLOR)

    draw.line([(cx - 36, head_y - 18), (cx - 12, head_y - 16)], fill=LINE_COLOR, width=3)
    draw.line([(cx + 12, head_y - 16), (cx + 36, head_y - 20)], fill=LINE_COLOR, width=3)

    # Mouth talking
    mouth_open = int(abs(math.sin(t * 14)) * 7)
    draw.ellipse([cx - 9, head_y + 26, cx + 9, head_y + 26 + mouth_open], fill=LINE_COLOR)


import indic_text_renderer

def render_scene_frame(backdrop_img, t, dur, w, h, scene_meta, hook_text, img_obj=None, language="hi", text_overlays=None):
    """
    Blazing-fast compositor: takes pre-baked backdrop, overlays dynamic diagram, text, and 3D character.
    Uses DirectWrite/PyQt OpenType shaping for 100% textbook Devanagari Hindi typography.
    """
    frame = backdrop_img.copy()

    # 1. Top Hook Card Content
    draw = ImageDraw.Draw(frame)
    badge_font = get_font(13, bold=True, language="en")
    draw.text((w // 2, 70), "DID YOU KNOW? • CURIOSITY LAB", fill=ACCENT_BLUE, font=badge_font, anchor="mm")

    if text_overlays and "hook" in text_overlays:
        frame.paste(text_overlays["hook"], (70, 94), text_overlays["hook"])
    else:
        clean_hook = re.sub(r'[^\x20-\x7E\u0900-\u097F]', '', hook_text).strip()
        h_font = get_font(24, bold=True, language=language)
        h_lines = textwrap.wrap(clean_hook, width=32 if language == "en" else 28)
        start_y = 98
        for i, line in enumerate(h_lines[:2]):
            draw.text((w // 2, start_y + i * 28), line, fill=LINE_COLOR, font=h_font, anchor="mm")

    # 2. Middle Diagram Inside 3D Frame
    box_x, box_y, box_w, box_h = 50, 200, 620, 420
    inner_pad = 14
    ix = box_x + inner_pad
    iy = box_y + inner_pad
    iw = box_w - inner_pad * 2
    ih = box_h - inner_pad * 2

    if img_obj:
        try:
            zoom_f = 1.0 + 0.05 * (t / max(dur, 1))
            nw = int(iw * zoom_f)
            nh = int(ih * zoom_f)
            fitted = ImageOps.fit(img_obj, (nw, nh), method=Image.Resampling.LANCZOS)
            left = (nw - iw) // 2
            top = (nh - ih) // 2
            diag_cropped = fitted.crop((left, top, left + iw, top + ih))

            imask = Image.new("L", (iw, ih), 0)
            ImageDraw.Draw(imask).rounded_rectangle([0, 0, iw, ih], radius=20, fill=255)
            frame.paste(diag_cropped, (ix, iy), imask)
        except Exception:
            pass

    # Inner black border & badge
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle([ix, iy, ix + iw, iy + ih], radius=20, outline=LINE_COLOR, width=3)
    draw.rounded_rectangle([ix + 14, iy + 14, ix + 200, iy + 44], radius=12, fill=(245, 248, 255), outline=LINE_COLOR, width=2)
    draw.ellipse([ix + 24, iy + 24, ix + 34, iy + 34], fill=ACCENT_RED)
    b_font = get_font(13, bold=True, language="en")
    draw.text((ix + 115, iy + 29), "SCIENCE DIAGRAM", fill=LINE_COLOR, font=b_font, anchor="mm")

    # 3. Scene Title Pill
    if text_overlays and "heading" in text_overlays:
        frame.paste(text_overlays["heading"], (200, 648), text_overlays["heading"])
    else:
        s_num = scene_meta.get("scene", 1)
        heading_text = scene_meta.get("heading", f"SCENE {s_num}")
        clean_heading = re.sub(r'[^\x20-\x7E\u0900-\u097F]', '', heading_text).strip().upper()
        head_font = get_font(20, bold=True, language=language)
        draw.text((w // 2, 670), f"• {clean_heading} •", fill=LINE_COLOR, font=head_font, anchor="mm")

    # 4. 3D Neomorphic Stickman
    action = scene_meta.get("animation_action", "pointing")
    draw_3d_stickman(draw, 240, 840, t, action=action)

    # 5. Bottom Kinetic Subtitles
    if text_overlays and "sub_p1" in text_overlays:
        sub_img = text_overlays["sub_p1"] if (t / max(dur, 1)) < 0.5 else text_overlays["sub_p2"]
        frame.paste(sub_img, (70, 1065), sub_img)
    else:
        narration_text = scene_meta.get("narration", "")
        clean_narr = re.sub(r'[^\x20-\x7E\u0900-\u097F]', '', narration_text).strip()
        all_lines = textwrap.wrap(clean_narr, width=34 if language == "en" else 28)

        if len(all_lines) <= 3:
            display_lines = all_lines
        else:
            mid = (len(all_lines) + 1) // 2
            progress = t / max(dur, 1)
            display_lines = all_lines[:mid] if progress < 0.5 else all_lines[mid:]

        body_font = get_font(23, bold=True, language=language)
        colors = [LINE_COLOR, ACCENT_BLUE, (180, 80, 0), LINE_COLOR]
        start_sub_y = 1095
        for i, line in enumerate(display_lines[:3]):
            draw.text((w // 2, start_sub_y + i * 34), line, fill=colors[i % len(colors)], font=body_font, anchor="mm")

    return np.array(frame.convert("RGB"))


def produce_curiosity_short(topic, base_filename=None, language="hi", voice_override=None):
    """
    Produces a 3D Neomorphic Curiosity Science Short in Hindi (Devanagari) or English.
    Defaults to HINDI ("hi") with hi-IN-MadhurNeural voice for maximum YouTube Shorts virality.
    """
    lang_name = "HINDI (हिंदी)" if language == "hi" else "ENGLISH"
    print("=" * 75)
    print(f"   PRODUCING 3D NEOMORPHISM {lang_name} SCIENCE SHORT (30-45s)")
    print("=" * 75)

    director_data = curiosity_director.get_curiosity_script(topic, language=language)
    hook = director_data.get("hook", f"Did you know the secret of {topic}?")
    title = director_data.get("title", f"{topic} Explained! #shorts #science")
    desc = director_data.get("description", f"Mind-blowing science behind {topic}!\n\n#shorts #science #didyouknow #stickman")
    tags = director_data.get("tags", ["shorts", "science", "didyouknow", "animation"])
    scenes = director_data.get("scenes", [])
    img_queries = director_data.get("image_queries", [topic])

    # Pre-bake backdrop for blazing-fast 30-60 FPS render speed!
    w, h = 720, 1280
    static_backdrop = bake_static_neomorphic_backdrop(w, h)

    # 1. Download a GUARANTEED UNIQUE diagram for EVERY SINGLE SCENE (1 to 4)
    scene_images = {}
    exclude_urls = set()

    for sc in scenes:
        s_num = sc.get("scene", 1)
        heading = sc.get("heading", f"SCENE {s_num}")
        q = sc.get("image_query") or sc.get("heading") or topic
        fname = f"asset_{abs(hash(topic))}_sc_{s_num}.jpg"

        p = curiosity_director.fetch_educational_image(
            query=q,
            filename=fname,
            fallback_topic=topic,
            exclude_urls=exclude_urls
        )
        img_prep = prepare_diagram_image(p) if p else None
        if img_prep:
            scene_images[s_num] = img_prep
            print(f"[+] Scene {s_num} Unique Web Diagram loaded: '{q}'")
        else:
            scene_images[s_num] = create_fallback_science_diagram(
                topic=topic,
                heading=heading,
                scene_num=s_num,
                iw=592,
                ih=392,
                language=language
            )
            print(f"[+] Scene {s_num} Unique Vector Diagram generated: '{heading}'")

    clips = []

    if voice_override:
        chosen_voice = voice_override
    elif language == "hi":
        chosen_voice = "hi-IN-MadhurNeural"
    else:
        chosen_voice = "en-US-GuyNeural"

    print(f"[*] Voice Selected: {chosen_voice} | Language: {language}")

    for sc in scenes:
        s_num = sc.get("scene", 1)
        heading = sc.get("heading", f"SCENE {s_num}")
        narration = sc.get("narration", "")
        sfx_list = sc.get("sfx", [])

        print(f"\n--- Scene {s_num}/4: [{heading}] ---")
        print(f"Narration: '{narration}'")

        voice_wav = os.path.join(TEMP_DIR, f"sc_{s_num}_voice.wav")
        temp_mp3 = voice_wav.replace(".wav", ".mp3")

        tts_cmd = [
            'edge-tts',
            '--voice', chosen_voice,
            '--text', narration,
            '--rate', '+12%',
            '--write-media', temp_mp3
        ]
        subprocess.run(tts_cmd, capture_output=True)

        ffmpeg_cmd = [
            'ffmpeg', '-y', '-i', temp_mp3,
            '-ar', '44100', '-ac', '2',
            '-af', 'volume=1.4',
            voice_wav
        ]
        subprocess.run(ffmpeg_cmd, capture_output=True)

        voice_clip = mp.AudioFileClip(voice_wav)
        dur = max(voice_clip.duration + 0.35, 4.5)

        # Dedicated, unique diagram for this scene
        curr_img_obj = scene_images.get(s_num)

        # Pre-render Indic typography overlays for 100% textbook Devanagari text
        text_overlays = None
        if language == "hi":
            try:
                hook_clean = re.sub(r'[^\x20-\x7E\u0900-\u097F]', '', hook).strip()
                hook_ov = indic_text_renderer.render_indic_text_image(
                    hook_clean, width=580, height=60, font_size=16, color=LINE_COLOR, bold=True, align="center"
                )
                head_clean = re.sub(r'[^\x20-\x7E\u0900-\u097F]', '', heading).strip().upper()
                heading_ov = indic_text_renderer.render_indic_text_image(
                    f"• {head_clean} •", width=320, height=44, font_size=18, color=LINE_COLOR, bold=True, align="center"
                )
                clean_n = re.sub(r'[^\x20-\x7E\u0900-\u097F]', '', narration).strip()
                sentences = [s.strip() for s in re.split(r'[।\.\!\?]', clean_n) if s.strip()]
                if len(sentences) >= 2:
                    mid_idx = (len(sentences) + 1) // 2
                    p1_text = "। ".join(sentences[:mid_idx]) + "।"
                    p2_text = "। ".join(sentences[mid_idx:]) + "।"
                else:
                    words = clean_n.split()
                    mid_idx = max(len(words) // 2, 1)
                    p1_text = " ".join(words[:mid_idx])
                    p2_text = " ".join(words[mid_idx:])
                sub_p1 = indic_text_renderer.render_indic_text_image(
                    p1_text, width=580, height=140, font_size=18, color=LINE_COLOR, bold=True, align="center"
                )
                sub_p2 = indic_text_renderer.render_indic_text_image(
                    p2_text, width=580, height=140, font_size=18, color=LINE_COLOR, bold=True, align="center"
                )
                text_overlays = {
                    "hook": hook_ov,
                    "heading": heading_ov,
                    "sub_p1": sub_p1,
                    "sub_p2": sub_p2
                }
            except Exception as e:
                print(f"[!] Indic text overlay note: {e}")

        def make_frame(t, s_meta=sc, d=dur, im=curr_img_obj, tov=text_overlays):
            return render_scene_frame(static_backdrop, t, d, w, h, s_meta, hook, im, language=language, text_overlays=tov)

        v_clip = mp.VideoClip(make_frame, duration=dur)

        # Layer Sound Effects
        audio_layers = [voice_clip]
        for sfx_name in sfx_list:
            sfx_file = os.path.join(SFX_DIR, f"{sfx_name}.mp3")
            if not os.path.exists(sfx_file):
                sfx_file = os.path.join(SFX_DIR, f"{sfx_name}.wav")
            if os.path.exists(sfx_file):
                try:
                    sfx_clip = mp.AudioFileClip(sfx_file).volumex(0.35)
                    audio_layers.append(sfx_clip)
                except Exception:
                    pass

        v_clip.audio = mp.CompositeAudioClip(audio_layers)
        clips.append(v_clip)

    final_video = mp.concatenate_videoclips(clips, method="compose")

    # Layer Sneaky / Dramatic BGM at 13% volume
    bgm_path = os.path.join(SFX_DIR, "sneaky_snitch.mp3")
    if os.path.exists(bgm_path):
        try:
            bgm = mp.AudioFileClip(bgm_path).volumex(0.13)
            if bgm.duration < final_video.duration:
                bgm = mp.afx.audio_loop(bgm, duration=final_video.duration)
            else:
                bgm = bgm.subclip(0, final_video.duration)
            final_video.audio = mp.CompositeAudioClip([final_video.audio, bgm])
        except Exception:
            pass

    out_name = base_filename if base_filename else f"neomorph_{int(os.path.getmtime(TEMP_DIR))}"
    out_path = os.path.join(OUTPUT_DIR, f"{out_name}.mp4")

    print(f"[*] Rendering 3D Neomorphic Short to: {out_path}")
    final_video.write_videofile(
        out_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        preset="ultrafast",
        ffmpeg_params=["-pix_fmt", "yuv420p"]
    )

    try:
        final_video.close()
        for c in clips:
            c.close()
    except Exception:
        pass

    # Verify file is completely written and valid on disk
    if os.path.exists(out_path) and os.path.getsize(out_path) > 1000000:
        chk = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", out_path, "-f", "null", "-"],
            capture_output=True,
            timeout=15
        )
        if chk.returncode == 0:
            print("\n" + "=" * 75)
            print(f"[SUCCESS] 3D NEOMORPHISM {lang_name} SHORT 100% VERIFIED: {out_path}")
            print("=" * 75)
            return out_path, title, desc, tags

    print(f"[!] Warning: Video file {out_path} validation check failed or file incomplete.")
    return out_path, title, desc, tags


if __name__ == "__main__":
    t = "Why Do We Get Brain Freeze From Ice Cream?"
    produce_curiosity_short(t, "test_neomorph_render", language="hi")
