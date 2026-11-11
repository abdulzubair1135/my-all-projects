"""
Subtitle Generator for StickForge AI.
Creates synchronized SubRip (.srt) files and line-wrapped caption cues with safe margin boundaries.
"""

from __future__ import annotations
import math
from pathlib import Path
from typing import List, Dict, Any
from pydantic import BaseModel

from app.ai.schema_validator import GeneratedStoryboard


class SubtitleCue(BaseModel):
    index: int
    start_seconds: float
    end_seconds: float
    text: str

    def to_srt_block(self) -> str:
        """Format as standard SRT block."""
        return (
            f"{self.index}\n"
            f"{format_timestamp(self.start_seconds)} --> {format_timestamp(self.end_seconds)}\n"
            f"{self.text}\n\n"
        )


def format_timestamp(seconds: float) -> str:
    """Format seconds into HH:MM:SS,mmm"""
    total_ms = int(round(seconds * 1000.0))
    ms = total_ms % 1000
    total_sec = total_ms // 1000
    sec = total_sec % 60
    total_min = total_sec // 60
    mins = total_min % 60
    hours = total_min // 60
    return f"{hours:02d}:{mins:02d}:{sec:02d},{ms:03d}"


def wrap_text_for_video(text: str, max_chars_per_line: int = 32) -> str:
    """Wrap subtitle text for comfortable reading on vertical mobile screens."""
    words = text.split()
    lines: List[str] = []
    current_line: List[str] = []
    current_len = 0

    for word in words:
        if current_len + len(word) + (1 if current_line else 0) <= max_chars_per_line:
            current_line.append(word)
            current_len += len(word) + (1 if len(current_line) > 1 else 0)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_len = len(word)

    if current_line:
        lines.append(" ".join(current_line))

    # Keep at most 2 lines per subtitle cue
    return "\n".join(lines[:2])


def generate_subtitles_from_storyboard(
    storyboard: GeneratedStoryboard,
    output_srt_path: Path,
    aspect_ratio: str = "9:16",
) -> List[SubtitleCue]:
    """Generates Subtitle cues and writes to .srt file."""
    max_chars = 30 if aspect_ratio == "9:16" else 50
    cues: List[SubtitleCue] = []

    current_time = 0.0
    cue_idx = 1

    for scene in storyboard.scenes:
        start_t = current_time
        end_t = current_time + scene.duration

        raw_text = scene.narration.strip() or scene.dialogue.strip()
        if raw_text:
            formatted_text = wrap_text_for_video(raw_text, max_chars_per_line=max_chars)
            cue = SubtitleCue(
                index=cue_idx,
                start_seconds=round(start_t, 2),
                end_seconds=round(end_t, 2),
                text=formatted_text,
            )
            cues.append(cue)
            cue_idx += 1

        current_time = end_t

    # Write to SRT file
    output_srt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_srt_path, "w", encoding="utf-8") as f:
        for cue in cues:
            f.write(cue.to_srt_block())

    return cues
