"""
Unit & Integration Tests for Phase 4 Curiosity & Autonomous Scheduler System.
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
from learning.knowledge_gap import KnowledgeGapEngine
from learning.curiosity import CuriosityEngine
from scheduler.scheduler import AutonomousScheduler

class TestPhase4CuriosityScheduler(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_phase4.db"
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

        self.gaps = KnowledgeGapEngine(db=self.db)
        self.curiosity = CuriosityEngine(
            gap_inst=self.gaps,
            adapter=self.adapter
        )

        self.scheduler = AutonomousScheduler(
            agent_inst=self.agent,
            queue_inst=self.queue,
            curiosity_inst=self.curiosity,
            gap_inst=self.gaps
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_knowledge_gap_lifecycle(self):
        gap_id = self.gaps.add_gap("WebSockets Protocols", rationale="Need socket knowledge", priority=3)
        open_gaps = self.gaps.get_open_gaps()
        self.assertEqual(len(open_gaps), 1)
        self.assertEqual(open_gaps[0]["topic"], "WebSockets Protocols")

        self.gaps.mark_resolved(gap_id)
        open_gaps_after = self.gaps.get_open_gaps()
        self.assertEqual(len(open_gaps_after), 0)

    def test_curiosity_proposal_from_gap(self):
        self.gaps.add_gap("TCP Window Scaling", priority=5)
        proposal = self.curiosity.propose_next_learning_topic()
        self.assertEqual(proposal["topic"], "TCP Window Scaling")
        self.assertEqual(proposal["source"], "knowledge_gap")

    def test_autonomous_scheduler_cycle_with_no_user_task(self):
        # 1. Add knowledge gap
        self.gaps.add_gap("AsyncIO Event Loops", rationale="Understand event loops", priority=2)

        # 2. Run autonomous cycle when queue is completely empty
        pending_before = self.queue.get_pending_tasks()
        self.assertEqual(len(pending_before), 0)

        step_result = self.scheduler.run_autonomous_cycle()

        self.assertIsNotNone(step_result)
        self.assertIn("task_id", step_result)
        self.assertEqual(step_result["execution"]["status"], "success")

        # Verify gap was resolved
        open_gaps = self.gaps.get_open_gaps()
        self.assertEqual(len(open_gaps), 0)

if __name__ == "__main__":
    unittest.main()
