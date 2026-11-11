"""
AUTO YT GENERATOR — Final Video Renderer & Exporter.

Encodes visual frame sequences and muxes with master audio to produce
a YouTube-ready 1080p MP4 file.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional
import cv2

from app.models.scene import SceneModel
from app.models.project import ProjectModel
from app.video.compositor import video_compositor
from app.video.subtitle import subtitle_engine
from app.logger import logger


class VideoRenderer:
    """Renders visual frames and exports the final complete MP4 video."""

    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height

    def render_project_video(
        self,
        project: ProjectModel,
        scenes: List[SceneModel],
        master_audio_path: Optional[str] = None,
        fps: int = 30,
        burn_subtitles: bool = True,
    ) -> str:
        """Renders complete 1080p MP4 video with synced audio and subtitles."""
        project_dir = Path(project.project_dir or f"projects/{project.id}")
        final_dir = project_dir / "final"
        final_dir.mkdir(parents=True, exist_ok=True)

        temp_video_path = str(final_dir / "temp_video.mp4")
        final_output_path = str(final_dir / "video.mp4")
        srt_output_path = str(final_dir / "subtitles.srt")

        # 1. Export .srt Subtitles File
        subtitle_engine.export_srt(scenes, srt_output_path)

        # 2. Encode Visual Video Stream with OpenCV VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(
            temp_video_path,
            fourcc,
            float(fps),
            (self.width, self.height),
        )

        logger.info(f"Encoding video stream ({self.width}x{self.height} @ {fps} fps)...")
        frame_generator = video_compositor.generate_video_frames(
            scenes=scenes,
            fps=fps,
            burn_subtitles=burn_subtitles,
            project_dir=str(project_dir),
        )

        for frame_idx, total_frames, frame_bgr in frame_generator:
            writer.write(frame_bgr)
            if frame_idx % int(fps * 3) == 0:
                pct = (frame_idx / max(1, total_frames)) * 100.0
                logger.info(f"Rendering frames: [{frame_idx}/{total_frames}] ({pct:.1f}%)")

        writer.release()
        logger.info(f"Visual video stream written -> {temp_video_path}")

        # 3. Audio Muxing (Combine temp_video.mp4 + master_audio.wav -> video.mp4)
        audio_file = master_audio_path or str(project_dir / "audio" / "master_audio.wav")

        if Path(audio_file).exists():
            success = self._mux_audio_video(temp_video_path, audio_file, final_output_path)
            if success and Path(final_output_path).exists():
                # Clean up temp raw video
                try:
                    os.remove(temp_video_path)
                except Exception:
                    pass
                logger.info(f"Final MP4 Video Exported Successfully -> {final_output_path}")
                return final_output_path

        # If audio muxing failed or audio missing, keep visual video
        shutil.move(temp_video_path, final_output_path)
        logger.info(f"Final MP4 Video Exported (Visual Only) -> {final_output_path}")
        return final_output_path

    def _mux_audio_video(self, video_path: str, audio_path: str, output_path: str) -> bool:
        """Muxes video and audio tracks using imageio-ffmpeg or ffmpeg subprocess."""
        # Try imageio_ffmpeg binary first
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            cmd = [
                ffmpeg_exe,
                "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                output_path,
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except Exception as e:
            logger.debug(f"imageio_ffmpeg mux failed: {e}")

        # Try system FFmpeg on PATH
        try:
            cmd = [
                "ffmpeg",
                "-y",
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",
                output_path,
            ]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except Exception as err:
            logger.warning(f"System ffmpeg mux failed: {err}")
            return False


# Default video renderer instance
video_renderer = VideoRenderer()
