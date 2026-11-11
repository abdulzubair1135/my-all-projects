"""
AUTO YT GENERATOR — Video Compositor.

Coordinates frame rendering across the timeline, binds visual animation with
spoken narration and burned-in subtitles, and yields composited frames.
"""

from pathlib import Path
from typing import List, Generator, Tuple, Optional
from PIL import Image
import numpy as np

from app.models.scene import SceneModel
from app.animation.animator import scene_animator
from app.video.subtitle import subtitle_engine
from app.logger import logger


class VideoCompositor:
    """Composites visual animation scenes with subtitle overlays for video rendering."""

    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height

    def generate_video_frames(
        self,
        scenes: List[SceneModel],
        fps: int = 30,
        burn_subtitles: bool = True,
        project_dir: Optional[str] = None,
    ) -> Generator[Tuple[int, int, np.ndarray], None, None]:
        """Yields (current_frame_index, total_frames, frame_bgr_array) for entire project timeline."""
        total_duration = sum(s.duration_sec for s in scenes)
        total_frames = int(total_duration * fps)

        logger.info(f"Compositing video: {len(scenes)} scenes ({total_duration:.1f}s) @ {fps} fps ({total_frames} total frames)")

        frame_idx = 0
        for s in scenes:
            scene_frames = max(1, int(s.duration_sec * fps))
            sub_text = s.subtitle_text or s.narration_text or ""

            for f_in_scene in range(scene_frames):
                t_in_scene = f_in_scene / float(fps)

                # 1. Render Animated Scene Canvas
                frame_pil = scene_animator.render_scene_frame(
                    scene=s,
                    time_sec=t_in_scene,
                    project_dir=project_dir,
                )

                # Resize to target resolution if needed
                if frame_pil.size != (self.width, self.height):
                    frame_pil = frame_pil.resize((self.width, self.height), Image.Resampling.BILINEAR)

                # 2. Burn Subtitles
                if burn_subtitles and sub_text:
                    frame_pil = subtitle_engine.burn_subtitle_on_frame(frame_pil, sub_text)

                # 3. Convert PIL RGBA -> BGR NumPy array for OpenCV video encoding
                frame_rgb = frame_pil.convert("RGB")
                frame_bgr = np.array(frame_rgb)[:, :, ::-1]  # RGB to BGR

                yield frame_idx, total_frames, frame_bgr
                frame_idx += 1


# Default video compositor instance
video_compositor = VideoCompositor()
