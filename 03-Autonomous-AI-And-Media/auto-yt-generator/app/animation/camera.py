"""
AUTO YT GENERATOR — 2D Camera Controller with Smooth Easing & Parallax.

Applies cinematic camera movements:
- Smooth Bezier / Cubic Ease-In-Out Zoom
- Parallax Layer Coordinate Offsets (Sky, BG, Mid, Character, Foreground)
- Camera Shake with Realistic Decay
- Directional Whip-Pan and Tilt
"""

import math
import random
from typing import Tuple, Optional
from PIL import Image
from app.constants import CameraMovement
from app.models.scene import CameraConfig, ParallaxConfig


class CameraController:
    """Computes smooth viewport curves and multi-layer parallax depth transforms."""

    def __init__(self, target_width: int = 1920, target_height: int = 1080):
        self.target_width = target_width
        self.target_height = target_height

    @staticmethod
    def ease_in_out(t: float) -> float:
        """Cubic ease-in-out curve for natural cinematic camera acceleration and deceleration."""
        return t * t * (3.0 - 2.0 * t)

    def get_parallax_offset(
        self,
        camera: Optional[CameraConfig],
        progress: float,
        layer_type: str = "character",
    ) -> Tuple[int, int]:
        """Calculates horizontal and vertical pixel offset for a specific depth layer."""
        if not camera:
            return 0, 0

        p = self.ease_in_out(max(0.0, min(1.0, progress)))
        cfg: ParallaxConfig = camera.parallax if hasattr(camera, "parallax") and camera.parallax else ParallaxConfig()

        speed_map = {
            "sky": cfg.sky_speed,
            "background": cfg.far_bg_speed,
            "midground": cfg.midground_speed,
            "character": cfg.character_speed,
            "foreground": cfg.foreground_speed,
        }
        layer_speed = speed_map.get(layer_type.lower(), 1.0)

        # Compute pan displacement
        dx = (camera.pan_x_start + (camera.pan_x_end - camera.pan_x_start) * p) * layer_speed
        dy = (camera.pan_y_start + (camera.pan_y_end - camera.pan_y_start) * p) * layer_speed
        return int(dx), int(dy)

    def apply_camera(
        self,
        canvas: Image.Image,
        camera: CameraConfig,
        progress: float,
    ) -> Image.Image:
        """Transforms canvas according to camera type, smooth easing, and timeline progress."""
        raw_p = max(0.0, min(1.0, progress))
        p = self.ease_in_out(raw_p)
        cam_type = camera.type.lower() if camera else CameraMovement.STATIC.value

        zoom_start = camera.zoom_start if camera else 1.0
        zoom_end = camera.zoom_end if camera else 1.0

        if cam_type == CameraMovement.SLOW_ZOOM_IN.value:
            current_zoom = zoom_start + (zoom_end - zoom_start) * p
            pan_x_pct = 0.5
            pan_y_pct = 0.5
        elif cam_type == CameraMovement.SLOW_ZOOM_OUT.value:
            current_zoom = zoom_start - (zoom_start - zoom_end) * p
            pan_x_pct = 0.5
            pan_y_pct = 0.5
        elif cam_type == CameraMovement.PAN_LEFT.value:
            current_zoom = max(1.08, zoom_start)
            pan_x_pct = 0.58 - 0.16 * p
            pan_y_pct = 0.5
        elif cam_type == CameraMovement.PAN_RIGHT.value:
            current_zoom = max(1.08, zoom_start)
            pan_x_pct = 0.42 + 0.16 * p
            pan_y_pct = 0.5
        elif cam_type == CameraMovement.TILT_UP.value:
            current_zoom = max(1.08, zoom_start)
            pan_x_pct = 0.5
            pan_y_pct = 0.58 - 0.16 * p
        elif cam_type == CameraMovement.TILT_DOWN.value:
            current_zoom = max(1.08, zoom_start)
            pan_x_pct = 0.5
            pan_y_pct = 0.42 + 0.16 * p
        elif cam_type == CameraMovement.SHAKE.value:
            # Trauma-damped camera shake
            current_zoom = max(1.08, zoom_start)
            shake_amp = 18.0 * (1.0 - raw_p * 0.6)
            angle = random.uniform(0, 2.0 * math.pi)
            pan_x_pct = 0.5 + (math.cos(angle) * shake_amp) / self.target_width
            pan_y_pct = 0.5 + (math.sin(angle) * shake_amp) / self.target_height
        else:
            current_zoom = zoom_start
            pan_x_pct = 0.5
            pan_y_pct = 0.5

        # Crop Box
        crop_w = int(self.target_width / current_zoom)
        crop_h = int(self.target_height / current_zoom)

        center_x = int(self.target_width * pan_x_pct)
        center_y = int(self.target_height * pan_y_pct)

        left = max(0, min(self.target_width - crop_w, center_x - crop_w // 2))
        top = max(0, min(self.target_height - crop_h, center_y - crop_h // 2))
        right = left + crop_w
        bottom = top + crop_h

        cropped = canvas.crop((left, top, right, bottom))
        return cropped.resize((self.target_width, self.target_height), Image.Resampling.BILINEAR)


# Default camera controller instance
camera_controller = CameraController()
