"""
Thumbnail Generator for StickForge AI.
Creates high-contrast cover cards with stickman composition, readable title headers, and safe margins.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

from app.animation.background_renderer import BackgroundRenderer
from app.animation.scene_renderer import SceneRenderer
from app.ai.schema_validator import GeneratedStoryboard, CharacterDef, SceneSpec, ActionSpec


class ThumbnailGenerator:
    """Generates social media cover cards for YouTube Shorts and Instagram Reels."""

    def __init__(self, width: int = 1080, height: int = 1920):
        self.w = width
        self.h = height
        self.bg_renderer = BackgroundRenderer(width, height)
        self.renderer = SceneRenderer(width=width, height=height, fps=1)

    def generate(
        self,
        storyboard: GeneratedStoryboard,
        output_path: Path,
        custom_title: Optional[str] = None,
    ) -> Path:
        """Render a thumbnail image."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Base frame using the climax or first scene
        first_scene = storyboard.scenes[0]
        chars_map = {c.id: c for c in storyboard.characters}
        img = self.renderer.render_frame(first_scene, chars_map, frame_idx=0, total_frames=1)
        draw = ImageDraw.Draw(img)

        # 2. High-contrast Title Card Header
        display_title = (custom_title or storyboard.title).upper()
        # Top banner overlay with semi-transparency
        banner_y1 = int(self.h * 0.12)
        banner_y2 = int(self.h * 0.28)
        draw.rectangle([(0, banner_y1), (self.w, banner_y2)], fill=(12, 14, 20))

        # Title text
        text_y = banner_y1 + 35
        draw.text((60, text_y), display_title, fill=(255, 220, 40))

        # Subtitle badge
        badge_y = text_y + 60
        draw.rectangle([(60, badge_y), (360, badge_y + 40)], fill=(2, 132, 199))
        draw.text((80, badge_y + 10), "STICKFORGE ORIGINAL", fill=(255, 255, 255))

        img.save(output_path, format="JPEG", quality=92)
        return output_path
