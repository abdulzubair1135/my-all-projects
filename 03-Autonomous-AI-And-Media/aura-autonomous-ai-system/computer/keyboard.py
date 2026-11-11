"""
AURA Keyboard Control Module.
Executes text typing and hotkey actions with autonomy level policy checks.
"""

from typing import Dict, Any, List
from core.controller import controller
from core.logger import setup_logger

logger = setup_logger("KeyboardControl")

class KeyboardControl:
    def type_text(self, text: str, interval: float = 0.05) -> Dict[str, Any]:
        if not controller.check_autonomy_permission(required_level=3):
            return {"status": "blocked", "reason": "Requires autonomy level 3 (Computer Automation)"}

        logger.info(f"Keyboard typing text (len={len(text)})")
        try:
            import pyautogui
            pyautogui.write(text, interval=interval)
            return {"status": "success", "action": "type_text", "length": len(text)}
        except Exception as e:
            logger.warning(f"PyAutoGUI type text simulated: {e}")
            return {"status": "simulated", "action": "type_text", "length": len(text)}

    def hotkey(self, keys: List[str]) -> Dict[str, Any]:
        if not controller.check_autonomy_permission(required_level=3):
            return {"status": "blocked", "reason": "Requires autonomy level 3"}

        logger.info(f"Keyboard hotkey: {keys}")
        try:
            import pyautogui
            pyautogui.hotkey(*keys)
            return {"status": "success", "action": "hotkey", "keys": keys}
        except Exception as e:
            return {"status": "simulated", "action": "hotkey", "keys": keys}

keyboard_control = KeyboardControl()
