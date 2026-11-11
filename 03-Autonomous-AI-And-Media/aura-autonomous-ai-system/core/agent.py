"""
AURA Main Cognitive Agent.
Orchestrates the Phase 1 autonomous cognitive loop: THINK -> PLAN -> EXECUTE -> VERIFY -> REMEMBER.
"""

import uuid
import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from config import config
from core.planner import Planner, planner
from core.task_queue import TaskQueue, task_queue, TaskItem
from core.executor import Executor, executor
from core.critic import Critic, critic
from core.reflection import Reflection, reflection
from core.decision import DecisionEngine, decision_engine
from core.controller import Controller, controller
from core.context import ContextManager, context_manager
from database.db import DatabaseManager, db_manager
from core.logger import setup_logger

logger = setup_logger("Agent")

class AgentState(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    CRITIQUING = "critiquing"
    REFLECTING = "reflecting"
    STOPPED = "stopped"

class Agent:
    def __init__(
        self,
        planner_inst: Optional[Planner] = None,
        queue_inst: Optional[TaskQueue] = None,
        executor_inst: Optional[Executor] = None,
        critic_inst: Optional[Critic] = None,
        reflection_inst: Optional[Reflection] = None,
        context_inst: Optional[ContextManager] = None,
        controller_inst: Optional[Controller] = None,
        db_inst: Optional[DatabaseManager] = None
    ):
        self.planner = planner_inst or planner
        self.queue = queue_inst or task_queue
        self.executor = executor_inst or executor
        self.critic = critic_inst or critic
        self.reflection = reflection_inst or reflection
        self.context = context_inst or context_manager
        self.controller = controller_inst or controller
        self.db = db_inst or db_manager
        self.state = AgentState.IDLE

    def set_goal(self, title: str, description: str = "") -> str:
        """Sets a high-level goal, stores it in SQLite, and plans initial sub-tasks."""
        goal_id = f"goal_{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now().isoformat()
        
        self.db.execute_update(
            "INSERT INTO goals (goal_id, title, description, status, priority, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (goal_id, title, description, "in_progress", 1, now, now)
        )

        self.context.working_memory.set_active_goal(goal_id, title)
        logger.info(f"Set goal [{goal_id}] '{title}'")

        # Plan sub-tasks for goal
        self.state = AgentState.PLANNING
        tasks = self.planner.plan_goal(title, description)
        for t in tasks:
            self.queue.add_task(
                title=t["title"],
                description=t.get("description", ""),
                goal_id=goal_id,
                priority=t.get("priority", 1)
            )

        self.state = AgentState.IDLE
        return goal_id

    def run_step(self) -> Optional[Dict[str, Any]]:
        """
        Executes a single step in the cognitive cycle:
        1. Pop highest priority task from TaskQueue.
        2. Execute task via Executor.
        3. Critique execution output via Critic.
        4. Reflect on outcome and store experience via Reflection.
        """
        if self.controller.is_stopped:
            self.state = AgentState.STOPPED
            logger.info("Agent is stopped. Aborting step.")
            return None

        if self.controller.is_paused:
            logger.info("Agent is paused. Waiting.")
            return None

        task = self.queue.pop_next_task()
        if not task:
            logger.info("No pending tasks in queue. Agent is IDLE.")
            self.state = AgentState.IDLE
            return None

        # 1. Execute
        self.state = AgentState.EXECUTING
        decision_engine.record_decision(
            task_id=task.task_id,
            reasoning=f"Selected pending task '{task.title}' for execution",
            choice="execute_task"
        )
        
        exec_result = self.executor.execute_task(task, self.context.working_memory)

        # 2. Critique
        self.state = AgentState.CRITIQUING
        critic_assessment = self.critic.evaluate(task, exec_result)

        # Update task status based on critique
        if critic_assessment.success:
            self.queue.update_task_status(task.task_id, "completed", result=exec_result.get("output"))
        else:
            if task.retry_count < config.max_task_retries:
                logger.warning(f"Task [{task.task_id}] failed critique. Scheduling retry.")
                self.queue.update_task_status(task.task_id, "pending", increment_retry=True)
            else:
                logger.error(f"Task [{task.task_id}] exceeded retry limit. Marking failed.")
                self.queue.update_task_status(task.task_id, "failed", result=exec_result.get("output"))

        # 3. Reflect & Store
        self.state = AgentState.REFLECTING
        refl_result = self.reflection.reflect_on_task(task, exec_result, critic_assessment)

        self.state = AgentState.IDLE
        return {
            "task_id": task.task_id,
            "title": task.title,
            "execution": exec_result,
            "critique": critic_assessment.to_dict(),
            "reflection": refl_result
        }

    def run_loop(self, max_steps: Optional[int] = None) -> List[Dict[str, Any]]:
        """Run cognitive loop until queue is empty or max_steps is reached."""
        steps_history = []
        step_count = 0
        logger.info("Starting Agent cognitive loop...")

        while not self.controller.is_stopped:
            if max_steps is not None and step_count >= max_steps:
                logger.info(f"Reached max steps limit ({max_steps}). Loop ending.")
                break

            result = self.run_step()
            if result is None:
                # No tasks or stopped
                break

            steps_history.append(result)
            step_count += 1

        logger.info(f"Cognitive loop finished. Executed {len(steps_history)} steps.")
        return steps_history

agent = Agent()
