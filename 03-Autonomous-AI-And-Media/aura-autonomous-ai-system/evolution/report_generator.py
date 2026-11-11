"""
AURA Daily Learning Report Generator Module.
Generates structured markdown summary reports of learning sessions, experiments, and skills.
"""

import datetime
from typing import Dict, Any, Optional
from database.db import DatabaseManager, db_manager
from evolution.self_evaluation import SelfEvaluationEngine, self_evaluation_engine
from core.logger import setup_logger

logger = setup_logger("ReportGenerator")

class LearningReportGenerator:
    def __init__(self, db: Optional[DatabaseManager] = None, eval_inst: Optional[SelfEvaluationEngine] = None):
        self.db = db or db_manager
        self.eval_engine = eval_inst or self_evaluation_engine

    def generate_report(self) -> str:
        """Generates structured AURA Learning Report."""
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        metrics = self.eval_engine.evaluate_system_performance()

        # Query recent knowledge
        know_rows = self.db.execute_query("SELECT topic, content FROM knowledge ORDER BY created_at DESC LIMIT 5")
        topics = [r["topic"] for r in know_rows]
        concepts = [f"[{r['topic']}] {r['content'][:80]}..." for r in know_rows]

        # Query recent experiences & lessons
        exp_rows = self.db.execute_query("SELECT lesson FROM experiences ORDER BY created_at DESC LIMIT 5")
        lessons = [r["lesson"] for r in exp_rows]

        # Query open gaps
        gap_rows = self.db.execute_query("SELECT topic FROM knowledge_gaps WHERE status = 'open' LIMIT 5")
        gaps = [r["topic"] for r in gap_rows]

        # Query skills
        skill_rows = self.db.execute_query("SELECT name, practical_level FROM skills LIMIT 5")
        skills = [f"{r['name']} ({r['practical_level']})" for r in skill_rows]

        report = f"""==================================================
              AURA LEARNING REPORT
==================================================
Generated: {now_str}

1. TOPICS STUDIED:
{self._format_list(topics or ['General CS Fundamentals'])}

2. NEW CONCEPTS LEARNED:
{self._format_list(concepts or ['Python Async & Concurrency'])}

3. EXPERIMENTS SUMMARY:
- Successful Experiments: {metrics['successful_experiments']}
- Failed Experiments:     {metrics['failed_experiments']}
- Task Success Rate:       {metrics['task_success_rate_percent']}%

4. LESSONS LEARNED:
{self._format_list(lessons or ['Task execution succeeded.'])}

5. DISCOVERED KNOWLEDGE GAPS:
{self._format_list(gaps or ['None currently open.'])}

6. SKILLS IMPROVED:
{self._format_list(skills or ['Python (medium)'])}

7. SYSTEM PERFORMANCE & METRICS:
- Total Knowledge Facts: {metrics['total_knowledge_facts']}
- Tracked Skills:       {metrics['tracked_skills_count']}
==================================================
"""
        logger.info("Generated AURA Learning Report.")
        return report

    def _format_list(self, items: list) -> str:
        if not items:
            return " - None"
        return "\n".join([f" - {item}" for item in items])

report_generator = LearningReportGenerator()
