"""
Unit tests for Subtitle Engine, Video Compositor, and Video Renderer.
"""

import unittest
import tempfile
from pathlib import Path
from PIL import Image
from app.models.scene import SceneModel, SceneAction, CameraConfig
from app.models.project import ProjectModel, ProjectConfig
from app.video.subtitle import SubtitleEngine
from app.video.compositor import VideoCompositor
from app.video.renderer import VideoRenderer


class TestVideoCompositorEngine(unittest.TestCase):
    def setUp(self):
        self.sub_engine = SubtitleEngine()
        self.compositor = VideoCompositor(width=640, height=360)
        self.renderer = VideoRenderer(width=640, height=360)

    def test_subtitle_export_and_burn(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            scenes = [
                SceneModel(
                    scene_index=1,
                    duration_sec=3.0,
                    narration_text="First line of narration.",
                    background_id="bedroom_dark",
                ),
                SceneModel(
                    scene_index=2,
                    duration_sec=4.0,
                    narration_text="Second scene explanation.",
                    background_id="brain_interior",
                ),
            ]

            srt_file = str(Path(tmp_dir) / "test.srt")
            out_path = self.sub_engine.export_srt(scenes, srt_file)
            self.assertTrue(Path(out_path).exists())

            with open(out_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("First line of narration.", content)
            self.assertIn("-->", content)

            # Test Burn on Frame
            frame = Image.new("RGBA", (640, 360), (30, 30, 40, 255))
            burned = self.sub_engine.burn_subtitle_on_frame(frame, "Sample Subtitle Text")
            self.assertEqual(burned.size, (640, 360))

    def test_video_compositor_frame_stream(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            scenes = [
                SceneModel(
                    scene_index=1,
                    duration_sec=1.0,
                    narration_text="Short test scene.",
                    background_id="bedroom_dark",
                )
            ]

            frames = list(self.compositor.generate_video_frames(scenes, fps=5, project_dir=tmp_dir))
            self.assertEqual(len(frames), 5)
            f_idx, total, bgr_arr = frames[0]
            self.assertEqual(f_idx, 0)
            self.assertEqual(total, 5)
            self.assertEqual(bgr_arr.shape, (360, 640, 3))


if __name__ == "__main__":
    unittest.main()
