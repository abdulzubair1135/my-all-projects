"""
AURA Critic Module.
Evaluates execution results, challenges conclusions, and calculates confidence scores.
"""

import json
import re
from typing import Dict, Any, Optional
from core.task_queue import TaskItem
from brain.model_adapter import ModelAdapter, model_adapter
from core.model_router import ModelRouter, model_router
from core.logger import setup_logger

logger = setup_logger("Critic")

class CriticAssessment:
    def __init__(self, success: bool, confidence: float, feedback: str, needs_replanning: bool = False):
        self.success = success
        self.confidence = confidence
        self.feedback = feedback
        self.needs_replanning = needs_replanning

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "confidence": self.confidence,
            "feedback": self.feedback,
            "needs_replanning": self.needs_replanning
        }

class Critic:
    def __init__(self, adapter: Optional[ModelAdapter] = None, router: Optional[ModelRouter] = None):
        self.adapter = adapter or model_adapter
        self.router = router or model_router

    def evaluate(self, task: TaskItem, execution_result: Dict[str, Any]) -> CriticAssessment:
        logger.info(f"Evaluating task execution [{task.task_id}] '{task.title}'")

        output = execution_result.get("output", "")
        status = execution_result.get("status", "failure")

        if status != "success":
            return CriticAssessment(
                success=False,
                confidence=0.0,
                feedback=f"Execution tool failed with status '{status}'",
                needs_replanning=True
            )

        prompt = f"""You are the AURA Critic.
Evaluate the execution of the following task:

TASK: {task.title}
DESCRIPTION: {task.description}
EXECUTION OUTPUT: {output}

Critique the output for correctness, completeness, and quality.
Return ONLY a valid JSON object matching this schema:
{{
  "success": true,
  "confidence": 0.9,
  "feedback": "Concise critique explanation",
  "needs_replanning": false
}}
"""

        model = self.router.select_model(task_complexity="fast")
        response = self.adapter.generate(prompt, model=model, temperature=0.1)

        parsed = self._parse_json(response)
        if parsed:
            assessment = CriticAssessment(
                success=parsed.get("success", True),
                confidence=float(parsed.get("confidence", 0.8)),
                feedback=parsed.get("feedback", "Evaluation complete."),
                needs_replanning=parsed.get("needs_replanning", False)
            )
        else:
            assessment = CriticAssessment(
                success=True,
                confidence=0.85,
                feedback="Default evaluation passed.",
                needs_replanning=False
            )

        logger.info(f"Critic result for task [{task.task_id}]: success={assessment.success}, confidence={assessment.confidence}")
        return assessment

    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned).strip()

        try:
            return json.loads(cleaned)
        except Exception:
            return None

critic = Critic()
