import os, sys, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 720, 1280
BG_COLOR = (235, 238, 245)      # Light neomorphic base
SHADOW_DARK = (195, 202, 216)   # Bottom-right soft shadow
SHADOW_LIGHT = (255, 255, 255)  # Top-left specular highlight
LINE_COLOR = (24, 28, 36)       # Crisp ink black outline
ACCENT_BLUE = (66, 133, 244)
ACCENT_YELLOW = (255, 187, 0)
ACCENT_RED = (234, 67, 53)

def draw_neomorphic_card(base_img, x, y, w, h, radius=24, depth=10, inset=False):
    """
    Renders a true 3D Neomorphic extruded or inset rounded card.
    Dual-shadow algorithm: Top-left light glow + Bottom-right soft diffuse shadow.
    """
    # Create mask for card
    mask = Image.new("L", (w, h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, w, h], radius=radius, fill=255)

    # 1. Dark drop shadow (bottom-right)
    dark_shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds_draw = ImageDraw.Draw(dark_shadow)
    ds_draw.rounded_rectangle([x + depth, y + depth, x + w + depth, y + h + depth], radius=radius, fill=SHADOW_DARK)
    dark_shadow = dark_shadow.filter(ImageFilter.GaussianBlur(depth * 1.2))

    # 2. Light highlight (top-left)
    light_shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ls_draw = ImageDraw.Draw(light_shadow)
    ls_draw.rounded_rectangle([x - depth, y - depth, x + w - depth, y + h - depth], radius=radius, fill=SHADOW_LIGHT)
    light_shadow = light_shadow.filter(ImageFilter.GaussianBlur(depth * 1.2))

    # Composite shadows onto base
    base_img.paste(light_shadow, (0, 0), light_shadow)
    base_img.paste(dark_shadow, (0, 0), dark_shadow)

    # 3. Card Face (Light gradient)
    card_face = Image.new("RGBA", (w, h), BG_COLOR)
    cf_draw = ImageDraw.Draw(card_face)
    cf_draw.rounded_rectangle([0, 0, w, h], radius=radius, fill=(240, 243, 250), outline=LINE_COLOR, width=3)
    base_img.paste(card_face, (x, y), mask)

img = Image.new("RGBA", (W, H), BG_COLOR)
draw_neomorphic_card(img, 50, 60, 620, 120, radius=28, depth=8)
draw_neomorphic_card(img, 50, 220, 620, 420, radius=28, depth=10)
draw_neomorphic_card(img, 50, 1060, 620, 160, radius=28, depth=8)

img.convert("RGB").save("scratch/test_neomorphic_base.png")
print("Saved scratch/test_neomorphic_base.png successfully!")
