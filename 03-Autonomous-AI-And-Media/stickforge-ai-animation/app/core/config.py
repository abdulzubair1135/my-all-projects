"""
Application configuration management for StickForge AI.
Handles paths, persistent settings, and non-secret defaults.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Dict
from pydantic import BaseModel, Field


# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
APP_DIR = PROJECT_ROOT / "app"
ASSETS_DIR = PROJECT_ROOT / "assets"
PROJECTS_DIR = PROJECT_ROOT / "projects"
BROWSER_USER_DATA_DIR = PROJECT_ROOT / "browser" / "user_data"
LOGS_DIR = PROJECT_ROOT / "logs"
CACHE_DIR = PROJECT_ROOT / "cache"
OUTPUT_DIR = PROJECT_ROOT / "output"
CONFIG_FILE = PROJECT_ROOT / "config.json"
DATABASE_PATH = PROJECT_ROOT / "stickforge.db"


class VideoSettings(BaseModel):
    default_resolution_w: int = 1080
    default_resolution_h: int = 1920
    default_fps: int = 30
    preview_scale: float = 0.5  # 540x960 for fast preview
    max_concurrent_renders: int = 1
    crf: int = 22
    preset: str = "medium"


class AISettings(BaseModel):
    provider: str = "deepseek_browser"  # deepseek_browser, deepseek_api, mock
    deepseek_api_base_url: str = "https://api.deepseek.com/v1"
    deepseek_api_key: str = ""  # Loaded from env or user entered
    request_timeout_seconds: int = 120
    continue_max_retries: int = 10
    continue_debounce_seconds: float = 2.5


class BrowserSettings(BaseModel):
    headless: bool = False  # Always visible by default
    slow_mo_ms: int = 50
    user_data_dir: str = str(BROWSER_USER_DATA_DIR)
    viewport_width: int = 1280
    viewport_height: int = 800
    deepseek_url: str = "https://chat.deepseek.com"
    navigation_timeout_ms: int = 45000


class TTSSettings(BaseModel):
    default_provider: str = "edge_tts"  # edge_tts, pyttsx3
    default_voice_en: str = "en-US-ChristopherNeural"
    default_voice_hi: str = "hi-IN-MadhurNeural"
    default_voice_hinglish: str = "hi-IN-MadhurNeural"
    rate: str = "+0%"
    pitch: str = "+0Hz"
    volume: str = "+0%"


class ResourceSettings(BaseModel):
    max_cache_mb: int = 2048
    auto_cleanup_cache: bool = True
    keep_intermediate_scenes: bool = True


class AppConfig(BaseModel):
    app_name: str = "StickForge AI"
    version: str = "1.0.0"
    theme: str = "dark"
    video: VideoSettings = Field(default_factory=VideoSettings)
    ai: AISettings = Field(default_factory=AISettings)
    browser: BrowserSettings = Field(default_factory=BrowserSettings)
    tts: TTSSettings = Field(default_factory=TTSSettings)
    resource: ResourceSettings = Field(default_factory=ResourceSettings)

    def save(self, filepath: Path = CONFIG_FILE) -> None:
        """Persist config safely with indentation."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        temp_file = filepath.with_suffix(".tmp")
        # Mask any potential sensitive key before saving to common config
        data = self.model_dump()
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        if temp_file.exists():
            temp_file.replace(filepath)

    @classmethod
    def load(cls, filepath: Path = CONFIG_FILE) -> AppConfig:
        """Load from JSON file, falling back to defaults if not found."""
        if not filepath.exists():
            config = cls()
            config.save(filepath)
            return config
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.model_validate(data)
        except Exception:
            # Corrupted config: return safe default without crashing
            return cls()


# Singleton instance
_config_instance: AppConfig | None = None


def get_config() -> AppConfig:
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig.load()
    return _config_instance


def save_config(config: AppConfig) -> None:
    global _config_instance
    _config_instance = config
    config.save()
