"""
Task Manager and State Machine for StickForge AI.
Handles job queues, transitions, bounded retries, and persistence.
"""

from __future__ import annotations
import enum
import time
import uuid
from typing import Any, Callable, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.logging_manager import get_logger
from app.core.event_bus import get_event_bus
from app.storage.repositories import CheckpointRepository

logger = get_logger("task_manager")


class TaskState(str, enum.Enum):
    IDLE = "IDLE"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    RETRY_WAIT = "RETRY_WAIT"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TaskJob(BaseModel):
    id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}")
    project_id: str
    task_type: str  # ai_generation, frame_render, video_export, publishing
    state: TaskState = TaskState.PENDING
    progress: float = 0.0
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskManager:
    """Coordinates task execution, state transitions, and checkpoints."""

    def __init__(self):
        self.jobs: Dict[str, TaskJob] = {}
        self.checkpoint_repo = CheckpointRepository()
        self.event_bus = get_event_bus()

    def create_job(
        self,
        project_id: str,
        task_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> TaskJob:
        job = TaskJob(
            project_id=project_id,
            task_type=task_type,
            metadata=metadata or {},
            max_retries=max_retries,
        )
        self.jobs[job.id] = job
        self.event_bus.publish("task_created", job=job)
        logger.info(f"Created task {job.id} [{task_type}] for project {project_id}")
        return job

    def transition(
        self,
        job_id: str,
        new_state: TaskState,
        progress: Optional[float] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """Execute a valid state transition and notify event bus."""
        job = self.jobs.get(job_id)
        if not job:
            logger.warning(f"Attempted transition on unknown job {job_id}")
            return

        old_state = job.state
        job.state = new_state
        job.updated_at = time.time()
        if progress is not None:
            job.progress = max(0.0, min(100.0, progress))
        if error_message is not None:
            job.error_message = error_message

        logger.info(f"Task {job_id} [{job.task_type}]: {old_state.value} -> {new_state.value} (progress: {job.progress:.1f}%)")
        self.event_bus.publish(
            "task_state_changed",
            job_id=job_id,
            old_state=old_state,
            new_state=new_state,
            progress=job.progress,
            error=job.error_message,
        )

    def save_checkpoint(self, job_id: str, step_name: str, state_data: Dict[str, Any]) -> None:
        """Persist intermediate state for crash recovery."""
        job = self.jobs.get(job_id)
        if not job:
            return
        self.checkpoint_repo.save_checkpoint(job_id, job.task_type, step_name, state_data)
        logger.debug(f"Saved checkpoint for task {job_id} at step '{step_name}'")

    def load_checkpoint(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.checkpoint_repo.get_checkpoint(job_id)

    def cancel_job(self, job_id: str) -> None:
        job = self.jobs.get(job_id)
        if job and job.state in [TaskState.PENDING, TaskState.RUNNING, TaskState.WAITING_FOR_USER, TaskState.RETRY_WAIT]:
            self.transition(job_id, TaskState.CANCELLED)

    def get_job(self, job_id: str) -> Optional[TaskJob]:
        return self.jobs.get(job_id)


# Global task manager instance
_task_manager: Optional[TaskManager] = None


def get_task_manager() -> TaskManager:
    global _task_manager
    if _task_manager is None:
        _task_manager = TaskManager()
    return _task_manager
