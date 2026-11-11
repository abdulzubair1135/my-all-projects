"""
Unit & Integration Tests for Phase 7 Coding Sandbox and Experiment Engine.
"""

import unittest
import tempfile
from pathlib import Path
from database.db import DatabaseManager
from coding.sandbox import CodeSandbox
from experiments.experiment_engine import ExperimentEngine

class TestPhase7CodingExperiments(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_phase7.db"
        self.db = DatabaseManager(self.db_path)

        self.sandbox = CodeSandbox()
        self.exp_engine = ExperimentEngine(sandbox_inst=self.sandbox, db=self.db)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sandbox_valid_python(self):
        code = "print('AURA Sandbox Test OK')"
        res = self.sandbox.execute_python_code(code)
        self.assertEqual(res["status"], "success")
        self.assertIn("AURA Sandbox Test OK", res["stdout"])

    def test_sandbox_error_python(self):
        code = "raise ValueError('Test Exception')"
        res = self.sandbox.execute_python_code(code)
        self.assertEqual(res["status"], "error")
        self.assertIn("ValueError", res["stderr"])

    def test_experiment_pass(self):
        code = "import json\nprint(json.dumps({'status': 'ok'}))"
        res = self.exp_engine.run_experiment(
            goal="Test JSON serialization",
            hypothesis="Python json module encodes dict properly",
            code=code,
            expected_output="status"
        )
        self.assertEqual(res["result"], "PASS")

        # Verify recorded in DB
        rows = self.db.execute_query("SELECT * FROM experiments WHERE result = 'PASS'")
        self.assertEqual(len(rows), 1)

if __name__ == "__main__":
    unittest.main()
