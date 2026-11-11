"""
Unit tests for AI Script Generation Engine.
"""

import unittest
import uuid
from app.ai.script import ScriptEngine
from app.ai.research import ResearchEngine
from app.ai.providers.local import LocalAIProvider
from app.models.project import ProjectModel, ProjectConfig
from app.models.script import ScriptModel


class TestAIScript(unittest.TestCase):
    def setUp(self):
        self.provider = LocalAIProvider()
        self.res_engine = ResearchEngine(provider=self.provider)
        self.script_engine = ScriptEngine(provider=self.provider)

    def test_generate_script(self):
        proj = ProjectModel(
            id=str(uuid.uuid4()),
            title="Sleep Deprivation",
            config=ProjectConfig(
                topic="What happens if humans stop sleeping?",
                language="en",
                duration_seconds=300,
                style="dark_cartoon",
            ),
        )
        research = self.res_engine.research_topic(proj.config.topic)
        script = self.script_engine.generate_script(proj, research)

        self.assertIsInstance(script, ScriptModel)
        self.assertEqual(len(script.sections), 7)
        section_types = [s.section_type for s in script.sections]
        self.assertEqual(
            section_types,
            ["hook", "setup", "question", "explanation", "escalation", "surprising_fact", "conclusion"],
        )
        self.assertTrue(len(script.youtube_title_options) > 0)
        self.assertTrue(len(script.youtube_tags) > 0)


if __name__ == "__main__":
    unittest.main()
