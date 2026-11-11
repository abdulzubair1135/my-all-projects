"""
Video Compositor and Render Pipeline for StickForge AI.
Assembles animated frame sequences, binds mixed audio tracks, and burns in subtitles.
"""

from __future__ import annotations
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Callable

from app.core.logging_manager import get_logger
from app.ai.schema_validator import GeneratedStoryboard, CharacterDef
from app.animation.scene_renderer import SceneRenderer
from app.audio.tts_provider import get_tts_provider, BaseTTSProvider
from app.audio.audio_mixer import AudioMixer
from app.audio.subtitle_generator import generate_subtitles_from_storyboard
from app.video.ffmpeg_manager import run_ffmpeg_command, probe_media

logger = get_logger("compositor")


class VideoCompositor:
    """End-to-end rendering pipeline coordinating frame rasterization and FFmpeg encoding."""

    def __init__(
        self,
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
        tts_provider: Optional[BaseTTSProvider] = None,
    ):
        self.w = width
        self.h = height
        self.fps = fps
        self.tts = tts_provider or get_tts_provider()
        self.renderer = SceneRenderer(width=width, height=height, fps=fps)

    def render_project_to_mp4(
        self,
        storyboard: GeneratedStoryboard,
        work_dir: Path,
        output_mp4_path: Path,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Path:
        """
        Executes full deterministic render pipeline:
        1. Synthesizes scene speech narration
        2. Renders frame image sequences
        3. Generates subtitles
        4. Mixes audio tracks
        5. Encodes final video with FFmpeg
        6. Validates result with FFprobe
        """
        work_dir.mkdir(parents=True, exist_ok=True)
        output_mp4_path.parent.mkdir(parents=True, exist_ok=True)

        def notify(p: float, msg: str):
            if progress_callback:
                progress_callback(p, msg)
            logger.info(f"Render progress: {p:.1f}% - {msg}")

        # 1. Voice Synthesis
        notify(5.0, "Synthesizing voice narration...")
        scene_audio_paths: List[Path] = []
        chars_map = {c.id: c for c in storyboard.characters}

        for idx, scene in enumerate(storyboard.scenes):
            audio_path = work_dir / f"scene_{idx:03d}.aac"
            narr_text = scene.narration.strip() or scene.dialogue.strip()
            if not narr_text:
                narr_text = "..."
            # Choose character voice or default
            v_id = None
            if scene.actions and scene.actions[0].character_id in chars_map:
                c_obj = chars_map[scene.actions[0].character_id]
                if hasattr(c_obj, "voice_id") and c_obj.voice_id:
                    v_id = c_obj.voice_id
            if not v_id:
                lang = getattr(storyboard, "language", "hinglish").lower()
                if "hi" in lang or "hing" in lang:
                    v_id = "hi-IN-MadhurNeural"
                else:
                    v_id = "en-US-ChristopherNeural"
            measured_dur = self.tts.synthesize(narr_text, audio_path, voice=v_id)
            # Sync scene duration to measured audio duration if needed
            scene.duration = max(scene.duration, measured_dur)
            scene_audio_paths.append(audio_path)

        # 2. Concatenate Narration
        notify(20.0, "Concatenating voiceover tracks...")
        combined_voice_path = work_dir / "voiceover.aac"
        AudioMixer.concatenate_audio_segments(scene_audio_paths, combined_voice_path)

        # 3. Subtitles
        notify(25.0, "Generating subtitle tracks...")
        srt_path = work_dir / "captions.srt"
        generate_subtitles_from_storyboard(storyboard, srt_path, storyboard.aspect_ratio)

        # 4. Render Scene Image Sequences
        frames_dir = work_dir / "frames"
        frames_dir.mkdir(parents=True, exist_ok=True)

        total_scenes = len(storyboard.scenes)
        global_frame_idx = 0

        for s_idx, scene in enumerate(storyboard.scenes):
            num_frames = int(scene.duration * self.fps)
            pct_base = 30.0 + (s_idx / total_scenes) * 45.0
            notify(pct_base, f"Rendering scene {s_idx + 1}/{total_scenes} ({num_frames} frames)...")

            for f_idx in range(num_frames):
                frame_img = self.renderer.render_frame(scene, chars_map, f_idx, num_frames)
                frame_path = frames_dir / f"frame_{global_frame_idx:06d}.png"
                frame_img.save(frame_path, format="PNG")
                global_frame_idx += 1

        # 5. FFmpeg Video + Audio Assembly
        notify(80.0, "Encoding video with FFmpeg...")
        input_pattern = str((frames_dir / "frame_%06d.png").resolve()).replace("\\", "/")
        total_duration = sum(s.duration for s in storyboard.scenes)

        args = [
            "-framerate", str(self.fps),
            "-i", input_pattern,
            "-i", str(combined_voice_path.resolve()),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(output_mp4_path.resolve()),
        ]

        run_ffmpeg_command(args, total_duration_seconds=total_duration)

        # 6. Quality Validation Check
        notify(95.0, "Inspecting output stream with FFprobe...")
        quality_info = probe_media(output_mp4_path)

        if not quality_info["has_video"]:
            raise RuntimeError("Render verification failed: No video stream found in output.")
        if quality_info["duration"] <= 0.0:
            raise RuntimeError("Render verification failed: Invalid zero duration in output.")

        notify(100.0, f"Render complete: {output_mp4_path.name} ({quality_info['duration']:.1f}s)")
        return output_mp4_path
