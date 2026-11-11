"""
2D Kinematic Skeleton and Pose Data Model for Stickman Animation.
Provides hierarchical forward kinematics (FK) calculations for joint positions.
"""

from __future__ import annotations
import math
from typing import Dict, Tuple, Any
from pydantic import BaseModel, Field


class JointAngles(BaseModel):
    """Joint angles in degrees (0 is straight down, positive clockwise)."""
    torso_tilt: float = 0.0          # Angle of spine tilt
    neck_tilt: float = 0.0           # Head tilt
    left_shoulder: float = 20.0      # Arm hanging slightly forward
    left_elbow: float = 10.0         # Forearm relative bend
    right_shoulder: float = -20.0    # Arm hanging slightly back
    right_elbow: float = -10.0
    left_hip: float = 10.0           # Thigh angle
    left_knee: float = 5.0           # Shin angle
    right_hip: float = -10.0
    right_knee: float = 5.0

    def lerp(self, target: JointAngles, t: float) -> JointAngles:
        """Linear interpolation between two joint angle sets."""
        t_clamped = max(0.0, min(1.0, t))
        res = {}
        for field in type(self).model_fields.keys():
            v0 = getattr(self, field)
            v1 = getattr(target, field)
            res[field] = v0 + (v1 - v0) * t_clamped
        return JointAngles(**res)


class SkeletonProportions(BaseModel):
    head_radius: float = 24.0
    torso_length: float = 65.0
    shoulder_width: float = 26.0
    hip_width: float = 22.0
    upper_arm_length: float = 35.0
    lower_arm_length: float = 32.0
    upper_leg_length: float = 42.0
    lower_leg_length: float = 40.0


class StickmanSkeleton:
    """Computes Cartesian (x, y) joint coordinates from root position and joint angles."""

    def __init__(self, proportions: SkeletonProportions | None = None):
        self.props = proportions or SkeletonProportions()

    def compute_joints(
        self,
        root_x: float,
        root_y: float,
        angles: JointAngles,
        scale: float = 1.0,
        facing_right: bool = True,
    ) -> Dict[str, Tuple[float, float]]:
        """Forward Kinematics calculation returning absolute (x, y) pixel coordinates."""
        direction = 1.0 if facing_right else -1.0

        p = self.props
        # Scale factors
        head_r = p.head_radius * scale
        torso_len = p.torso_length * scale
        sh_w = (p.shoulder_width / 2.0) * scale * direction
        hp_w = (p.hip_width / 2.0) * scale * direction
        u_arm = p.upper_arm_length * scale
        l_arm = p.lower_arm_length * scale
        u_leg = p.upper_leg_length * scale
        l_leg = p.lower_leg_length * scale

        # Pelvis / Root
        pelvis = (root_x, root_y)

        # Neck: tilted from pelvis
        spine_rad = math.radians(angles.torso_tilt * direction - 90.0)
        neck = (
            pelvis[0] + torso_len * math.cos(spine_rad),
            pelvis[1] + torso_len * math.sin(spine_rad),
        )

        # Head center
        head_rad = math.radians((angles.torso_tilt + angles.neck_tilt) * direction - 90.0)
        head_center = (
            neck[0] + head_r * math.cos(head_rad),
            neck[1] + head_r * math.sin(head_rad),
        )

        # Helper for arm & leg segments
        def polar(origin: Tuple[float, float], length: float, deg: float) -> Tuple[float, float]:
            rad = math.radians(deg * direction + 90.0)  # 0 deg = down (+90 in screen space)
            return (origin[0] + length * math.sin(rad), origin[1] + length * math.cos(rad))

        # Shoulders
        l_shoulder = (neck[0] - sh_w, neck[1])
        r_shoulder = (neck[0] + sh_w, neck[1])

        # Arms
        l_elbow = polar(l_shoulder, u_arm, angles.left_shoulder)
        l_hand = polar(l_elbow, l_arm, angles.left_shoulder + angles.left_elbow)

        r_elbow = polar(r_shoulder, u_arm, angles.right_shoulder)
        r_hand = polar(r_elbow, l_arm, angles.right_shoulder + angles.right_elbow)

        # Hips
        l_hip = (pelvis[0] - hp_w, pelvis[1])
        r_hip = (pelvis[0] + hp_w, pelvis[1])

        # Legs
        l_knee = polar(l_hip, u_leg, angles.left_hip)
        l_foot = polar(l_knee, l_leg, angles.left_hip + angles.left_knee)

        r_knee = polar(r_hip, u_leg, angles.right_hip)
        r_foot = polar(r_knee, l_leg, angles.right_hip + angles.right_knee)

        return {
            "pelvis": pelvis,
            "neck": neck,
            "head_center": head_center,
            "head_radius": (head_r, head_r),
            "left_shoulder": l_shoulder,
            "left_elbow": l_elbow,
            "left_hand": l_hand,
            "right_shoulder": r_shoulder,
            "right_elbow": r_elbow,
            "right_hand": r_hand,
            "left_hip": l_hip,
            "left_knee": l_knee,
            "left_foot": l_foot,
            "right_hip": r_hip,
            "right_knee": r_knee,
            "right_foot": r_foot,
        }
