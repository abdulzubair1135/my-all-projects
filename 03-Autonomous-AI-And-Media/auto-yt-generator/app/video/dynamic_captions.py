"""
AUTO YT GENERATOR — Mobile Dynamic Karaoke Captions Engine.

Renders high-retention YouTube Shorts & Mobile Widescreen captions:
- 2 to 4 word dynamic chunks
- Active-word bouncing scale animation
- High-contrast neon color highlights
- Thick dark outline and drop shadows
"""

import math
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw


class DynamicCaptionsEngine:
    """Renders kinetic word-by-word bouncing karaoke captions."""

    def __init__(self, font_size: int = 48):
        self.font_size = font_size
        self.text_color = (255, 255, 255, 255)
        self.active_color = (255, 225, 40, 255)   # Vibrant yellow
        self.highlight_color = (56, 189, 248, 255) # Cyber cyan
        self.outline_color = (10, 10, 15, 255)
        self.outline_width = 5

    def render_karaoke_caption(
        self,
        frame: Image.Image,
        text: str,
        time_sec: float,
        duration_sec: float,
        is_vertical: bool = False,
    ) -> Image.Image:
        """Renders time-synchronized word-by-word bouncing captions onto a frame."""
        if not text or not text.strip():
            return frame

        canvas = frame.copy()
        draw = ImageDraw.Draw(canvas)
        w, h = canvas.size

        words = text.split()
        if not words:
            return frame

        # Calculate active word index based on time progress
        progress = max(0.0, min(1.0, time_sec / max(0.1, duration_sec)))
        active_idx = min(len(words) - 1, int(progress * len(words)))

        # Group words into 3-4 word chunks
        chunk_size = 3 if is_vertical else 5
        chunk_start = (active_idx // chunk_size) * chunk_size
        current_chunk = words[chunk_start:chunk_start + chunk_size]

        font_sz = int(self.font_size * 1.35) if is_vertical else self.font_size
        char_w = int(font_sz * 0.55)

        # Total width of chunk
        full_chunk_text = " ".join(current_chunk)
        total_w = len(full_chunk_text) * char_w

        # Position (Lower third for 16:9, Middle-lower for 9:16 Shorts)
        base_y = int(h * 0.70) if is_vertical else (h - font_sz - 75)
        start_x = max(30, (w - total_w) // 2)

        curr_x = start_x
        for i, word in enumerate(current_chunk):
            global_word_idx = chunk_start + i
            is_active = (global_word_idx == active_idx)

            # Active word scale bounce
            bounce_y = int(math.sin((time_sec * 12.0) % math.pi) * 6.0) if is_active else 0
            word_color = self.active_color if is_active else self.text_color

            # Draw word outline
            for dx in range(-self.outline_width, self.outline_width + 1):
                for dy in range(-self.outline_width, self.outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((curr_x + dx, base_y - bounce_y + dy), word, fill=self.outline_color)

            # Draw main word text
            draw.text((curr_x, base_y - bounce_y), word, fill=word_color)

            # Advance X for next word + space
            curr_x += (len(word) + 1) * char_w

        return canvas


# Default dynamic captions engine instance
dynamic_captions_engine = DynamicCaptionsEngine()
