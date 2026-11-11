"""
AUTO YT GENERATOR — Pyttsx3 Offline Local TTS Provider.

Generates speech using the local OS speech engine (SAPI5 on Windows).
"""

from pathlib import Path
from typing import Optional
from app.audio.provider import TTSProvider
from app.logger import logger


class Pyttsx3Provider(TTSProvider):
    """Local offline TTS provider using pyttsx3."""

    def __init__(self, voice_name: Optional[str] = None):
        super().__init__(voice_name=voice_name)

    def generate_speech(
        self,
        text: str,
        output_path: str,
        language: str = "en",
        speed: float = 1.0,
    ) -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        import pyttsx3

        engine = pyttsx3.init()
        # Adjust rate
        base_rate = engine.getProperty("rate")
        engine.setProperty("rate", int(base_rate * speed))

        logger.info("Pyttsx3 generating offline speech audio...")
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        return output_path
