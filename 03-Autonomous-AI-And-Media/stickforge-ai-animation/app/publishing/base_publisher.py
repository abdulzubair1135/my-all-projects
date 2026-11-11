"""
Base Publisher interface for social media platforms.
"""

from __future__ import annotations
import abc
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class PublishingMetadata(BaseModel):
    title: str = Field(max_length=100)
    description: str = Field(default="", max_length=5000)
    tags: list[str] = Field(default_factory=list)
    privacy_status: str = "private"  # private, unlisted, public
    scheduled_time_iso: Optional[str] = None


class PublishingResult(BaseModel):
    success: bool
    platform: str
    video_id: Optional[str] = None
    url: Optional[str] = None
    status: str = "PENDING"
    error_message: Optional[str] = None
    is_simulated: bool = False


class BasePublisher(abc.ABC):
    """Abstract interface for video publishing integrations."""

    @abc.abstractmethod
    def validate_media_and_metadata(self, media_path: Path, metadata: PublishingMetadata) -> list[str]:
        """Returns list of validation error strings, empty if valid."""
        pass

    @abc.abstractmethod
    def publish_video(
        self,
        media_path: Path,
        metadata: PublishingMetadata,
        progress_callback: Optional[callable] = None,
    ) -> PublishingResult:
        pass
