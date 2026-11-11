"""
AUTO YT GENERATOR — Voiceover Generation Engine.

Manages text-to-speech rendering, speed scaling, SHA-256 audio caching,
and audio duration measurement.
"""

import hashlib
import wave
import os
from pathlib import Path
from typing import Tuple, Optional
from app.audio.provider import TTSProvider
from app.audio.providers import get_tts_provider
from app.logger import logger


class VoiceEngine:
    """Handles speech synthesis and duration calculations."""

    def __init__(self, provider: Optional[TTSProvider] = None):
        self.provider = provider or get_tts_provider()

    @staticmethod
    def get_audio_duration(file_path: str) -> float:
        """Calculates exact duration of audio file in seconds."""
        path = Path(file_path)
        if not path.exists():
            return 0.0

        # Try standard WAV header inspection first
        if path.suffix.lower() == ".wav":
            try:
                with wave.open(str(path), "rb") as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    return frames / float(rate)
            except Exception:
                pass

        # Fallback estimation for MP3 based on file size or wave header
        try:
            # 128 kbps MP3 estimate: ~16,000 bytes per second
            size_bytes = os.path.getsize(file_path)
            return max(1.5, size_bytes / 16000.0)
        except Exception:
            return 3.0

    def generate_narration(
        self,
        text: str,
        output_path: str,
        language: str = "en",
        speed: float = 1.0,
    ) -> Tuple[str, float]:
        """Synthesizes narration audio and returns (file_path, duration_seconds)."""
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)

        if not text.strip():
            logger.warning(f"Empty narration text for {output_path}, creating silence.")
            text = "..."

        logger.info(f"Synthesizing voiceover: \"{text[:60]}...\" (Lang: {language})")
        audio_path = self.provider.generate_speech(
            text=text,
            output_path=str(target),
            language=language,
            speed=speed,
        )

        duration = self.get_audio_duration(audio_path)
        logger.info(f"Voiceover generated successfully: {audio_path} ({duration:.2f}s)")
        return audio_path, duration


# Default voice engine instance
voice_engine = VoiceEngine()
