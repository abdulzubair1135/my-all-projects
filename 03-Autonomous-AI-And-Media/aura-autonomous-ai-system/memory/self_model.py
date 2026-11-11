"""
AURA Self Model Module.
Provides self-awareness of system capabilities, known topics, knowledge gaps, and mistake patterns.
"""

from typing import List, Dict, Any, Optional
from database.db import DatabaseManager, db_manager
from tools.tool_registry import ToolRegistry, tool_registry
from core.logger import setup_logger

logger = setup_logger("SelfModel")

class SelfModel:
    def __init__(self, db: Optional[DatabaseManager] = None, registry: Optional[ToolRegistry] = None):
        self.db = db or db_manager
        self.registry = registry or tool_registry

    def get_self_summary(self) -> Dict[str, Any]:
        """Returns structured self-awareness representation."""
        # 1. Known topics
        know_rows = self.db.execute_query("SELECT DISTINCT topic FROM knowledge LIMIT 10")
        known_topics = [r["topic"] for r in know_rows]

        # 2. Knowledge gaps (what it does not know)
        gap_rows = self.db.execute_query("SELECT topic FROM knowledge_gaps WHERE status = 'open' LIMIT 10")
        unknown_topics = [r["topic"] for r in gap_rows]

        # 3. Available vs unavailable tools
        available_tools = list(self.registry.list_tools().keys())

        # 4. Common mistake patterns / failed experiences
        fail_rows = self.db.execute_query("SELECT cause, count(*) as cnt FROM experiences WHERE result = 'FAILURE' GROUP BY cause ORDER BY cnt DESC LIMIT 5")
        frequent_mistakes = [f"{r['cause']} (count: {r['cnt']})" for r in fail_rows if r["cause"]]

        # 5. Practiced skills
        skill_rows = self.db.execute_query("SELECT name, practical_level FROM skills ORDER BY last_used DESC LIMIT 10")
        practiced_skills = [f"{r['name']} ({r['practical_level']})" for r in skill_rows]

        return {
            "known_topics": known_topics,
            "knowledge_gaps": unknown_topics,
            "available_tools": available_tools,
            "frequent_mistakes": frequent_mistakes,
            "practiced_skills": practiced_skills
        }

self_model = SelfModel()
