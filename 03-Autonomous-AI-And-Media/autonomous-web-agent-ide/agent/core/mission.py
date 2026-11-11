"""
mission.py
Structured Mission dataclass for Autonomous Web-Agent IDE.

Every user request becomes a Mission — a rich, observable, persisted object
that tracks the full lifecycle from goal to delivery.
"""

import json
import sqlite3
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any


@dataclass
class Mission:
    """Represents a single autonomous software engineering mission."""

    id: str = field(default_factory=lambda: f"mission-{uuid.uuid4().hex[:8]}")
    user_goal: str = ""
    requirements: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)

    # Inputs
    images: List[str] = field(default_factory=list)       # file paths
    zip_file: Optional[str] = None                         # file path
    reference_urls: List[str] = field(default_factory=list)

    # Status
    status: str = "IDLE"  # IDLE → PLANNING → RUNNING → SUCCESS → FAILED → CANCELLED
    current_phase: str = ""
    progress_pct: int = 0

    # Project
    project_id: Optional[str] = None
    project_path: Optional[str] = None
    project_info: Dict[str, Any] = field(default_factory=dict)  # from ProjectInspector

    # AI
    provider: str = "deepseek_web"

    # Task graph
    task_graph: List[Dict[str, Any]] = field(default_factory=list)
    completed_tasks: int = 0
    total_tasks: int = 0

    # Timing
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None

    # Result
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    commands_run: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)

    def start(self):
        self.status = "RUNNING"
        self.started_at = time.time()

    def complete(self, result: Dict[str, Any] = None):
        self.status = "SUCCESS"
        self.completed_at = time.time()
        self.result = result or {}
        self.progress_pct = 100

    def fail(self, error: str):
        self.status = "FAILED"
        self.completed_at = time.time()
        self.error = error

    def cancel(self):
        self.status = "CANCELLED"
        self.completed_at = time.time()

    def set_phase(self, phase: str, progress: int = None):
        self.current_phase = phase
        if progress is not None:
            self.progress_pct = min(100, max(0, progress))

    def add_file_created(self, path: str):
        if path not in self.files_created:
            self.files_created.append(path)

    def add_file_modified(self, path: str):
        if path not in self.files_modified:
            self.files_modified.append(path)

    def add_command(self, cmd: str):
        self.commands_run.append(cmd)

    @property
    def duration_seconds(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def summary_log(self) -> str:
        """Short terminal-friendly summary line."""
        return (
            f"📋 [Mission] {self.id} | "
            f"Goal: {self.user_goal[:60]}{'...' if len(self.user_goal) > 60 else ''} | "
            f"Status: {self.status} | "
            f"Tasks: {self.completed_tasks}/{self.total_tasks}"
        )


class MissionStore:
    """Persist and load missions from SQLite."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_tables()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS missions (
                    id TEXT PRIMARY KEY,
                    project_id TEXT,
                    user_goal TEXT,
                    status TEXT,
                    provider TEXT,
                    progress_pct INTEGER DEFAULT 0,
                    current_phase TEXT,
                    data_json TEXT,
                    created_at REAL,
                    started_at REAL,
                    completed_at REAL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_mission_project ON missions(project_id)")
            conn.commit()

    def save(self, mission: Mission):
        with self._conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO missions
                (id, project_id, user_goal, status, provider, progress_pct, current_phase,
                 data_json, created_at, started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mission.id, mission.project_id, mission.user_goal,
                mission.status, mission.provider, mission.progress_pct,
                mission.current_phase, mission.to_json(),
                mission.created_at, mission.started_at, mission.completed_at,
            ))
            conn.commit()

    def load(self, mission_id: str) -> Optional[Mission]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT data_json FROM missions WHERE id = ?", (mission_id,)
            ).fetchone()
        if not row:
            return None
        data = json.loads(row["data_json"])
        return Mission(**{k: v for k, v in data.items() if k in Mission.__dataclass_fields__})

    def list_recent(self, project_id: str = None, limit: int = 20) -> List[Dict]:
        with self._conn() as conn:
            if project_id:
                rows = conn.execute(
                    "SELECT id, user_goal, status, provider, progress_pct, created_at FROM missions WHERE project_id = ? ORDER BY created_at DESC LIMIT ?",
                    (project_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, user_goal, status, provider, progress_pct, created_at FROM missions ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [dict(r) for r in rows]


def create_mission_from_prompt(
    prompt: str,
    project_id: str = None,
    project_path: str = None,
    provider: str = "deepseek_web",
    images: List[str] = None,
    zip_file: str = None,
) -> Mission:
    """
    Create a Mission from a user's natural language prompt.
    Extracts requirements and acceptance criteria with simple heuristics.
    The AI will refine these during the planning phase.
    """
    mission = Mission(
        user_goal=prompt.strip(),
        project_id=project_id,
        project_path=project_path,
        provider=provider,
        images=images or [],
        zip_file=zip_file,
    )

    # Simple heuristic extraction
    lines = prompt.strip().split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith(("-", "*", "•")) and len(line) > 3:
            mission.requirements.append(line.lstrip("-*• ").strip())

    # Default acceptance criteria
    mission.acceptance_criteria = [
        "All generated code is complete (no placeholders)",
        "Application runs without errors",
        "All files are properly created/modified",
    ]

    return mission
