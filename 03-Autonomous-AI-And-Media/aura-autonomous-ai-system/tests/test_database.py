"""
Unit tests for AURA Database Manager module.
"""

import unittest
import tempfile
from pathlib import Path
from database.db import DatabaseManager

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_aura.db"
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_tables_created(self):
        tables = [
            "tasks", "goals", "knowledge", "sources", "experiences",
            "experiments", "skills", "errors", "decisions", "actions",
            "sessions", "projects", "learning_sessions", "knowledge_gaps"
        ]
        rows = self.db.execute_query("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [r["name"] for r in rows]

        for table in tables:
            self.assertIn(table, existing_tables, f"Table '{table}' should exist in SQLite database")

    def test_insert_and_query(self):
        self.db.execute_update(
            "INSERT INTO goals (goal_id, title, description, status, priority, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("g1", "Test Goal", "Description", "pending", 1, "now", "now")
        )
        rows = self.db.execute_query("SELECT * FROM goals WHERE goal_id = ?", ("g1",))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["title"], "Test Goal")

if __name__ == "__main__":
    unittest.main()
