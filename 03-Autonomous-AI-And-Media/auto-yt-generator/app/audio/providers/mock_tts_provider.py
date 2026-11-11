"""
AUTO YT GENERATOR — Synthetic Offline Mock TTS Provider.

Generates valid WAV audio files using Python's built-in standard library.
Ensures 100% reliable execution in testing and offline environments.
"""

import math
import struct
import wave
from pathlib import Path
from typing import Optional
from app.audio.provider import TTSProvider
from app.logger import logger


class MockTTSProvider(TTSProvider):
    """Synthetic TTS provider that generates valid audio wave files."""

    def __init__(self, voice_name: Optional[str] = "synthetic-narrator"):
        super().__init__(voice_name=voice_name)

    def generate_speech(
        self,
        text: str,
        output_path: str,
        language: str = "en",
        speed: float = 1.0,
    ) -> str:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        # Approximate duration: ~150 words per minute -> 2.5 words per second
        word_count = max(1, len(text.split()))
        duration_sec = max(1.5, word_count / (2.5 * speed))

        sample_rate = 22050
        num_samples = int(duration_sec * sample_rate)

        # Generate a gentle documentary narration tone (~150 Hz base frequency with harmonic)
        with wave.open(output_path, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)

            raw_data = bytearray()
            for i in range(num_samples):
                t = i / sample_rate
                # Subtle modulation simulating speech cadence
                envelope = 0.5 * (1.0 + math.sin(2.0 * math.pi * 3.0 * t))
                val = int(
                    (0.7 * math.sin(2.0 * math.pi * 140.0 * t) + 0.3 * math.sin(2.0 * math.pi * 280.0 * t))
                    * envelope
                    * 16000
                )
                raw_data.extend(struct.pack("<h", val))

            wav_file.writeframes(raw_data)

        logger.debug(f"MockTTS generated {duration_sec:.2f}s audio at {output_path}")
        return output_path
