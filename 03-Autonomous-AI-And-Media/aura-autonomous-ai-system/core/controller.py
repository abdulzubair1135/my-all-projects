"""
AURA Controller Module.
Enforces autonomy levels, safety checks, and manages agent execution flow.
"""

from typing import Dict, Any, Optional
from config import config
from core.logger import setup_logger

logger = setup_logger("Controller")

class Controller:
    def __init__(self):
        self.autonomy_level = config.autonomy_level
        self.is_paused = False
        self.is_stopped = False

    def check_autonomy_permission(self, required_level: int) -> bool:
        """
        Level 0: Think/Research only
        Level 1: Local files + Research
        Level 2: Browser + Coding sandbox
        Level 3: Computer automation
        Level 4: Controlled self-improvement
        """
        permitted = self.autonomy_level >= required_level
        if not permitted:
            logger.warning(
                f"Action blocked by autonomy policy: required level {required_level}, current level {self.autonomy_level}"
            )
        return permitted

    def pause(self):
        self.is_paused = True
        logger.info("Agent controller paused.")

    def resume(self):
        self.is_paused = False
        logger.info("Agent controller resumed.")

    def stop(self):
        self.is_stopped = True
        logger.info("EMERGENCY STOP triggered for Agent Controller.")

controller = Controller()
