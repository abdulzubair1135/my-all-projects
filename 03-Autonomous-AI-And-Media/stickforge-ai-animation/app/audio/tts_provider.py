"""
Provider-independent Text-to-Speech (TTS) architecture for StickForge AI.
Supports Edge-TTS (online multilingual), Pyttsx3 (offline SAPI5), and Mock generators.
"""

from __future__ import annotations
import abc
import asyncio
import os
import wave
import struct
from pathlib import Path
from typing import Dict, Any, Optional, List

try:
    import edge_tts
except ImportError:
    edge_tts = None

from app.core.config import get_config
from app.core.logging_manager import get_logger

logger = get_logger("tts_provider")


class BaseTTSProvider(abc.ABC):
    """Abstract speech synthesis provider."""

    @abc.abstractmethod
    def synthesize(
        self,
        text: str,
        output_path: Path,
        voice: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz",
    ) -> float:
        """
        Synthesizes text into audio at output_path.
        Returns the duration of the audio in seconds.
        """
        pass

    @abc.abstractmethod
    def get_available_voices(self) -> List[Dict[str, str]]:
        pass


class EdgeTTSProvider(BaseTTSProvider):
    """High-quality Microsoft Edge neural speech synthesizer with seamless offline fallback."""

    _online_available: Optional[bool] = None

    def synthesize(
        self,
        text: str,
        output_path: Path,
        voice: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz",
    ) -> float:
        # If already determined offline during this session, use local TTS immediately
        if EdgeTTSProvider._online_available is False or not edge_tts:
            return Pyttsx3Provider().synthesize(text, output_path, voice=voice, rate=rate, pitch=pitch)

        valid_neural_voices = {
            "en-US-ChristopherNeural", "en-US-JennyNeural", "en-US-GuyNeural",
            "hi-IN-MadhurNeural", "hi-IN-SwaraNeural"
        }
        voice_name = voice
        if not voice_name or voice_name not in valid_neural_voices:
            # Check if text has Hindi/Hinglish keywords
            lower = text.lower()
            if any(k in lower for k in ["hai", "nahi", "tha", "uske", "kya", "aur", "toh", "kaise"]):
                voice_name = "hi-IN-MadhurNeural"
            else:
                voice_name = get_config().tts.default_voice_en or "en-US-ChristopherNeural"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        async def _run():
            communicate = edge_tts.Communicate(text=text, voice=voice_name, rate=rate, pitch=pitch)
            await communicate.save(str(output_path))

        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    new_loop = asyncio.new_event_loop()
                    new_loop.run_until_complete(_run())
                    new_loop.close()
                else:
                    loop.run_until_complete(_run())
            except RuntimeError:
                asyncio.run(_run())

            EdgeTTSProvider._online_available = True
            return self._measure_duration(output_path, text)

        except Exception as e:
            EdgeTTSProvider._online_available = False
            logger.info("Online speech service unavailable (network/403). Seamlessly activated Windows SAPI5 voice synthesizer.")
            try:
                return Pyttsx3Provider().synthesize(text, output_path, voice=voice, rate=rate, pitch=pitch)
            except Exception as e2:
                logger.info(f"Using synthetic audio generator for local testing.")
                return MockTTSProvider().synthesize(text, output_path, voice=voice, rate=rate, pitch=pitch)

    def get_available_voices(self) -> List[Dict[str, str]]:
        return [
            {"id": "en-US-ChristopherNeural", "name": "English (US) - Christopher (Male)", "lang": "en"},
            {"id": "en-US-JennyNeural", "name": "English (US) - Jenny (Female)", "lang": "en"},
            {"id": "hi-IN-MadhurNeural", "name": "Hindi / Hinglish - Madhur (Male)", "lang": "hi"},
            {"id": "hi-IN-SwaraNeural", "name": "Hindi / Hinglish - Swara (Female)", "lang": "hi"},
        ]

    def _measure_duration(self, audio_path: Path, text: str) -> float:
        """Inspect audio file or approximate duration based on word count."""
        try:
            from app.video.ffmpeg_manager import probe_media
            info = probe_media(audio_path)
            if info.get("duration", 0.0) > 0:
                return info["duration"]
        except Exception:
            pass
        # Fallback approximation: ~2.8 words per second + 0.5s pause
        words = len(text.split())
        return max(1.5, words / 2.8 + 0.5)


