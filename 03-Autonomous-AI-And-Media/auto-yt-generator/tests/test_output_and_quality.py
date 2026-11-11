"""
Unit tests for YouTube Thumbnail, Metadata, and Quality Validator.
"""

import unittest
import tempfile
from pathlib import Path
from app.models.project import ProjectModel, ProjectConfig
from app.models.script import ScriptModel, ScriptSection
from app.models.scene import SceneModel
from app.output.thumbnail import ThumbnailGenerator
from app.output.metadata import MetadataGenerator
from app.quality.validator import QualityValidator


class TestOutputAndQuality(unittest.TestCase):
    def setUp(self):
        self.thumb_gen = ThumbnailGenerator(width=640, height=360)
        self.meta_gen = MetadataGenerator()
        self.validator = QualityValidator()

    def test_thumbnail_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = ProjectModel(
                id="test_thumb_proj",
                title="What happens if brain stops?",
                config=ProjectConfig(topic="What happens if your brain stops?"),
                project_dir=tmp_dir,
            )
            out_png = str(Path(tmp_dir) / "thumbnail.png")
            res = self.thumb_gen.generate_thumbnail(project, output_path=out_png)
            self.assertTrue(Path(res).exists())
            self.assertTrue(Path(res).stat().st_size > 5000)

    def test_metadata_and_quality(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            project = ProjectModel(
                id="test_meta_proj",
                title="Brain Stop Test",
                config=ProjectConfig(topic="What happens if your brain stops?"),
                project_dir=tmp_dir,
            )
            script = ScriptModel(
                project_id=project.id,
                title="What Happens If Your Brain Stops?",
                hook="Imagine this...",
                target_duration_sec=60,
                total_estimated_duration_sec=60,
                youtube_title_options=["What Happens If Your Brain Stops?", "The Day Your Brain Dies"],
                youtube_description="Full science breakdown of brain shutdown.",
                youtube_tags=["brain", "science", "biology", "facts"],
                sections=[],
            )
            scenes = [
                SceneModel(
                    scene_index=1,
                    duration_sec=10.0,
                    section_ref="hook",
                    narration_text="Imagine your brain stopping.",
                    background_id="bedroom_dark",
                )
            ]

            meta_res = self.meta_gen.generate_all_metadata(project, script, scenes)
            self.assertEqual(meta_res["total_scenes"], 1)
            self.assertTrue((Path(tmp_dir) / "final" / "description.txt").exists())
            self.assertTrue((Path(tmp_dir) / "final" / "chapters.txt").exists())

            # Validate Quality
            q_res = self.validator.validate_project(project, scenes=scenes)
            self.assertTrue(q_res["passed"])


if __name__ == "__main__":
    unittest.main()
