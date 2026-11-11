"""
AURA Base Tool Interface.
Defines base class for all tools executable by AURA.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    name: str
    description: str
    parameters_schema: Dict[str, Any]

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool action and return a structured result dict."""
        pass
