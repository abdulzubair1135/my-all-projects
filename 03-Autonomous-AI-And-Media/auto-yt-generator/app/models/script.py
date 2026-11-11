"""
AUTO YT GENERATOR — Script Data Models.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ScriptSection(BaseModel):
    """A distinct structural narrative block (hook, setup, explanation, etc.)."""

    section_type: str = Field(
        ...,
        description="Type of section: hook, setup, question, explanation, escalation, surprising_fact, conclusion",
    )
    title: str = Field(..., description="Short label for this section")
    narration_text: str = Field(..., description="The spoken narration text for TTS")
    estimated_duration_sec: float = Field(..., ge=1.0, description="Estimated speaking duration in seconds")
    visual_intent: str = Field(..., description="High-level description of what should be visually happening")
    sound_intent: Optional[str] = Field(default=None, description="Suggested SFX or music mood shift")


class ScriptModel(BaseModel):
    """Complete generated and validated script output."""

    project_id: str
    title: str
    hook: str
    target_duration_sec: int
    total_estimated_duration_sec: float
    sections: List[ScriptSection]
    facts_used: List[str] = Field(default_factory=list)
    hypotheticals_used: List[str] = Field(default_factory=list)
    youtube_title_options: List[str] = Field(default_factory=list)
    youtube_description: str = Field(default="")
    youtube_tags: List[str] = Field(default_factory=list)
