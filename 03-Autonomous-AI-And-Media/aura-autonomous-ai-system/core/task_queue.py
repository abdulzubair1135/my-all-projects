"""
AURA Task Queue Module.
Manages persistent SQLite task queue with priority ordering, retries, and status tracking.
"""

import uuid
import datetime
from typing import List, Dict, Any, Optional
from database.db import DatabaseManager, db_manager
from core.logger import setup_logger

logger = setup_logger("TaskQueue")

class TaskItem:
    def __init__(
        self,
        title: str,
        description: str,
        goal_id: Optional[str] = None,
        priority: int = 1,
        task_id: Optional[str] = None,
        status: str = "pending",
        retry_count: int = 0,
        result: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        now = datetime.datetime.now().isoformat()
        self.task_id = task_id or f"task_{uuid.uuid4().hex[:8]}"
        self.goal_id = goal_id
        self.title = title
        self.description = description
        self.status = status
        self.priority = priority
        self.retry_count = retry_count
        self.result = result
        self.created_at = created_at or now
        self.updated_at = updated_at or now

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "goal_id": self.goal_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "retry_count": self.retry_count,
            "result": self.result,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

class TaskQueue:
    def __init__(self, db: Optional[DatabaseManager] = None):
        self.db = db or db_manager

    def add_task(self, title: str, description: str, goal_id: Optional[str] = None, priority: int = 1) -> TaskItem:
        task = TaskItem(title=title, description=description, goal_id=goal_id, priority=priority)
        self.db.execute_update(
            """INSERT INTO tasks (task_id, goal_id, title, description, status, priority, retry_count, result, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (task.task_id, task.goal_id, task.title, task.description, task.status, task.priority, task.retry_count, task.result, task.created_at, task.updated_at)
        )
        logger.info(f"Added task [{task.task_id}] '{task.title}' with priority {task.priority}")
        return task

    def pop_next_task(self) -> Optional[TaskItem]:
        """Fetch and mark the highest priority pending task as 'in_progress'."""
        rows = self.db.execute_query(
            "SELECT * FROM tasks WHERE status = 'pending' ORDER BY priority DESC, created_at ASC LIMIT 1"
        )
        if not rows:
            return None

        row = rows[0]
        task = TaskItem(
            task_id=row["task_id"],
            goal_id=row["goal_id"],
            title=row["title"],
            description=row["description"],
            status="in_progress",
            priority=row["priority"],
            retry_count=row["retry_count"],
            result=row["result"],
            created_at=row["created_at"],
            updated_at=datetime.datetime.now().isoformat()
        )

        self.db.execute_update(
            "UPDATE tasks SET status = 'in_progress', updated_at = ? WHERE task_id = ?",
            (task.updated_at, task.task_id)
        )
        logger.info(f"Popped task [{task.task_id}] '{task.title}'")
        return task

    def update_task_status(self, task_id: str, status: str, result: Optional[str] = None, increment_retry: bool = False):
        now = datetime.datetime.now().isoformat()
        if increment_retry:
            self.db.execute_update(
                "UPDATE tasks SET status = ?, result = ?, retry_count = retry_count + 1, updated_at = ? WHERE task_id = ?",
                (status, result, now, task_id)
            )
        else:
            self.db.execute_update(
                "UPDATE tasks SET status = ?, result = ?, updated_at = ? WHERE task_id = ?",
                (status, result, now, task_id)
            )
        logger.info(f"Updated task [{task_id}] status -> {status}")

    def get_pending_tasks(self) -> List[TaskItem]:
        rows = self.db.execute_query(
            "SELECT * FROM tasks WHERE status = 'pending' ORDER BY priority DESC, created_at ASC"
        )
        return [
            TaskItem(
                task_id=r["task_id"],
                goal_id=r["goal_id"],
                title=r["title"],
                description=r["description"],
                status=r["status"],
                priority=r["priority"],
                retry_count=r["retry_count"],
                result=r["result"],
                created_at=r["created_at"],
                updated_at=r["updated_at"]
            ) for r in rows
        ]

    def clear(self):
        self.db.execute_update("DELETE FROM tasks")
        logger.info("Task queue cleared")

task_queue = TaskQueue()
