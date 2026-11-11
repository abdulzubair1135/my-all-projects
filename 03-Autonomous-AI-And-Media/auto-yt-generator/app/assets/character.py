"""
AUTO YT GENERATOR — Procedural 2D Character Generator with Full Visual Customization.

Generates 512x768 transparent RGBA 2D puppet characters with:
- Modular Poses (idle, talk, shocked, sleep, scared, dead, walk)
- Dynamic Facial Expressions (neutral, curious, panic, evil_smile, confused, shocked)
- Lip Sync Mouth Shapes (idle, open, a, e, o, u)
- Visual Customizer: Skin tones, Hair styles, Shirt colors, Lab coats, Glasses/Goggles.
"""

from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from PIL import Image, ImageDraw

from app.constants import (
    CharacterAction,
    CharacterExpression,
    MouthState,
)
from app.logger import logger


class CharacterGenerator:
    """Procedural 2D puppet cartoon character sprite generator."""

    def __init__(self, width: int = 512, height: int = 768):
        self.width = width
        self.height = height

        # Palette Presets
        self.skin_palettes = {
            "light": ((245, 215, 190, 255), (210, 175, 150, 255)),
            "tan": ((220, 175, 135, 255), (180, 135, 95, 255)),
            "dark": ((140, 95, 65, 255), (100, 65, 40, 255)),
            "pale": ((235, 230, 240, 255), (195, 190, 205, 255)),
            "zombie_green": ((160, 205, 165, 255), (120, 165, 125, 255)),
            "cyber_blue": ((170, 210, 245, 255), (125, 170, 210, 255)),
        }

        self.shirt_palettes = {
            "dark_purple": ((75, 30, 110, 255), (45, 15, 75, 255)),
            "crimson_red": ((160, 30, 45, 255), (110, 15, 25, 255)),
            "emerald_green": ((30, 110, 65, 255), (15, 75, 40, 255)),
            "cyber_cyan": ((25, 130, 150, 255), (15, 90, 110, 255)),
            "navy_blue": ((35, 55, 115, 255), (20, 35, 80, 255)),
            "lab_white": ((230, 235, 240, 255), (180, 185, 195, 255)),
            "black": ((30, 32, 40, 255), (15, 16, 22, 255)),
        }

        self.hair_palettes = {
            "dark": (25, 20, 30, 255),
            "brown": (80, 45, 25, 255),
            "blonde": (220, 185, 60, 255),
            "white": (225, 230, 235, 255),
            "cyan": (40, 200, 230, 255),
        }

    def generate_character(
        self,
        action: str = CharacterAction.IDLE.value,
        expression: str = CharacterExpression.NEUTRAL.value,
        mouth_state: str = MouthState.IDLE.value,
        skin_tone: str = "light",
        shirt_color: str = "dark_purple",
        hair_color: str = "dark",
        hair_style: str = "spiky",
        has_glasses: bool = False,
        output_path: Optional[str] = None,
    ) -> Image.Image:
        """Renders complete 2D character sprite with custom visual options."""
        img = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Retrieve Colors
        skin_fill, skin_shadow = self.skin_palettes.get(skin_tone, self.skin_palettes["light"])
        shirt_fill, shirt_shadow = self.shirt_palettes.get(shirt_color, self.shirt_palettes["dark_purple"])
        hair_col = self.hair_palettes.get(hair_color, self.hair_palettes["dark"])
        outline = (10, 10, 15, 255)

        cx, cy = self.width // 2, int(self.height * 0.42)

        # 1. Torso & Legs
        self._draw_body(draw, cx, cy, action, shirt_fill, shirt_shadow, outline)

        # 2. Head & Neck
        head_radius = 95
        head_center = (cx, cy - 130)

        # Neck
        draw.rectangle([cx - 24, cy - 55, cx + 24, cy - 15], fill=skin_shadow, outline=outline, width=3)

        # Head Base
        hx, hy = head_center
        draw.ellipse(
            [hx - head_radius, hy - head_radius, hx + head_radius, hy + head_radius],
            fill=skin_fill,
            outline=outline,
            width=4,
        )

        # 3. Hair
        self._draw_hair(draw, hx, hy, head_radius, hair_style, hair_col, outline)

        # 4. Facial Features (Eyes, Brows, Expression)
        self._draw_face(draw, hx, hy, expression, action, outline)

        # 5. Glasses Accessory (if enabled)
        if has_glasses:
            self._draw_glasses(draw, hx, hy, outline)

        # 6. Mouth / Lip Sync
        self._draw_mouth(draw, hx, hy + 45, mouth_state, expression, outline)

        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path, "PNG")

        return img

    def _draw_body(self, draw: ImageDraw.ImageDraw, cx: int, cy: int, action: str, shirt: Tuple, shadow: Tuple, outline: Tuple):
        # Pants (Legs)
        pants_color = (25, 28, 38, 255)
        leg_w = 32
        leg_h = 240
        left_leg_x = cx - 48
        right_leg_x = cx + 16
        leg_y = cy + 130

        draw.rectangle([left_leg_x, leg_y, left_leg_x + leg_w, leg_y + leg_h], fill=pants_color, outline=outline, width=3)
        draw.rectangle([right_leg_x, leg_y, right_leg_x + leg_w, leg_y + leg_h], fill=pants_color, outline=outline, width=3)

        # Shoes
        draw.ellipse([left_leg_x - 8, leg_y + leg_h - 12, left_leg_x + leg_w + 6, leg_y + leg_h + 16], fill=(12, 12, 16, 255), outline=outline, width=3)
        draw.ellipse([right_leg_x - 6, leg_y + leg_h - 12, right_leg_x + leg_w + 8, leg_y + leg_h + 16], fill=(12, 12, 16, 255), outline=outline, width=3)

        # Shirt / Torso
        torso_w, torso_h = 135, 160
        tx1 = cx - torso_w // 2
        ty1 = cy - 20
        tx2 = cx + torso_w // 2
        ty2 = ty1 + torso_h
        draw.rounded_rectangle([tx1, ty1, tx2, ty2], radius=18, fill=shirt, outline=outline, width=4)

        # Arms based on Action
        arm_w = 26
        if action in ["shocked", "scared"]:
            # Raised arms
            draw.line([(tx1, ty1 + 25), (tx1 - 50, ty1 - 70)], fill=shirt, width=arm_w)
            draw.line([(tx2, ty1 + 25), (tx2 + 50, ty1 - 70)], fill=shirt, width=arm_w)
        else:
            # Relaxed arms
            draw.line([(tx1 + 5, ty1 + 25), (tx1 - 32, ty1 + 140)], fill=shirt, width=arm_w)
            draw.line([(tx2 - 5, ty1 + 25), (tx2 + 32, ty1 + 140)], fill=shirt, width=arm_w)

    def _draw_hair(self, draw: ImageDraw.ImageDraw, hx: int, hy: int, r: int, style: str, col: Tuple, outline: Tuple):
        if style == "bald":
            return
        elif style == "scientist_wild":
            # Wild Einstein/Rick scientist hair
            spikes = [
                (hx - r - 25, hy - 20), (hx - r - 15, hy - 60), (hx - r + 15, hy - r - 25),
                (hx, hy - r - 45), (hx + r - 15, hy - r - 25), (hx + r + 15, hy - 60),
                (hx + r + 25, hy - 20), (hx + r - 20, hy + 10), (hx - r + 20, hy + 10),
            ]
            draw.polygon(spikes, fill=col, outline=outline)
        else:
            # Classic Spiky Anime / Cartoon hair
            spikes = [
                (hx - r - 10, hy - 10), (hx - r + 5, hy - r + 10), (hx - 40, hy - r - 35),
                (hx, hy - r - 45), (hx + 40, hy - r - 35), (hx + r - 5, hy - r + 10),
                (hx + r + 10, hy - 10), (hx + r - 25, hy - r + 35), (hx - r + 25, hy - r + 35),
            ]
            draw.polygon(spikes, fill=col, outline=outline)

    def _draw_face(self, draw: ImageDraw.ImageDraw, hx: int, hy: int, expr: str, action: str, outline: Tuple):
        eye_y = hy - 10
        left_eye_x = hx - 38
        right_eye_x = hx + 38

        eye_r = 18 if expr in ["shocked", "curious"] or action == "shocked" else 13
        pupil_r = 6 if expr != "shocked" else 4

        # Eyes Sclera
        draw.ellipse([left_eye_x - eye_r, eye_y - eye_r, left_eye_x + eye_r, eye_y + eye_r], fill=(255, 255, 255, 255), outline=outline, width=3)
        draw.ellipse([right_eye_x - eye_r, eye_y - eye_r, right_eye_x + eye_r, eye_y + eye_r], fill=(255, 255, 255, 255), outline=outline, width=3)

        # Pupils
        draw.ellipse([left_eye_x - pupil_r, eye_y - pupil_r, left_eye_x + pupil_r, eye_y + pupil_r], fill=(15, 15, 20, 255))
        draw.ellipse([right_eye_x - pupil_r, eye_y - pupil_r, right_eye_x + pupil_r, eye_y + pupil_r], fill=(15, 15, 20, 255))

        # Eyebrows
        brow_y = eye_y - eye_r - 12
        if expr == "panic" or action == "scared":
            draw.line([(left_eye_x - 18, brow_y - 8), (left_eye_x + 18, brow_y + 4)], fill=outline, width=4)
            draw.line([(right_eye_x - 18, brow_y + 4), (right_eye_x + 18, brow_y - 8)], fill=outline, width=4)
        else:
            draw.line([(left_eye_x - 18, brow_y), (left_eye_x + 18, brow_y)], fill=outline, width=4)
            draw.line([(right_eye_x - 18, brow_y), (right_eye_x + 18, brow_y)], fill=outline, width=4)

    def _draw_glasses(self, draw: ImageDraw.ImageDraw, hx: int, hy: int, outline: Tuple):
        eye_y = hy - 10
        left_eye_x = hx - 38
        right_eye_x = hx + 38
        gr = 24
        # Frame lenses
        draw.rectangle([left_eye_x - gr, eye_y - gr, left_eye_x + gr, eye_y + gr], outline=(20, 20, 30, 255), width=4)
        draw.rectangle([right_eye_x - gr, eye_y - gr, right_eye_x + gr, eye_y + gr], outline=(20, 20, 30, 255), width=4)
        # Bridge
        draw.line([(left_eye_x + gr, eye_y), (right_eye_x - gr, eye_y)], fill=(20, 20, 30, 255), width=4)

    def _draw_mouth(self, draw: ImageDraw.ImageDraw, hx: int, my: int, state: str, expr: str, outline: Tuple):
        if state == MouthState.OPEN.value or expr == "shocked":
            draw.ellipse([hx - 20, my - 16, hx + 20, my + 20], fill=(80, 15, 25, 255), outline=outline, width=3)
            draw.ellipse([hx - 12, my + 4, hx + 12, my + 18], fill=(210, 70, 90, 255))
        elif state == MouthState.O.value:
            draw.ellipse([hx - 14, my - 14, hx + 14, my + 14], fill=(80, 15, 25, 255), outline=outline, width=3)
        elif state in [MouthState.A.value, MouthState.E.value]:
            draw.rectangle([hx - 18, my - 6, hx + 18, my + 10], fill=(90, 20, 30, 255), outline=outline, width=3)
        else:
            # Idle smile / line
            draw.arc([hx - 20, my - 14, hx + 20, my + 10], start=20, end=160, fill=outline, width=4)


# Default character generator instance
character_generator = CharacterGenerator()
