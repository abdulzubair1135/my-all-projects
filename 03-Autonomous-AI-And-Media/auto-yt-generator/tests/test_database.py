"""
Unit tests for SQLite database operations.
"""

import os
import uuid
import unittest
import tempfile
from pathlib import Path
from app.database import Database
from app.models.project import ProjectModel, ProjectConfig
from app.constants import PipelineStage


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_auto_yt.db"
        self.db = Database(str(self.db_path))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_and_get_project(self):
        proj_id = str(uuid.uuid4())
        cfg = ProjectConfig(
            topic="Test Topic",
            language="hi",
            duration_seconds=120,
            style="dark_cartoon",
        )
        proj = ProjectModel(
            id=proj_id,
            title="Test Project",
            config=cfg,
            current_stage=PipelineStage.QUEUED,
            progress_percent=0.0,
        )

        created = self.db.create_project(proj)
        self.assertEqual(created.id, proj_id)

        fetched = self.db.get_project(proj_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.config.topic, "Test Topic")
        self.assertEqual(fetched.config.language, "hi")

    def test_list_and_delete_project(self):
        proj_id = str(uuid.uuid4())
        proj = ProjectModel(
            id=proj_id,
            title="To Delete",
            config=ProjectConfig(topic="Delete Me"),
            current_stage=PipelineStage.QUEUED,
        )
        self.db.create_project(proj)

        summaries = self.db.list_projects()
        self.assertTrue(any(s.id == proj_id for s in summaries))

        deleted = self.db.delete_project(proj_id)
        self.assertTrue(deleted)

        fetched = self.db.get_project(proj_id)
        self.assertIsNone(fetched)


if __name__ == "__main__":
    unittest.main()
