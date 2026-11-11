"""
AURA Decision Engine Module.
Makes high-level tactical and operational decisions for the autonomous agent loop.
"""

import uuid
import datetime
import json
from typing import Dict, Any, Optional
from database.db import DatabaseManager, db_manager
from core.logger import setup_logger

logger = setup_logger("DecisionEngine")

class DecisionEngine:
    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or db_manager

    def record_decision(
        self,
        task_id: Optional[str],
        reasoning: str,
        choice: str,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        decision_id = f"dec_{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now().isoformat()
        options_json = json.dumps(options or {})

        self.db.execute_update(
            """INSERT INTO decisions (id, task_id, reasoning, choice, options, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (decision_id, task_id, reasoning, choice, options_json, now)
        )
        logger.info(f"Recorded decision [{decision_id}] choice='{choice}': {reasoning}")
        return decision_id

decision_engine = DecisionEngine()
