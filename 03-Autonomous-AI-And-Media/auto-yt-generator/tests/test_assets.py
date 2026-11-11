"""
Unit tests for Procedural 2D Character, Background, and Prop Assets Engine.
"""

import unittest
import tempfile
from pathlib import Path
from PIL import Image
from app.assets.character import CharacterGenerator
from app.assets.background import BackgroundGenerator
from app.assets.props import PropGenerator
from app.assets.manager import AssetManager
from app.models.scene import ScenePlan, SceneModel, SceneAction, CameraConfig


class TestAssetsEngine(unittest.TestCase):
    def setUp(self):
        self.char_gen = CharacterGenerator(width=512, height=768)
        self.bg_gen = BackgroundGenerator(width=1920, height=1080)
        self.prop_gen = PropGenerator()

    def test_character_poses_and_mouth(self):
        # 1. Idle Pose
        idle_img = self.char_gen.generate_character(action="idle", expression="neutral", mouth_state="idle")
        self.assertEqual(idle_img.size, (512, 768))
        self.assertEqual(idle_img.mode, "RGBA")

        # 2. Sleeping Pose
        sleep_img = self.char_gen.generate_character(action="sleep", expression="neutral")
        self.assertEqual(sleep_img.size, (512, 768))

        # 3. Dead Pose (X-Eyes)
        dead_img = self.char_gen.generate_character(action="dead", expression="sad")
        self.assertEqual(dead_img.size, (512, 768))

        # 4. Scared / Shocked Pose with open mouth
        scared_img = self.char_gen.generate_character(action="scared", expression="shocked", mouth_state="open")
        self.assertEqual(scared_img.size, (512, 768))

    def test_procedural_backgrounds_1080p(self):
        background_ids = [
            "bedroom_dark",
            "brain_interior",
            "laboratory_microscopic",
            "cellular_landscape",
            "emergency_room_dark",
            "abstract_space",
            "night_landscape_stars",
        ]
        for bg_id in background_ids:
            img = self.bg_gen.generate_background(bg_id)
            self.assertEqual(img.size, (1920, 1080), f"Failed dimensions for {bg_id}")
            self.assertEqual(img.mode, "RGBA", f"Failed mode for {bg_id}")

    def test_procedural_props(self):
        prop_ids = ["clock", "microscope", "bed", "energy_beam", "isolated_glow"]
        for p_id in prop_ids:
            img = self.prop_gen.generate_prop(p_id, width=300, height=300)
            self.assertEqual(img.size, (300, 300))
            self.assertEqual(img.mode, "RGBA")

    def test_asset_manager_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            manager = AssetManager(assets_dir=tmp_dir)

            plan = ScenePlan(
                project_id="test-proj-asset",
                total_scenes=2,
                total_duration_sec=30.0,
                scenes=[
                    SceneModel(
                        scene_index=1,
                        duration_sec=15.0,
                        background_id="bedroom_dark",
                        characters=["char_main"],
                        props=["clock"],
                        actions=[
                            SceneAction(
                                entity_id="char_main",
                                action="sleep",
                                expression="neutral",
                                duration_sec=15.0,
                            )
                        ],
                    ),
                    SceneModel(
                        scene_index=2,
                        duration_sec=15.0,
                        background_id="brain_interior",
                        characters=["char_neuron"],
                        props=["energy_beam"],
                        actions=[
                            SceneAction(
                                entity_id="char_neuron",
                                action="talk",
                                expression="confused",
                                duration_sec=15.0,
                            )
                        ],
                    ),
                ],
            )

            result = manager.generate_all_scene_assets(plan, project_dir=tmp_dir)
            self.assertEqual(len(result["backgrounds"]), 2)
            self.assertEqual(len(result["characters"]), 2)
            self.assertEqual(len(result["props"]), 2)

            for bg in result["backgrounds"]:
                self.assertTrue(Path(bg).exists())
            for ch in result["characters"]:
                self.assertTrue(Path(ch).exists())
            for pr in result["props"]:
                self.assertTrue(Path(pr).exists())


if __name__ == "__main__":
    unittest.main()
