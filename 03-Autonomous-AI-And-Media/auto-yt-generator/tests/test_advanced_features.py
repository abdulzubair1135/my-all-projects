"""
Unit tests for Advanced Features (Shorts 9:16, YouTube Uploader, Batch Generator, Character Customizer).
"""

import unittest
import tempfile
from pathlib import Path
from PIL import Image

from app.video.subtitle import SubtitleEngine
from app.upload.youtube_uploader import YouTubeUploader
from app.assets.character import CharacterGenerator
from app.models.project import ProjectModel, ProjectConfig
from app.audio.providers.elevenlabs_provider import ElevenLabsProvider


class TestAdvancedFeatures(unittest.TestCase):
    def setUp(self):
        self.sub_engine = SubtitleEngine()
        self.uploader = YouTubeUploader()
        self.char_gen = CharacterGenerator()
        self.eleven = ElevenLabsProvider()

    def test_shorts_vertical_subtitles(self):
        frame = Image.new("RGBA", (1080, 1920), (20, 20, 30, 255))
        burned = self.sub_engine.burn_subtitle_on_frame(
            frame=frame,
            text="THIS IS A CRAZY YOUTUBE SHORT FACT!",
            is_vertical=True,
        )
        self.assertEqual(burned.size, (1080, 1920))

    def test_character_visual_customizer(self):
        char_custom = self.char_gen.generate_character(
            action="talk",
            expression="curious",
            skin_tone="tan",
            shirt_color="cyber_cyan",
            hair_style="scientist_wild",
            has_glasses=True,
        )
        self.assertEqual(char_custom.size, (512, 768))

    def test_youtube_uploader_simulation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            final_dir = Path(tmp_dir) / "final"
            final_dir.mkdir(parents=True, exist_ok=True)
            (final_dir / "video.mp4").write_text("fake video")

            project = ProjectModel(
                id="test_upload_proj",
                title="Test Video Title",
                config=ProjectConfig(topic="Test Topic"),
                project_dir=tmp_dir,
            )

            res = self.uploader.upload_project_video(project, dry_run=True)
            self.assertIn("status", res)
            self.assertIn("https://youtu.be/", res.get("video_url", ""))


if __name__ == "__main__":
    unittest.main()
