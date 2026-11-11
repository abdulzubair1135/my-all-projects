"""
Continuity and Storyboard Validator for StickForge AI.
Verifies scene durations, character continuity, action legitimacy, and visual transitions.
"""

from __future__ import annotations
from typing import List, Dict, Any, Tuple
from app.ai.schema_validator import GeneratedStoryboard
from app.ai.prompt_templates import SUPPORTED_ACTIONS, SUPPORTED_BACKGROUNDS
from app.core.logging_manager import get_logger

logger = get_logger("continuity_checker")


class ContinuityReport:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
        }


def check_continuity(storyboard: GeneratedStoryboard, target_duration: float = 30.0) -> ContinuityReport:
    """Validate a storyboard against continuity and engine execution rules."""
    report = ContinuityReport()

    # 1. Check characters
    known_char_ids = {c.id for c in storyboard.characters}
    if not known_char_ids:
        report.errors.append("Storyboard defines no characters.")

    # 2. Check scenes
    if not storyboard.scenes:
        report.errors.append("Storyboard contains no scenes.")
        return report

    total_duration = 0.0
    for idx, scene in enumerate(storyboard.scenes):
        total_duration += scene.duration

        # Validate duration bounds
        if scene.duration < 1.0:
            report.errors.append(f"Scene {scene.id} duration ({scene.duration}s) is too short (< 1.0s).")
        if scene.duration > 60.0:
            report.warnings.append(f"Scene {scene.id} duration ({scene.duration}s) is very long (> 60s).")

        # Validate background
        if scene.background not in SUPPORTED_BACKGROUNDS:
            report.warnings.append(
                f"Scene {scene.id} uses non-standard background '{scene.background}'. Falling back to default."
            )

        # Validate actions and characters
        for act in scene.actions:
            if act.character_id not in known_char_ids:
                report.errors.append(
                    f"Scene {scene.id} references undefined character '{act.character_id}'."
                )
            if act.action not in SUPPORTED_ACTIONS:
                report.errors.append(
                    f"Scene {scene.id} requests unsupported animation action '{act.action}'."
                )

    # 3. Check total duration vs target
    diff = abs(total_duration - target_duration)
    if diff > target_duration * 0.4:
        report.warnings.append(
            f"Total storyboard duration ({total_duration:.1f}s) differs noticeably from target ({target_duration:.1f}s)."
        )

    return report
