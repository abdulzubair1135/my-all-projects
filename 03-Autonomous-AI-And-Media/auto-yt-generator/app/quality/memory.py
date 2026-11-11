"""
AUTO YT GENERATOR — Persistent Quality Rules Memory.

Stores learned video quality standards and stylistic guidelines across project runs.
"""

import json
from pathlib import Path
from typing import Dict, Any

from app.config import settings
from app.logger import logger


class QualityMemory:
    """Maintains persistent quality memory and learned heuristics."""

    DEFAULT_RULES = {
        "min_visual_change_frequency_sec": 4.5,
        "recommended_cutaway_ratio": 0.25,
        "prefer_word_bounce_captions": True,
        "audio_ducking_attenuation_db": -12.0,
        "default_voice_speed": 1.05,
        "min_quality_score_target": 80,
    }

    def __init__(self, memory_path: str = "quality_rules.json"):
        self.memory_path = Path(memory_path)
        self.rules: Dict[str, Any] = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        if self.memory_path.exists():
            try:
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not read {self.memory_path}: {e}")
        return dict(self.DEFAULT_RULES)

    def save_rules(self):
        try:
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(self.rules, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to persist {self.memory_path}: {e}")

    def update_rule(self, key: str, value: Any):
        self.rules[key] = value
        self.save_rules()


# Default quality memory instance
quality_memory = QualityMemory()
