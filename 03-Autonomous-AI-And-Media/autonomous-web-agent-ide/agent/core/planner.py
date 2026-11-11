import json
from typing import Dict, Any, List, Optional

try:
    from protocol.schemas import ProjectPlan, TaskNode
    from protocol.parser import ProtocolParser
    from protocol.validator import ProtocolValidator
    from browser.providers.base import LLMProvider
    from prompts.system_prompts import PLANNER_SYSTEM_PROMPT
except ImportError:
    from ..protocol.schemas import ProjectPlan, TaskNode
    from ..protocol.parser import ProtocolParser
    from ..protocol.validator import ProtocolValidator
    from ..browser.providers.base import LLMProvider
    from ..prompts.system_prompts import PLANNER_SYSTEM_PROMPT

class Planner:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    async def create_plan(self, user_prompt: str) -> ProjectPlan:
        prompt = f"Requirement: {user_prompt}\n\nPlease generate project plan with tasks and dependencies."
        raw_response = await self.provider.generate(prompt, system_prompt=PLANNER_SYSTEM_PROMPT)

        parsed_dict = ProtocolParser.parse_raw_response(raw_response)
        is_valid, plan, error = ProtocolValidator.validate_plan(parsed_dict)

        if not is_valid or plan is None:
            raise ValueError(f"Failed to generate valid project plan: {error}")

        return plan
