"""
Unit tests for 2D Animation Engine, Camera, and Visual Effects (VFX).
"""

import unittest
import tempfile
from PIL import Image
from app.animation.camera import CameraController
from app.animation.effects import EffectsEngine
from app.animation.animator import SceneAnimator
from app.models.scene import SceneModel, SceneAction, CameraConfig


class TestAnimationEngine(unittest.TestCase):
    def setUp(self):
        self.camera_ctrl = CameraController(target_width=1920, target_height=1080)
        self.effects_engine = EffectsEngine(width=1920, height=1080)
        self.animator = SceneAnimator(width=1920, height=1080)

    def test_camera_zoom_and_pan(self):
        canvas = Image.new("RGBA", (1920, 1080), (50, 50, 80, 255))
        cam_zoom = CameraConfig(type="slow_zoom_in", zoom_start=1.0, zoom_end=1.3)

        # Progress 0.0
        frame_0 = self.camera_ctrl.apply_camera(canvas, cam_zoom, progress=0.0)
        self.assertEqual(frame_0.size, (1920, 1080))

        # Progress 1.0
        frame_1 = self.camera_ctrl.apply_camera(canvas, cam_zoom, progress=1.0)
        self.assertEqual(frame_1.size, (1920, 1080))

    def test_camera_shake(self):
        canvas = Image.new("RGBA", (1920, 1080), (30, 40, 50, 255))
        cam_shake = CameraConfig(type="shake", zoom_start=1.1, zoom_end=1.1)
        shaken = self.camera_ctrl.apply_camera(canvas, cam_shake, progress=0.5)
        self.assertEqual(shaken.size, (1920, 1080))

    def test_effects_engine(self):
        frame = Image.new("RGBA", (1920, 1080), (30, 30, 40, 255))
        effects = ["heartbeat", "vignette", "grain", "glitch", "warning_flash"]
        processed = self.effects_engine.apply_effects(frame, effects, time_sec=1.5, duration_sec=5.0)
        self.assertEqual(processed.size, (1920, 1080))
        self.assertEqual(processed.mode, "RGBA")

    def test_scene_animator_render_frame(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            scene = SceneModel(
                scene_index=1,
                duration_sec=3.0,
                background_id="bedroom_dark",
                characters=["main_char"],
                props=["clock"],
                actions=[
                    SceneAction(
                        entity_id="main_char",
                        action="sleep",
                        expression="neutral",
                        start_time_sec=0.0,
                        duration_sec=3.0,
                        position_x_percent=50.0,
                        position_y_percent=60.0,
                    )
                ],
                camera=CameraConfig(type="slow_zoom_in", zoom_start=1.0, zoom_end=1.2),
                effects=["vignette", "film_grain"],
            )

            frame = self.animator.render_scene_frame(scene, time_sec=1.0, project_dir=tmp_dir)
            self.assertEqual(frame.size, (1920, 1080))
            self.assertEqual(frame.mode, "RGBA")


if __name__ == "__main__":
    unittest.main()
