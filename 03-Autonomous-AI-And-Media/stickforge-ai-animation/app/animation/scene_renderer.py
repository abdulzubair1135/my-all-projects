"""
Scene Renderer for StickForge AI.
Renders deterministic animated frames by combining characters, skeletal kinematics,
motion interpolation, virtual cameras, and background layers.
"""

from __future__ import annotations
import math
from pathlib import Path
from typing import Dict, List, Tuple, Generator, Optional
from PIL import Image, ImageDraw, ImageFont

from app.ai.schema_validator import SceneSpec, CharacterDef, ActionSpec
from app.animation.skeleton import StickmanSkeleton, SkeletonProportions
from app.animation.motion_library import get_pose_and_offset
from app.animation.camera import VirtualCamera
from app.animation.background_renderer import BackgroundRenderer, hex_to_rgb


class SceneRenderer:
    """Renders full scenes frame-by-frame with deterministic camera and stickman animation."""

    def __init__(
        self,
        width: int = 1080,
        height: int = 1920,
        fps: int = 30,
    ):
        self.w = width
        self.h = height
        self.fps = fps
        self.bg_renderer = BackgroundRenderer(width, height)
        self.skeleton = StickmanSkeleton()

    def render_frame(
        self,
        scene: SceneSpec,
        characters: Dict[str, CharacterDef],
        frame_idx: int,
        total_frames: int,
    ) -> Image.Image:
        """Render a single frame of a scene at index frame_idx."""
        t = frame_idx / max(1, total_frames - 1)

        # 1. Background layer
        frame = self.bg_renderer.render(scene.background)
        draw = ImageDraw.Draw(frame)

        # 2. Virtual Camera
        cam = VirtualCamera(
            shot=scene.camera.shot,
            movement=scene.camera.movement,
            speed=scene.camera.speed,
            viewport_w=self.w,
            viewport_h=self.h,
        )

        # Focus center for camera
        ground_y = self.h * 0.72
        focus_center = (self.w * 0.5, ground_y - 120.0)

        # 3. Render Characters
        # Spread multiple characters evenly if not specified
        num_chars = max(1, len(scene.actions))
        char_spacing = 220.0

        for idx, act in enumerate(scene.actions):
            char_def = characters.get(act.character_id) or CharacterDef(
                id=act.character_id, name="Hero", color="#FFFFFF"
            )

            # Base world position
            base_x = (self.w * 0.5) + (idx - (num_chars - 1) / 2.0) * char_spacing
            base_y = ground_y - 82.0

            # Kinematic motion angles and delta offsets
            angles, dx, dy = get_pose_and_offset(
                act.action, t, scene.duration, act.parameters
            )

            world_root_x = base_x + dx
            world_root_y = base_y + dy

            # Calculate FK joints in world space
            facing_right = act.parameters.get("direction", "right") == "right"
            joints = self.skeleton.compute_joints(
                root_x=world_root_x,
                root_y=world_root_y,
                angles=angles,
                scale=1.45,  # Scale for high-res vertical screen
                facing_right=facing_right,
            )

            # Map joints through virtual camera to screen pixels
            screen_joints = {}
            for name, pt in joints.items():
                if name == "head_radius":
                    # Scale radius with camera
                    scale, _, _ = cam.get_transform(t)
                    screen_joints[name] = pt[0] * scale
                else:
                    screen_joints[name] = cam.world_to_screen(pt, t, focus_center)

            # Draw character onto frame
            self._draw_stickman(draw, screen_joints, char_def)

        return frame

    def _draw_stickman(
        self,
        draw: ImageDraw.ImageDraw,
        joints: Dict[str, Any],
        char_def: CharacterDef,
    ) -> None:
        """Draw stickman lines and head using character styles."""
        stroke_color = hex_to_rgb(char_def.color)
        line_w = 6

        # Helper to draw limb segment with rounded end joints
        def draw_segment(p1, p2, width=line_w):
            draw.line([p1, p2], fill=stroke_color, width=width)
            r = int(width / 2)
            draw.ellipse([p1[0] - r, p1[1] - r, p1[0] + r, p1[1] + r], fill=stroke_color)
            draw.ellipse([p2[0] - r, p2[1] - r, p2[0] + r, p2[1] + r], fill=stroke_color)

        # 1. Torso Spine
        draw_segment(joints["neck"], joints["pelvis"], width=line_w + 1)

        # 2. Legs
        draw_segment(joints["pelvis"], joints["left_hip"])
        draw_segment(joints["left_hip"], joints["left_knee"])
        draw_segment(joints["left_knee"], joints["left_foot"])

        draw_segment(joints["pelvis"], joints["right_hip"])
        draw_segment(joints["right_hip"], joints["right_knee"])
        draw_segment(joints["right_knee"], joints["right_foot"])

        # 3. Arms
        draw_segment(joints["neck"], joints["left_shoulder"])
        draw_segment(joints["left_shoulder"], joints["left_elbow"])
        draw_segment(joints["left_elbow"], joints["left_hand"])

        draw_segment(joints["neck"], joints["right_shoulder"])
        draw_segment(joints["right_shoulder"], joints["right_elbow"])
        draw_segment(joints["right_elbow"], joints["right_hand"])

        # 4. Head
        hx, hy = joints["head_center"]
        hr = int(joints["head_radius"])
        # Filled head with stroke
        draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(22, 24, 30), outline=stroke_color, width=line_w)

        # Eyes
        eye_offset_x = int(hr * 0.35)
        eye_y = int(hy - hr * 0.15)
        eye_r = max(2, int(hr * 0.12))
        draw.ellipse([hx - eye_offset_x - eye_r, eye_y - eye_r, hx - eye_offset_x + eye_r, eye_y + eye_r], fill=stroke_color)
        draw.ellipse([hx + eye_offset_x - eye_r, eye_y - eye_r, hx + eye_offset_x + eye_r, eye_y + eye_r], fill=stroke_color)

    def render_scene_to_directory(
        self,
        scene: SceneSpec,
        characters: Dict[str, CharacterDef],
        output_dir: Path,
        progress_callback: Optional[callable] = None,
    ) -> List[Path]:
        """Render all frames of a scene to numbered PNG files on disk."""
        output_dir.mkdir(parents=True, exist_ok=True)
        num_frames = int(scene.duration * self.fps)
        frame_paths: List[Path] = []

        for f_idx in range(num_frames):
            img = self.render_frame(scene, characters, f_idx, num_frames)
            path = output_dir / f"frame_{f_idx:05d}.png"
            img.save(path, format="PNG")
            frame_paths.append(path)
            if progress_callback and f_idx % 15 == 0:
                progress_callback(f_idx / num_frames)

        return frame_paths
