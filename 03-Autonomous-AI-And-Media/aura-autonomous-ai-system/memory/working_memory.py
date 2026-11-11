"""
AURA Working Memory Module.
Maintains short-term contextual state, current goal, active task, and recent execution history.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from config import config
from core.logger import setup_logger

logger = setup_logger("WorkingMemory")

@dataclass
class ContextStep:
    step_id: str
    action: str
    input_data: Any
    output_data: Any
    status: str
    timestamp: str

class WorkingMemory:
    def __init__(self, max_items: Optional[int] = None):
        self.max_items = max_items or config.working_memory_max_items
        self.current_goal_id: Optional[str] = None
        self.current_goal_title: Optional[str] = None
        self.current_task_id: Optional[str] = None
        self.current_task_title: Optional[str] = None
        self.history: List[ContextStep] = []
        self.scratchpad: Dict[str, Any] = {}

    def set_active_goal(self, goal_id: str, title: str):
        self.current_goal_id = goal_id
        self.current_goal_title = title
        logger.info(f"Active goal set to [{goal_id}] '{title}'")

    def set_active_task(self, task_id: str, title: str):
        self.current_task_id = task_id
        self.current_task_title = title
        logger.info(f"Active task set to [{task_id}] '{title}'")

    def add_step(self, step: ContextStep):
        self.history.append(step)
        if len(self.history) > self.max_items:
            self.history.pop(0)  # Sliding window truncation
        logger.debug(f"Added step {step.step_id} to working memory. Total steps: {len(self.history)}")

    def get_context_summary(self) -> str:
        lines = [
            f"Active Goal: {self.current_goal_title or 'None'} (ID: {self.current_goal_id or 'None'})",
            f"Active Task: {self.current_task_title or 'None'} (ID: {self.current_task_id or 'None'})",
            "Recent Steps:"
        ]
        for step in self.history[-5:]:  # Last 5 steps
            lines.append(f" - [{step.action}] {step.status}: input={step.input_data} -> output={step.output_data}")
        return "\n".join(lines)

    def clear(self):
        self.current_goal_id = None
        self.current_goal_title = None
        self.current_task_id = None
        self.current_task_title = None
        self.history.clear()
        self.scratchpad.clear()
        logger.info("Working memory cleared")
