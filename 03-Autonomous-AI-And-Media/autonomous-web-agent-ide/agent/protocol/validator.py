from typing import Dict, Any, Tuple, Optional
from pydantic import ValidationError

try:
    from protocol.schemas import AgentResponse, ProjectPlan
except ImportError:
    from .schemas import AgentResponse, ProjectPlan

class ProtocolValidator:
    @staticmethod
    def validate_response(data: Dict[str, Any]) -> Tuple[bool, Optional[AgentResponse], Optional[str]]:
        try:
            response = AgentResponse.model_validate(data)
            return True, response, None
        except ValidationError as e:
            return False, None, f"Schema validation error: {e}"

    @staticmethod
    def validate_plan(data: Dict[str, Any]) -> Tuple[bool, Optional[ProjectPlan], Optional[str]]:
        try:
            plan = ProjectPlan.model_validate(data)
            return True, plan, None
        except ValidationError as e:
            return False, None, f"Plan schema error: {e}"
