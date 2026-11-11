"""
AUTO YT GENERATOR — Abstract TTS Provider Interface.

Defines the contract for Text-To-Speech providers (EdgeTTS, Pyttsx3, ElevenLabs, Google TTS).
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class TTSProvider(ABC):
    """Abstract interface for all Text-to-Speech audio providers."""

    def __init__(self, voice_name: Optional[str] = None):
        self.voice_name = voice_name

    @abstractmethod
    def generate_speech(
        self,
        text: str,
        output_path: str,
        language: str = "en",
        speed: float = 1.0,
    ) -> str:
        """Generates audio file from text and saves to output_path. Returns the path."""
        pass
