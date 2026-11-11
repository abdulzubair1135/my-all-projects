"""
Procedural Motion Library for StickForge AI.
Computes frame-by-frame joint angles and root displacements for all supported actions.
"""

from __future__ import annotations
import math
from typing import Tuple, Dict, Any
from app.animation.skeleton import JointAngles
from app.animation.pose import (
    POSE_STAND, POSE_SIT, POSE_WALK_1, POSE_WALK_2,
    POSE_RUN_1, POSE_RUN_2, POSE_JUMP_APEX, POSE_WAVE_1, POSE_WAVE_2,
    POSE_POINT, POSE_HAPPY, POSE_SAD, POSE_FIGHT_PUNCH, POSE_FIGHT_KICK,
)


def get_pose_and_offset(
    action: str,
    normalized_t: float,
    duration: float,
    params: Dict[str, Any] | None = None,
) -> Tuple[JointAngles, float, float]:
    """
    Returns (JointAngles, root_delta_x, root_delta_y) at time progress normalized_t (0.0 to 1.0).
    """
    params = params or {}
    t = max(0.0, min(1.0, normalized_t))
    speed = float(params.get("speed", 1.0))
    direction = 1.0 if params.get("direction", "right") == "right" else -1.0

    action = action.lower()

    if action == "stand":
        # Subtle breathing idle bob
        bob = math.sin(t * duration * 2.5) * 2.0
        return POSE_STAND, 0.0, bob

    elif action == "sit":
        # Transition from stand to sit in first 30%, then hold
        blend = min(1.0, t / 0.3)
        angles = POSE_STAND.lerp(POSE_SIT, blend)
        delta_y = blend * 35.0  # Lower pelvis to sitting height
        return angles, 0.0, delta_y

    elif action == "walk":
        # Walk cycle at ~2 steps per second
        freq = 2.0 * speed
        cycle = (t * duration * freq) % 1.0
        # Ping-pong lerp between WALK_1 and WALK_2
        phase = math.sin(cycle * 2.0 * math.pi) * 0.5 + 0.5
        angles = POSE_WALK_1.lerp(POSE_WALK_2, phase)
        # Translation across ground
        total_dist = 160.0 * duration * speed * direction
        dx = t * total_dist
        # Vertical footstep bounce
        dy = -abs(math.sin(cycle * 2.0 * math.pi)) * 6.0
        return angles, dx, dy

    elif action == "run":
        # Run cycle at ~3.5 strides per second
        freq = 3.5 * speed
        cycle = (t * duration * freq) % 1.0
        phase = math.sin(cycle * 2.0 * math.pi) * 0.5 + 0.5
        angles = POSE_RUN_1.lerp(POSE_RUN_2, phase)
        total_dist = 320.0 * duration * speed * direction
        dx = t * total_dist
        dy = -abs(math.sin(cycle * 2.0 * math.pi)) * 14.0
        return angles, dx, dy

    elif action == "jump":
        # Parabolic jump arc: apex at t = 0.5
        apex_height = float(params.get("height", 90.0))
        # dy = -4 * H * t * (1 - t)
        dy = -4.0 * apex_height * t * (1.0 - t)
        dx = t * (120.0 * speed * direction)

        if t < 0.2:
            # Crouch into jump
            angles = POSE_STAND.lerp(POSE_JUMP_APEX, t / 0.2)
        elif t < 0.8:
            angles = POSE_JUMP_APEX
        else:
            # Landing
            angles = POSE_JUMP_APEX.lerp(POSE_STAND, (t - 0.8) / 0.2)
        return angles, dx, dy

    elif action == "wave":
        freq = 3.0 * speed
        phase = math.sin(t * duration * freq * 2.0 * math.pi) * 0.5 + 0.5
        angles = POSE_WAVE_1.lerp(POSE_WAVE_2, phase)
        return angles, 0.0, 0.0

    elif action == "point":
        blend = min(1.0, t / 0.2)
        angles = POSE_STAND.lerp(POSE_POINT, blend)
        return angles, 0.0, 0.0

    elif action == "happy":
        # Joyful bouncing with raised arms
        cycle = (t * duration * 3.0) % 1.0
        bounce = -abs(math.sin(cycle * math.pi)) * 25.0
        return POSE_HAPPY, 0.0, bounce

    elif action == "sad":
        blend = min(1.0, t / 0.4)
        angles = POSE_STAND.lerp(POSE_SAD, blend)
        return angles, 0.0, 8.0

    elif action in ["fight_punch", "punch"]:
        # Quick punch cycle
        cycle = (t * duration * 2.5) % 1.0
        punch_phase = math.sin(cycle * math.pi)
        angles = POSE_STAND.lerp(POSE_FIGHT_PUNCH, punch_phase)
        dx = punch_phase * 15.0 * direction
        return angles, dx, 0.0

    elif action in ["fight_kick", "kick"]:
        cycle = (t * duration * 2.0) % 1.0
        kick_phase = math.sin(cycle * math.pi)
        angles = POSE_STAND.lerp(POSE_FIGHT_KICK, kick_phase)
        dx = kick_phase * 10.0 * direction
        return angles, dx, 0.0

    # Fallback to stand
    return POSE_STAND, 0.0, 0.0
