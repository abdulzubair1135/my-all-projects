"""
AUTO YT GENERATOR — Camera & Composition Director.

Directs cinematography, shot types, framing composition, and 5-layer parallax speeds:
- Shot Types: Wide, Medium, Close-Up, Extreme Close-Up, Reaction, Infographic Cutaway
- Cinematic Eased Camera Motions: Dramatic Punch-In, Slow Tension Zoom, Parallax Tracking Pan, Trauma Shake
"""

from app.models.scene import SemanticCue, CameraConfig, ShotType, ParallaxConfig
from app.constants import CameraMovement


class CameraDirector:
    """Calculates professional camera movements and multi-layer parallax depth."""

    def direct_camera_for_scene(
        self,
        semantic: SemanticCue,
        is_cutaway: bool = False,
    ) -> CameraConfig:
        """Determines shot composition, motion curve, and parallax speeds."""
        emotion = semantic.emotion
        intent = semantic.intent
        importance = semantic.importance

        cam_type = CameraMovement.SLOW_ZOOM_IN.value
        shot_type = ShotType.MEDIUM
        zoom_start = 1.0
        zoom_end = 1.15
        pan_x_s = 0.0
        pan_x_e = 0.0

        if is_cutaway:
            # Subtle slow push for infographics
            shot_type = ShotType.INFOGRAPHIC_CUTAWAY
            cam_type = CameraMovement.SLOW_ZOOM_IN.value
            zoom_start = 1.0
            zoom_end = 1.08
        elif emotion == "fear" or emotion == "shock":
            # Dramatic punch-in or shake
            shot_type = ShotType.CLOSE_UP if importance > 0.8 else ShotType.REACTION
            cam_type = CameraMovement.SHAKE.value if emotion == "shock" else CameraMovement.SLOW_ZOOM_IN.value
            zoom_start = 1.15
            zoom_end = 1.35
        elif intent == "hook":
            # Fast punchy hook establishing shot -> close-up
            shot_type = ShotType.CLOSE_UP
            cam_type = CameraMovement.SLOW_ZOOM_IN.value
            zoom_start = 1.05
            zoom_end = 1.28
        elif intent == "question":
            # Thinking pan
            shot_type = ShotType.MEDIUM
            cam_type = CameraMovement.PAN_RIGHT.value
            zoom_start = 1.08
            zoom_end = 1.08
            pan_x_s = -40.0
            pan_x_e = 40.0
        elif intent == "conclude":
            # Pull-out reveal
            shot_type = ShotType.WIDE
            cam_type = CameraMovement.SLOW_ZOOM_OUT.value
            zoom_start = 1.20
            zoom_end = 1.0

        # Layered Parallax Speeds
        parallax = ParallaxConfig(
            sky_speed=0.05,
            far_bg_speed=0.20,
            midground_speed=0.45,
            character_speed=0.85,
            foreground_speed=1.25,
        )

        return CameraConfig(
            type=cam_type,
            shot_type=shot_type,
            zoom_start=zoom_start,
            zoom_end=zoom_end,
            pan_x_start=pan_x_s,
            pan_x_end=pan_x_e,
            parallax=parallax,
        )


# Default camera director instance
camera_director = CameraDirector()
