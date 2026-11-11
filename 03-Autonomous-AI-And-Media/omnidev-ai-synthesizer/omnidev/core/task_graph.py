import uuid
import time
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    READY = "READY"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"

class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: f"task_{str(uuid.uuid4())[:8]}")
    title: str
    description: str = ""
    assigned_agent: str = "CoderAgent"
    dependencies: List[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 1
    risk: str = "LOW"
    required_tools: List[str] = Field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

class TaskGraph:
    """
    Dependency-aware DAG for OmniDev tasks.
    """
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def add_task(self, task: Task) -> str:
        self.tasks[task.task_id] = task
        return task.task_id

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def detect_cycles(self) -> bool:
        visited = set()
        rec_stack = set()

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            task = self.tasks.get(node)
            if task:
                for dep in task.dependencies:
                    if dep not in visited:
                        if dfs(dep):
                            return True
                    elif dep in rec_stack:
                        return True
            rec_stack.remove(node)
            return False

        for task_id in self.tasks:
            if task_id not in visited:
                if dfs(task_id):
                    return True
        return False

    def get_ready_tasks(self) -> List[Task]:
        ready = []
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING:
                deps_satisfied = True
                for dep_id in task.dependencies:
                    dep = self.tasks.get(dep_id)
                    if not dep or dep.status != TaskStatus.COMPLETED:
                        deps_satisfied = False
                        break
                if deps_satisfied:
                    task.status = TaskStatus.READY
                    ready.append(task)
            elif task.status == TaskStatus.READY:
                ready.append(task)
        ready.sort(key=lambda t: t.priority)
        return ready

    def mark_completed(self, task_id: str, result: Optional[Dict[str, Any]] = None):
        if task_id in self.tasks:
            t = self.tasks[task_id]
            t.status = TaskStatus.COMPLETED
            t.result = result or {}
            t.completed_at = time.time()

    def mark_failed(self, task_id: str, error: str):
        if task_id in self.tasks:
            t = self.tasks[task_id]
            t.error = error
            t.retry_count += 1
            if t.retry_count >= t.max_retries:
                t.status = TaskStatus.FAILED
            else:
                t.status = TaskStatus.PENDING
            t.completed_at = time.time()

    def is_all_completed(self) -> bool:
        if not self.tasks:
            return True
        return all(t.status in [TaskStatus.COMPLETED, TaskStatus.SKIPPED] for t in self.tasks.values())

    def has_failures(self) -> bool:
        return any(t.status == TaskStatus.FAILED for t in self.tasks.values())
