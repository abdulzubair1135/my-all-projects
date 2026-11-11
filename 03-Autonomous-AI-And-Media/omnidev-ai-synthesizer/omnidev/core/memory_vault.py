import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
import config

class MemoryVault:
    """
    SQLite-backed Persistent Memory Engine for OmniDev.
    """
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or (config.WORKSPACE_DIR / ".omnidev_memory.db")).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS missions (
                    mission_id TEXT PRIMARY KEY,
                    goal TEXT NOT NULL,
                    status TEXT NOT NULL,
                    data_json TEXT,
                    created_at REAL,
                    completed_at REAL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_fingerprints (
                    fingerprint TEXT PRIMARY KEY,
                    error_type TEXT,
                    normalized_message TEXT,
                    root_cause TEXT,
                    solution_patch TEXT,
                    success_count INTEGER DEFAULT 1,
                    failed_count INTEGER DEFAULT 0,
                    last_seen REAL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mission_id TEXT,
                    decision_type TEXT,
                    context TEXT,
                    choice TEXT,
                    rationale TEXT,
                    timestamp REAL
                )
            """)
            conn.commit()

    def record_mission(self, mission_id: str, goal: str, status: str, data: Dict[str, Any]):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO missions (mission_id, goal, status, data_json, created_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (mission_id, goal, status, json.dumps(data), time.time(), time.time() if status in ["COMPLETED", "FAILED"] else None))
            conn.commit()

    def store_context(self, key: str, data: Dict[str, Any]):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kv_context (
                    key TEXT PRIMARY KEY,
                    data_json TEXT,
                    updated_at REAL
                )
            """)
            cursor.execute("""
                INSERT OR REPLACE INTO kv_context (key, data_json, updated_at)
                VALUES (?, ?, ?)
            """, (key, json.dumps(data), time.time()))
            conn.commit()

    def get_context(self, key: str) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kv_context (
                    key TEXT PRIMARY KEY,
                    data_json TEXT,
                    updated_at REAL
                )
            """)
            cursor.execute("SELECT data_json FROM kv_context WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row and row["data_json"]:
                try:
                    return json.loads(row["data_json"])
                except Exception:
                    pass
            return None
