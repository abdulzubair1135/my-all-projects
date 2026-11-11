"""
End-to-End Integration Test for Phase 1 Cognitive Loop.
Tests goal setting, task planning, task execution, critic evaluation, and reflection recording.
"""

import unittest
import tempfile
from pathlib import Path
from database.db import DatabaseManager
from brain.ollama_backend import MockBackend
from brain.model_adapter import ModelAdapter
from core.planner import Planner
from core.task_queue import TaskQueue
from core.executor import Executor
from core.critic import Critic
from core.reflection import Reflection
from core.context import ContextManager
from core.controller import Controller
from core.agent import Agent

class TestAgentPhase1(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_phase1_agent.db"
        self.db = DatabaseManager(self.db_path)

        self.mock_backend = MockBackend()
        self.adapter = ModelAdapter(backend=self.mock_backend)

        self.queue = TaskQueue(db=self.db)
        self.planner = Planner(adapter=self.adapter)
        self.executor = Executor(adapter=self.adapter, db=self.db)
        self.critic = Critic(adapter=self.adapter)
        self.reflection = Reflection(adapter=self.adapter, db=self.db)
        self.context = ContextManager(db=self.db)
        self.controller = Controller()

        self.agent = Agent(
            planner_inst=self.planner,
            queue_inst=self.queue,
            executor_inst=self.executor,
            critic_inst=self.critic,
            reflection_inst=self.reflection,
            context_inst=self.context,
            controller_inst=self.controller,
            db_inst=self.db
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_full_phase1_loop(self):
        # 1. Set goal and plan tasks
        goal_id = self.agent.set_goal("Learn Python Socket Programming", "Build basic TCP server client")
        self.assertIsNotNone(goal_id)

        pending = self.queue.get_pending_tasks()
        self.assertGreaterEqual(len(pending), 1)

        # 2. Run steps until completed
        results = self.agent.run_loop(max_steps=5)
        self.assertGreaterEqual(len(results), 1)

        # 3. Verify SQLite DB state
        # Check tasks completed
        tasks_rows = self.db.execute_query("SELECT * FROM tasks WHERE status = 'completed'")
        self.assertGreaterEqual(len(tasks_rows), 1)

        # Check actions recorded
        actions_rows = self.db.execute_query("SELECT * FROM actions")
        self.assertGreaterEqual(len(actions_rows), 1)

        # Check experiences recorded
        exp_rows = self.db.execute_query("SELECT * FROM experiences")
        self.assertGreaterEqual(len(exp_rows), 1)
        self.assertEqual(exp_rows[0]["result"], "SUCCESS")

if __name__ == "__main__":
    unittest.main()
