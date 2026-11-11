"""
AUTO YT GENERATOR — App-wide constants.

All magic strings and enumerations live here.
Never scatter string literals across modules.
"""

from enum import Enum

# ── Application ──────────────────────────────────────────────────────────────

APP_NAME = "AUTO YT GENERATOR"
APP_VERSION = "0.1.0"
CONFIG_FILE = "config.json"
DB_FILE = "auto_yt.db"

# ── Video ─────────────────────────────────────────────────────────────────────

SUPPORTED_RESOLUTIONS = {
    "1920x1080": (1920, 1080),
    "1280x720": (1280, 720),
    "1080x1920": (1080, 1920),
}
DEFAULT_FPS = 30
DEFAULT_DURATION = 300  # seconds


# ── Styles ────────────────────────────────────────────────────────────────────

class VideoStyle(str, Enum):
    DARK_CARTOON = "dark_cartoon"
    DARK_SCIENCE = "dark_science"
    WEIRD_SCIENCE = "weird_science"
    HORROR_SCIENCE = "horror_science"
    FUNNY_SCIENCE = "funny_science"
    DOCUMENTARY = "documentary"
    EDUCATIONAL = "educational"
    MYSTERY = "mystery"
    CUSTOM = "custom"


# ── Languages ─────────────────────────────────────────────────────────────────

class Language(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    URDU = "ur"


# ── Pipeline Stages ───────────────────────────────────────────────────────────

class PipelineStage(str, Enum):
    QUEUED = "QUEUED"
    RESEARCHING = "RESEARCHING"
    SCRIPTING = "SCRIPTING"
    PLANNING = "PLANNING"
    GENERATING_ASSETS = "GENERATING_ASSETS"
    GENERATING_AUDIO = "GENERATING_AUDIO"
    ANIMATING = "ANIMATING"
    COMPOSITING = "COMPOSITING"
    MIXING = "MIXING"
    RENDERING = "RENDERING"
    VALIDATING = "VALIDATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"


class StageStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


# ── Asset Types ───────────────────────────────────────────────────────────────

class AssetType(str, Enum):
    CHARACTER = "character"
    BACKGROUND = "background"
    PROP = "prop"
    SPRITE = "sprite"
    MUSIC = "music"
    SFX = "sfx"
    VOICE = "voice"
    FONT = "font"
    THUMBNAIL = "thumbnail"


# ── Provider Types ────────────────────────────────────────────────────────────

class AIProviderType(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    LOCAL = "local"


class TTSProviderType(str, Enum):
    GTTS = "gtts"
    ELEVENLABS = "elevenlabs"
    GOOGLE_CLOUD = "google_cloud"
    LOCAL = "local"


class MusicProviderType(str, Enum):
    PROCEDURAL = "procedural"


class ImageProviderType(str, Enum):
    PROCEDURAL = "procedural"
    STABLE_DIFFUSION = "stable_diffusion"


# ── Character Animations ──────────────────────────────────────────────────────

class CharacterAction(str, Enum):
    IDLE = "idle"
    WALK = "walk"
    RUN = "run"
    SLEEP = "sleep"
    TALK = "talk"
    SIT = "sit"
    STAND = "stand"
    FALL = "fall"
    JUMP = "jump"
    ATTACK = "attack"
    SCARED = "scared"
    SHOCKED = "shocked"
    CONFUSED = "confused"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    DEAD = "dead"


class FacialExpression(str, Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    CONFUSED = "confused"
    SCARED = "scared"
    SHOCKED = "shocked"


CharacterExpression = FacialExpression


# ── Camera Movements ──────────────────────────────────────────────────────────

class CameraMovement(str, Enum):
    STATIC = "static"
    SLOW_ZOOM_IN = "slow_zoom_in"
    SLOW_ZOOM_OUT = "slow_zoom_out"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    TILT_UP = "tilt_up"
    TILT_DOWN = "tilt_down"
    SHAKE = "shake"
    DOLLY = "dolly"


# ── Mood / Music ──────────────────────────────────────────────────────────────

class Mood(str, Enum):
    NEUTRAL = "neutral"
    SUSPENSE = "suspense"
    DARK = "dark"
    HORROR = "horror"
    HAPPY = "happy"
    MYSTERIOUS = "mysterious"
    EMOTIONAL = "emotional"
    ENERGETIC = "energetic"
    CALM = "calm"


# ── Mouth States (lip sync) ───────────────────────────────────────────────────

class MouthState(str, Enum):
    IDLE = "idle"
    A = "a"
    E = "e"
    O = "o"
    U = "u"
    OPEN = "open"
