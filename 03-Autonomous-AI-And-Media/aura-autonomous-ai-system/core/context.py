"""
AURA System Context Manager.
Coordinates working memory, environment variables, and persistent database state.
"""

from typing import Dict, Any, Optional
from memory.working_memory import WorkingMemory
from database.db import DatabaseManager, db_manager
from core.logger import setup_logger

logger = setup_logger("ContextManager")

class ContextManager:
    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or db_manager
        self.working_memory = WorkingMemory()
        self.session_id: Optional[str] = None

    def start_session(self, session_id: str):
        self.session_id = session_id
        import datetime
        now = datetime.datetime.now().isoformat()
        self.db.execute_update(
            "INSERT INTO sessions (session_id, start_time, status) VALUES (?, ?, ?)",
            (session_id, now, "active")
        )
        logger.info(f"Started session {session_id}")

    def end_session(self):
        if self.session_id:
            import datetime
            now = datetime.datetime.now().isoformat()
            self.db.execute_update(
                "UPDATE sessions SET end_time = ?, status = ? WHERE session_id = ?",
                (now, "completed", self.session_id)
            )
            logger.info(f"Ended session {self.session_id}")
            self.session_id = None

    def build_prompt_context(self) -> str:
        return self.working_memory.get_context_summary()

context_manager = ContextManager()
