"""
AURA Tool Registry.
Registers and provides lookup for execution tools.
"""

from typing import Dict, Any, Optional
from tools.base_tool import BaseTool
from tools.echo_tool import EchoTool
from core.logger import setup_logger

logger = setup_logger("ToolRegistry")

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        # Register default phase 1 tools
        self.register_tool(EchoTool())

    def register_tool(self, tool: BaseTool):
        self._tools[tool.name] = tool
        logger.info(f"Registered tool '{tool.name}'")

    def get_tool(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> Dict[str, str]:
        return {name: tool.description for name, tool in self._tools.items()}

tool_registry = ToolRegistry()
