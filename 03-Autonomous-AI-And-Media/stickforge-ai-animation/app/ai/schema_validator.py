"""
Schema definitions and Pydantic validators for AI Script and Storyboard outputs.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class CharacterDef(BaseModel):
    id: str
    name: str
    role: str = "protagonist"  # protagonist, antagonist, friend, bystander
    style: str = "classic_stickman"
    color: str = "#FFFFFF"
    voice_id: str = "en-US-ChristopherNeural"
    description: str = ""


class StoryBeat(BaseModel):
    beat_name: str  # beginning, conflict, escalation, climax, ending
    summary: str
    narration: str
    estimated_duration: float = 6.0


class GeneratedScript(BaseModel):
    title: str
    premise: str
    language: str = "hinglish"
    genre: str = "comedy"
    estimated_duration_seconds: float = 30.0
    characters: List[CharacterDef] = Field(default_factory=list)
    beats: List[StoryBeat] = Field(default_factory=list)
    full_narration: str = ""


class ActionSpec(BaseModel):
    character_id: str
    action: str  # walk, run, jump, sit, wave, fight, etc.
    parameters: Dict[str, Any] = Field(default_factory=dict)


class CameraSpec(BaseModel):
    shot: str = "medium"  # wide, medium, close_up
    movement: str = "static"  # static, pan_left, pan_right, zoom_in, zoom_out
    speed: float = 1.0


class SceneSpec(BaseModel):
    id: str
    sequence_order: int
    duration: float = Field(ge=1.0, le=60.0)
    background: str = "classroom"  # classroom, street, room, forest, office, plain_white, plain_dark
    actions: List[ActionSpec] = Field(default_factory=list)
    narration: str = ""
    dialogue: str = ""
    camera: CameraSpec = Field(default_factory=CameraSpec)
    sound_effects: List[str] = Field(default_factory=list)
    transition: str = "none"  # none, fade, slide_left, slide_right

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Scene duration must be positive")
        return round(v, 2)


class GeneratedStoryboard(BaseModel):
    schema_version: int = 1
    project_id: str
    title: str
    language: str = "hinglish"
    aspect_ratio: str = "9:16"
    characters: List[CharacterDef] = Field(default_factory=list)
    scenes: List[SceneSpec] = Field(default_factory=list)

    @field_validator("scenes")
    @classmethod
    def validate_scenes_not_empty(cls, v: List[SceneSpec]) -> List[SceneSpec]:
        if not v:
            raise ValueError("Storyboard must contain at least one scene")
        return v
