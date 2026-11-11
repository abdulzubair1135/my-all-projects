"""
AUTO YT GENERATOR — Transition Blending Engine.

Renders seamless cinematic transitions between scene boundaries:
- Zoom Punch Transition
- Directional Whip Pan
- Glitch & Chromatic Aberration Flash
- Smooth Crossfade
"""

import math
from typing import Optional
from PIL import Image, ImageEnhance, ImageChops


class TransitionEngine:
    """Applies visual transitions between consecutive scene frames."""

    def apply_transition(
        self,
        frame_a: Image.Image,
        frame_b: Image.Image,
        progress: float,
        transition_type: str = "crossfade",
    ) -> Image.Image:
        """Blends frame_a and frame_b at transition progress [0.0 -> 1.0]."""
        p = max(0.0, min(1.0, progress))

        if p <= 0.0:
            return frame_a
        elif p >= 1.0:
            return frame_b

        trans = transition_type.lower()

        if "zoom" in trans:
            # Zoom punch into frame B
            scale = 1.0 + (1.0 - p) * 0.35
            w, h = frame_b.size
            nw, nh = int(w * scale), int(h * scale)
            scaled_b = frame_b.resize((nw, nh), Image.Resampling.BILINEAR)
            crop_x = (nw - w) // 2
            crop_y = (nh - h) // 2
            zoomed_b = scaled_b.crop((crop_x, crop_y, crop_x + w, crop_y + h))
            return Image.blend(frame_a.convert("RGB"), zoomed_b.convert("RGB"), p).convert("RGBA")

        elif "flash" in trans or "glitch" in trans:
            # White impact flash at peak
            blend = Image.blend(frame_a.convert("RGB"), frame_b.convert("RGB"), p)
            flash_intensity = math.sin(p * math.pi) * 0.7
            enhancer = ImageEnhance.Brightness(blend)
            return enhancer.enhance(1.0 + flash_intensity).convert("RGBA")

        # Default smooth linear crossfade
        return Image.blend(frame_a.convert("RGB"), frame_b.convert("RGB"), p).convert("RGBA")


# Default transition engine instance
transition_engine = TransitionEngine()
