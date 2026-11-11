"""
AUTO YT GENERATOR — Subtitle and Caption Engine with Dynamic Karaoke Mode.

Features:
- Kinetic word-by-word bouncing karaoke captions (via DynamicCaptionsEngine)
- Standard 16:9 widescreen and 9:16 vertical Shorts support
- Standard .srt file export
"""

from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw

from app.models.scene import SceneModel
from app.video.dynamic_captions import dynamic_captions_engine
from app.logger import logger


class SubtitleEngine:
    """Handles subtitle generation, .srt file export, and frame overlay rendering."""

    def __init__(self, font_size: int = 42):
        self.font_size = font_size
        self.text_color = (255, 255, 255, 255)
        self.highlight_color = (255, 220, 40, 255)  # Bright yellow
        self.neon_cyan = (50, 240, 255, 255)
        self.outline_color = (10, 10, 15, 255)
        self.outline_width = 4

    def export_srt(self, scenes: List[SceneModel], output_srt_path: str) -> str:
        """Exports scene narration timeline as a standard .srt subtitle file."""
        Path(output_srt_path).parent.mkdir(parents=True, exist_ok=True)
        lines = []

        current_time = 0.0
        for i, s in enumerate(scenes, 1):
            start_sec = current_time
            end_sec = current_time + s.duration_sec
            text = s.subtitle_text or s.narration_text or ""

            if text.strip():
                start_srt = self._format_srt_timestamp(start_sec)
                end_srt = self._format_srt_timestamp(end_sec)

                lines.append(f"{i}")
                lines.append(f"{start_srt} --> {end_srt}")
                lines.append(text.strip())
                lines.append("")

            current_time += s.duration_sec

        with open(output_srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info(f"Subtitles exported to SRT -> {output_srt_path}")
        return output_srt_path

    @staticmethod
    def _format_srt_timestamp(seconds: float) -> str:
        """Converts float seconds into HH:MM:SS,mmm SRT format."""
        hrs = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

    def burn_subtitle_on_frame(
        self,
        frame: Image.Image,
        text: str,
        is_vertical: bool = False,
        time_sec: Optional[float] = None,
        duration_sec: Optional[float] = None,
    ) -> Image.Image:
        """Draws dynamic word-by-word karaoke captions or clean wrapped text onto a frame."""
        if not text or not text.strip():
            return frame

        if time_sec is not None and duration_sec is not None:
            return dynamic_captions_engine.render_karaoke_caption(
                frame=frame,
                text=text,
                time_sec=time_sec,
                duration_sec=duration_sec,
                is_vertical=is_vertical,
            )

        # Fallback static wrap
        canvas = frame.copy()
        draw = ImageDraw.Draw(canvas)
        w, h = canvas.size

        font_sz = int(self.font_size * 1.35) if is_vertical else self.font_size
        max_chars = 24 if is_vertical else 42

        words = text.split()
        wrapped_lines = []
        curr = []
        for word in words:
            if sum(len(w) + 1 for w in curr) + len(word) > max_chars:
                wrapped_lines.append(" ".join(curr))
                curr = [word]
            else:
                curr.append(word)
        if curr:
            wrapped_lines.append(" ".join(curr))

        line_height = font_sz + 16
        total_h = len(wrapped_lines) * line_height
        base_y = int(h * 0.68) - (total_h // 2) if is_vertical else h - total_h - 60

        for line_idx, line in enumerate(wrapped_lines):
            line_y = base_y + line_idx * line_height
            char_w = int(font_sz * 0.55)
            line_x = max(20, (w - len(line) * char_w) // 2)

            for dx in range(-self.outline_width, self.outline_width + 1):
                for dy in range(-self.outline_width, self.outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((line_x + dx, line_y + dy), line, fill=self.outline_color)

            draw.text((line_x, line_y), line, fill=self.highlight_color if is_vertical else self.text_color)

        return canvas


# Default subtitle engine instance
subtitle_engine = SubtitleEngine()
