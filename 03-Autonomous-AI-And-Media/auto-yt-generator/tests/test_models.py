"""
Unit tests for Pydantic data models.
"""

import unittest
from app.models.project import ProjectConfig, ProjectModel
from app.models.script import ScriptSection, ScriptModel
from app.models.scene import SceneModel, SceneAction, CameraConfig
from app.constants import PipelineStage, VideoStyle


class TestModels(unittest.TestCase):
    def test_project_config_validation(self):
        cfg = ProjectConfig(
            topic="What happens if the sun disappears?",
            language="en",
            duration_seconds=300,
            style=VideoStyle.DARK_SCIENCE.value,
        )
        self.assertEqual(cfg.topic == "What happens if the sun disappears?", True)
        self.assertEqual(cfg.duration_seconds, 300)

    def test_script_model_structure(self):
        section = ScriptSection(
            section_type="hook",
            title="Opening Hook",
            narration_text="Imagine waking up and the sky is pitch black forever.",
            estimated_duration_sec=5.0,
            visual_intent="Dark room with window looking out to space",
        )
        script = ScriptModel(
            project_id="test-proj-1",
            title="When Sun Disappears",
            hook="Imagine waking up...",
            target_duration_sec=300,
            total_estimated_duration_sec=5.0,
            sections=[section],
        )
        self.assertEqual(len(script.sections), 1)
        self.assertEqual(script.sections[0].section_type, "hook")

    def test_scene_model(self):
        scene = SceneModel(
            scene_index=1,
            duration_sec=5.0,
            narration_text="The sun is gone.",
            background_id="space_void",
            characters=["earth_character"],
            camera=CameraConfig(type="slow_zoom_in", zoom_start=1.0, zoom_end=1.2),
        )
        self.assertEqual(scene.scene_index, 1)
        self.assertEqual(scene.camera.type, "slow_zoom_in")


if __name__ == "__main__":
    unittest.main()
