"""
AUTO YT GENERATOR — 2D Animation Engine & Multi-Layer Timeline Compositor.

Renders complete multi-layer 2D animation frames:
1. Parallax Sky & Background layers
2. Prop items with ground shadows
3. Articulated 2D Character Rig (natural blinking, gaze tracking, 14-visemes, gestures)
4. Infographics & B-Roll Cutaways
5. Camera viewport motion with cubic ease-in-out
6. Atmospheric VFX overlays (heartbeat, glitch, film grain, vignette)
"""

import math
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PIL import Image, ImageDraw

from app.models.scene import SceneModel, SceneAction
from app.assets.manager import asset_manager
from app.assets.rig import character_rig
from app.audio.viseme import viseme_engine
from app.motion.infographics import infographics_engine
from app.motion.broll import broll_engine
from app.animation.camera import camera_controller
from app.animation.effects import effects_engine
from app.logger import logger


class SceneAnimator:
    """Composites and renders multi-layer 2D cartoon scenes and motion cutaways."""

    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        self.camera_ctrl = camera_controller
        self.effects_engine = effects_engine

    def render_scene_frame(
        self,
        scene: SceneModel,
        time_sec: float,
        project_dir: Optional[str] = None,
    ) -> Image.Image:
        """Renders a single composited 1080p frame at timestamp `time_sec`."""
        progress = time_sec / max(0.1, scene.duration_sec)

        # ── 1. Check for Infographic / B-Roll Cutaway ──────────────────────────
        if getattr(scene, "is_cutaway", False) and scene.infographic:
            # Render animated infographic card
            bg_path = asset_manager.get_or_create_background(scene.background_id, project_dir=project_dir)
            try:
                canvas = Image.open(bg_path).convert("RGBA").resize((self.width, self.height), Image.Resampling.BILINEAR)
            except Exception:
                canvas = Image.new("RGBA", (self.width, self.height), (12, 16, 28, 255))

            info_layer = infographics_engine.render_infographic_frame(
                config=scene.infographic,
                time_sec=time_sec,
                duration_sec=scene.duration_sec,
            )
            canvas = Image.alpha_composite(canvas, info_layer)

            # Camera & VFX
            canvas = self.camera_ctrl.apply_camera(canvas, scene.camera, progress=progress)
            canvas = self.effects_engine.apply_effects(canvas, scene.effects, time_sec=time_sec, duration_sec=scene.duration_sec)
            return canvas

        # ── 2. Base Background Layer (with Parallax Offset) ───────────────────
        bg_path = asset_manager.get_or_create_background(scene.background_id, project_dir=project_dir)
        try:
            canvas = Image.open(bg_path).convert("RGBA")
            if canvas.size != (self.width, self.height):
                canvas = canvas.resize((self.width, self.height), Image.Resampling.BILINEAR)
        except Exception as e:
            canvas = Image.new("RGBA", (self.width, self.height), (20, 20, 30, 255))

        # ── 3. Render Props Layer ─────────────────────────────────────────────
        for i, prop_id in enumerate(scene.props):
            prop_path = asset_manager.get_or_create_prop(prop_id, project_dir=project_dir)
            try:
                prop_img = Image.open(prop_path).convert("RGBA")
                prop_x = int(self.width * (0.22 + i * 0.40))
                prop_y = int(self.height * 0.62)
                bob = int(math.sin(time_sec * 2.0 + i) * 6)
                canvas.alpha_composite(prop_img, (prop_x - prop_img.width // 2, prop_y - prop_img.height // 2 + bob))
            except Exception as err:
                logger.debug(f"Failed to composite prop {prop_id}: {err}")

        # ── 4. Render Articulated Character Puppet Rig ────────────────────────
        active_actions = [
            a for a in scene.actions
            if a.start_time_sec <= time_sec <= (a.start_time_sec + a.duration_sec)
        ]
        if not active_actions and scene.actions:
            active_actions = [scene.actions[0]]

        for action in active_actions:
            # 14-Viseme Lip Sync Calculation
            is_talking = "talk" in action.action.lower() or bool(scene.narration_text)
            current_viseme = viseme_engine.get_viseme_at_time(
                audio_path=scene.audio_file,
                time_sec=time_sec,
                is_talking=is_talking,
            )

            # Gesture & Gaze
            gesture_val = getattr(action.gesture, "value", action.gesture) if hasattr(action, "gesture") else "talk_explain"
            gaze_val = getattr(action.gaze, "value", action.gaze) if hasattr(action, "gaze") else "direct"

            # Render Articulated Puppet Frame
            puppet_img = character_rig.render_puppet_frame(
                time_sec=time_sec,
                gesture=gesture_val,
                expression=action.expression,
                gaze=gaze_val,
                viseme=current_viseme,
            )

            # Scale and Staging
            scale_factor = action.scale
            target_w = int(puppet_img.width * scale_factor)
            target_h = int(puppet_img.height * scale_factor)
            scaled_puppet = puppet_img.resize((target_w, target_h), Image.Resampling.BILINEAR)

            pos_x = int(self.width * (action.position_x_percent / 100.0))
            pos_y = int(self.height * (action.position_y_percent / 100.0))

            top_left_x = pos_x - target_w // 2
            top_left_y = pos_y - target_h // 2

            puppet_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
            puppet_layer.paste(scaled_puppet, (top_left_x, top_left_y), scaled_puppet)
            canvas = Image.alpha_composite(canvas, puppet_layer)

        # ── 5. Apply Camera Motion Transform ──────────────────────────────────
        canvas = self.camera_ctrl.apply_camera(canvas, scene.camera, progress=progress)

        # ── 6. Apply Atmospheric VFX Overlays ─────────────────────────────────
        canvas = self.effects_engine.apply_effects(
            canvas,
            effects_list=scene.effects,
            time_sec=time_sec,
            duration_sec=scene.duration_sec,
        )

        return canvas

    def render_scene_to_frames(
        self,
        scene: SceneModel,
        fps: int = 15,
        project_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> List[str]:
        """Renders all frames for a single scene to PNG sequence on disk."""
        target_dir = Path(output_dir or (Path(project_dir or "") / "renders" / f"scene_{scene.scene_index:03d}"))
        target_dir.mkdir(parents=True, exist_ok=True)

        total_frames = max(1, int(scene.duration_sec * fps))
        frame_paths = []

        logger.info(f"Rendering scene #{scene.scene_index} ({total_frames} frames @ {fps} fps)...")
        for f_idx in range(total_frames):
            t = f_idx / float(fps)
            frame_img = self.render_scene_frame(scene, time_sec=t, project_dir=project_dir)
            frame_path = target_dir / f"frame_{f_idx:05d}.png"
            frame_img.save(frame_path, "PNG")
            frame_paths.append(str(frame_path))

        return frame_paths


# Default scene animator instance
scene_animator = SceneAnimator()
