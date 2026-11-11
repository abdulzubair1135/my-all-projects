import uuid
import time
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AutonomyLevel(int, Enum):
    LEVEL_0 = 0  # Manual
    LEVEL_1 = 1  # Approve every tool
    LEVEL_2 = 2  # Low-risk autonomous
    LEVEL_3 = 3  # Low/Medium autonomous
    LEVEL_4 = 4  # Full mission autonomous

class MissionStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    HEALING = "HEALING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class Requirement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str
    is_critical: bool = True
    category: str = "functional"
    acceptance_criterion: str = ""
    satisfied: bool = False

class Constraint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str
    type: str = "technology"

class Mission(BaseModel):
    id: str = Field(default_factory=lambda: f"mission_{int(time.time())}_{str(uuid.uuid4())[:6]}")
    user_goal: str
    requirements: List[Requirement] = Field(default_factory=list)
    constraints: List[Constraint] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: List[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    autonomy_level: AutonomyLevel = AutonomyLevel.LEVEL_3
    status: MissionStatus = MissionStatus.PENDING
    target_directory: str = ""
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def mark_updated(self):
        self.updated_at = time.time()

    def get_progress_percentage(self) -> int:
        if not self.requirements:
            return 0 if self.status != MissionStatus.COMPLETED else 100
        completed = sum(1 for r in self.requirements if r.satisfied)
        return int((completed / len(self.requirements)) * 100)
