"""
Background Renderer for StickForge AI.
Generates styled 2D procedural environments (classroom, street, room, forest, plain).
"""

from __future__ import annotations
from typing import Tuple
from PIL import Image, ImageDraw


def hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    hex_code = hex_code.lstrip("#")
    if len(hex_code) == 6:
        return tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore
    return (255, 255, 255)


class BackgroundRenderer:
    """Renders background layers for scenes."""

    def __init__(self, width: int = 1080, height: int = 1920):
        self.w = width
        self.h = height

    def render(self, bg_name: str) -> Image.Image:
        """Render a background by name onto an RGB PIL Image."""
        bg = bg_name.lower().strip()
        img = Image.new("RGB", (self.w, self.h), (18, 19, 24))
        draw = ImageDraw.Draw(img)

        ground_y = int(self.h * 0.72)

        if bg == "classroom":
            # Wall & Floor
            draw.rectangle([(0, 0), (self.w, ground_y)], fill=(30, 32, 40))
            draw.rectangle([(0, ground_y), (self.w, self.h)], fill=(45, 48, 58))
            draw.line([(0, ground_y), (self.w, ground_y)], fill=(70, 75, 90), width=4)

            # Blackboard
            board_w, board_h = int(self.w * 0.75), int(self.h * 0.28)
            bx1 = int((self.w - board_w) / 2)
            by1 = int(self.h * 0.18)
            draw.rectangle([(bx1, by1), (bx1 + board_w, by1 + board_h)], fill=(20, 45, 30), outline=(139, 90, 43), width=6)
            # Chalk text / equations
            draw.text((bx1 + 30, by1 + 30), "MATH: E = mc²", fill=(220, 230, 220))
            draw.text((bx1 + 30, by1 + 70), "Chapter 4: Stickman Physics", fill=(180, 200, 180))

        elif bg == "street":
            # Sky & Road
            draw.rectangle([(0, 0), (self.w, ground_y)], fill=(15, 20, 35))
            draw.rectangle([(0, ground_y), (self.w, self.h)], fill=(35, 36, 40))
            draw.line([(0, ground_y), (self.w, ground_y)], fill=(80, 85, 95), width=4)

            # Road dashed stripe
            stripe_y = int(ground_y + (self.h - ground_y) * 0.5)
            for x in range(20, self.w, 80):
                draw.line([(x, stripe_y), (x + 45, stripe_y)], fill=(230, 200, 50), width=6)

            # Distant city buildings silhouette
            b_coords = [
                (40, 150), (160, 220), (280, 180), (420, 250), (560, 160),
                (700, 230), (840, 190), (960, 210)
            ]
            for bx, bh in b_coords:
                draw.rectangle([(bx, ground_y - bh), (bx + 100, ground_y)], fill=(25, 30, 45))
                # Window dots
                for wy in range(ground_y - bh + 20, ground_y - 20, 30):
                    draw.rectangle([(bx + 20, wy), (bx + 35, wy + 15)], fill=(255, 240, 150))
                    draw.rectangle([(bx + 60, wy), (bx + 75, wy + 15)], fill=(255, 240, 150))

        elif bg == "forest":
            # Sky & Grass
            draw.rectangle([(0, 0), (self.w, ground_y)], fill=(25, 45, 60))
            draw.rectangle([(0, ground_y), (self.w, self.h)], fill=(20, 55, 25))
            draw.line([(0, ground_y), (self.w, ground_y)], fill=(40, 90, 45), width=5)

            # Trees
            tree_xs = [80, 260, 780, 950]
            for tx in tree_xs:
                draw.rectangle([(tx - 15, ground_y - 280), (tx + 15, ground_y)], fill=(75, 45, 25))
                draw.polygon(
                    [(tx - 90, ground_y - 220), (tx + 90, ground_y - 220), (tx, ground_y - 420)],
                    fill=(30, 95, 40)
                )
                draw.polygon(
                    [(tx - 70, ground_y - 320), (tx + 70, ground_y - 320), (tx, ground_y - 480)],
                    fill=(38, 120, 50)
                )

        elif bg == "room":
            # Living Room
            draw.rectangle([(0, 0), (self.w, ground_y)], fill=(40, 35, 45))
            draw.rectangle([(0, ground_y), (self.w, self.h)], fill=(60, 45, 35))
            draw.line([(0, ground_y), (self.w, ground_y)], fill=(90, 70, 55), width=4)

            # Window with moon/stars
            wx1, wy1 = int(self.w * 0.65), int(self.h * 0.2)
            draw.rectangle([(wx1, wy1), (wx1 + 240, wy1 + 280)], fill=(20, 30, 60), outline=(200, 180, 160), width=6)
            draw.ellipse([(wx1 + 140, wy1 + 40), (wx1 + 200, wy1 + 100)], fill=(250, 250, 210))

        elif bg == "plain_white":
            draw.rectangle([(0, 0), (self.w, self.h)], fill=(245, 245, 248))
            draw.line([(0, ground_y), (self.w, ground_y)], fill=(200, 200, 210), width=3)

        else:  # plain_dark default
            draw.rectangle([(0, 0), (self.w, self.h)], fill=(18, 19, 24))
            draw.line([(0, ground_y), (self.w, ground_y)], fill=(45, 48, 58), width=3)

        return img
