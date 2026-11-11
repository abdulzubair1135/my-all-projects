"""
AUTO YT GENERATOR — ElevenLabs TTS Provider.

High-end AI voice cloning and neural voice synthesis via ElevenLabs API.
Works when ELEVENLABS_API_KEY is configured in .env, with graceful fallback.
"""

import os
from pathlib import Path
from typing import Optional
import requests

from app.audio.provider import TTSProvider
from app.config import settings
from app.logger import logger


class ElevenLabsProvider(TTSProvider):
    """ElevenLabs TTS Provider for studio-grade voice cloning."""

    DEFAULT_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Adam / Rachel deep voice

    def __init__(self, voice_name: Optional[str] = None):
        super().__init__(voice_name=voice_name)
        self.api_key = settings.elevenlabs_api_key or os.getenv("ELEVENLABS_API_KEY")

    def generate_speech(
        self,
        text: str,
        output_path: str,
        language: str = "en",
        speed: float = 1.0,
    ) -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY not found. Falling back to Microsoft EdgeTTS.")
            from app.audio.providers.edge_tts_provider import EdgeTTSProvider
            return EdgeTTSProvider(voice_name=self.voice_name).generate_speech(
                text=text,
                output_path=output_path,
                language=language,
                speed=speed,
            )

        voice_id = self.voice_name or self.DEFAULT_VOICE_ID
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key,
        }

        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }

        logger.info(f"ElevenLabs synthesizing audio with voice '{voice_id}'...")
        response = requests.post(url, json=payload, headers=headers, timeout=60)

        if response.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path
        else:
            logger.error(f"ElevenLabs error ({response.status_code}): {response.text}")
            logger.info("Falling back to Microsoft EdgeTTS...")
            from app.audio.providers.edge_tts_provider import EdgeTTSProvider
            return EdgeTTSProvider().generate_speech(text, output_path, language, speed)
