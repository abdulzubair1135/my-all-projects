"""
Keyframe Pose Presets for Stickman Animation.
Defines canonical skeletal joint configurations for actions, emotions, and interactions.
"""

from app.animation.skeleton import JointAngles

# Canonical Poses

POSE_STAND = JointAngles(
    torso_tilt=0.0,
    neck_tilt=0.0,
    left_shoulder=15.0,
    left_elbow=10.0,
    right_shoulder=-15.0,
    right_elbow=10.0,
    left_hip=5.0,
    left_knee=2.0,
    right_hip=-5.0,
    right_knee=2.0,
)

POSE_SIT = JointAngles(
    torso_tilt=5.0,
    neck_tilt=0.0,
    left_shoulder=40.0,
    left_elbow=60.0,
    right_shoulder=40.0,
    right_elbow=60.0,
    left_hip=85.0,
    left_knee=-90.0,
    right_hip=85.0,
    right_knee=-90.0,
)

POSE_WALK_1 = JointAngles(
    torso_tilt=3.0,
    neck_tilt=0.0,
    left_shoulder=-35.0,
    left_elbow=20.0,
    right_shoulder=35.0,
    right_elbow=25.0,
    left_hip=30.0,
    left_knee=5.0,
    right_hip=-25.0,
    right_knee=20.0,
)

POSE_WALK_2 = JointAngles(
    torso_tilt=2.0,
    neck_tilt=0.0,
    left_shoulder=35.0,
    left_elbow=25.0,
    right_shoulder=-35.0,
    right_elbow=20.0,
    left_hip=-25.0,
    left_knee=20.0,
    right_hip=30.0,
    right_knee=5.0,
)

POSE_RUN_1 = JointAngles(
    torso_tilt=18.0,
    neck_tilt=-5.0,
    left_shoulder=-60.0,
    left_elbow=65.0,
    right_shoulder=55.0,
    right_elbow=70.0,
    left_hip=55.0,
    left_knee=40.0,
    right_hip=-45.0,
    right_knee=60.0,
)

POSE_RUN_2 = JointAngles(
    torso_tilt=18.0,
    neck_tilt=-5.0,
    left_shoulder=55.0,
    left_elbow=70.0,
    right_shoulder=-60.0,
    right_elbow=65.0,
    left_hip=-45.0,
    left_knee=60.0,
    right_hip=55.0,
    right_knee=40.0,
)

POSE_JUMP_APEX = JointAngles(
    torso_tilt=-5.0,
    neck_tilt=-10.0,
    left_shoulder=-140.0,
    left_elbow=20.0,
    right_shoulder=-140.0,
    right_elbow=20.0,
    left_hip=45.0,
    left_knee=-60.0,
    right_hip=45.0,
    right_knee=-60.0,
)

POSE_WAVE_1 = JointAngles(
    torso_tilt=0.0,
    neck_tilt=5.0,
    left_shoulder=15.0,
    left_elbow=10.0,
    right_shoulder=-150.0,
    right_elbow=-30.0,
    left_hip=5.0,
    left_knee=2.0,
    right_hip=-5.0,
    right_knee=2.0,
)

POSE_WAVE_2 = JointAngles(
    torso_tilt=0.0,
    neck_tilt=-5.0,
    left_shoulder=15.0,
    left_elbow=10.0,
    right_shoulder=-150.0,
    right_elbow=30.0,
    left_hip=5.0,
    left_knee=2.0,
    right_hip=-5.0,
    right_knee=2.0,
)

POSE_POINT = JointAngles(
    torso_tilt=5.0,
    neck_tilt=0.0,
    left_shoulder=15.0,
    left_elbow=15.0,
    right_shoulder=-90.0,
    right_elbow=5.0,
    left_hip=5.0,
    left_knee=5.0,
    right_hip=-5.0,
    right_knee=5.0,
)

POSE_HAPPY = JointAngles(
    torso_tilt=-5.0,
    neck_tilt=-15.0,
    left_shoulder=-135.0,
    left_elbow=40.0,
    right_shoulder=-135.0,
    right_elbow=40.0,
    left_hip=15.0,
    left_knee=-20.0,
    right_hip=15.0,
    right_knee=-20.0,
)

POSE_SAD = JointAngles(
    torso_tilt=22.0,
    neck_tilt=30.0,
    left_shoulder=20.0,
    left_elbow=15.0,
    right_shoulder=20.0,
    right_elbow=15.0,
    left_hip=5.0,
    left_knee=10.0,
    right_hip=-5.0,
    right_knee=10.0,
)

POSE_FIGHT_PUNCH = JointAngles(
    torso_tilt=12.0,
    neck_tilt=-5.0,
    left_shoulder=40.0,
    left_elbow=90.0,  # Guarding fist
    right_shoulder=-95.0,
    right_elbow=0.0,  # Extended punch
    left_hip=25.0,
    left_knee=20.0,
    right_hip=-30.0,
    right_knee=25.0,
)

POSE_FIGHT_KICK = JointAngles(
    torso_tilt=-20.0,
    neck_tilt=10.0,
    left_shoulder=-45.0,
    left_elbow=60.0,
    right_shoulder=45.0,
    right_elbow=60.0,
    left_hip=5.0,
    left_knee=15.0,  # Planted leg
    right_hip=-95.0,
    right_knee=0.0,  # High kick
)
