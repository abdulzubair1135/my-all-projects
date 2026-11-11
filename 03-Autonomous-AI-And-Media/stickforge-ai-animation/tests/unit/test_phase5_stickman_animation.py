"""
Tests for Phase 5: Stickman Kinematics, Poses, Virtual Camera, and Scene Rendering.
"""

from pathlib import Path
import pytest
from app.animation.skeleton import StickmanSkeleton, JointAngles, SkeletonProportions
from app.animation.pose import POSE_STAND, POSE_SIT, POSE_WALK_1
from app.animation.motion_library import get_pose_and_offset
from app.animation.camera import VirtualCamera
from app.animation.scene_renderer import SceneRenderer
from app.ai.schema_validator import SceneSpec, CharacterDef, ActionSpec


def test_skeleton_forward_kinematics():
    skel = StickmanSkeleton()
    joints = skel.compute_joints(
        root_x=500.0,
        root_y=900.0,
        angles=POSE_STAND,
        scale=1.0,
        facing_right=True,
    )

    required_joints = [
        "pelvis", "neck", "head_center",
        "left_shoulder", "left_elbow", "left_hand",
        "right_shoulder", "right_elbow", "right_hand",
        "left_hip", "left_knee", "left_foot",
        "right_hip", "right_knee", "right_foot",
    ]
    for j in required_joints:
        assert j in joints
        assert len(joints[j]) == 2
        assert isinstance(joints[j][0], float)
        assert isinstance(joints[j][1], float)

    # Pelvis is at root
    assert joints["pelvis"] == (500.0, 900.0)
    # Neck is above pelvis
    assert joints["neck"][1] < joints["pelvis"][1]
    # Head is above neck
    assert joints["head_center"][1] < joints["neck"][1]


def test_motion_library_actions():
    # Stand has zero dx
    angles, dx, dy = get_pose_and_offset("stand", 0.5, 5.0)
    assert dx == 0.0

    # Walk moves forward
    angles, dx, dy = get_pose_and_offset("walk", 0.5, 4.0, {"direction": "right", "speed": 1.0})
    assert dx > 0.0

    # Jump apex has maximum negative dy (upward)
    angles_start, dx_start, dy_start = get_pose_and_offset("jump", 0.0, 3.0, {"height": 80.0})
    angles_mid, dx_mid, dy_mid = get_pose_and_offset("jump", 0.5, 3.0, {"height": 80.0})
    assert dy_mid < dy_start  # Jump is higher at mid than start


def test_virtual_camera_transform():
    cam = VirtualCamera(shot="medium", movement="pan_right", speed=1.0, viewport_w=1080, viewport_h=1920)
    scale, px, py = cam.get_transform(0.5)
    assert scale > 1.0
    assert px > 0.0  # Panned right

    screen_pt = cam.world_to_screen((500.0, 800.0), t=0.5)
    assert isinstance(screen_pt[0], int)
    assert isinstance(screen_pt[1], int)


def test_scene_renderer_frame_generation(tmp_path):
    renderer = SceneRenderer(width=540, height=960, fps=15)
    scene = SceneSpec(
        id="test_sc_1",
        sequence_order=1,
        duration=1.0,  # 15 frames
        background="classroom",
        actions=[ActionSpec(character_id="hero", action="walk")],
    )
    chars = {"hero": CharacterDef(id="hero", name="Rahul", color="#38BDF8")}

    # Test single frame render
    img = renderer.render_frame(scene, chars, frame_idx=0, total_frames=15)
    assert img.size == (540, 960)
    assert img.mode == "RGB"

    # Test rendering frames to disk
    frames = renderer.render_scene_to_directory(scene, chars, tmp_path)
    assert len(frames) == 15
    assert all(f.exists() for f in frames)
