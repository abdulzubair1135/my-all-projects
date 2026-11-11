"""
AUTO YT GENERATOR — Procedural 2D Background Generator.

Creates high-contrast, moody vector/raster cartoon backgrounds at 1080p (1920x1080)
with distinct parallax-friendly depth layers and lighting vignettes.
"""

import math
import random
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFilter


class BackgroundGenerator:
    """Procedural generator for high-contrast educational cartoon background scenes."""

    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height

    def generate_background(self, background_id: str) -> Image.Image:
        """Generates a complete 1080p background based on the given background identifier."""
        bg_id = background_id.lower().strip()

        if "bedroom" in bg_id:
            return self._draw_bedroom_night()
        elif "brain" in bg_id:
            return self._draw_brain_interior()
        elif "lab" in bg_id or "microscop" in bg_id:
            return self._draw_laboratory()
        elif "cell" in bg_id or "decay" in bg_id:
            return self._draw_cellular_landscape()
        elif "emergency" in bg_id or "hospital" in bg_id or "room" in bg_id:
            return self._draw_emergency_room()
        elif "space" in bg_id or "void" in bg_id:
            return self._draw_abstract_space()
        elif "night" in bg_id or "star" in bg_id or "landscape" in bg_id:
            return self._draw_night_landscape()
        else:
            return self._draw_abstract_dark()

    def _draw_bedroom_night(self) -> Image.Image:
        """Dark moody bedroom at night with window moonbeam and wallpaper."""
        img = Image.new("RGBA", (self.width, self.height), (18, 20, 32, 255))
        draw = ImageDraw.Draw(img)

        # Wallpaper stripes
        for x in range(0, self.width, 60):
            draw.line([(x, 0), (x, self.height - 250)], fill=(24, 26, 40, 255), width=30)

        # Floor boards
        floor_y = self.height - 250
        draw.rectangle([0, floor_y, self.width, self.height], fill=(28, 22, 26, 255))
        draw.line([0, floor_y, self.width, floor_y], fill=(45, 35, 40, 255), width=6)
        for x in range(0, self.width, 120):
            draw.line([(x, floor_y), (x - 60, self.height)], fill=(20, 16, 20, 255), width=3)

        # Window with moon glow
        win_left, win_top, win_right, win_bottom = 200, 120, 550, 520
        draw.rectangle([win_left, win_top, win_right, win_bottom], fill=(12, 18, 45, 255), outline=(60, 70, 100, 255), width=8)
        # Moon in window
        draw.ellipse([win_left + 50, win_top + 40, win_left + 150, win_top + 140], fill=(220, 235, 255, 255))
        # Window frame cross
        mid_x = (win_left + win_right) // 2
        mid_y = (win_top + win_bottom) // 2
        draw.line([(mid_x, win_top), (mid_x, win_bottom)], fill=(60, 70, 100, 255), width=6)
        draw.line([(win_left, mid_y), (win_right, mid_y)], fill=(60, 70, 100, 255), width=6)

        # Light beam cast from window
        beam = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        beam_draw = ImageDraw.Draw(beam)
        beam_draw.polygon(
            [(win_left, win_top), (win_right, win_top), (self.width - 200, self.height), (350, self.height)],
            fill=(180, 210, 255, 22),
        )
        img = Image.alpha_composite(img, beam)

        # Bed silhouette
        bed_draw = ImageDraw.Draw(img)
        bed_left, bed_top = self.width - 700, self.height - 380
        bed_right, bed_bottom = self.width - 100, self.height - 180
        # Headboard
        bed_draw.rounded_rectangle([bed_right - 40, bed_top - 120, bed_right, bed_bottom], radius=10, fill=(40, 30, 42, 255))
        # Mattress
        bed_draw.rounded_rectangle([bed_left, bed_top, bed_right, bed_bottom], radius=15, fill=(35, 45, 65, 255), outline=(55, 65, 90, 255), width=4)
        # Pillow
        bed_draw.ellipse([bed_right - 180, bed_top - 30, bed_right - 40, bed_top + 30], fill=(160, 175, 205, 255))
        # Blanket
        bed_draw.rounded_rectangle([bed_left, bed_top + 10, bed_right - 160, bed_bottom], radius=10, fill=(60, 35, 55, 255))

        self._apply_vignette(img)
        return img

    def _draw_brain_interior(self) -> Image.Image:
        """Deep neural cyberspace inside the human brain with glowing synapses."""
        img = Image.new("RGBA", (self.width, self.height), (12, 10, 24, 255))
        draw = ImageDraw.Draw(img)

        # Random neural nodes
        random.seed(42)
        nodes = [(random.randint(100, self.width - 100), random.randint(100, self.height - 100)) for _ in range(35)]

        # Synapse connecting lines
        for i, (x1, y1) in enumerate(nodes):
            for x2, y2 in nodes[i + 1:i + 4]:
                dist = math.hypot(x2 - x1, y2 - y1)
                if dist < 450:
                    alpha = max(30, int(200 - dist * 0.4))
                    draw.line([(x1, y1), (x2, y2)], fill=(0, 210, 255, alpha), width=3)

        # Glowing Node points
        for x, y in nodes:
            # Outer glow
            draw.ellipse([x - 18, y - 18, x + 18, y + 18], fill=(0, 180, 255, 60))
            # Core
            draw.ellipse([x - 8, y - 8, x + 8, y + 8], fill=(180, 245, 255, 255))

        # Central massive energy core
        cx, cy = self.width // 2, self.height // 2
        for r, a in [(240, 15), (180, 30), (120, 60), (70, 150)]:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(140, 0, 255, a))
        draw.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=(220, 180, 255, 255))

        self._apply_vignette(img)
        return img

    def _draw_laboratory(self) -> Image.Image:
        """Sleek science laboratory background with tables, monitors, and glass flasks."""
        img = Image.new("RGBA", (self.width, self.height), (22, 28, 38, 255))
        draw = ImageDraw.Draw(img)

        # Tile grid
        for y in range(0, self.height - 300, 80):
            draw.line([(0, y), (self.width, y)], fill=(32, 40, 54, 255), width=2)
        for x in range(0, self.width, 100):
            draw.line([(x, 0), (x, self.height - 300)], fill=(32, 40, 54, 255), width=2)

        # Lab workbench
        bench_y = self.height - 320
        draw.rectangle([0, bench_y, self.width, self.height], fill=(45, 55, 70, 255), outline=(70, 85, 110, 255), width=5)

        # Microscope silhouette on left
        mx, my = 350, bench_y
        draw.rectangle([mx - 50, my - 20, mx + 50, my], fill=(20, 24, 30, 255))  # base
        draw.line([(mx, my - 20), (mx, my - 160)], fill=(30, 36, 45, 255), width=22)  # stand
        draw.line([(mx - 30, my - 160), (mx + 40, my - 120)], fill=(50, 60, 75, 255), width=28)  # eyepiece

        # Glowing Monitor on right
        mon_x, mon_y = self.width - 450, bench_y - 200
        draw.rectangle([mon_x - 140, mon_y - 90, mon_x + 140, mon_y + 90], fill=(15, 20, 28, 255), outline=(60, 75, 95, 255), width=6)
        draw.rectangle([mon_x - 125, mon_y - 75, mon_x + 125, mon_y + 75], fill=(5, 35, 45, 255))
        # Sine wave graph on monitor
        points = []
        for gx in range(mon_x - 120, mon_x + 120, 8):
            gy = mon_y + int(math.sin((gx - mon_x) * 0.1) * 35)
            points.append((gx, gy))
        if len(points) > 1:
            draw.line(points, fill=(0, 255, 180, 255), width=3)

        self._apply_vignette(img)
        return img

    def _draw_cellular_landscape(self) -> Image.Image:
        """Microscopic cellular interior with floating mitochondria, membranes, and ion particles."""
        img = Image.new("RGBA", (self.width, self.height), (35, 15, 22, 255))
        draw = ImageDraw.Draw(img)

        # Organic cell membrane arcs
        for r in range(1200, 200, -250):
            draw.arc([-200, -200, r * 2, r * 2], start=0, end=90, fill=(75, 30, 45, 120), width=18)

        # Floating mitochondria / vesicles
        random.seed(99)
        for _ in range(12):
            cx = random.randint(200, self.width - 200)
            cy = random.randint(150, self.height - 150)
            rx, ry = random.randint(40, 80), random.randint(25, 45)
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(130, 40, 60, 200), outline=(190, 60, 80, 255), width=4)
            # Internal folds
            draw.line([(cx - rx + 15, cy), (cx + rx - 15, cy)], fill=(190, 60, 80, 255), width=3)

        # Floating ion particles (calcium / sodium)
        for _ in range(50):
            px = random.randint(50, self.width - 50)
            py = random.randint(50, self.height - 50)
            draw.circle((px, py), radius=random.randint(3, 7), fill=(255, 220, 100, 220))

        self._apply_vignette(img)
        return img

    def _draw_emergency_room(self) -> Image.Image:
        """Dark dramatic medical emergency room with red warning strobe accents."""
        img = Image.new("RGBA", (self.width, self.height), (20, 14, 18, 255))
        draw = ImageDraw.Draw(img)

        # Wall & medical curtain
        draw.rectangle([0, 0, self.width, self.height - 250], fill=(28, 20, 25, 255))
        # Curtain folds
        for x in range(100, 600, 70):
            draw.line([(x, 0), (x, self.height - 250)], fill=(40, 28, 35, 255), width=35)

        # Floor
        draw.rectangle([0, self.height - 250, self.width, self.height], fill=(15, 12, 16, 255))

        # Heart monitor machine
        hx, hy = self.width - 400, self.height - 400
        draw.rectangle([hx - 90, hy - 140, hx + 90, hy + 80], fill=(30, 30, 35, 255), outline=(50, 50, 60, 255), width=5)
        # Monitor screen with flatline
        draw.rectangle([hx - 75, hy - 125, hx + 75, hy + 20], fill=(10, 10, 15, 255))
        draw.line([(hx - 70, hy - 50), (hx + 70, hy - 50)], fill=(255, 50, 50, 255), width=4)  # Flatline

        # Red emergency overhead lamp glow
        glow = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glow)
        for r, a in [(350, 15), (250, 30), (150, 60)]:
            g_draw.ellipse([self.width // 2 - r, 0 - r, self.width // 2 + r, 0 + r], fill=(255, 30, 40, a))
        img = Image.alpha_composite(img, glow)

        self._apply_vignette(img)
        return img

    def _draw_abstract_space(self) -> Image.Image:
        """Deep cosmic space with nebula clouds and star dust."""
        img = Image.new("RGBA", (self.width, self.height), (8, 6, 16, 255))
        draw = ImageDraw.Draw(img)

        # Nebula clouds
        for cx, cy, col, r in [
            (500, 400, (120, 30, 180, 35), 450),
            (1400, 600, (30, 100, 200, 40), 500),
            (960, 540, (200, 60, 100, 25), 400),
        ]:
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)

        # Stars
        random.seed(777)
        for _ in range(160):
            sx = random.randint(0, self.width)
            sy = random.randint(0, self.height)
            size = random.choice([1, 2, 3])
            brightness = random.randint(160, 255)
            draw.circle((sx, sy), radius=size, fill=(brightness, brightness, brightness, 255))

        self._apply_vignette(img)
        return img

    def _draw_night_landscape(self) -> Image.Image:
        """Cinematic night cliff with starry sky and deep purple twilight."""
        img = Image.new("RGBA", (self.width, self.height), (15, 12, 28, 255))
        draw = ImageDraw.Draw(img)

        # Gradient horizon twilight
        for y in range(self.height - 450, self.height - 200):
            progress = (y - (self.height - 450)) / 250.0
            r = int(15 + progress * 45)
            g = int(12 + progress * 20)
            b = int(28 + progress * 60)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b, 255))

        # Stars in upper sky
        random.seed(123)
        for _ in range(90):
            sx = random.randint(0, self.width)
            sy = random.randint(0, self.height - 400)
            draw.circle((sx, sy), radius=random.choice([1, 2]), fill=(240, 240, 255, 230))

        # Mountain and Cliff silhouettes
        # Distant mountain
        draw.polygon([(0, self.height - 200), (600, self.height - 450), (1200, self.height - 200)], fill=(22, 18, 35, 255))
        draw.polygon([(800, self.height - 200), (1450, self.height - 420), (self.width, self.height - 200)], fill=(18, 15, 30, 255))

        # Foreground cliff edge
        cliff = [(0, self.height), (0, self.height - 220), (850, self.height - 220), (1100, self.height - 120), (self.width, self.height - 120), (self.width, self.height)]
        draw.polygon(cliff, fill=(10, 8, 16, 255))

        self._apply_vignette(img)
        return img

    def _draw_abstract_dark(self) -> Image.Image:
        """Generic moody dark cartoon background with subtle radial gradient."""
        img = Image.new("RGBA", (self.width, self.height), (16, 18, 26, 255))
        draw = ImageDraw.Draw(img)

        cx, cy = self.width // 2, self.height // 2
        for r in range(800, 100, -100):
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(24, 28, 40, 35))

        self._apply_vignette(img)
        return img

    def _apply_vignette(self, img: Image.Image):
        """Applies a smooth dark vignette around the edges for cinematic focus."""
        draw = ImageDraw.Draw(img)
        # Corner dark gradients
        w, h = self.width, self.height
        draw.rectangle([0, 0, w, 20], fill=(0, 0, 0, 100))
        draw.rectangle([0, h - 20, w, h], fill=(0, 0, 0, 100))

    def save_background(self, img: Image.Image, output_path: str) -> str:
        """Saves background image to output path."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG")
        return output_path
