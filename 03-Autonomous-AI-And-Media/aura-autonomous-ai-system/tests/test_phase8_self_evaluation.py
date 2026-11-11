"""
Unit & Integration Tests for Phase 8 Self-Evaluation and Learning Report System.
"""

import unittest
import tempfile
from pathlib import Path
from database.db import DatabaseManager
from evolution.self_evaluation import SelfEvaluationEngine
from evolution.report_generator import LearningReportGenerator

class TestPhase8SelfEvaluation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_phase8.db"
        self.db = DatabaseManager(self.db_path)

        self.eval_engine = SelfEvaluationEngine(db=self.db)
        self.reporter = LearningReportGenerator(db=self.db, eval_inst=self.eval_engine)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_self_evaluation_metrics(self):
        # Insert sample task and experiment
        self.db.execute_update(
            "INSERT INTO tasks (task_id, title, status, created_at, updated_at) VALUES ('t1', 'Task 1', 'completed', 'now', 'now')"
        )
        self.db.execute_update(
            "INSERT INTO experiments (experiment_id, goal, result, timestamp) VALUES ('e1', 'Goal 1', 'PASS', 'now')"
        )

        metrics = self.eval_engine.evaluate_system_performance()
        self.assertEqual(metrics["completed_tasks"], 1)
        self.assertEqual(metrics["successful_experiments"], 1)
        self.assertEqual(metrics["task_success_rate_percent"], 100.0)

    def test_learning_report_generation(self):
        report = self.reporter.generate_report()
        self.assertIn("AURA LEARNING REPORT", report)
        self.assertIn("TOPICS STUDIED", report)
        self.assertIn("EXPERIMENTS SUMMARY", report)

if __name__ == "__main__":
    unittest.main()
