"""
AUTO YT GENERATOR — Procedural B-Roll Video Engine.

Generates dynamic science and documentary cutaway visuals:
- Glowing Neural Synapse network
- High-Energy Particle Vortex
- Cellular Biology / DNA Helix
- Digital Matrix Grid
"""

import math
import random
from typing import Tuple
from PIL import Image, ImageDraw


class BRollEngine:
    """Renders procedural animated B-roll cutaways."""

    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height

    def render_broll_frame(
        self,
        broll_type: str,
        time_sec: float,
        duration_sec: float = 4.0,
    ) -> Image.Image:
        """Renders an animated B-roll frame at timestamp `time_sec`."""
        canvas = Image.new("RGBA", (self.width, self.height), (8, 10, 18, 255))
        draw = ImageDraw.Draw(canvas)

        b_type = broll_type.lower().strip()

        if "neural" in b_type or "brain" in b_type or "synapse" in b_type:
            self._render_neural_synapses(draw, time_sec)
        elif "space" in b_type or "earth" in b_type or "planet" in b_type:
            self._render_space_vortex(draw, time_sec)
        else:
            self._render_electric_grid(draw, time_sec)

        return canvas

    def _render_neural_synapses(self, draw: ImageDraw.ImageDraw, t: float):
        # 12 animated neural nodes with pulsing connecting axons
        nodes = [
            (350, 250), (600, 180), (960, 220), (1350, 200), (1600, 320),
            (420, 580), (800, 520), (1150, 550), (1520, 620),
            (550, 850), (960, 880), (1400, 820),
        ]

        # Draw connecting axons
        for i, (x1, y1) in enumerate(nodes):
            for j, (x2, y2) in enumerate(nodes[i + 1:], i + 1):
                dist = math.hypot(x2 - x1, y2 - y1)
                if dist < 450:
                    # Pulsing energy
                    pulse = math.sin(t * 5.0 + i + j) * 0.5 + 0.5
                    alpha = int(120 * pulse + 30)
                    draw.line([(x1, y1), (x2, y2)], fill=(56, 189, 248, alpha), width=3)

        # Draw glowing soma nodes
        for i, (x, y) in enumerate(nodes):
            pulse = math.sin(t * 6.0 + i) * 8.0
            r = int(24 + pulse)
            draw.ellipse([x - r, y - r, x + r, y + r], fill=(236, 72, 153, 200), outline=(255, 255, 255, 255), width=3)

    def _render_space_vortex(self, draw: ImageDraw.ImageDraw, t: float):
        cx, cy = self.width // 2, self.height // 2
        # Rotating galaxy vortex particles
        for i in range(80):
            angle = i * 0.25 + t * 0.8
            dist = (i * 12.0 + t * 40.0) % 650
            px = int(cx + math.cos(angle) * dist)
            py = int(cy + math.sin(angle) * dist)
            pr = int(2 + (dist / 650.0) * 5)
            draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(255, 220, 100, 220))

    def _render_electric_grid(self, draw: ImageDraw.ImageDraw, t: float):
        # 3D perspective grid floor
        cy = int(self.height * 0.6)
        for y in range(cy, self.height, 40):
            pulse = math.sin(t * 4.0 + y * 0.05) * 0.4 + 0.6
            alpha = int(180 * pulse)
            draw.line([(0, y), (self.width, y)], fill=(139, 92, 246, alpha), width=2)


# Default B-roll engine instance
broll_engine = BRollEngine()
