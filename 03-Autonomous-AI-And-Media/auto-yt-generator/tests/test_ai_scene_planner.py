"""
Unit tests for Scene Planner & Storyboard Engine.
"""

import unittest
import uuid
from app.ai.scene_planner import ScenePlannerEngine
from app.ai.script import ScriptEngine
from app.ai.research import ResearchEngine
from app.ai.providers.local import LocalAIProvider
from app.models.project import ProjectModel, ProjectConfig
from app.models.scene import ScenePlan, SceneModel
from app.database import Database
import tempfile
from pathlib import Path


class TestAIScenePlanner(unittest.TestCase):
    def setUp(self):
        self.provider = LocalAIProvider()
        self.res_engine = ResearchEngine(provider=self.provider)
        self.script_engine = ScriptEngine(provider=self.provider)
        self.planner_engine = ScenePlannerEngine(provider=self.provider)

        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_scenes.db"
        self.db = Database(str(self.db_path))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_plan_scenes_structure(self):
        proj = ProjectModel(
            id=str(uuid.uuid4()),
            title="Brain Stop Scenario",
            config=ProjectConfig(
                topic="What happens if the brain stops?",
                language="en",
                duration_seconds=300,
                style="dark_cartoon",
            ),
        )
        research = self.res_engine.research_topic(proj.config.topic)
        script = self.script_engine.generate_script(proj, research)
        scene_plan = self.planner_engine.plan_scenes(proj, script)

        self.assertIsInstance(scene_plan, ScenePlan)
        self.assertEqual(scene_plan.project_id, proj.id)
        self.assertTrue(len(scene_plan.scenes) >= 7)

        first_scene = scene_plan.scenes[0]
        self.assertEqual(first_scene.scene_index, 1)
        self.assertIsNotNone(first_scene.background_id)
        self.assertIsNotNone(first_scene.camera)
        self.assertTrue(first_scene.duration_sec > 0)

    def test_database_scene_persistence(self):
        proj_id = str(uuid.uuid4())
        proj = ProjectModel(
            id=proj_id,
            title="DB Scene Test",
            config=ProjectConfig(topic="Test Topic"),
        )
        self.db.create_project(proj)

        scenes = [
            SceneModel(
                scene_index=1,
                section_ref="hook",
                duration_sec=10.0,
                narration_text="Scene 1 narration",
                background_id="dark_bedroom",
                characters=["main_char"],
                props=["clock"],
            ),
            SceneModel(
                scene_index=2,
                section_ref="setup",
                duration_sec=15.0,
                narration_text="Scene 2 narration",
                background_id="laboratory",
                characters=["main_char"],
                props=["microscope"],
            ),
        ]

        self.db.save_scenes(proj_id, scenes)
        fetched = self.db.get_scenes(proj_id)

        self.assertEqual(len(fetched), 2)
        self.assertEqual(fetched[0].scene_index, 1)
        self.assertEqual(fetched[0].background_id, "dark_bedroom")
        self.assertEqual(fetched[1].scene_index, 2)
        self.assertEqual(fetched[1].background_id, "laboratory")


if __name__ == "__main__":
    unittest.main()
