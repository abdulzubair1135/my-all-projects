"""
Data repositories for database persistence in StickForge AI.
"""

from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.storage.database import get_db, Database


class ProjectRepository:
    """CRUD operations for StickForge AI projects."""

    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    def create(self, project_data: Dict[str, Any]) -> str:
        query = """
        INSERT INTO projects (id, name, topic, genre, language, duration_target, aspect_ratio, status, file_path)
        VALUES (:id, :name, :topic, :genre, :language, :duration_target, :aspect_ratio, :status, :file_path)
        """
        self.db.execute(query, project_data)
        self.db.commit()
        return project_data["id"]

    def get(self, project_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_all(self, limit: int = 50, filter_missing: bool = True) -> List[Dict[str, Any]]:
        cursor = self.db.execute(
            "SELECT * FROM projects ORDER BY updated_at DESC LIMIT ?", (limit,)
        )
        rows = [dict(row) for row in cursor.fetchall()]
        if not filter_missing:
            return rows

        valid_rows: List[Dict[str, Any]] = []
        for r in rows:
            fp = r.get("file_path")
            if fp and Path(fp).exists():
                valid_rows.append(r)
            else:
                # Silently prune orphaned record from DB
                try:
                    self.delete(r["id"])
                except Exception:
                    pass
        return valid_rows

    def update(self, project_id: str, updates: Dict[str, Any]) -> None:
        fields = [f"{k} = :{k}" for k in updates.keys()]
        updates["id"] = project_id
        query = f"UPDATE projects SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = :id"
        self.db.execute(query, updates)
        self.db.commit()

    def delete(self, project_id: str) -> None:
        self.db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.db.commit()


class AIJobRepository:
    """Tracks AI generation tasks, segment outputs, and retry state."""

    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    def create_job(self, job_id: str, project_id: str, task_type: str, provider: str, prompt: str) -> None:
        query = """
        INSERT INTO ai_jobs (id, project_id, task_type, provider, status, prompt)
        VALUES (?, ?, ?, ?, 'PENDING', ?)
        """
        self.db.execute(query, (job_id, project_id, task_type, provider, prompt))
        self.db.commit()

    def update_status(self, job_id: str, status: str, result_json: str | None = None, error_message: str | None = None) -> None:
        query = """
        UPDATE ai_jobs
        SET status = ?, result_json = COALESCE(?, result_json), error_message = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        self.db.execute(query, (status, result_json, error_message, job_id))
        self.db.commit()

    def add_segment(self, job_id: str, segment_index: int, content: str) -> None:
        query = """
        INSERT INTO ai_response_segments (job_id, segment_index, content)
        VALUES (?, ?, ?)
        """
        self.db.execute(query, (job_id, segment_index, content))
        self.db.commit()

    def get_segments(self, job_id: str) -> List[Dict[str, Any]]:
        query = "SELECT * FROM ai_response_segments WHERE job_id = ? ORDER BY segment_index ASC"
        cursor = self.db.execute(query, (job_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.db.execute("SELECT * FROM ai_jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


class RenderJobRepository:
    """Tracks video export jobs and completion status."""

    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    def create(self, job_id: str, project_id: str, output_profile: str) -> None:
        query = """
        INSERT INTO render_jobs (id, project_id, output_profile, status, progress)
        VALUES (?, ?, ?, 'PENDING', 0.0)
        """
        self.db.execute(query, (job_id, project_id, output_profile))
        self.db.commit()

    def update_progress(self, job_id: str, progress: float, status: str = "RUNNING") -> None:
        query = "UPDATE render_jobs SET progress = ?, status = ? WHERE id = ?"
        self.db.execute(query, (progress, status, job_id))
        self.db.commit()

    def mark_completed(self, job_id: str, output_file_path: str) -> None:
        query = """
        UPDATE render_jobs
        SET status = 'COMPLETED', progress = 100.0, output_file_path = ?, completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """
        self.db.execute(query, (output_file_path, job_id))
        self.db.commit()

    def mark_failed(self, job_id: str, error_message: str) -> None:
        query = "UPDATE render_jobs SET status = 'FAILED', error_message = ? WHERE id = ?"
        self.db.execute(query, (error_message, job_id))
        self.db.commit()

    def list_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.db.execute("SELECT * FROM render_jobs ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(row) for row in cursor.fetchall()]


class CheckpointRepository:
    """Stores checkpoint states for background recovery."""

    def __init__(self, db: Database | None = None):
        self.db = db or get_db()

    def save_checkpoint(self, job_id: str, task_type: str, step_name: str, state_data: Dict[str, Any]) -> None:
        query = """
        INSERT INTO task_checkpoints (job_id, task_type, step_name, state_data_json, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(job_id) DO UPDATE SET
            step_name = excluded.step_name,
            state_data_json = excluded.state_data_json,
            updated_at = CURRENT_TIMESTAMP
        """
        self.db.execute(query, (job_id, task_type, step_name, json.dumps(state_data)))
        self.db.commit()

    def get_checkpoint(self, job_id: str) -> Optional[Dict[str, Any]]:
        cursor = self.db.execute("SELECT * FROM task_checkpoints WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        if not row:
            return None
        res = dict(row)
        res["state_data"] = json.loads(res["state_data_json"])
        return res

    def delete_checkpoint(self, job_id: str) -> None:
        self.db.execute("DELETE FROM task_checkpoints WHERE job_id = ?", (job_id,))
        self.db.commit()
