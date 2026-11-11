"""
AURA Controlled Self-Improvement Module.
Handles architectural evolution via Git branch isolation, automated benchmark testing, and safe rollback.
"""

import subprocess
import sys
import uuid
import datetime
from typing import Dict, Any, Optional
from core.controller import controller
from core.logger import setup_logger

logger = setup_logger("SelfImprovementEngine")

class SelfImprovementEngine:
    def __init__(self, repo_dir: str = "."):
        self.repo_dir = repo_dir

    def run_benchmark(self) -> Dict[str, Any]:
        """Runs pytest benchmark suite and measures test status and duration."""
        logger.info("Running system benchmark test suite...")
        start_time = datetime.datetime.now()
        res = subprocess.run([sys.executable, "-m", "pytest"], capture_output=True, text=True, cwd=self.repo_dir)
        duration = (datetime.datetime.now() - start_time).total_seconds()
        
        passed = (res.returncode == 0)
        logger.info(f"Benchmark finished in {duration:.2f}s (Passed: {passed})")
        return {
            "passed": passed,
            "returncode": res.returncode,
            "duration": duration,
            "stdout": res.stdout[:1000]
        }

    def attempt_self_improvement(self, proposal_title: str, modification_fn) -> Dict[str, Any]:
        """
        Safely attempts architectural self-modification:
        1. Checks autonomy level (requires Level 4: Controlled Self-Improvement).
        2. Creates git branch checkpoint.
        3. Runs pre-modification benchmark.
        4. Applies modification_fn.
        5. Runs post-modification benchmark.
        6. Retains candidate if better/passing; rolls back if worse/failing.
        """
        if not controller.check_autonomy_permission(required_level=4):
            logger.warning("Self-improvement attempt blocked by autonomy policy.")
            return {"status": "blocked", "reason": "Requires autonomy level 4 (Controlled Self-Improvement)"}

        branch_name = f"improvement_{uuid.uuid4().hex[:6]}"
        logger.info(f"Initiating self-improvement attempt on git branch '{branch_name}'")

        # 1. Pre-benchmark
        pre_bench = self.run_benchmark()

        # 2. Git Checkpoint Branch
        try:
            subprocess.run(["git", "checkout", "-b", branch_name], check=True, capture_output=True, cwd=self.repo_dir)
        except Exception as e:
            logger.error(f"Git branch checkout failed: {e}")
            return {"status": "error", "reason": f"Git branch creation failed: {e}"}

        # 3. Apply Modification
        try:
            modification_fn()
        except Exception as e:
            logger.error(f"Modification function threw exception: {e}. Rolling back branch.")
            self._rollback(branch_name)
            return {"status": "rollback", "reason": f"Modification exception: {e}"}

        # 4. Post-benchmark
        post_bench = self.run_benchmark()

        # 5. Evaluate & Decide
        if post_bench["passed"] and post_bench["duration"] <= pre_bench["duration"] * 1.25:
            logger.info(f"Self-improvement SUCCESSFUL for '{proposal_title}'. Retaining candidate branch.")
            subprocess.run(["git", "checkout", "main"], capture_output=True, cwd=self.repo_dir)
            return {
                "status": "retained",
                "branch": branch_name,
                "pre_duration": pre_bench["duration"],
                "post_duration": post_bench["duration"]
            }
        else:
            logger.warning(f"Self-improvement DEGRADED or FAILED for '{proposal_title}'. Rolling back.")
            self._rollback(branch_name)
            return {
                "status": "rollback",
                "branch": branch_name,
                "reason": "Post-benchmark failed or degraded performance."
            }

    def _rollback(self, branch_name: str):
        try:
            subprocess.run(["git", "checkout", "main"], capture_output=True, cwd=self.repo_dir)
            subprocess.run(["git", "branch", "-D", branch_name], capture_output=True, cwd=self.repo_dir)
            logger.info(f"Successfully rolled back and deleted candidate branch '{branch_name}'")
        except Exception as e:
            logger.error(f"Failed during git rollback: {e}")

self_improvement_engine = SelfImprovementEngine()
