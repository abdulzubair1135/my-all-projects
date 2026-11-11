"""
AURA Semantic Memory Module.
Stores and retrieves general knowledge facts with vector index integration.
"""

import uuid
import datetime
import json
from typing import List, Dict, Any, Optional
from database.db import DatabaseManager, db_manager
from memory.vector_store import VectorStore, vector_store
from core.logger import setup_logger

logger = setup_logger("SemanticMemory")

class SemanticMemory:
    def __init__(self, db: Optional[DatabaseManager] = None, store: Optional[VectorStore] = None):
        self.db = db or db_manager
        self.store = store or vector_store
        self._load_index()

    def _load_index(self):
        """Loads existing knowledge entries from SQLite into vector index."""
        rows = self.db.execute_query("SELECT * FROM knowledge")
        for row in rows:
            index_text = f"{row['topic']} {row['topic']} {row['content'][:200]}"
            self.store.add_item(
                item_id=row["id"],
                text=index_text,
                metadata={
                    "topic": row["topic"],
                    "content": row["content"],
                    "source": row["source"],
                    "confidence": row["confidence"]
                }
            )
        logger.info(f"Loaded {len(rows)} facts into Semantic Memory vector index.")

    def add_fact(self, topic: str, content: str, source: str = "internal", confidence: float = 1.0) -> str:
        fact_id = f"know_{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now().isoformat()

        self.db.execute_update(
            """INSERT INTO knowledge (id, topic, content, source, confidence, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (fact_id, topic, content, source, confidence, now)
        )

        index_text = f"{topic} {topic} {content[:200]}"
        self.store.add_item(item_id=fact_id, text=index_text, metadata={
            "topic": topic,
            "content": content,
            "source": source,
            "confidence": confidence
        })

        logger.info(f"Added semantic fact [{fact_id}] topic='{topic}'")
        return fact_id

    def search_facts(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        results = self.store.search(query, top_k=top_k, threshold=0.1)
        facts = []
        for item, sim in results:
            facts.append({
                "id": item.item_id,
                "topic": item.metadata.get("topic"),
                "content": item.metadata.get("content"),
                "source": item.metadata.get("source"),
                "confidence": item.metadata.get("confidence"),
                "similarity": sim
            })
        return facts

semantic_memory = SemanticMemory()
