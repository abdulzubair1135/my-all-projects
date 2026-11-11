"""
AURA Autonomous Scheduler Module.
Drives continuous learning cycles even when no explicit user task is provided.
"""

from typing import Dict, Any, Optional
from core.agent import Agent, agent
from core.task_queue import TaskQueue, task_queue
from learning.curiosity import CuriosityEngine, curiosity_engine
from learning.knowledge_gap import KnowledgeGapEngine, knowledge_gap_engine
from core.logger import setup_logger

logger = setup_logger("AutonomousScheduler")

class AutonomousScheduler:
    def __init__(
        self,
        agent_inst: Optional[Agent] = None,
        queue_inst: Optional[TaskQueue] = None,
        curiosity_inst: Optional[CuriosityEngine] = None,
        gap_inst: Optional[KnowledgeGapEngine] = None
    ):
        self.agent = agent_inst or agent
        self.queue = queue_inst or task_queue
        self.curiosity = curiosity_inst or curiosity_engine
        self.gaps = gap_inst or knowledge_gap_engine

    def run_autonomous_cycle(self, max_steps: int = 1) -> Optional[Dict[str, Any]]:
        """
        Executes an autonomous cycle:
        1. If tasks exist in queue, execute next task.
        2. If queue is empty, trigger CuriosityEngine to propose topic, set goal, and execute step.
        """
        logger.info("Scheduler checking task queue...")

        pending = self.queue.get_pending_tasks()
        if pending:
            logger.info(f"Found {len(pending)} pending tasks. Executing next task.")
            return self.agent.run_step()

        # Queue is empty: trigger autonomous curiosity
        logger.info("No pending tasks found. Triggering CuriosityEngine...")
        proposal = self.curiosity.propose_next_learning_topic()
        topic = proposal["topic"]
        rationale = proposal["rationale"]

        logger.info(f"Autonomous Scheduler selected topic: '{topic}' (rationale: {rationale})")

        # Set new goal & plan tasks
        self.agent.set_goal(
            title=f"Autonomous Research: {topic}",
            description=rationale
        )

        # Mark gap resolved if source was knowledge_gap
        if proposal.get("source") == "knowledge_gap" and proposal.get("gap_id"):
            self.gaps.mark_resolved(proposal["gap_id"])

        # Execute first step of new goal
        return self.agent.run_step()

autonomous_scheduler = AutonomousScheduler()
