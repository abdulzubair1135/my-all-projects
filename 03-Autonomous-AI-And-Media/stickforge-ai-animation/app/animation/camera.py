"""
Virtual 2D Camera for StickForge AI.
Handles shots (wide, medium, close-up) and dynamic camera movements (pan, zoom, follow).
"""

from __future__ import annotations
from typing import Tuple, Dict, Any


class VirtualCamera:
    """Computes screen transformations based on camera settings and timestamp."""

    def __init__(
        self,
        shot: str = "medium",
        movement: str = "static",
        speed: float = 1.0,
        viewport_w: int = 1080,
        viewport_h: int = 1920,
    ):
        self.shot = shot.lower()
        self.movement = movement.lower()
        self.speed = speed
        self.vw = viewport_w
        self.vh = viewport_h

    def get_transform(self, t: float) -> Tuple[float, float, float]:
        """
        Returns (scale, offset_x, offset_y) for normalized progress t (0.0 to 1.0).
        """
        # Base scale from shot type
        if self.shot == "close_up":
            base_scale = 1.9
        elif self.shot == "wide":
            base_scale = 0.9
        else:  # medium
            base_scale = 1.35

        scale = base_scale
        pan_x = 0.0
        pan_y = 0.0

        if self.movement == "zoom_in":
            scale = base_scale * (1.0 + 0.25 * t * self.speed)
        elif self.movement == "zoom_out":
            scale = base_scale * (1.25 - 0.25 * t * self.speed)
        elif self.movement == "pan_left":
            pan_x = -120.0 * t * self.speed
        elif self.movement == "pan_right":
            pan_x = 120.0 * t * self.speed
        elif self.movement == "pan_up":
            pan_y = -80.0 * t * self.speed
        elif self.movement == "pan_down":
            pan_y = 80.0 * t * self.speed

        return scale, pan_x, pan_y

    def world_to_screen(
        self,
        world_pt: Tuple[float, float],
        t: float,
        focus_center: Tuple[float, float] = (540.0, 960.0),
    ) -> Tuple[int, int]:
        """Maps world coordinate to screen pixel coordinate."""
        scale, pan_x, pan_y = self.get_transform(t)
        cx, cy = focus_center
        # Scale around focus center then apply pan
        sx = cx + (world_pt[0] - cx) * scale + pan_x
        sy = cy + (world_pt[1] - cy) * scale + pan_y
        return int(round(sx)), int(round(sy))
