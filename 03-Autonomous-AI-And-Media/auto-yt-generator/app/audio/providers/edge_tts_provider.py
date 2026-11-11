"""
AUTO YT GENERATOR — Microsoft Edge TTS Provider.

Generates high-quality natural neural voiceover audio in English, Hindi, Urdu, etc.
"""

import asyncio
from pathlib import Path
from typing import Optional
from app.audio.provider import TTSProvider
from app.logger import logger


class EdgeTTSProvider(TTSProvider):
    """Edge TTS provider supporting multilingual neural voices."""

    VOICE_MAP = {
        "en": "en-US-ChristopherNeural",       # Deep documentary male
        "en_female": "en-US-JennyNeural",
        "hi": "hi-IN-MadhurNeural",            # Natural Hindi documentary male
        "hi_female": "hi-IN-SwaraNeural",
        "ur": "ur-PK-AsadNeural",              # Natural Urdu male
    }

    def __init__(self, voice_name: Optional[str] = None):
        super().__init__(voice_name=voice_name)

    def _get_voice_for_language(self, language: str) -> str:
        if self.voice_name:
            return self.voice_name
        return self.VOICE_MAP.get(language.lower(), "en-US-ChristopherNeural")

    async def _async_generate(self, text: str, output_path: str, voice: str, rate_str: str):
        import edge_tts
        communicate = edge_tts.Communicate(text, voice, rate=rate_str)
        await communicate.save(output_path)

    def generate_speech(
        self,
        text: str,
        output_path: str,
        language: str = "en",
        speed: float = 1.0,
    ) -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        voice = self._get_voice_for_language(language)

        # Format speed percentage (e.g. +0%, +10%, -10%)
        rate_diff = int((speed - 1.0) * 100)
        rate_str = f"{rate_diff:+d}%"

        logger.info(f"EdgeTTS generating audio with voice '{voice}' (rate: {rate_str})...")

        try:
            # Run asynchronous edge-tts call
            asyncio.run(self._async_generate(text, output_path, voice, rate_str))
            return output_path
        except Exception as e:
            logger.error(f"EdgeTTS failed: {e}")
            raise
