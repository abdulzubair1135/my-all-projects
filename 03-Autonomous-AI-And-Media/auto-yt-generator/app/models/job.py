"""
AUTO YT GENERATOR — Job and Pipeline Execution Models.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.constants import PipelineStage, StageStatus


class StageLog(BaseModel):
    """Execution status and metric log for a single stage in the pipeline."""

    stage_name: str
    status: StageStatus = StageStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    retry_count: int = 0
    error_message: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class JobModel(BaseModel):
    """Orchestrator tracking for an active or completed generation job."""

    job_id: str
    project_id: str
    current_stage: PipelineStage = PipelineStage.QUEUED
    status: StageStatus = StageStatus.PENDING
    overall_progress: float = 0.0
    stage_logs: List[StageLog] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
