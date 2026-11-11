import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

class StateManager:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path).resolve()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA busy_timeout=30000;")
        except Exception:
            pass
        return conn

    def _init_schema(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS tasks (
                  id TEXT PRIMARY KEY,
                  project_id TEXT,
                  run_id TEXT,
                  title TEXT,
                  description TEXT,
                  status TEXT,
                  order_index INTEGER,
                  retry_count INTEGER DEFAULT 0,
                  error_message TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS task_dependencies (
                  id TEXT PRIMARY KEY,
                  task_id TEXT,
                  depends_on_task_id TEXT
                );
                CREATE TABLE IF NOT EXISTS commands (
                  id TEXT PRIMARY KEY,
                  project_id TEXT,
                  run_id TEXT,
                  task_id TEXT,
                  command TEXT,
                  cwd TEXT,
                  exit_code INTEGER,
                  duration_ms INTEGER,
                  stdout TEXT,
                  stderr TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS approvals (
                  id TEXT PRIMARY KEY,
                  project_id TEXT,
                  run_id TEXT,
                  action_type TEXT,
                  action_payload TEXT,
                  status TEXT,
                  reason TEXT,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

    def save_tasks(self, project_id: str, run_id: str, tasks: List[Dict[str, Any]], dependencies: Dict[str, List[str]]):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for t in tasks:
                cursor.execute("""
                    INSERT OR REPLACE INTO tasks (id, project_id, run_id, title, description, status, order_index, retry_count, error_message, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (t["id"], project_id, run_id, t["title"], t["description"], t["status"], t["order_index"], t.get("retry_count", 0), t.get("error_message")))

                # Insert dependencies
                deps = dependencies.get(t["id"], [])
                for dep_id in deps:
                    dep_key = f"{t['id']}_{dep_id}"
                    cursor.execute("""
                        INSERT OR REPLACE INTO task_dependencies (id, task_id, depends_on_task_id)
                        VALUES (?, ?, ?)
                    """, (dep_key, t["id"], dep_id))
            conn.commit()

    def update_task_status(self, task_id: str, status: str, error_message: Optional[str] = None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks SET status = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
            """, (status, error_message, task_id))
            conn.commit()

    def record_command(self, cmd_id: str, project_id: str, run_id: str, task_id: Optional[str], command: str, cwd: str, exit_code: int, duration_ms: int, stdout: str, stderr: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO commands (id, project_id, run_id, task_id, command, cwd, exit_code, duration_ms, stdout, stderr, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (cmd_id, project_id, run_id, task_id, command, cwd, exit_code, duration_ms, stdout, stderr))
            conn.commit()

    def create_approval(self, approval_id: str, project_id: str, run_id: str, action_type: str, action_payload: Dict[str, Any], reason: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO approvals (id, project_id, run_id, action_type, action_payload, status, reason, created_at)
                VALUES (?, ?, ?, ?, ?, 'PENDING', ?, CURRENT_TIMESTAMP)
            """, (approval_id, project_id, run_id, action_type, json.dumps(action_payload), reason))
            conn.commit()

    def close(self):
        pass
