"""
Unit & Integration Tests for Phase 9 Self-Improvement Engine.
"""

import unittest
from unittest.mock import MagicMock, patch
from evolution.self_improvement import SelfImprovementEngine
from core.controller import controller

class TestPhase9SelfImprovement(unittest.TestCase):
    def setUp(self):
        self.engine = SelfImprovementEngine()

    def test_autonomy_level_gate(self):
        controller.autonomy_level = 1
        res = self.engine.attempt_self_improvement("Optimization proposal", lambda: None)
        self.assertEqual(res["status"], "blocked")
        controller.autonomy_level = 1

    @patch("subprocess.run")
    def test_run_benchmark_mocked(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "================ 40 passed in 1.0s ================"
        mock_run.return_value = mock_proc

        bench = self.engine.run_benchmark()
        self.assertTrue(bench["passed"])
        self.assertEqual(bench["returncode"], 0)

if __name__ == "__main__":
    unittest.main()
