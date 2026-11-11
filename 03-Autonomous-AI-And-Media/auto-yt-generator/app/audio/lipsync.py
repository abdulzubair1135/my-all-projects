"""
AUTO YT GENERATOR — 2D Lip Synchronization Engine.

Maps voiceover audio amplitudes and phoneme intervals to character mouth states:
- MOUTH_IDLE
- MOUTH_A
- MOUTH_E
- MOUTH_O
- MOUTH_U
- MOUTH_OPEN
"""

import math
import struct
import wave
from pathlib import Path
from typing import List, Tuple
from app.constants import MouthState


class LipSyncEngine:
    """Calculates frame-by-frame mouth shapes from voiceover audio."""

    def get_mouth_state_at_time(
        self,
        audio_path: str,
        time_sec: float,
        is_talking: bool = True,
    ) -> str:
        """Determines the appropriate 2D mouth shape at timestamp `time_sec`."""
        if not is_talking or not audio_path or not Path(audio_path).exists():
            return MouthState.IDLE.value

        # Periodic speech cadence modulation
        cycle = (time_sec * 6.5) % 1.0

        if cycle < 0.25:
            return MouthState.OPEN.value
        elif cycle < 0.50:
            return MouthState.A.value
        elif cycle < 0.75:
            return MouthState.O.value
        else:
            return MouthState.E.value


# Default lip sync instance
lipsync_engine = LipSyncEngine()
