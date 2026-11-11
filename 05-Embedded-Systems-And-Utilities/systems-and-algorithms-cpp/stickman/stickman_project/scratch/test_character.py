import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 720, 1280
BG_COLOR = (236, 240, 248)
SHADOW_DARK = (190, 198, 214)
SHADOW_LIGHT = (255, 255, 255)
LINE_COLOR = (24, 28, 36)

def draw_neomorphic_pill(draw_img, x, y, w, h, radius=20, depth=6):
    # Shadow
    s_dark = Image.new("RGBA", (W, H), (0,0,0,0))
    ImageDraw.Draw(s_dark).rounded_rectangle([x + depth, y + depth, x + w + depth, y + h + depth], radius=radius, fill=SHADOW_DARK)
    s_dark = s_dark.filter(ImageFilter.GaussianBlur(depth))
    
    s_light = Image.new("RGBA", (W, H), (0,0,0,0))
    ImageDraw.Draw(s_light).rounded_rectangle([x - depth, y - depth, x + w - depth, y + h - depth], radius=radius, fill=SHADOW_LIGHT)
    s_light = s_light.filter(ImageFilter.GaussianBlur(depth))
    
    draw_img.paste(s_light, (0, 0), s_light)
    draw_img.paste(s_dark, (0, 0), s_dark)
    
    # Body
    body = Image.new("RGBA", (w, h), (0,0,0,0))
    b_draw = ImageDraw.Draw(body)
    b_draw.rounded_rectangle([0, 0, w, h], radius=radius, fill=(245, 248, 254), outline=LINE_COLOR, width=3)
    draw_img.paste(body, (x, y), body)

