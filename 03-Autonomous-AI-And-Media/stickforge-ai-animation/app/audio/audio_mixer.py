"""
Multi-track Audio Mixer for StickForge AI.
Handles voiceover concatenation, background music looping, and music ducking using FFmpeg.
"""

from __future__ import annotations
import math
from pathlib import Path
from typing import List, Optional

from app.core.logging_manager import get_logger
from app.video.ffmpeg_manager import run_ffmpeg_command, probe_media

logger = get_logger("audio_mixer")


class AudioMixer:
    """Mixes narration, dialogue, and background music."""

    @staticmethod
    def concatenate_audio_segments(segment_paths: List[Path], output_path: Path) -> Path:
        """Concatenates individual scene voice tracks into a single continuous voiceover track."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if not segment_paths:
            raise ValueError("No audio segments provided for concatenation.")

        if len(segment_paths) == 1:
            import shutil
            shutil.copyfile(segment_paths[0], output_path)
            return output_path

        # Create FFmpeg concat demuxer text file
        concat_list_file = output_path.with_suffix(".concat.txt")
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for seg in segment_paths:
                # Escape backslashes for FFmpeg concat demuxer
                clean_path = str(seg.resolve()).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        args = [
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_list_file),
            "-c:a", "aac",
            "-b:a", "192k",
            str(output_path),
        ]
        run_ffmpeg_command(args)

        if concat_list_file.exists():
            concat_list_file.unlink()

        return output_path

    @staticmethod
    def mix_narration_and_music(
        narration_path: Path,
        music_path: Optional[Path],
        output_path: Path,
        music_volume: float = 0.15,
        narration_volume: float = 1.0,
    ) -> Path:
        """
        Mixes speech narration with background music.
        Ducks background music volume so speech remains crisp and intelligible.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not music_path or not music_path.exists():
            # If no BGM, simply copy or re-encode narration
            args = ["-i", str(narration_path), "-c:a", "aac", "-b:a", "192k", str(output_path)]
            run_ffmpeg_command(args)
            return output_path

        # FFmpeg filter: loop music and adjust volume with amix
        filter_complex = (
            f"[0:a]volume={narration_volume}[a0];"
            f"[1:a]volume={music_volume}[a1];"
            f"[a0][a1]amix=inputs=2:duration=first:dropout_transition=2[outa]"
        )

        args = [
            "-i", str(narration_path),
            "-stream_loop", "-1",
            "-i", str(music_path),
            "-filter_complex", filter_complex,
            "-map", "[outa]",
            "-c:a", "aac",
            "-b:a", "192k",
            str(output_path),
        ]
        run_ffmpeg_command(args)
        return output_path
