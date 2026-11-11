"""
AUTO YT GENERATOR — Acting & Character Reaction Director.

Translates semantic narrative cues into frame-accurate character acting:
- Gestures (pointing, thinking, explaining, panic, freeze, shrug)
- Facial Expressions (confused, scared, shocked, curious, happy)
- Eye Gaze Direction (looking at diagrams, looking up in thought, direct eye contact)
- Dynamic Staging (Rule of thirds positioning, scale, depth)
"""

from typing import Tuple
from app.models.scene import SemanticCue, SceneAction, ActingGesture, EyeGaze, FacialExpression, CharacterAction


class ActingDirector:
    """Directs character performance, gestures, and reactions according to narrative beats."""

    def direct_acting_performance(
        self,
        semantic: SemanticCue,
        character_id: str,
        duration_sec: float,
        is_infographic_present: bool = False,
    ) -> SceneAction:
        """Determines the exact acting gesture, expression, gaze, and staging."""
        emotion = semantic.emotion
        intent = semantic.intent

        # 1. Determine Gesture & Expression
        gesture = ActingGesture.TALK_EXPLAIN
        expression = FacialExpression.NEUTRAL.value
        action = CharacterAction.TALK.value
        gaze = EyeGaze.DIRECT

        if emotion == "fear":
            gesture = ActingGesture.PANIC_HANDS
            expression = FacialExpression.SCARED.value
            action = CharacterAction.SCARED.value
            gaze = EyeGaze.UP
        elif emotion == "shock":
            gesture = ActingGesture.SHOCK_FREEZE
            expression = FacialExpression.SHOCKED.value
            action = CharacterAction.SHOCKED.value
            gaze = EyeGaze.DIRECT
        elif emotion == "curiosity" or intent == "question":
            gesture = ActingGesture.THINK_CURIOUS
            expression = FacialExpression.CONFUSED.value
            action = CharacterAction.CONFUSED.value
            gaze = EyeGaze.UP
        elif emotion == "urgency" or intent == "escalate":
            gesture = ActingGesture.TALK_EXPLAIN
            expression = FacialExpression.SCARED.value
            action = CharacterAction.TALK.value
            gaze = EyeGaze.DIRECT
        elif intent == "hook":
            gesture = ActingGesture.EXCITED_WAVE
            expression = FacialExpression.SHOCKED.value
            action = CharacterAction.TALK.value
            gaze = EyeGaze.DIRECT
        elif intent == "conclude":
            gesture = ActingGesture.SHRUG
            expression = FacialExpression.NEUTRAL.value
            action = CharacterAction.TALK.value
            gaze = EyeGaze.DIRECT

        # If an infographic / prop is present on the right side, point towards it
        if is_infographic_present:
            gesture = ActingGesture.POINT_RIGHT
            gaze = EyeGaze.RIGHT
            pos_x = 28.0  # Stage character on left side (Rule of Thirds)
            scale = 0.95
        else:
            # Vary staging across center and rule-of-thirds
            if intent in ["hook", "shock"]:
                pos_x = 50.0  # Center dramatic framing
                scale = 1.25  # Close-up punch
            elif intent == "question":
                pos_x = 38.0  # Off-center thinking pose
                scale = 1.05
            else:
                pos_x = 62.0  # Right third
                scale = 1.0

        pos_y = 55.0

        return SceneAction(
            entity_id=character_id,
            action=action,
            gesture=gesture,
            expression=expression,
            gaze=gaze,
            start_time_sec=0.0,
            duration_sec=duration_sec,
            position_x_percent=pos_x,
            position_y_percent=pos_y,
            scale=scale,
        )


# Default acting director instance
acting_director = ActingDirector()
