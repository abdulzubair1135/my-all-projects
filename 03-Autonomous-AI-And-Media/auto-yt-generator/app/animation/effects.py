"""
AUTO YT GENERATOR — Visual Effects (VFX) Overlays.

Procedural video effects applied on top of rendered scene frames:
- heartbeat_pulse (rhythmic red tint and dilation)
- red_warning_flash (emergency strobe)
- vignette (cinematic corner shadow)
- film_grain (subtle atmospheric noise)
- glitch (scanline displacement and chromatic aberration)
- floating_particles (ambient dust / glowing motes)
- electric_pulse_fading
"""

import math
import random
from typing import List
from PIL import Image, ImageDraw, ImageEnhance, ImageChops


class EffectsEngine:
    """Applies dynamic visual effects to frames during compositing."""

    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height

    def apply_effects(
        self,
        frame: Image.Image,
        effects_list: List[str],
        time_sec: float,
        duration_sec: float,
    ) -> Image.Image:
        """Applies a chain of named visual effects to the given frame."""
        if not effects_list:
            return frame

        result = frame.copy()
        progress = time_sec / max(0.1, duration_sec)

        for eff in effects_list:
            eff_name = eff.lower().strip()

            if "heartbeat" in eff_name:
                result = self._apply_heartbeat(result, time_sec)
            elif "warning" in eff_name or "red" in eff_name:
                result = self._apply_warning_flash(result, time_sec)
            elif "vignette" in eff_name:
                result = self._apply_vignette(result)
            elif "grain" in eff_name:
                result = self._apply_film_grain(result, time_sec)
            elif "glitch" in eff_name:
                result = self._apply_glitch(result, time_sec)
            elif "particle" in eff_name:
                result = self._apply_particles(result, time_sec)
            elif "electric" in eff_name or "pulse" in eff_name:
                result = self._apply_electric_pulse(result, progress)

        return result

    def _apply_heartbeat(self, frame: Image.Image, time_sec: float) -> Image.Image:
        """Rhythmic red vignette pulse matching heartbeat BPM (~72 BPM = 1.2 Hz)."""
        bpm_freq = 1.2
        cycle = (time_sec * bpm_freq) % 1.0
        # Quick double pulse: lub-dub
        if cycle < 0.15:
            intensity = math.sin((cycle / 0.15) * math.pi)
        elif 0.2 < cycle < 0.35:
            intensity = math.sin(((cycle - 0.2) / 0.15) * math.pi) * 0.7
        else:
            intensity = 0.0

        if intensity > 0.05:
            overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            alpha = int(intensity * 120)
            draw.rectangle([0, 0, self.width, self.height], fill=(220, 20, 30, alpha))
            return Image.alpha_composite(frame.convert("RGBA"), overlay)
        return frame

    def _apply_warning_flash(self, frame: Image.Image, time_sec: float) -> Image.Image:
        """Strobe red warning overlay pulsing every 0.8 seconds."""
        pulse = abs(math.sin(time_sec * 4.0))
        if pulse > 0.3:
            overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            alpha = int(pulse * 90)
            draw.rectangle([0, 0, self.width, self.height], fill=(255, 30, 30, alpha))
            return Image.alpha_composite(frame.convert("RGBA"), overlay)
        return frame

    def _apply_vignette(self, frame: Image.Image) -> Image.Image:
        """Applies corner dark vignette."""
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        # Top and bottom bars
        draw.rectangle([0, 0, self.width, 35], fill=(0, 0, 0, 110))
        draw.rectangle([0, self.height - 35, self.width, self.height], fill=(0, 0, 0, 110))
        # Left and right
        draw.rectangle([0, 0, 35, self.height], fill=(0, 0, 0, 90))
        draw.rectangle([self.width - 35, 0, self.width, self.height], fill=(0, 0, 0, 90))
        return Image.alpha_composite(frame.convert("RGBA"), overlay)

    def _apply_film_grain(self, frame: Image.Image, time_sec: float) -> Image.Image:
        """Subtle animated film grain."""
        random.seed(int(time_sec * 30))
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for _ in range(350):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            draw.point((x, y), fill=(255, 255, 255, random.randint(20, 60)))
        return Image.alpha_composite(frame.convert("RGBA"), overlay)

    def _apply_glitch(self, frame: Image.Image, time_sec: float) -> Image.Image:
        """Horizontal scanline shift and RGB split."""
        # Glitch triggers occasionally
        if (int(time_sec * 8) % 7) == 0:
            result = frame.copy()
            # Displace a horizontal band
            band_y = int((math.sin(time_sec * 10) * 0.5 + 0.5) * (self.height - 100))
            band_h = random.randint(20, 70)
            band = result.crop((0, band_y, self.width, band_y + band_h))
            shift_x = random.randint(-25, 25)
            result.paste(band, (shift_x, band_y))
            return result
        return frame

    def _apply_particles(self, frame: Image.Image, time_sec: float) -> Image.Image:
        """Floating ambient particles drifting upwards."""
        overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for i in range(25):
            seed = i * 137
            base_x = (seed * 31) % self.width
            drift_y = (seed * 17 - int(time_sec * 40)) % self.height
            sway_x = int(base_x + math.sin(time_sec + i) * 20)
            draw.circle((sway_x, drift_y), radius=random.randint(2, 5), fill=(200, 240, 255, 120))
        return Image.alpha_composite(frame.convert("RGBA"), overlay)

    def _apply_electric_pulse(self, frame: Image.Image, progress: float) -> Image.Image:
        """Fading electric blue overlay."""
        intensity = max(0.0, 1.0 - progress)
        if intensity > 0.05:
            overlay = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            draw.rectangle([0, 0, self.width, self.height], fill=(0, 180, 255, int(intensity * 50)))
            return Image.alpha_composite(frame.convert("RGBA"), overlay)
        return frame


# Default effects engine instance
effects_engine = EffectsEngine()
