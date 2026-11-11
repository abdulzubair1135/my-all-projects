"""
AURA Skill Memory Module.
Tracks practical and theoretical competency levels across technical domains.
"""

import uuid
import datetime
from typing import List, Dict, Any, Optional
from database.db import DatabaseManager, db_manager
from core.logger import setup_logger

logger = setup_logger("SkillMemory")

class SkillMemory:
    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or db_manager

    def record_skill_level(
        self,
        name: str,
        theoretical_level: str = "medium",
        practical_level: str = "medium"
    ) -> str:
        skill_id = f"skill_{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now().isoformat()

        self.db.execute_update(
            """INSERT INTO skills (id, name, theoretical_level, practical_level, last_used)
               VALUES (?, ?, ?, ?, ?)
               ON CONFLICT(name) DO UPDATE SET
                   theoretical_level=excluded.theoretical_level,
                   practical_level=excluded.practical_level,
                   last_used=excluded.last_used""",
            (skill_id, name, theoretical_level, practical_level, now)
        )
        logger.info(f"Recorded skill '{name}' (theory={theoretical_level}, practice={practical_level})")
        return skill_id

    def get_skill(self, name: str) -> Optional[Dict[str, Any]]:
        rows = self.db.execute_query("SELECT * FROM skills WHERE name = ?", (name,))
        if not rows:
            return None
        r = rows[0]
        return {
            "id": r["id"],
            "name": r["name"],
            "theoretical_level": r["theoretical_level"],
            "practical_level": r["practical_level"],
            "last_used": r["last_used"]
        }

    def list_skills(self) -> List[Dict[str, Any]]:
        rows = self.db.execute_query("SELECT * FROM skills ORDER BY name ASC")
        return [
            {
                "name": r["name"],
                "theoretical_level": r["theoretical_level"],
                "practical_level": r["practical_level"],
                "last_used": r["last_used"]
            } for r in rows
        ]

skill_memory = SkillMemory()
