import json
import asyncio
from typing import Dict, Any, Optional
try:
    from browser.providers.base import LLMProvider
    from core.cognitive_engine import CognitiveAIEngine
except ImportError:
    from .base import LLMProvider
    from ...core.cognitive_engine import CognitiveAIEngine

class MockLocalProvider(LLMProvider):
    """
    Intelligent high-fidelity local LLM simulator.
    Dynamically generates full-stack code for Pomodoro Apps, Calculators, Note Apps, Expense Trackers, and Web Apps.
    """

    def __init__(self):
        self.iteration = 0

    async def connect(self) -> bool:
        return True

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "provider": "mock_provider"}

    async def close(self):
        pass

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        await asyncio.sleep(0.02)
        self.iteration += 1

        sys_lower = (system_prompt or "").lower()
        prompt_lower = prompt.lower()

        # Extract core task title/prompt without attached context blob for deterministic mock routing
        core_prompt = prompt.split("📂 EXISTING CODEBASE")[0] if "📂 EXISTING CODEBASE" in prompt else prompt

        # 1. Refiner request (checked first because refiner prompt references reviewer critique)
        if "refiner" in sys_lower or ("refine" in prompt_lower and "plan" not in prompt_lower and "architect" not in sys_lower):
            resp = CognitiveAIEngine.generate_code_actions(core_prompt)
            return f"```json\n{json.dumps(resp, indent=2)}\n```"

        # 2. Reviewer Judge request
        if ("reviewer" in sys_lower and "refiner" not in sys_lower) or "evaluate quality and edge cases" in prompt_lower or ("review" in prompt_lower and "actions generated" in prompt_lower):
            return json.dumps({
                "passed": True,
                "score": 95,
                "critique": "High code quality, modular components, and comprehensive error handling verified.",
                "required_fixes": []
            })

        # 3. Planner / Architect request
        if "planner" in sys_lower or "architect" in sys_lower or "project plan" in prompt_lower or "architectural mission" in prompt_lower:
            if "engineering task" not in prompt_lower and "coding" not in sys_lower:
                plan_data = CognitiveAIEngine.generate_plan(core_prompt)
                return f"```json\n{json.dumps(plan_data, indent=2)}\n```"

        # 4. Coding / Engineering turn
        resp = CognitiveAIEngine.generate_code_actions(core_prompt)
        return f"```json\n{json.dumps(resp, indent=2)}\n```"