class Pyttsx3Provider(BaseTTSProvider):
    """Local offline TTS provider using SAPI5 on Windows."""

    def __init__(self):
        self._engine = None

    def _get_engine(self):
        import pyttsx3
        if self._engine is None:
            self._engine = pyttsx3.init()
        return self._engine

    def synthesize(
        self,
        text: str,
        output_path: Path,
        voice: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz",
    ) -> float:
        engine = self._get_engine()
        if voice:
            v_lower = voice.lower()
            try:
                for v in engine.getProperty("voices"):
                    if ("female" in v_lower or "zira" in v_lower or "swara" in v_lower or "jenny" in v_lower) and "zira" in v.name.lower():
                        engine.setProperty("voice", v.id)
                        break
                    elif ("male" in v_lower or "david" in v_lower or "madhur" in v_lower or "christopher" in v_lower) and "david" in v.name.lower():
                        engine.setProperty("voice", v.id)
                        break
            except Exception:
                pass

        output_path.parent.mkdir(parents=True, exist_ok=True)
        # pyttsx3 outputs WAV
        wav_path = output_path.with_suffix(".wav")
        engine.save_to_file(text, str(wav_path))
        engine.runAndWait()

        duration = 0.0
        if wav_path.exists():
            try:
                with wave.open(str(wav_path), "rb") as wf:
                    frames = wf.getnframes()
                    rate_hz = wf.getframerate()
                    duration = frames / float(rate_hz)
            except Exception:
                pass

        if duration <= 0.0:
            duration = max(1.5, len(text.split()) / 2.8 + 0.5)

        # Convert to requested format if not .wav
        if output_path.suffix.lower() != ".wav" and wav_path.exists():
            try:
                from app.video.ffmpeg_manager import run_ffmpeg_command
                run_ffmpeg_command(["-i", str(wav_path), "-c:a", "aac", "-b:a", "192k", str(output_path)])
            except Exception as e:
                logger.warning(f"Audio conversion to {output_path.suffix} failed: {e}")

        return duration

    def get_available_voices(self) -> List[Dict[str, str]]:
        engine = self._get_engine()
        voices = engine.getProperty("voices")
        return [{"id": v.id, "name": v.name, "lang": "en"} for v in voices]


class MockTTSProvider(BaseTTSProvider):
    """Generates synthetic WAV audio files locally for fast testing."""

    def synthesize(
        self,
        text: str,
        output_path: Path,
        voice: Optional[str] = None,
        rate: str = "+0%",
        pitch: str = "+0Hz",
    ) -> float:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        wav_path = output_path.with_suffix(".wav")

        # Estimate duration: ~3 words per second, min 1.0s
        duration = max(1.0, len(text.split()) / 3.0)
        sample_rate = 22050
        num_samples = int(duration * sample_rate)

        with wave.open(str(wav_path), "w") as f:
            f.setnchannels(1)  # Mono
            f.setsampwidth(2)  # 16-bit
            f.setframerate(sample_rate)
            # Write subtle 440Hz tone or silence
            data = bytearray()
            for i in range(num_samples):
                val = int(1200.0 * (1.0 if (i // 50) % 2 == 0 else -1.0))
                data.extend(struct.pack("<h", val))
            f.writeframes(data)

        # Convert to requested format if not .wav
        if output_path.suffix.lower() != ".wav" and wav_path.exists():
            try:
                from app.video.ffmpeg_manager import run_ffmpeg_command
                run_ffmpeg_command(["-i", str(wav_path), "-c:a", "aac", "-b:a", "192k", str(output_path)])
            except Exception as e:
                logger.warning(f"Audio conversion to {output_path.suffix} failed: {e}")

        return duration

    def get_available_voices(self) -> List[Dict[str, str]]:
        return [{"id": "mock_voice_1", "name": "Mock Test Voice", "lang": "en"}]


def get_tts_provider(provider_type: Optional[str] = None) -> BaseTTSProvider:
    ptype = provider_type or get_config().tts.default_provider
    if ptype == "edge_tts":
        return EdgeTTSProvider()
    elif ptype == "pyttsx3":
        return Pyttsx3Provider()
    elif ptype == "mock":
        return MockTTSProvider()
    return EdgeTTSProvider()
