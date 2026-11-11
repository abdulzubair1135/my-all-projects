"""
AUTO YT GENERATOR — 2D Modular Puppet Rigging Engine.

Renders high-quality articulated character puppets with:
- Multi-component hierarchy (Torso, Head, Eyes, Brows, Viseme Mouth, Limbs)
- Autonomous Natural Blinking cycle (every 3-4 seconds with 150ms blink duration)
- Pupil Gaze Tracking (Direct, Left, Right, Up, Down)
- 14 Phonetic Viseme Mouth Shapes
- Expressive Arm Gestures (Pointing, Thinking, Explaining, Panic, Waving, Freezing)
- Subtle Breathing and Secondary Physics
"""

import math
from typing import Tuple, Optional, Dict
from PIL import Image, ImageDraw

from app.models.scene import ActingGesture, EyeGaze, FacialExpression


class CharacterRig:
    """2D Modular puppet character rig for natural acting and viseme animation."""

    def __init__(self, width: int = 512, height: int = 768):
        self.width = width
        self.height = height

    def render_puppet_frame(
        self,
        time_sec: float,
        gesture: str = "talk_explain",
        expression: str = "neutral",
        gaze: str = "direct",
        viseme: str = "REST",
        skin_color: Tuple[int, int, int, int] = (245, 215, 190, 255),
        shirt_color: Tuple[int, int, int, int] = (75, 30, 110, 255),
        hair_color: Tuple[int, int, int, int] = (25, 20, 30, 255),
        has_glasses: bool = False,
    ) -> Image.Image:
        """Renders an articulated puppet frame at timestamp `time_sec`."""
        canvas = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)
        outline = (10, 10, 15, 255)

        # 1. Subtle Secondary Motion & Idle Breathing
        breathe = math.sin(time_sec * 2.5) * 3.5
        head_tilt = math.sin(time_sec * 1.8) * 1.5 if gesture == "think_curious" else 0.0

        cx = self.width // 2
        cy = int(self.height * 0.44) + int(breathe)

        # 2. Draw Legs & Feet
        self._draw_legs(draw, cx, cy, outline)

        # 3. Draw Torso & Arms
        self._draw_torso_and_arms(draw, cx, cy, gesture, shirt_color, outline, time_sec)

        # 4. Draw Neck & Head
        hx, hy = cx, cy - 135
        head_radius = 95
        # Neck
        draw.rectangle([cx - 22, cy - 55, cx + 22, cy - 15], fill=(skin_color[0] - 25, skin_color[1] - 25, skin_color[2] - 25, 255), outline=outline, width=3)
        # Head Base
        draw.ellipse([hx - head_radius, hy - head_radius, hx + head_radius, hy + head_radius], fill=skin_color, outline=outline, width=4)

        # 5. Draw Hair
        self._draw_hair(draw, hx, hy, head_radius, hair_color, outline)

        # 6. Autonomous Blinking & Eyes
        is_blinking = (time_sec % 3.8) < 0.16 or gaze == "closed"
        self._draw_eyes(draw, hx, hy, expression, gaze, is_blinking, outline)

        # 7. Eyebrows
        self._draw_brows(draw, hx, hy, expression, outline)

        # 8. Glasses
        if has_glasses:
            self._draw_glasses(draw, hx, hy, outline)

        # 9. 14-Viseme Mouth
        self._draw_viseme_mouth(draw, hx, hy + 46, viseme, expression, outline)

        return canvas

    def _draw_legs(self, draw: ImageDraw.ImageDraw, cx: int, cy: int, outline: Tuple):
        pants_color = (25, 28, 38, 255)
        leg_w, leg_h = 32, 235
        l_x = cx - 48
        r_x = cx + 16
        l_y = cy + 130
        draw.rectangle([l_x, l_y, l_x + leg_w, l_y + leg_h], fill=pants_color, outline=outline, width=3)
        draw.rectangle([r_x, l_y, r_x + leg_w, l_y + leg_h], fill=pants_color, outline=outline, width=3)
        # Shoes
        draw.ellipse([l_x - 8, l_y + leg_h - 12, l_x + leg_w + 6, l_y + leg_h + 16], fill=(12, 12, 16, 255), outline=outline, width=3)
        draw.ellipse([r_x - 6, l_y + leg_h - 12, r_x + leg_w + 8, l_y + leg_h + 16], fill=(12, 12, 16, 255), outline=outline, width=3)

    def _draw_torso_and_arms(self, draw: ImageDraw.ImageDraw, cx: int, cy: int, gesture: str, shirt: Tuple, outline: Tuple, t: float):
        torso_w, torso_h = 138, 165
        tx1, ty1 = cx - torso_w // 2, cy - 20
        tx2, ty2 = cx + torso_w // 2, ty1 + torso_h

        draw.rounded_rectangle([tx1, ty1, tx2, ty2], radius=20, fill=shirt, outline=outline, width=4)
        arm_w = 26

        # Gestural Arm IK Positioning
        if gesture in ["point_right", "point_left"]:
            if gesture == "point_right":
                # Right arm extended pointing right
                draw.line([(tx2, ty1 + 25), (tx2 + 85, ty1 + 10)], fill=shirt, width=arm_w)
                draw.ellipse([tx2 + 75, ty1 - 5, tx2 + 100, ty1 + 25], fill=shirt, outline=outline, width=2)
                # Left arm relaxed
                draw.line([(tx1 + 5, ty1 + 25), (tx1 - 25, ty1 + 130)], fill=shirt, width=arm_w)
            else:
                # Left arm pointing left
                draw.line([(tx1, ty1 + 25), (tx1 - 85, ty1 + 10)], fill=shirt, width=arm_w)
                draw.ellipse([tx1 - 100, ty1 - 5, tx1 - 75, ty1 + 25], fill=shirt, outline=outline, width=2)
                draw.line([(tx2 - 5, ty1 + 25), (tx2 + 25, ty1 + 130)], fill=shirt, width=arm_w)
        elif gesture == "think_curious":
            # Hand on chin
            draw.line([(tx1 + 5, ty1 + 25), (tx1 - 25, ty1 + 130)], fill=shirt, width=arm_w)
            draw.line([(tx2, ty1 + 25), (cx + 35, cy - 80)], fill=shirt, width=arm_w)
        elif gesture == "panic_hands" or gesture == "shock_freeze":
            # Both hands up in shock / panic
            shiver = math.sin(t * 30.0) * 4.0 if gesture == "panic_hands" else 0.0
            draw.line([(tx1, ty1 + 25), (tx1 - 55 + shiver, ty1 - 65)], fill=shirt, width=arm_w)
            draw.line([(tx2, ty1 + 25), (tx2 + 55 - shiver, ty1 - 65)], fill=shirt, width=arm_w)
        elif gesture == "excited_wave":
            wave = math.sin(t * 10.0) * 25.0
            draw.line([(tx1 + 5, ty1 + 25), (tx1 - 25, ty1 + 130)], fill=shirt, width=arm_w)
            draw.line([(tx2, ty1 + 25), (tx2 + 65, ty1 - 60 + wave)], fill=shirt, width=arm_w)
        else:
            # Natural talking explain gesture with slight hand sway
            hand_sway = math.sin(t * 4.0) * 12.0
            draw.line([(tx1 + 5, ty1 + 25), (tx1 - 38, ty1 + 95 + hand_sway)], fill=shirt, width=arm_w)
            draw.line([(tx2 - 5, ty1 + 25), (tx2 + 38, ty1 + 95 - hand_sway)], fill=shirt, width=arm_w)

    def _draw_hair(self, draw: ImageDraw.ImageDraw, hx: int, hy: int, r: int, col: Tuple, outline: Tuple):
        spikes = [
            (hx - r - 15, hy - 10), (hx - r + 5, hy - r + 10), (hx - 45, hy - r - 35),
            (hx, hy - r - 50), (hx + 45, hy - r - 35), (hx + r - 5, hy - r + 10),
            (hx + r + 15, hy - 10), (hx + r - 25, hy - r + 35), (hx - r + 25, hy - r + 35),
        ]
        draw.polygon(spikes, fill=col, outline=outline)

    def _draw_eyes(self, draw: ImageDraw.ImageDraw, hx: int, hy: int, expr: str, gaze: str, is_blinking: bool, outline: Tuple):
        eye_y = hy - 10
        l_x = hx - 38
        r_x = hx + 38

        if is_blinking:
            # Draw closed curved eye slit
            draw.arc([l_x - 16, eye_y - 6, l_x + 16, eye_y + 8], start=10, end=170, fill=outline, width=4)
            draw.arc([r_x - 16, eye_y - 6, r_x + 16, eye_y + 8], start=10, end=170, fill=outline, width=4)
            return

        eye_r = 18 if expr in ["shocked", "scared"] else 14
        pupil_r = 6 if expr != "shocked" else 4

        # Gaze Offset
        dx, dy = 0, 0
        if gaze == "left":
            dx = -5
        elif gaze == "right":
            dx = 5
        elif gaze == "up":
            dy = -4
        elif gaze == "down":
            dy = 4

        # Eye Sclera
        draw.ellipse([l_x - eye_r, eye_y - eye_r, l_x + eye_r, eye_y + eye_r], fill=(255, 255, 255, 255), outline=outline, width=3)
        draw.ellipse([r_x - eye_r, eye_y - eye_r, r_x + eye_r, eye_y + eye_r], fill=(255, 255, 255, 255), outline=outline, width=3)

        # Pupils
        draw.ellipse([l_x + dx - pupil_r, eye_y + dy - pupil_r, l_x + dx + pupil_r, eye_y + dy + pupil_r], fill=(15, 15, 20, 255))
        draw.ellipse([r_x + dx - pupil_r, eye_y + dy - pupil_r, r_x + dx + pupil_r, eye_y + dy + pupil_r], fill=(15, 15, 20, 255))

        # Eye specular highlights
        draw.ellipse([l_x + dx - 2, eye_y + dy - 4, l_x + dx + 2, eye_y + dy], fill=(255, 255, 255, 255))
        draw.ellipse([r_x + dx - 2, eye_y + dy - 4, r_x + dx + 2, eye_y + dy], fill=(255, 255, 255, 255))

    def _draw_brows(self, draw: ImageDraw.ImageDraw, hx: int, hy: int, expr: str, outline: Tuple):
        eye_y = hy - 10
        l_x = hx - 38
        r_x = hx + 38
        b_y = eye_y - 24

        if expr in ["scared", "panic"]:
            # Slanted up in worry
            draw.line([(l_x - 18, b_y - 8), (l_x + 18, b_y + 4)], fill=outline, width=4)
            draw.line([(r_x - 18, b_y + 4), (r_x + 18, b_y - 8)], fill=outline, width=4)
        elif expr in ["confused", "curious"]:
            # One raised, one neutral
            draw.line([(l_x - 18, b_y - 12), (l_x + 18, b_y - 6)], fill=outline, width=4)
            draw.line([(r_x - 18, b_y), (r_x + 18, b_y)], fill=outline, width=4)
        elif expr == "angry":
            # Slanted down in anger
            draw.line([(l_x - 18, b_y + 6), (l_x + 18, b_y - 6)], fill=outline, width=4)
            draw.line([(r_x - 18, b_y - 6), (r_x + 18, b_y + 6)], fill=outline, width=4)
        else:
            # Calm horizontal
            draw.line([(l_x - 18, b_y), (l_x + 18, b_y)], fill=outline, width=4)
            draw.line([(r_x - 18, b_y), (r_x + 18, b_y)], fill=outline, width=4)

    def _draw_glasses(self, draw: ImageDraw.ImageDraw, hx: int, hy: int, outline: Tuple):
        eye_y = hy - 10
        l_x, r_x = hx - 38, hx + 38
        gr = 24
        draw.rectangle([l_x - gr, eye_y - gr, l_x + gr, eye_y + gr], outline=(20, 20, 30, 255), width=4)
        draw.rectangle([r_x - gr, eye_y - gr, r_x + gr, eye_y + gr], outline=(20, 20, 30, 255), width=4)
        draw.line([(l_x + gr, eye_y), (r_x - gr, eye_y)], fill=(20, 20, 30, 255), width=4)

    def _draw_viseme_mouth(self, draw: ImageDraw.ImageDraw, hx: int, my: int, viseme: str, expr: str, outline: Tuple):
        """Renders exact 14-viseme phoneme shapes for realistic lip sync."""
        vis = viseme.upper().strip()

        if vis in ["A", "E", "OPEN"]:
            draw.ellipse([hx - 20, my - 16, hx + 20, my + 20], fill=(80, 15, 25, 255), outline=outline, width=3)
            # Tongue & Teeth
            draw.rectangle([hx - 14, my - 14, hx + 14, my - 6], fill=(255, 255, 255, 255))
            draw.ellipse([hx - 12, my + 4, hx + 12, my + 18], fill=(210, 70, 90, 255))
        elif vis in ["O", "U", "W"]:
            # Round pucker
            draw.ellipse([hx - 13, my - 13, hx + 13, my + 13], fill=(80, 15, 25, 255), outline=outline, width=3)
        elif vis in ["MBP", "REST"]:
            # Closed neutral lips
            draw.arc([hx - 18, my - 12, hx + 18, my + 10], start=20, end=160, fill=outline, width=4)
        elif vis in ["FV"]:
            # Top teeth biting lower lip
            draw.rectangle([hx - 16, my - 4, hx + 16, my + 8], fill=(80, 15, 25, 255), outline=outline, width=2)
            draw.rectangle([hx - 12, my - 4, hx + 12, my + 1], fill=(255, 255, 255, 255))
        elif vis in ["SZ", "SHCH", "TH", "L", "NDT"]:
            # Wide teeth showing
            draw.rectangle([hx - 22, my - 6, hx + 22, my + 10], fill=(80, 15, 25, 255), outline=outline, width=3)
            draw.rectangle([hx - 18, my - 4, hx + 18, my + 4], fill=(255, 255, 255, 255))
        else:
            # Default talking aperture
            draw.rectangle([hx - 18, my - 8, hx + 18, my + 10], fill=(80, 15, 25, 255), outline=outline, width=3)


# Default character rig instance
character_rig = CharacterRig()