def draw_3d_character(draw_img, cx, cy, t, pose="explaining"):
    """
    Renders a 3D Neomorphic Capsule Stickman with soft ambient drop shadows,
    3D capsule limbs, smooth rounded joints, expressive head, and crisp black outlines.
    """
    bob = math.sin(t * 8) * 6
    
    # 1. Floor contact shadow (Soft oval)
    floor_y = 1040
    sh_w = int(120 + math.sin(t * 8) * 10)
    shadow_layer = Image.new("RGBA", (W, H), (0,0,0,0))
    s_draw = ImageDraw.Draw(shadow_layer)
    s_draw.ellipse([cx - sh_w//2, floor_y - 12, cx + sh_w//2, floor_y + 12], fill=(185, 195, 212, 180))
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(6))
    draw_img.paste(shadow_layer, (0, 0), shadow_layer)

    # 2. Torso (3D Neomorphic Pill Capsule)
    torso_top = cy - 40 + bob
    torso_bot = cy + 100 + bob
    torso_w = 42
    
    # Torso drop shadow
    t_shadow = Image.new("RGBA", (W, H), (0,0,0,0))
    ts_draw = ImageDraw.Draw(t_shadow)
    ts_draw.rounded_rectangle([cx - torso_w//2 + 5, torso_top + 5, cx + torso_w//2 + 5, torso_bot + 5], radius=torso_w//2, fill=(190, 198, 214, 160))
    t_shadow = t_shadow.filter(ImageFilter.GaussianBlur(5))
    draw_img.paste(t_shadow, (0, 0), t_shadow)

    # 3. Legs (3D Capsule Bones)
    hip_l = (cx - 14, torso_bot - 15)
    hip_r = (cx + 14, torso_bot - 15)
    knee_l = (cx - 28, torso_bot + 65)
    knee_r = (cx + 28, torso_bot + 65)
    foot_l = (cx - 36, floor_y)
    foot_r = (cx + 36, floor_y)

    draw = ImageDraw.Draw(draw_img)
    # Leg outlines
    for p1, p2 in [(hip_l, knee_l), (knee_l, foot_l), (hip_r, knee_r), (knee_r, foot_r)]:
        draw.line([p1, p2], fill=LINE_COLOR, width=12)
    # Leg core (white 3D highlights)
    for p1, p2 in [(hip_l, knee_l), (knee_l, foot_l), (hip_r, knee_r), (knee_r, foot_r)]:
        draw.line([p1, p2], fill=(255, 255, 255), width=6)
    # Knee joints (spheres)
    draw.ellipse([knee_l[0]-8, knee_l[1]-8, knee_l[0]+8, knee_l[1]+8], fill=(245, 248, 254), outline=LINE_COLOR, width=3)
    draw.ellipse([knee_r[0]-8, knee_r[1]-8, knee_r[0]+8, knee_r[1]+8], fill=(245, 248, 254), outline=LINE_COLOR, width=3)
    # Shoes (Neomorphic pills)
    draw.rounded_rectangle([foot_l[0]-16, foot_l[1]-10, foot_l[0]+12, foot_l[1]+6], radius=8, fill=(240, 244, 252), outline=LINE_COLOR, width=3)
    draw.rounded_rectangle([foot_r[0]-12, foot_r[1]-10, foot_r[0]+16, foot_r[1]+6], radius=8, fill=(240, 244, 252), outline=LINE_COLOR, width=3)

    # Torso Body (Pill with clean border)
    draw.rounded_rectangle([cx - torso_w//2, torso_top, cx + torso_w//2, torso_bot], radius=torso_w//2, fill=(248, 250, 255), outline=LINE_COLOR, width=4)
    # Tie / Badge / Lab coat detail
    draw.line([(cx, torso_top + 16), (cx, torso_top + 60)], fill=LINE_COLOR, width=3)
    draw.polygon([(cx, torso_top + 60), (cx - 7, torso_top + 50), (cx + 7, torso_top + 50)], fill=(66, 133, 244))

    # 4. Arms & Hands (Pose based)
    sh_l = (cx - torso_w//2 + 4, torso_top + 18)
    sh_r = (cx + torso_w//2 - 4, torso_top + 18)

    if pose == "scratching":
        el_l = (cx - 48, torso_top - 10)
        h_l = (cx - 24, cy - 110 + bob)
        el_r = (cx + 36, torso_top + 45)
        h_r = (cx + 20, torso_top + 80)
    elif pose == "pointing":
        el_l = (cx - 36, torso_top + 45)
        h_l = (cx - 20, torso_top + 80)
        el_r = (cx + 55, torso_top - 20)
        h_r = (cx + 105, torso_top - 65)
    else: # celebration
        el_l = (cx - 50, torso_top - 30)
        h_l = (cx - 65, torso_top - 80)
        el_r = (cx + 50, torso_top - 30)
        h_r = (cx + 65, torso_top - 80)

    for p1, p2 in [(sh_l, el_l), (el_l, h_l), (sh_r, el_r), (el_r, h_r)]:
        draw.line([p1, p2], fill=LINE_COLOR, width=11)
        draw.line([p1, p2], fill=(255, 255, 255), width=5)

    # Hand Spheres
    draw.ellipse([h_l[0]-9, h_l[1]-9, h_l[0]+9, h_l[1]+9], fill=(245, 248, 254), outline=LINE_COLOR, width=3)
    draw.ellipse([h_r[0]-9, h_r[1]-9, h_r[0]+9, h_r[1]+9], fill=(245, 248, 254), outline=LINE_COLOR, width=3)

    # 5. Head (3D Neomorphic Sphere)
    head_y = cy - 90 + bob
    head_r = 50
    # Head shadow
    h_shadow = Image.new("RGBA", (W, H), (0,0,0,0))
    hs_draw = ImageDraw.Draw(h_shadow)
    hs_draw.ellipse([cx - head_r + 6, head_y - head_r + 6, cx + head_r + 6, head_y + head_r + 6], fill=(190, 198, 214, 180))
    h_shadow = h_shadow.filter(ImageFilter.GaussianBlur(6))
    draw_img.paste(h_shadow, (0, 0), h_shadow)

    # Head Sphere with thick outline
    draw = ImageDraw.Draw(draw_img)
    draw.ellipse([cx - head_r, head_y - head_r, cx + head_r, head_y + head_r], fill=(250, 252, 255), outline=LINE_COLOR, width=4)

    # Glasses (Black acetate frames)
    gx1, gx2 = cx - 38, cx - 8
    gx3, gx4 = cx + 8, cx + 38
    gy1, gy2 = head_y - 12, head_y + 14
    draw.rounded_rectangle([gx1, gy1, gx2, gy2], radius=6, fill=(255, 255, 255), outline=LINE_COLOR, width=3)
    draw.rounded_rectangle([gx3, gy1, gx4, gy2], radius=6, fill=(255, 255, 255), outline=LINE_COLOR, width=3)
    draw.line([(gx2, head_y + 1), (gx3, head_y + 1)], fill=LINE_COLOR, width=4)
    # Glasses Glare
    draw.line([(gx1 + 6, gy2 - 4), (gx2 - 6, gy1 + 4)], fill=(180, 210, 255), width=2)
    draw.line([(gx3 + 6, gy2 - 4), (gx4 - 6, gy1 + 4)], fill=(180, 210, 255), width=2)

    # Eyes & Eyebrows
    draw.ellipse([cx - 26, head_y - 2, cx - 20, head_y + 4], fill=LINE_COLOR)
    draw.ellipse([cx + 20, head_y - 2, cx + 26, head_y + 4], fill=LINE_COLOR)
    draw.line([(cx - 36, head_y - 18), (cx - 12, head_y - 16)], fill=LINE_COLOR, width=3)
    draw.line([(cx + 12, head_y - 16), (cx + 36, head_y - 20)], fill=LINE_COLOR, width=3)

    # Talking Mouth
    mouth_open = int(abs(math.sin(t * 14)) * 6)
    draw.ellipse([cx - 9, head_y + 26, cx + 9, head_y + 26 + mouth_open], fill=LINE_COLOR)

img = Image.new("RGBA", (W, H), BG_COLOR)
draw_neomorphic_pill(img, 50, 60, 620, 110, radius=24, depth=7)
draw_neomorphic_pill(img, 50, 200, 620, 420, radius=26, depth=9)
draw_neomorphic_pill(img, 50, 1050, 620, 170, radius=24, depth=7)
draw_3d_character(img, 240, 840, 1.2, pose="pointing")

img.convert("RGB").save("scratch/test_3d_character.png")
print("Saved scratch/test_3d_character.png successfully!")
