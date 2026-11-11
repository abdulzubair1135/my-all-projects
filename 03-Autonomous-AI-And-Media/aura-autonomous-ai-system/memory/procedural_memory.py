"""
AURA Procedural Memory Module.
Stores and retrieves step-by-step procedures and standard operating workflows.
"""

import uuid
import datetime
import json
from typing import List, Dict, Any, Optional
from database.db import DatabaseManager, db_manager
from core.logger import setup_logger

logger = setup_logger("ProceduralMemory")

class ProceduralMemory:
    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or db_manager

    def add_procedure(self, name: str, steps: List[str], description: str = "") -> str:
        proc_id = f"proc_{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now().isoformat()
        steps_json = json.dumps(steps)

        self.db.execute_update(
            """INSERT INTO procedures (id, name, description, steps, created_at)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(name) DO UPDATE SET description=excluded.description, steps=excluded.steps""",
            (proc_id, name, description, steps_json, now)
        )
        logger.info(f"Added procedure '{name}' with {len(steps)} steps.")
        return proc_id

    def get_procedure(self, name: str) -> Optional[Dict[str, Any]]:
        rows = self.db.execute_query("SELECT * FROM procedures WHERE name = ?", (name,))
        if not rows:
            return None
        r = rows[0]
        return {
            "id": r["id"],
            "name": r["name"],
            "description": r["description"],
            "steps": json.loads(r["steps"]),
            "created_at": r["created_at"]
        }

procedural_memory = ProceduralMemory()
