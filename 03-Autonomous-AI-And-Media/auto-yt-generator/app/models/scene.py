"""
AUTO YT GENERATOR — Enhanced Professional Scene & Director Data Models.

Provides comprehensive schemas for:
- Semantic Analysis & Emotion Direction
- Shot Framing & Composition (Wide, Medium, Close-Up, Infographic, B-Roll)
- Character Acting Gestures & Eye Gaze Cues
- Multi-Layer Parallax Speeds
- Motion Graphics / Infographic Cutaways
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.constants import (
    CharacterAction,
    FacialExpression,
    CameraMovement,
    Mood,
)


class ShotType(str, Enum):
    ESTABLISHING = "establishing"
    WIDE = "wide"
    MEDIUM = "medium"
    CLOSE_UP = "close_up"
    EXTREME_CLOSE_UP = "extreme_close_up"
    REACTION = "reaction"
    INFOGRAPHIC_CUTAWAY = "infographic_cutaway"
    BROLL = "broll"


class ActingGesture(str, Enum):
    IDLE = "idle"
    TALK_EXPLAIN = "talk_explain"
    POINT_LEFT = "point_left"
    POINT_RIGHT = "point_right"
    THINK_CURIOUS = "think_curious"
    SHOCK_FREEZE = "shock_freeze"
    FACEPALM = "facepalm"
    SHRUG = "shrug"
    PANIC_HANDS = "panic_hands"
    EXCITED_WAVE = "excited_wave"


class EyeGaze(str, Enum):
    DIRECT = "direct"
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    CLOSED = "closed"


class InfographicConfig(BaseModel):
    """Configuration for animated infographics and data visuals."""

    type: str = Field(default="stats_counter", description="stats_counter, progress_bar, brain_diagram, comparison, alert_card")
    title: str = Field(default="")
    stat_number: Optional[float] = Field(default=None)
    stat_prefix: str = Field(default="")
    stat_suffix: str = Field(default="")
    description: str = Field(default="")
    highlight_color: str = Field(default="#38bdf8")


class ParallaxConfig(BaseModel):
    """Speed multipliers for 5-layer parallax depth."""

    sky_speed: float = Field(default=0.05)
    far_bg_speed: float = Field(default=0.20)
    midground_speed: float = Field(default=0.50)
    character_speed: float = Field(default=0.85)
    foreground_speed: float = Field(default=1.20)


class CameraConfig(BaseModel):
    """Camera direction, shot type, and framing within a scene."""

    type: str = Field(default=CameraMovement.STATIC.value, description="Camera motion type")
    shot_type: ShotType = Field(default=ShotType.MEDIUM, description="Shot framing composition")
    zoom_start: float = Field(default=1.0, ge=0.5, le=3.0)
    zoom_end: float = Field(default=1.0, ge=0.5, le=3.0)
    pan_x_start: float = Field(default=0.0)
    pan_x_end: float = Field(default=0.0)
    pan_y_start: float = Field(default=0.0)
    pan_y_end: float = Field(default=0.0)
    focus_target: Optional[str] = Field(default=None, description="Focus target entity")
    parallax: ParallaxConfig = Field(default_factory=ParallaxConfig)


class SceneAction(BaseModel):
    """A visual acting cue mapped to a character or prop."""

    entity_id: str = Field(..., description="Target character or prop identifier")
    action: str = Field(default=CharacterAction.IDLE.value)
    gesture: ActingGesture = Field(default=ActingGesture.IDLE)
    expression: str = Field(default=FacialExpression.NEUTRAL.value)
    gaze: EyeGaze = Field(default=EyeGaze.DIRECT)
    start_time_sec: float = Field(default=0.0, ge=0.0)
    duration_sec: float = Field(default=3.0, ge=0.1)
    position_x_percent: float = Field(default=50.0, ge=0.0, le=100.0)
    position_y_percent: float = Field(default=50.0, ge=0.0, le=100.0)
    scale: float = Field(default=1.0, ge=0.1, le=5.0)


class SemanticCue(BaseModel):
    """Semantic analysis of the spoken narration beat."""

    emotion: str = Field(default="neutral", description="fear, surprise, curiosity, warning, excitement, humor")
    intent: str = Field(default="explain", description="hook, question, explain, escalate, shock, conclude")
    importance: float = Field(default=0.5, ge=0.0, le=1.0, description="Visual emphasis weight")
    highlight_keywords: List[str] = Field(default_factory=list, description="Words to emphasize in captions/graphics")


class SceneModel(BaseModel):
    """Complete visual, acting, audio, and camera plan for a single scene beat."""

    scene_index: int = Field(..., ge=1, description="1-based scene sequence number")
    section_ref: Optional[str] = Field(default=None, description="Corresponding script section")
    duration_sec: float = Field(..., ge=0.5, description="Scene duration in seconds")
    narration_text: str = Field(default="", description="Narration line for this scene")
    audio_file: Optional[str] = Field(default=None, description="Path to rendered voice clip")

    # Visual Scene Type
    is_cutaway: bool = Field(default=False, description="True if scene is an infographic/B-roll cutaway")
    infographic: Optional[InfographicConfig] = Field(default=None, description="Infographic details if cutaway")

    background_id: str = Field(default="bedroom_dark", description="Background asset template")
    characters: List[str] = Field(default_factory=list, description="Character IDs in scene")
    props: List[str] = Field(default_factory=list, description="Prop asset IDs in scene")

    actions: List[SceneAction] = Field(default_factory=list)
    camera: CameraConfig = Field(default_factory=CameraConfig)
    semantic: SemanticCue = Field(default_factory=SemanticCue)

    effects: List[str] = Field(default_factory=list, description="Visual VFX overlays (e.g. heartbeat, glitch, vignette)")
    sfx: List[str] = Field(default_factory=list, description="Contextual SFX cues (whoosh, heartbeat, impact, chime)")
    mood: str = Field(default=Mood.SUSPENSE.value)
    subtitle_text: Optional[str] = Field(default=None)


class ScenePlan(BaseModel):
    """Complete storyboard / collection of scenes for an entire video project."""

    project_id: str
    total_scenes: int
    total_duration_sec: float
    scenes: List[SceneModel]
