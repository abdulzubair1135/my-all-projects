"""
AURA Knowledge Graph Module.
Manages SQLite-based relational triples and concept hierarchy traversals.
"""

import uuid
import datetime
from typing import List, Dict, Any, Optional
from database.db import DatabaseManager, db_manager
from core.logger import setup_logger

logger = setup_logger("KnowledgeGraph")

class KnowledgeGraph:
    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or db_manager

    def add_relation(
        self,
        subject: str,
        predicate: str,
        object_concept: str,
        confidence: float = 1.0
    ) -> str:
        rel_id = f"rel_{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now().isoformat()

        self.db.execute_update(
            """INSERT INTO knowledge_relations (id, subject, predicate, object, confidence, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (rel_id, subject, predicate, object_concept, confidence, now)
        )
        logger.info(f"Added relation: ({subject}) --[{predicate}]--> ({object_concept})")
        return rel_id

    def get_subtopics(self, parent_concept: str) -> List[str]:
        rows = self.db.execute_query(
            "SELECT object FROM knowledge_relations WHERE subject = ? AND predicate IN ('has_subtopic', 'includes', 'child_of')",
            (parent_concept,)
        )
        return [r["object"] for r in rows]

    def get_prerequisites(self, concept: str) -> List[str]:
        rows = self.db.execute_query(
            "SELECT object FROM knowledge_relations WHERE subject = ? AND predicate IN ('requires', 'prerequisite')",
            (concept,)
        )
        return [r["object"] for r in rows]

    def get_relations(self, concept: str) -> List[Dict[str, Any]]:
        rows = self.db.execute_query(
            "SELECT * FROM knowledge_relations WHERE subject = ? OR object = ?",
            (concept, concept)
        )
        return [
            {
                "id": r["id"],
                "subject": r["subject"],
                "predicate": r["predicate"],
                "object": r["object"],
                "confidence": r["confidence"]
            } for r in rows
        ]

knowledge_graph = KnowledgeGraph()
