"""
AURA Self Evaluation Engine Module.
Analyzes performance metrics, task success rates, experiment outcomes, and system health.
"""

from typing import Dict, Any, Optional
from database.db import DatabaseManager, db_manager
from core.logger import setup_logger

logger = setup_logger("SelfEvaluationEngine")

class SelfEvaluationEngine:
    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or db_manager

    def evaluate_system_performance(self) -> Dict[str, Any]:
        """
        Computes system performance metrics across completed tasks, experiments, and memory facts.
        """
        logger.info("Computing AURA self-evaluation metrics...")

        # Tasks stats
        completed_tasks = self.db.execute_query("SELECT count(*) as cnt FROM tasks WHERE status = 'completed'")[0]["cnt"]
        failed_tasks = self.db.execute_query("SELECT count(*) as cnt FROM tasks WHERE status = 'failed'")[0]["cnt"]
        total_tasks = completed_tasks + failed_tasks
        task_success_rate = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 100.0

        # Experiments stats
        pass_exp = self.db.execute_query("SELECT count(*) as cnt FROM experiments WHERE result = 'PASS'")[0]["cnt"]
        fail_exp = self.db.execute_query("SELECT count(*) as cnt FROM experiments WHERE result IN ('FAIL', 'ERROR')")[0]["cnt"]
        total_exp = pass_exp + fail_exp
        exp_success_rate = (pass_exp / total_exp * 100.0) if total_exp > 0 else 100.0

        # Knowledge stats
        total_facts = self.db.execute_query("SELECT count(*) as cnt FROM knowledge")[0]["cnt"]
        total_gaps = self.db.execute_query("SELECT count(*) as cnt FROM knowledge_gaps WHERE status = 'open'")[0]["cnt"]
        total_skills = self.db.execute_query("SELECT count(*) as cnt FROM skills")[0]["cnt"]

        metrics = {
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "task_success_rate_percent": round(task_success_rate, 2),
            "successful_experiments": pass_exp,
            "failed_experiments": fail_exp,
            "exp_success_rate_percent": round(exp_success_rate, 2),
            "total_knowledge_facts": total_facts,
            "open_knowledge_gaps": total_gaps,
            "tracked_skills_count": total_skills
        }

        logger.info(f"Self-Evaluation computed: Task Success Rate = {metrics['task_success_rate_percent']}%, Exp Success Rate = {metrics['exp_success_rate_percent']}%")
        return metrics

self_evaluation_engine = SelfEvaluationEngine()
