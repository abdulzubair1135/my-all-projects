"""
AUTO YT GENERATOR — Procedural SFX (Sound Effects) Engine.

Synthesizes frame-accurate sound effects mathematically using NumPy and Python's wave module:
- whoosh (bandpass filtered noise sweep)
- impact / sub_bass_drop (exponential sub pitch dive)
- heartbeat (acoustic lub-dub double thud)
- clock_ticking (sharp mechanical metallic transient)
- flatline_beep (continuous medical telemetry tone)
- power_down_hum / glitch (frequency modulated decay)
"""

import math
import struct
import wave
from pathlib import Path
from typing import Optional
import numpy as np

from app.logger import logger


class SFXGenerator:
    """Procedural audio synthesizer for sound effects."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def generate_sfx(self, sfx_id: str, output_path: str, duration_sec: Optional[float] = None) -> str:
        """Synthesizes sound effect based on identifier and writes to WAV file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        s_id = sfx_id.lower().strip()

        if "whoosh" in s_id or "transition" in s_id or "fadeout" in s_id:
            dur = duration_sec or 1.2
            samples = self._synth_whoosh(dur)
        elif "heartbeat" in s_id or "heart" in s_id:
            dur = duration_sec or 2.0
            samples = self._synth_heartbeat(dur)
        elif "clock" in s_id or "tick" in s_id:
            dur = duration_sec or 1.0
            samples = self._synth_clock_tick(dur)
        elif "flatline" in s_id or "beep" in s_id:
            dur = duration_sec or 2.5
            samples = self._synth_flatline(dur)
        elif "glitch" in s_id or "power_down" in s_id:
            dur = duration_sec or 1.0
            samples = self._synth_glitch(dur)
        elif "drop" in s_id or "impact" in s_id or "hit" in s_id or "sub_bass" in s_id:
            dur = duration_sec or 1.5
            samples = self._synth_sub_drop(dur)
        else:
            # Default cinematic ambient chime
            dur = duration_sec or 1.5
            samples = self._synth_chime(dur)

        self._write_wav(output_path, samples)
        logger.debug(f"Generated procedural SFX: {sfx_id} -> {output_path}")
        return output_path

    def _write_wav(self, path: str, samples: np.ndarray):
        """Writes float array [-1.0, 1.0] to 16-bit PCM WAV."""
        # Normalize and clip
        max_val = np.max(np.abs(samples))
        if max_val > 0:
            samples = samples / max_val * 0.95

        int_samples = (samples * 32767.0).astype(np.int16)

        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(int_samples.tobytes())

    def _synth_whoosh(self, duration: float) -> np.ndarray:
        """Noise sweep creating aerodynamic whoosh."""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        noise = np.random.uniform(-1.0, 1.0, n_samples)

        # Bell-shaped volume envelope
        envelope = np.sin(np.pi * (t / duration)) ** 2

        # Modulated lowpass filter simulation
        cutoff = 200.0 + 3000.0 * envelope
        carrier = np.sin(2.0 * np.pi * cutoff * t)
        return noise * envelope * 0.7 + carrier * envelope * 0.3

    def _synth_sub_drop(self, duration: float) -> np.ndarray:
        """Heavy sub bass impact dive (150 Hz -> 35 Hz)."""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        # Exponential frequency glide
        freq = 160.0 * np.exp(-3.5 * t) + 35.0
        phase = 2.0 * np.pi * np.cumsum(freq) / self.sample_rate
        decay = np.exp(-2.5 * t)
        # Add slight sub distortion
        sub = np.sin(phase) + 0.2 * np.sin(2.0 * phase)
        return sub * decay

    def _synth_heartbeat(self, duration: float) -> np.ndarray:
        """Realistic acoustic double pulse (lub-dub)."""
        n_samples = int(duration * self.sample_rate)
        out = np.zeros(n_samples, dtype=np.float32)

        # Pulse 1 (Lub) at t=0.1s, Pulse 2 (Dub) at t=0.35s
        for p_time, amp, f_base in [(0.1, 1.0, 55.0), (0.35, 0.75, 65.0)]:
            p_idx = int(p_time * self.sample_rate)
            p_len = int(0.18 * self.sample_rate)
            if p_idx + p_len < n_samples:
                t_sub = np.linspace(0, 0.18, p_len, endpoint=False)
                sub_wave = np.sin(2.0 * np.pi * f_base * t_sub)
                env = np.sin(np.pi * (t_sub / 0.18)) ** 2
                out[p_idx:p_idx + p_len] += sub_wave * env * amp

        return out

    def _synth_clock_tick(self, duration: float) -> np.ndarray:
        """High-frequency metallic mechanical click."""
        n_samples = int(duration * self.sample_rate)
        out = np.zeros(n_samples, dtype=np.float32)

        tick_len = int(0.02 * self.sample_rate)
        t_tick = np.linspace(0, 0.02, tick_len, endpoint=False)
        click = np.sin(2.0 * np.pi * 3200.0 * t_tick) * np.exp(-250.0 * t_tick)
        out[:tick_len] = click
        return out

    def _synth_flatline(self, duration: float) -> np.ndarray:
        """Continuous hospital cardiac monitor emergency tone (1000 Hz)."""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        return np.sin(2.0 * np.pi * 1000.0 * t) * 0.4

    def _synth_glitch(self, duration: float) -> np.ndarray:
        """Frequency-modulated digital glitch with bitcrush."""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        mod = np.sin(2.0 * np.pi * 80.0 * t) * 800.0
        carrier = np.sin(2.0 * np.pi * (400.0 + mod) * t)
        noise = np.random.choice([-1.0, 0.0, 1.0], size=n_samples)
        env = np.exp(-3.0 * t)
        return (carrier * 0.7 + noise * 0.3) * env

    def _synth_chime(self, duration: float) -> np.ndarray:
        """Atmospheric melodic chime tone."""
        n_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, n_samples, endpoint=False)
        chime = (
            0.5 * np.sin(2.0 * np.pi * 587.33 * t)  # D5
            + 0.3 * np.sin(2.0 * np.pi * 880.00 * t)  # A5
            + 0.2 * np.sin(2.0 * np.pi * 1174.66 * t)  # D6
        )
        return chime * np.exp(-2.0 * t)


# Default SFX generator instance
sfx_generator = SFXGenerator()
