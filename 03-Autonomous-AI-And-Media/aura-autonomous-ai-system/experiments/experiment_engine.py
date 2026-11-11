"""
AURA Experiment Engine Module.
Formulates hypotheses, runs practical coding experiments, verifies outputs, and stores lessons in SQLite.
"""

import uuid
import datetime
from typing import Dict, Any, Optional
from coding.sandbox import CodeSandbox, code_sandbox
from database.db import DatabaseManager, db_manager
from core.logger import setup_logger

logger = setup_logger("ExperimentEngine")

class ExperimentEngine:
    def __init__(self, sandbox_inst: Optional[CodeSandbox] = None, db: Optional[DatabaseManager] = None):
        self.sandbox = sandbox_inst or code_sandbox
        self.db = db or db_manager

    def run_experiment(
        self,
        goal: str,
        hypothesis: str,
        code: str,
        method: str = "python_sandbox",
        expected_output: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs a practical code experiment, evaluates result, and stores record in SQLite experiments table.
        """
        exp_id = f"exp_{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now().isoformat()
        logger.info(f"Running experiment [{exp_id}] goal='{goal}'")

        # Execute code in sandbox
        exec_res = self.sandbox.execute_python_code(code)
        stdout = exec_res.get("stdout", "")
        stderr = exec_res.get("stderr", "")
        status = exec_res.get("status", "error")

        if status == "success":
            if expected_output and expected_output not in stdout:
                result_str = "FAIL"
                lesson = f"Code executed but output did not contain expected text '{expected_output}'."
                solution = "Adjust logic or output formatting."
            else:
                result_str = "PASS"
                lesson = f"Experiment succeeded. Verified hypothesis: {hypothesis}"
                solution = "N/A"
        else:
            result_str = "ERROR"
            lesson = f"Experiment encountered execution error: {stderr[:100]}"
            solution = f"Fix exception: {stderr[:100]}"

        # Store in SQLite experiments table
        self.db.execute_update(
            """INSERT INTO experiments (experiment_id, goal, hypothesis, method, code, input, output, result, error, solution, lesson, confidence, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (exp_id, goal, hypothesis, method, code, expected_output or "", stdout, result_str, stderr, solution, lesson, 0.9 if result_str == "PASS" else 0.4, now)
        )

        logger.info(f"Experiment [{exp_id}] finished with result: '{result_str}'")
        return {
            "experiment_id": exp_id,
            "goal": goal,
            "hypothesis": hypothesis,
            "result": result_str,
            "output": stdout,
            "error": stderr,
            "lesson": lesson
        }

experiment_engine = ExperimentEngine()
