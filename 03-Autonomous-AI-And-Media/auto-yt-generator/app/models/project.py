"""
AUTO YT GENERATOR — Project Data Models.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.constants import (
    VideoStyle,
    Language,
    PipelineStage,
    SUPPORTED_RESOLUTIONS,
    DEFAULT_FPS,
    DEFAULT_DURATION,
)


class ProjectConfig(BaseModel):
    """User input configuration for a video project."""

    topic: str = Field(..., min_length=3, description="Core topic or question of the video")
    language: str = Field(default=Language.ENGLISH.value, description="Language code (en, hi, ur)")
    duration_seconds: int = Field(default=DEFAULT_DURATION, ge=10, le=3600, description="Target duration in seconds")
    style: str = Field(default=VideoStyle.DARK_CARTOON.value, description="Visual aesthetic style")
    resolution: str = Field(default="1920x1080", description="Video dimensions string (e.g. 1920x1080)")
    fps: int = Field(default=DEFAULT_FPS, ge=15, le=60, description="Frames per second")
    voice_style: str = Field(default="deep_narrator", description="Voice persona/tone for TTS")
    music_style: str = Field(default="dark_suspense", description="Mood/genre for background score")
    tone: str = Field(default="scientific_mysterious", description="Narrative tone")


class ProjectModel(BaseModel):
    """Full representation of a video generation project."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(default="Untitled Project")
    config: ProjectConfig
    current_stage: PipelineStage = Field(default=PipelineStage.QUEUED)
    progress_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    # Paths
    project_dir: Optional[str] = None
    output_video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None

    class Config:
        use_enum_values = True


class ProjectSummary(BaseModel):
    """Lightweight project information for listings."""

    id: str
    title: str
    topic: str
    style: str
    language: str
    duration_seconds: int
    current_stage: str
    progress_percent: float
    created_at: datetime
