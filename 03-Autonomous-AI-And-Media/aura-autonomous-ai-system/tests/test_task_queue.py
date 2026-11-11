"""
Unit tests for AURA Task Queue module.
"""

import unittest
import tempfile
from pathlib import Path
from database.db import DatabaseManager
from core.task_queue import TaskQueue

class TestTaskQueue(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_queue.db"
        self.db = DatabaseManager(self.db_path)
        self.queue = TaskQueue(db=self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_pop_priority(self):
        t1 = self.queue.add_task("Low Priority Task", "desc", priority=1)
        t2 = self.queue.add_task("High Priority Task", "desc", priority=5)

        popped = self.queue.pop_next_task()
        self.assertIsNotNone(popped)
        self.assertEqual(popped.task_id, t2.task_id)
        self.assertEqual(popped.status, "in_progress")

        popped_next = self.queue.pop_next_task()
        self.assertIsNotNone(popped_next)
        self.assertEqual(popped_next.task_id, t1.task_id)

    def test_update_status(self):
        t = self.queue.add_task("Task to complete", "desc")
        self.queue.update_task_status(t.task_id, "completed", result="Done")

        pending = self.queue.get_pending_tasks()
        self.assertEqual(len(pending), 0)

if __name__ == "__main__":
    unittest.main()
