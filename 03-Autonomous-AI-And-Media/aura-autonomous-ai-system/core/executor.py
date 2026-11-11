"""
AURA Executor Module.
Executes individual tasks using available tools or LLM reasoning actions.
"""

import uuid
import datetime
import json
from typing import Dict, Any, Optional
from core.task_queue import TaskItem
from tools.tool_registry import ToolRegistry, tool_registry
from memory.working_memory import WorkingMemory, ContextStep
from brain.model_adapter import ModelAdapter, model_adapter
from core.model_router import ModelRouter, model_router
from database.db import DatabaseManager, db_manager
from core.logger import setup_logger

logger = setup_logger("Executor")

class Executor:
    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        adapter: Optional[ModelAdapter] = None,
        router: Optional[ModelRouter] = None,
        db: Optional[DatabaseManager] = None
    ):
        self.registry = registry or tool_registry
        self.adapter = adapter or model_adapter
        self.router = router or model_router
        self.db = db or db_manager

    def execute_task(self, task: TaskItem, working_memory: WorkingMemory) -> Dict[str, Any]:
        """
        Executes a task and records action output into working memory and SQLite database.
        """
        logger.info(f"Executing task [{task.task_id}] '{task.title}'")
        working_memory.set_active_task(task.task_id, task.title)

        # Check if task specifies a direct tool execution (e.g. echo tool or generic execution)
        tool = self.registry.get_tool("echo")
        if tool and ("echo" in task.title.lower() or "test" in task.title.lower()):
            tool_result = tool.execute(message=task.description or task.title)
            output_str = tool_result.get("output", str(tool_result))
            status = tool_result.get("status", "success")
            tool_name = "echo"
        else:
            # Generate action response using model adapter
            context_summary = working_memory.get_context_summary()
            prompt = f"""You are the AURA Task Executor.
Context:
{context_summary}

TASK TO EXECUTE: {task.title}
DESCRIPTION: {task.description}

Provide the execution step and answer or result for this task:"""

            model = self.router.select_model(task_complexity="normal")
            response = self.adapter.generate(prompt, model=model)
            output_str = response
            status = "success"
            tool_name = "llm_reasoning"

        now = datetime.datetime.now().isoformat()
        action_id = f"action_{uuid.uuid4().hex[:8]}"

        # Record action in SQLite
        self.db.execute_update(
            """INSERT INTO actions (id, task_id, tool_name, tool_input, tool_output, status, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (action_id, task.task_id, tool_name, task.description, output_str, status, now)
        )

        # Record in Working Memory
        step = ContextStep(
            step_id=action_id,
            action=tool_name,
            input_data=task.description,
            output_data=output_str,
            status=status,
            timestamp=now
        )
        working_memory.add_step(step)

        logger.info(f"Execution completed for task [{task.task_id}] with status '{status}'")
        return {
            "action_id": action_id,
            "tool_name": tool_name,
            "status": status,
            "output": output_str
        }

executor = Executor()
