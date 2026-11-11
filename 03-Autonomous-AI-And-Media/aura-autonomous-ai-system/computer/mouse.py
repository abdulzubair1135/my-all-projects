"""
AURA Mouse Control Module.
Executes mouse movement, clicking, and scrolling with autonomy level policy checks.
"""

from typing import Dict, Any
from core.controller import controller
from core.logger import setup_logger

logger = setup_logger("MouseControl")

class MouseControl:
    def click(self, x: int, y: int, button: str = "left") -> Dict[str, Any]:
        if not controller.check_autonomy_permission(required_level=3):
            return {"status": "blocked", "reason": "Requires autonomy level 3 (Computer Automation)"}

        logger.info(f"Mouse click at ({x}, {y}) button={button}")
        try:
            import pyautogui
            pyautogui.click(x, y, button=button)
            return {"status": "success", "action": "click", "x": x, "y": y}
        except Exception as e:
            logger.warning(f"PyAutoGUI click simulated: {e}")
            return {"status": "simulated", "action": "click", "x": x, "y": y}

    def scroll(self, clicks: int = 5) -> Dict[str, Any]:
        if not controller.check_autonomy_permission(required_level=3):
            return {"status": "blocked", "reason": "Requires autonomy level 3"}

        logger.info(f"Mouse scroll clicks={clicks}")
        try:
            import pyautogui
            pyautogui.scroll(clicks)
            return {"status": "success", "action": "scroll", "clicks": clicks}
        except Exception as e:
            return {"status": "simulated", "action": "scroll", "clicks": clicks}

mouse_control = MouseControl()
