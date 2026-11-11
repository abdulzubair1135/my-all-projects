"""
Unit tests for Pipeline Orchestrator and Caching.
"""

import uuid
import unittest
import tempfile
from pathlib import Path
from app.models.project import ProjectModel, ProjectConfig
from app.constants import PipelineStage, StageStatus
from app.pipeline.stages import BaseStage, StageContext, StageResult
from app.pipeline.pipeline import PipelineOrchestrator
from app.pipeline.cache import CacheManager


class MockSuccessStage(BaseStage):
    def __init__(self):
        super().__init__(PipelineStage.RESEARCHING)

    def execute(self, context: StageContext) -> StageResult:
        return StageResult(
            success=True,
            stage=self.stage_enum,
            data={"facts": ["Fact 1", "Fact 2"]},
        )


class TestPipeline(unittest.TestCase):
    def test_pipeline_execution(self):
        orchestrator = PipelineOrchestrator()
        orchestrator.register_stage(MockSuccessStage())

        proj = ProjectModel(
            id=str(uuid.uuid4()),
            title="Pipeline Test",
            config=ProjectConfig(topic="Testing Pipeline"),
        )

        job = orchestrator.run_pipeline(proj)
        self.assertEqual(job.status, StageStatus.COMPLETED)
        self.assertEqual(job.current_stage, PipelineStage.COMPLETED)
        self.assertEqual(len(job.stage_logs), 1)
        self.assertEqual(job.stage_logs[0].status, StageStatus.COMPLETED)

    def test_cache_hashing(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            db_file = str(Path(tmp_dir) / "cache_test.db")
            cache = CacheManager(db_path=db_file)

            key = cache.generate_key("script", {"topic": "Black Holes", "duration": 300})
            self.assertIsInstance(key, str)
            self.assertEqual(len(key), 64)  # SHA256 hex string

            cache.set(key, "script", {"result": "Calculated script"})
            cached_data = cache.get(key)
            self.assertIsNotNone(cached_data)
            self.assertEqual(cached_data["result"], "Calculated script")


if __name__ == "__main__":
    unittest.main()
