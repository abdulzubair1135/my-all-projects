"""
AURA Planner Module.
Breaks high-level goals into structured executable sub-tasks using local LLM capabilities.
"""

import json
import re
from typing import List, Dict, Any, Optional
from brain.model_adapter import ModelAdapter, model_adapter
from core.model_router import ModelRouter, model_router
from core.logger import setup_logger

logger = setup_logger("Planner")

class Planner:
    def __init__(self, adapter: Optional[ModelAdapter] = None, router: Optional[ModelRouter] = None):
        self.adapter = adapter or model_adapter
        self.router = router or model_router

    def plan_goal(self, goal_title: str, goal_description: str = "") -> List[Dict[str, Any]]:
        """
        Generates a list of structured sub-tasks for a given goal.
        Each task dict contains: 'title', 'description', 'priority'.
        """
        logger.info(f"Planning goal: '{goal_title}'")
        
        prompt = f"""You are the AURA Task Planner.
Decompose the following high-level goal into 1 to 4 concrete, sequential sub-tasks.

GOAL: {goal_title}
DESCRIPTION: {goal_description}

Return ONLY a valid JSON object matching this exact schema:
{{
  "tasks": [
    {{
      "title": "Sub-task title",
      "description": "Detailed description of what to perform",
      "priority": 1
    }}
  ]
}}
"""

        model = self.router.select_model(task_complexity="normal")
        response = self.adapter.generate(prompt, model=model, temperature=0.2)
        
        parsed_tasks = self._parse_json_tasks(response)
        if not parsed_tasks:
            logger.warning("LLM response did not yield structured JSON tasks. Creating default fallback task.")
            parsed_tasks = [{
                "title": f"Execute goal: {goal_title}",
                "description": goal_description or goal_title,
                "priority": 1
            }]

        logger.info(f"Planner generated {len(parsed_tasks)} tasks for goal '{goal_title}'")
        return parsed_tasks

    def _parse_json_tasks(self, text: str) -> List[Dict[str, Any]]:
        # Clean potential markdown block fences
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned).strip()

        try:
            data = json.loads(cleaned)
            if isinstance(data, dict) and "tasks" in data and isinstance(data["tasks"], list):
                return data["tasks"]
            elif isinstance(data, list):
                return data
        except Exception as e:
            logger.debug(f"JSON parse error in Planner output: {e}")
        
        return []

planner = Planner()
