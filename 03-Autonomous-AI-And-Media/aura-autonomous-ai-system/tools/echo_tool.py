"""
AURA Echo Tool.
Basic tool for testing execution pipeline.
"""

from typing import Dict, Any
from tools.base_tool import BaseTool

class EchoTool(BaseTool):
    name = "echo"
    description = "Echoes back the provided message for testing and basic verification."
    parameters_schema = {
        "message": {"type": "string", "description": "The message to echo"}
    }

    def execute(self, message: str = "", **kwargs) -> Dict[str, Any]:
        return {
            "status": "success",
            "output": f"Echo: {message}"
        }
