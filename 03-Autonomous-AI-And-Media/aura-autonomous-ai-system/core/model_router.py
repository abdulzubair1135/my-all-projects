"""
AURA Model Router.
Routes tasks to fast, normal, or heavy models based on task complexity and VRAM limits.
"""

from typing import Dict, Any, Optional
from config import config
from core.logger import setup_logger

logger = setup_logger("ModelRouter")

class ModelRouter:
    def __init__(self):
        self.fast_model = config.models.fast_model
        self.normal_model = config.models.normal_model
        self.heavy_model = config.models.heavy_model
        self.vram_limit_mb = config.hardware.vram_mb

    def select_model(self, task_complexity: str = "normal", priority: int = 1, context_size: int = 0) -> str:
        """
        Select model based on complexity ('trivial', 'normal', 'difficult'), priority, and context size.
        Hardware aware: RTX 2050 4GB VRAM target.
        """
        complexity = task_complexity.lower()

        if complexity in ("trivial", "simple", "low"):
            selected = self.fast_model
        elif complexity in ("difficult", "complex", "high") and priority >= 3 and context_size < 4000:
            # Only route to heavy model if context size is moderate (fitting in 4GB VRAM)
            selected = self.heavy_model
        else:
            selected = self.normal_model

        logger.info(f"ModelRouter selected '{selected}' (complexity: {task_complexity}, priority: {priority})")
        return selected

model_router = ModelRouter()
