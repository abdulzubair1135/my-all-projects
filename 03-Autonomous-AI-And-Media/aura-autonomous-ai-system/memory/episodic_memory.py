"""
AURA Episodic Memory Module.
Stores and queries past experiences, causes, fixes, and lessons.
"""

import uuid
import datetime
from typing import List, Dict, Any, Optional
from database.db import DatabaseManager, db_manager
from memory.vector_store import VectorStore, vector_store
from core.logger import setup_logger

logger = setup_logger("EpisodicMemory")

class EpisodicMemory:
    def __init__(self, db: Optional[DatabaseManager] = None, store: Optional[VectorStore] = None):
        self.db = db or db_manager
        self.store = store or vector_store
        self._load_index()

    def _load_index(self):
        rows = self.db.execute_query("SELECT * FROM experiences")
        for row in rows:
            text = f"Goal: {row['goal']} | Result: {row['result']} | Lesson: {row['lesson']} | Cause: {row['cause']}"
            self.store.add_item(
                item_id=f"exp_vec_{row['id']}",
                text=text,
                metadata={
                    "exp_id": row["id"],
                    "goal": row["goal"],
                    "result": row["result"],
                    "cause": row["cause"],
                    "fix": row["fix"],
                    "lesson": row["lesson"]
                }
            )
        logger.info(f"Loaded {len(rows)} experiences into Episodic Memory vector index.")

    def add_experience(
        self,
        goal: str,
        result: str,
        lesson: str,
        task_id: Optional[str] = None,
        cause: Optional[str] = None,
        fix: Optional[str] = None
    ) -> str:
        exp_id = f"exp_{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now().isoformat()

        self.db.execute_update(
            """INSERT INTO experiences (id, task_id, goal, result, cause, fix, lesson, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (exp_id, task_id, goal, result, cause, fix, lesson, now)
        )

        text = f"Goal: {goal} | Result: {result} | Lesson: {lesson} | Cause: {cause or 'N/A'}"
        self.store.add_item(
            item_id=f"exp_vec_{exp_id}",
            text=text,
            metadata={
                "exp_id": exp_id,
                "goal": goal,
                "result": result,
                "cause": cause,
                "fix": fix,
                "lesson": lesson
            }
        )

        logger.info(f"Added experience [{exp_id}] result='{result}' lesson='{lesson[:40]}...'")
        return exp_id

    def search_experiences(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.store.search(query, top_k=top_k)
        exps = []
        for item, sim in results:
            if item.item_id.startswith("exp_vec_"):
                exps.append({
                    "id": item.metadata.get("exp_id"),
                    "goal": item.metadata.get("goal"),
                    "result": item.metadata.get("result"),
                    "cause": item.metadata.get("cause"),
                    "fix": item.metadata.get("fix"),
                    "lesson": item.metadata.get("lesson"),
                    "similarity": sim
                })
        return exps

episodic_memory = EpisodicMemory()
