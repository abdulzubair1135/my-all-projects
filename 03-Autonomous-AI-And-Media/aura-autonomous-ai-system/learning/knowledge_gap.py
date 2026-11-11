"""
AURA Knowledge Gap Engine Module.
Tracks, prioritizes, and resolves autonomous knowledge gaps.
"""

import uuid
import datetime
from typing import List, Dict, Any, Optional
from database.db import DatabaseManager, db_manager
from core.logger import setup_logger

logger = setup_logger("KnowledgeGapEngine")

class KnowledgeGapEngine:
    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or db_manager

    def add_gap(self, topic: str, rationale: str = "", priority: int = 1) -> str:
        gap_id = f"gap_{uuid.uuid4().hex[:8]}"
        self.db.execute_update(
            """INSERT INTO knowledge_gaps (id, topic, rationale, priority, status)
               VALUES (?, ?, ?, ?, ?)""",
            (gap_id, topic, rationale, priority, "open")
        )
        logger.info(f"Added knowledge gap [{gap_id}] topic='{topic}'")
        return gap_id

    def get_open_gaps(self, limit: int = 5) -> List[Dict[str, Any]]:
        rows = self.db.execute_query(
            "SELECT * FROM knowledge_gaps WHERE status = 'open' ORDER BY priority DESC LIMIT ?",
            (limit,)
        )
        return [
            {
                "id": r["id"],
                "topic": r["topic"],
                "rationale": r["rationale"],
                "priority": r["priority"],
                "status": r["status"]
            } for r in rows
        ]

    def mark_resolved(self, gap_id: str):
        self.db.execute_update(
            "UPDATE knowledge_gaps SET status = 'resolved' WHERE id = ?",
            (gap_id,)
        )
        logger.info(f"Marked knowledge gap [{gap_id}] as resolved.")

knowledge_gap_engine = KnowledgeGapEngine()
