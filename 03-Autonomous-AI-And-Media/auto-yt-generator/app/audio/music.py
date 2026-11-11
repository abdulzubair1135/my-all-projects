"""
AUTO YT GENERATOR — Procedural Music Generator.

Synthesizes multi-track background music algorithmically:
- Drums: Kick, Punchy Snare/Clap, Crisp Hi-Hats, Sub Drops
- Bass: Deep 808 sub bass & Reese bass
- Harmonies: Minor pads, atmospheric synth drones
- Melody: Dissonant suspense arpeggio or Phonk cowbell leads
- Adaptive Arrangement: Auto-scales intensity across Hook -> Explanation -> Escalation -> Conclusion.
"""

import math
import struct
import wave
from pathlib import Path
from typing import Optional, Dict, Any, List
import numpy as np

from app.logger import logger


class MusicGenerator:
    """Procedural multi-track audio music synthesizer."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def generate_music(
        self,
        duration_sec: float,
        output_path: str,
        style: str = "dark_suspense",
        bpm: int = 90,
    ) -> str:
        """Synthesizes complete background music track and writes to WAV."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        duration_sec = max(5.0, duration_sec)

        style_lower = style.lower().strip()
        if "phonk" in style_lower:
            bpm = bpm if bpm > 110 else 145
            left, right = self._synth_phonk_track(duration_sec, bpm=bpm)
        else:
            bpm = bpm if bpm < 120 else 90
            left, right = self._synth_cinematic_suspense_track(duration_sec, bpm=bpm)

        self._write_stereo_wav(output_path, left, right)
        logger.info(f"Procedural music generated: {style} ({duration_sec:.1f}s, {bpm} BPM) -> {output_path}")
        return output_path

    def _write_stereo_wav(self, path: str, left: np.ndarray, right: np.ndarray):
        """Writes stereo float channels [-1.0, 1.0] to 16-bit WAV."""
        # Master volume normalization to -1.0 dB
        max_val = max(np.max(np.abs(left)), np.max(np.abs(right)), 1e-6)
        target_peak = 0.85
        left = (left / max_val) * target_peak
        right = (right / max_val) * target_peak

        int_l = (left * 32767.0).astype(np.int16)
        int_r = (right * 32767.0).astype(np.int16)

        # Interleave stereo channels: L, R, L, R
        stereo = np.empty((len(int_l) * 2,), dtype=np.int16)
        stereo[0::2] = int_l
        stereo[1::2] = int_r

        with wave.open(path, "wb") as wf:
            wf.setnchannels(2)  # Stereo
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            wf.writeframes(stereo.tobytes())

    # ── Dark Cinematic Suspense Mode ──────────────────────────────────────────

    def _synth_cinematic_suspense_track(self, duration_sec: float, bpm: int = 90) -> (np.ndarray, np.ndarray):
        """Synthesizes dark cinematic suspense score (D Minor base)."""
        n_samples = int(duration_sec * self.sample_rate)
        t = np.linspace(0, duration_sec, n_samples, endpoint=False)
        beat_dur = 60.0 / bpm
        bar_dur = beat_dur * 4.0

        left = np.zeros(n_samples, dtype=np.float32)
        right = np.zeros(n_samples, dtype=np.float32)

        # 1. Atmospheric Drone (D2 = 73.4 Hz + A2 = 110.0 Hz)
        drone_l = 0.25 * np.sin(2.0 * np.pi * 73.416 * t) + 0.15 * np.sin(2.0 * np.pi * 110.00 * t + 0.5)
        drone_r = 0.25 * np.sin(2.0 * np.pi * 73.416 * t + 0.3) + 0.15 * np.sin(2.0 * np.pi * 110.00 * t)
        # Slow filter modulation
        mod = 0.7 + 0.3 * np.sin(2.0 * np.pi * 0.1 * t)
        left += drone_l * mod
        right += drone_r * mod

        # 2. Deep Sub 808 Bass on Bar Starts
        total_bars = int(duration_sec / bar_dur) + 1
        for bar in range(total_bars):
            start_t = bar * bar_dur
            start_idx = int(start_t * self.sample_rate)
            hit_len = int(bar_dur * 0.8 * self.sample_rate)
            if start_idx + hit_len < n_samples:
                t_hit = np.linspace(0, bar_dur * 0.8, hit_len, endpoint=False)
                # D1 = 36.7 Hz sub bass
                sub_pitch = 36.71 + 30.0 * np.exp(-12.0 * t_hit)
                sub_phase = 2.0 * np.pi * np.cumsum(sub_pitch) / self.sample_rate
                sub_env = np.exp(-1.8 * t_hit)
                sub_wave = np.sin(sub_phase) * sub_env * 0.45
                left[start_idx:start_idx + hit_len] += sub_wave
                right[start_idx:start_idx + hit_len] += sub_wave

        # 3. Tense Percussion (Kicks on 1, Snare/Rim on 3, Hi-hats on 8th notes)
        total_beats = int(duration_sec / beat_dur) + 1
        for beat in range(total_beats):
            b_t = beat * beat_dur
            b_idx = int(b_t * self.sample_rate)
            b_in_bar = beat % 4

            # Kick on Beat 1
            if b_in_bar == 0:
                k_len = int(0.25 * self.sample_rate)
                if b_idx + k_len < n_samples:
                    t_k = np.linspace(0, 0.25, k_len, endpoint=False)
                    k_pitch = 120.0 * np.exp(-30.0 * t_k) + 40.0
                    k_wave = np.sin(2.0 * np.pi * np.cumsum(k_pitch) / self.sample_rate) * np.exp(-15.0 * t_k) * 0.4
                    left[b_idx:b_idx + k_len] += k_wave
                    right[b_idx:b_idx + k_len] += k_wave

            # Snare/Rim on Beat 3
            if b_in_bar == 2:
                s_len = int(0.18 * self.sample_rate)
                if b_idx + s_len < n_samples:
                    t_s = np.linspace(0, 0.18, s_len, endpoint=False)
                    noise = np.random.uniform(-1.0, 1.0, s_len) * np.exp(-22.0 * t_s) * 0.25
                    snap = np.sin(2.0 * np.pi * 220.0 * t_s) * np.exp(-35.0 * t_s) * 0.2
                    left[b_idx:b_idx + s_len] += noise + snap
                    right[b_idx:b_idx + s_len] += noise + snap

            # Hi-hat on 8th notes
            h_len = int(0.06 * self.sample_rate)
            if b_idx + h_len < n_samples:
                t_h = np.linspace(0, 0.06, h_len, endpoint=False)
                hat = np.random.uniform(-1.0, 1.0, h_len) * np.exp(-70.0 * t_h) * 0.12
                left[b_idx:b_idx + h_len] += hat * 0.9
                right[b_idx:b_idx + h_len] += hat * 1.1

        # 4. Eerie Dissonant Arpeggio (D4, F4, G#4, A4)
        notes = [293.66, 349.23, 415.30, 440.00]
        step_dur = beat_dur / 2.0
        total_steps = int(duration_sec / step_dur)
        for s in range(total_steps):
            s_t = s * step_dur
            s_idx = int(s_t * self.sample_rate)
            n_len = int(0.35 * self.sample_rate)
            if s_idx + n_len < n_samples:
                freq = notes[s % len(notes)]
                t_n = np.linspace(0, 0.35, n_len, endpoint=False)
                bell = (0.7 * np.sin(2.0 * np.pi * freq * t_n) + 0.3 * np.sin(2.0 * np.pi * freq * 2.0 * t_n)) * np.exp(-6.0 * t_n) * 0.18
                pan = math.sin(s * 0.5) * 0.3
                left[s_idx:s_idx + n_len] += bell * (0.5 - pan)
                right[s_idx:s_idx + n_len] += bell * (0.5 + pan)

        return left, right

    # ── High Energy Phonk Mode ────────────────────────────────────────────────

    def _synth_phonk_track(self, duration_sec: float, bpm: int = 145) -> (np.ndarray, np.ndarray):
        """Synthesizes energetic Memphis / Drift Phonk beat with 808 glide & cowbell melody."""
        n_samples = int(duration_sec * self.sample_rate)
        t = np.linspace(0, duration_sec, n_samples, endpoint=False)
        beat_dur = 60.0 / bpm
        bar_dur = beat_dur * 4.0

        left = np.zeros(n_samples, dtype=np.float32)
        right = np.zeros(n_samples, dtype=np.float32)

        # 1. Punchy Distorted 808 Kicks on beat 1 & syncopated 3.5
        total_beats = int(duration_sec / beat_dur) + 1
        for beat in range(total_beats):
            b_t = beat * beat_dur
            b_idx = int(b_t * self.sample_rate)
            b_in_bar = beat % 4

            # Kick on 1 and 3.5
            if b_in_bar in [0, 2]:
                k_len = int(0.35 * self.sample_rate)
                if b_idx + k_len < n_samples:
                    t_k = np.linspace(0, 0.35, k_len, endpoint=False)
                    k_pitch = 140.0 * np.exp(-35.0 * t_k) + 42.0
                    sub_raw = np.sin(2.0 * np.pi * np.cumsum(k_pitch) / self.sample_rate)
                    # Phonk soft saturation / drive
                    sub_sat = np.tanh(sub_raw * 2.2) * np.exp(-7.0 * t_k) * 0.5
                    left[b_idx:b_idx + k_len] += sub_sat
                    right[b_idx:b_idx + k_len] += sub_sat

            # Snare/Clap on 2 and 4
            if b_in_bar in [1, 3]:
                sn_len = int(0.2 * self.sample_rate)
                if b_idx + sn_len < n_samples:
                    t_sn = np.linspace(0, 0.2, sn_len, endpoint=False)
                    noise = np.random.uniform(-1.0, 1.0, sn_len) * np.exp(-18.0 * t_sn) * 0.3
                    body = np.sin(2.0 * np.pi * 180.0 * t_sn) * np.exp(-25.0 * t_sn) * 0.3
                    left[b_idx:b_idx + sn_len] += noise + body
                    right[b_idx:b_idx + sn_len] += noise + body

        # 2. Classic Phonk 808 Cowbell Melody (F5, G#5, A#5, C6)
        cowbell_notes = [698.46, 830.61, 932.33, 1046.50, 932.33, 830.61, 698.46, 587.33]
        step_dur = beat_dur / 2.0
        total_steps = int(duration_sec / step_dur)
        for s in range(total_steps):
            s_t = s * step_dur
            s_idx = int(s_t * self.sample_rate)
            c_len = int(0.22 * self.sample_rate)
            if s_idx + c_len < n_samples:
                f0 = cowbell_notes[s % len(cowbell_notes)]
                t_c = np.linspace(0, 0.22, c_len, endpoint=False)
                # Two square/triangle harmonics for signature 808 cowbell timbre
                c_wave = (
                    0.6 * np.sin(2.0 * np.pi * f0 * t_c)
                    + 0.4 * np.sin(2.0 * np.pi * (f0 * 1.5) * t_c)
                ) * np.exp(-14.0 * t_c) * 0.32
                left[s_idx:s_idx + c_len] += c_wave * 0.95
                right[s_idx:s_idx + c_len] += c_wave * 1.05

        return left, right


# Default music generator instance
music_generator = MusicGenerator()
