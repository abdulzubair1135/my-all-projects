"""
AUTO YT GENERATOR — Configuration Manager.

Loads global settings from config.json and overrides from environment variables / .env.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from app.logger import logger
from app.constants import CONFIG_FILE

# Load .env into environment
load_dotenv()


class AppSettings(BaseModel):
    name: str = "AUTO YT GENERATOR"
    version: str = "0.1.0"
    env: str = "development"


class ProviderSettings(BaseModel):
    ai_provider: str = "gemini"
    tts_provider: str = "gtts"
    image_provider: str = "procedural"
    music_provider: str = "procedural"
    sfx_provider: str = "procedural"


class VideoSettings(BaseModel):
    default_resolution: str = "1920x1080"
    default_fps: int = 30
    default_duration: int = 300
    supported_resolutions: List[str] = ["1920x1080", "1280x720", "1080x1920"]


class AudioSettings(BaseModel):
    sample_rate: int = 44100
    channels: int = 2
    voice_volume: float = 1.0
    music_volume: float = 0.35
    sfx_volume: float = 0.6
    ducking_ratio: float = 0.25


class StyleSettings(BaseModel):
    available: List[str] = [
        "dark_cartoon",
        "dark_science",
        "weird_science",
        "horror_science",
        "funny_science",
        "documentary",
        "educational",
        "mystery",
        "custom",
    ]
    default: str = "dark_cartoon"


class LanguageSettings(BaseModel):
    available: List[str] = ["en", "hi", "ur"]
    default: str = "en"


class CacheSettings(BaseModel):
    enabled: bool = True
    ttl_seconds: int = 86400
    max_size_mb: int = 1024


class PipelineSettings(BaseModel):
    max_retries: int = 3
    retry_delay_seconds: int = 5
    preview_resolution: str = "640x360"


class PathSettings(BaseModel):
    projects_dir: str = "projects"
    assets_dir: str = "assets"
    output_dir: str = "output"
    logs_dir: str = "logs"
    cache_dir: str = ".cache"


class Config(BaseModel):
    """Global validated configuration schema."""

    app: AppSettings = Field(default_factory=AppSettings)
    providers: ProviderSettings = Field(default_factory=ProviderSettings)
    video: VideoSettings = Field(default_factory=VideoSettings)
    audio: AudioSettings = Field(default_factory=AudioSettings)
    styles: StyleSettings = Field(default_factory=StyleSettings)
    languages: LanguageSettings = Field(default_factory=LanguageSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    pipeline: PipelineSettings = Field(default_factory=PipelineSettings)
    paths: PathSettings = Field(default_factory=PathSettings)

    # API Keys loaded safely from environment
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    google_cloud_tts_key: Optional[str] = None


def load_config(config_path: Optional[str] = None) -> Config:
    """Loads config.json and overlays environment variables securely."""
    target_path = Path(config_path or CONFIG_FILE)
    config_dict: Dict[str, Any] = {}

    if target_path.exists():
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                config_dict = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to parse {target_path}, falling back to defaults: {e}")
    else:
        logger.info(f"{target_path} not found, using default configuration.")

    config = Config(**config_dict)

    # Inject environment variables safely
    config.gemini_api_key = os.getenv("GEMINI_API_KEY")
    config.openai_api_key = os.getenv("OPENAI_API_KEY")
    config.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
    config.google_cloud_tts_key = os.getenv("GOOGLE_CLOUD_TTS_KEY")

    if os.getenv("APP_ENV"):
        config.app.env = os.getenv("APP_ENV")

    # Ensure required base directory structure exists
    for dir_path in [
        config.paths.projects_dir,
        config.paths.assets_dir,
        config.paths.output_dir,
        config.paths.logs_dir,
        config.paths.cache_dir,
    ]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    return config


# Global singleton instance
settings = load_config()
