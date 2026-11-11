import sqlite3
import os
import json
from datetime import datetime

class AgentMemory:
    """
    Persistent SQLite Long-Term Memory:
    - Self-learning error fixes
    - User preferences
    - Execution history
    """
    def __init__(self, db_path="storage/memory.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Error knowledge base
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_fixes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project TEXT,
                error TEXT NOT NULL,
                root_cause TEXT,
                solution TEXT NOT NULL,
                commands TEXT,
                status TEXT DEFAULT 'RESOLVED',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # User preferences and learned habits
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Task and workflow history
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                route TEXT NOT NULL,
                result_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()

    def save_fix(self, project: str, error: str, root_cause: str, solution: str, commands: str = ""):
        """Stores a successful fix in memory for future reuse."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO error_fixes (project, error, root_cause, solution, commands, status)
                VALUES (?, ?, ?, ?, ?, 'RESOLVED')
            """, (project, error, root_cause, solution, commands))
            conn.commit()

    def search_fix(self, error_snippet: str):
        """Looks up existing solutions matching the error snippet."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = f"%{error_snippet.strip()}%"
            cursor.execute("""
                SELECT project, error, root_cause, solution, commands, created_at
                FROM error_fixes
                WHERE error LIKE ? OR root_cause LIKE ?
                ORDER BY id DESC LIMIT 3
            """, (query, query))
            rows = cursor.fetchall()
            results = []
            for r in rows:
                results.append({
                    "project": r[0],
                    "error": r[1],
                    "root_cause": r[2],
                    "solution": r[3],
                    "commands": r[4],
                    "timestamp": r[5]
                })
            return results

    def set_preference(self, key: str, value: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_preferences (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
            """, (key, value))
            conn.commit()

    def get_preference(self, key: str, default=None):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_preferences WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else default

    def log_task(self, prompt: str, route: str, result_summary: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO task_history (prompt, route, result_summary)
                VALUES (?, ?, ?)
            """, (prompt, route, result_summary))
            conn.commit()

    def get_recent_history(self, limit=5):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT prompt, route, result_summary, created_at
                FROM task_history
                ORDER BY id DESC LIMIT ?
            """, (limit,))
            return cursor.fetchall()
