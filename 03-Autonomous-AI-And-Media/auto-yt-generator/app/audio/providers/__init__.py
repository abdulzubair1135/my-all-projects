"""
AUTO YT GENERATOR — TTS Provider Factory.
"""

from typing import Optional
from app.config import settings
from app.audio.provider import TTSProvider
from app.audio.providers.edge_tts_provider import EdgeTTSProvider
from app.audio.providers.pyttsx3_provider import Pyttsx3Provider
from app.audio.providers.elevenlabs_provider import ElevenLabsProvider
from app.audio.providers.mock_tts_provider import MockTTSProvider
from app.logger import logger


def get_tts_provider(provider_name: Optional[str] = None) -> TTSProvider:
    """Returns configured TTS provider with automatic graceful fallbacks."""
    target = (provider_name or settings.providers.tts_provider).lower()

    if "eleven" in target:
        return ElevenLabsProvider()

    if target in ["edge", "edgetts", "edge_tts", "gtts"]:
        try:
            import edge_tts
            return EdgeTTSProvider()
        except ImportError:
            logger.warning("edge_tts not found, falling back to pyttsx3/mock.")

    if target in ["pyttsx3", "local"]:
        try:
            import pyttsx3
            return Pyttsx3Provider()
        except Exception:
            logger.warning("pyttsx3 failed to initialize, using MockTTSProvider.")

    return MockTTSProvider()
