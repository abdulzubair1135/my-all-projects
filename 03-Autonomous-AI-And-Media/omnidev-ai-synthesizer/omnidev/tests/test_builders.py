import unittest
from pathlib import Path
import sys

OMNIDEV_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(OMNIDEV_DIR))

from builders.ppt_builder import PPTBuilder
from builders.image_builder import ImageBuilder
from brains.base_brain import BaseBrain
import config

class MockBrain(BaseBrain):
    def ask(self, prompt: str) -> str:
        if "presentation" in prompt.lower() or "ppt" in prompt.lower():
            return """[
              {"slide_number": 1, "type": "title", "title": "AI in Healthcare", "subtitle": "Modern Innovations", "bullets": []},
              {"slide_number": 2, "type": "content", "title": "Diagnostic AI", "subtitle": "Imaging and Oncology", "bullets": ["Early detection algorithms", "Reduced radiologist burnout", "High sensitivity"]}
            ]"""
        return "Enhanced futuristic digital concept art 8k photorealistic"

    def is_available(self) -> bool:
        return True

class TestBuilders(unittest.TestCase):
    def setUp(self):
        self.mock_brain = MockBrain()

    def test_ppt_generation(self):
        ppt_builder = PPTBuilder(self.mock_brain, config.OUTPUTS_DIR)
        res = ppt_builder.generate_presentation("AI in Healthcare", num_slides=2, filename="test_presentation.pptx")
        self.assertTrue(res["success"])
        self.assertTrue(Path(res["filepath"]).exists())
        self.assertGreater(Path(res["filepath"]).stat().st_size, 1000)

    def test_image_generation(self):
        img_builder = ImageBuilder(self.mock_brain, config.OUTPUTS_DIR)
        res = img_builder.generate_image("Modern high tech robot", filename="test_robot.jpg", width=256, height=256)
        self.assertTrue(res["success"])
        self.assertTrue(Path(res["filepath"]).exists())
        self.assertGreater(Path(res["filepath"]).stat().st_size, 500)

if __name__ == "__main__":
    unittest.main()
