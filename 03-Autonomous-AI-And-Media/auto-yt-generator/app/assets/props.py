"""
AUTO YT GENERATOR — Procedural 2D Prop Generator.

Generates standalone transparent RGBA props (clocks, microscopes, beds, nodes, monitors)
that can be dynamically placed and animated on any scene layer.
"""

from pathlib import Path
from PIL import Image, ImageDraw


class PropGenerator:
    """Procedural generator for transparent 2D prop overlays."""

    def __init__(self):
        self.outline_color = (25, 25, 30, 255)
        self.outline_width = 4

    def generate_prop(self, prop_id: str, width: int = 300, height: int = 300) -> Image.Image:
        """Generates a transparent RGBA prop based on identifier."""
        p_id = prop_id.lower().strip()
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        cx, cy = width // 2, height // 2

        if "clock" in p_id:
            # Wall clock
            r = min(width, height) // 2 - 20
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(240, 240, 245, 255), outline=self.outline_color, width=self.outline_width + 2)
            # Clock hands (ticking at 11:55)
            draw.line([(cx, cy), (cx - 10, cy - r + 35)], fill=(30, 30, 35, 255), width=6)
            draw.line([(cx, cy), (cx + r - 45, cy - 20)], fill=(200, 40, 40, 255), width=4)
            draw.circle((cx, cy), radius=7, fill=self.outline_color)

        elif "microscope" in p_id:
            # Scientific microscope
            draw.rectangle([cx - 70, cy + 80, cx + 70, cy + 110], fill=(45, 55, 65, 255), outline=self.outline_color, width=4)
            draw.line([(cx, cy + 80), (cx, cy - 60)], fill=(70, 80, 95, 255), width=24)
            draw.line([(cx - 40, cy - 60), (cx + 50, cy - 20)], fill=(120, 135, 155, 255), width=32)

        elif "bed" in p_id:
            # Dark modern bed
            draw.rounded_rectangle([cx - 130, cy - 50, cx + 130, cy + 70], radius=12, fill=(45, 55, 75, 255), outline=self.outline_color, width=4)
            draw.ellipse([cx + 40, cy - 70, cx + 120, cy - 10], fill=(210, 220, 240, 255), outline=self.outline_color, width=3)
            draw.rounded_rectangle([cx - 130, cy - 30, cx + 30, cy + 70], radius=8, fill=(80, 45, 70, 255))

        elif "beam" in p_id or "laser" in p_id or "energy" in p_id:
            # Glowing cyan energy beam
            for r, a in [(60, 25), (40, 50), (20, 120), (8, 255)]:
                draw.line([(0, cy), (width, cy)], fill=(0, 230, 255, a), width=r)

        elif "glow" in p_id or "node" in p_id or "isolated" in p_id:
            # Glowing celestial orb / neuron node
            for r, a in [(90, 20), (65, 45), (40, 90), (20, 220)]:
                draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 240, 255, a))
            draw.circle((cx, cy), radius=12, fill=(255, 255, 255, 255))

        else:
            # Generic scientific device
            draw.rounded_rectangle([cx - 80, cy - 60, cx + 80, cy + 60], radius=15, fill=(50, 60, 75, 255), outline=self.outline_color, width=4)
            draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(0, 210, 255, 180))

        return img

    def save_prop(self, img: Image.Image, output_path: str) -> str:
        """Saves prop image to path."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "PNG")
        return output_path
