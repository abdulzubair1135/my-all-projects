"""
AUTO YT GENERATOR — Motion Graphics & Infographics Engine.

Procedurally renders high-impact animated infographics and visual data cutaways:
- Stats Counter Cards (animated numbers, currency, percentages)
- Brain Energy & Neural Infographics
- Warning / Alert Cards
- Comparison Metrics
"""

import math
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont

from app.models.scene import InfographicConfig


class InfographicsEngine:
    """Renders dynamic motion graphics and data visualization cutaways."""

    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height

    def render_infographic_frame(
        self,
        config: InfographicConfig,
        time_sec: float,
        duration_sec: float = 4.0,
    ) -> Image.Image:
        """Renders an infographic card or diagram at timestamp `time_sec`."""
        canvas = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(canvas)

        progress = min(1.0, max(0.0, time_sec / max(0.1, duration_sec)))

        # Animated Ease-Out scale
        scale_in = 1.0 - (1.0 - progress) ** 3
        card_w = int(820 * scale_in)
        card_h = int(480 * scale_in)

        # Center Position
        cx, cy = self.width // 2, self.height // 2
        x1 = cx - card_w // 2
        y1 = cy - card_h // 2
        x2 = cx + card_w // 2
        y2 = cy + card_h // 2

        if card_w < 50:
            return canvas

        # Card Backdrop with Glowing Neon Border
        border_col = (56, 189, 248, 255) if config.highlight_color == "#38bdf8" else (236, 72, 153, 255)
        draw.rounded_rectangle([x1, y1, x2, y2], radius=24, fill=(15, 20, 32, 235), outline=border_col, width=5)

        # Card Title Header
        draw.text((x1 + 40, y1 + 35), config.title.upper(), fill=border_col)

        # Animated Counter Number
        if config.stat_number is not None:
            current_num = config.stat_number * min(1.0, progress * 1.5)
            if config.stat_number >= 10:
                num_str = f"{config.stat_prefix}{int(current_num):,}{config.stat_suffix}"
            else:
                num_str = f"{config.stat_prefix}{current_num:.1f}{config.stat_suffix}"

            draw.text((x1 + 40, y1 + 110), num_str, fill=(255, 255, 255, 255))

        # Animated Progress Bar
        bar_w = card_w - 80
        bar_x = x1 + 40
        bar_y = y1 + 240
        draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + 18], radius=9, fill=(30, 41, 59, 255))

        fill_w = int(bar_w * progress)
        if fill_w > 10:
            draw.rounded_rectangle([bar_x, bar_y, bar_x + fill_w, bar_y + 18], radius=9, fill=border_col)

        # Subtitle / Description Text
        draw.text((x1 + 40, y1 + 280), config.description[:65], fill=(203, 213, 225, 255))
        if len(config.description) > 65:
            draw.text((x1 + 40, y1 + 320), config.description[65:130], fill=(203, 213, 225, 255))

        return canvas


# Default infographics engine instance
infographics_engine = InfographicsEngine()
