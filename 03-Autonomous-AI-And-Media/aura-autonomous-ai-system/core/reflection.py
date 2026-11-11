"""
AURA Reflection Module (Phase 2 Enhanced).
Analyzes task execution, extracts lessons, updates semantic memory, episodic memory, skill memory, and knowledge gaps.
"""

import uuid
import datetime
import json
import re
from typing import Dict, Any, Optional
from core.task_queue import TaskItem
from core.critic import CriticAssessment
from brain.model_adapter import ModelAdapter, model_adapter
from core.model_router import ModelRouter, model_router
from database.db import DatabaseManager, db_manager
from memory.semantic_memory import SemanticMemory, semantic_memory
from memory.episodic_memory import EpisodicMemory, episodic_memory
from memory.skill_memory import SkillMemory, skill_memory
from core.logger import setup_logger

logger = setup_logger("Reflection")

class Reflection:
    def __init__(
        self,
        adapter: Optional[ModelAdapter] = None,
        router: Optional[ModelRouter] = None,
        db: Optional[DatabaseManager] = None,
        episodic_inst: Optional[EpisodicMemory] = None,
        semantic_inst: Optional[SemanticMemory] = None,
        skill_inst: Optional[SkillMemory] = None
    ):
        self.adapter = adapter or model_adapter
        self.router = router or model_router
        self.db = db or db_manager
        self.episodic = episodic_inst or EpisodicMemory(db=self.db)
        self.semantic = semantic_inst or SemanticMemory(db=self.db)
        self.skill = skill_inst or SkillMemory(db=self.db)

    def reflect_on_task(
        self,
        task: TaskItem,
        execution_result: Dict[str, Any],
        critic_assessment: CriticAssessment
    ) -> Dict[str, Any]:
        """
        Extracts lessons learned and updates episodic memory, semantic facts, skills, and knowledge gaps.
        """
        logger.info(f"Reflecting on task [{task.task_id}] '{task.title}'")

        prompt = f"""You are the AURA Reflection Engine.
Analyze this task outcome:

TASK: {task.title}
GOAL_ID: {task.goal_id}
EXECUTION OUTPUT: {execution_result.get('output', '')}
CRITIC FEEDBACK: {critic_assessment.feedback}
CRITIC SUCCESS: {critic_assessment.success}

Summarize lessons learned and knowledge gained.
Return ONLY a valid JSON object matching this schema:
{{
  "lesson": "Key lesson learned",
  "cause": "Cause of success or failure",
  "fix": "Fix or optimization applied if any",
  "fact": "General concept fact learned if any",
  "skill_name": "Technical skill name exercised",
  "knowledge_gaps": ["List of follow-up knowledge gaps discovered"]
}}
"""

        model = self.router.select_model(task_complexity="fast")
        response = self.adapter.generate(prompt, model=model, temperature=0.2)
        parsed = self._parse_json(response)

        lesson = parsed.get("lesson", "Task executed.") if parsed else "Task execution recorded."
        cause = parsed.get("cause", "Direct tool execution.") if parsed else "Direct execution."
        fix = parsed.get("fix", "N/A") if parsed else "N/A"
        fact = parsed.get("fact") if parsed else None
        skill_n = parsed.get("skill_name", task.title.split()[0] if task.title else "General") if parsed else "General"
        knowledge_gaps = parsed.get("knowledge_gaps", []) if parsed else []

        result_str = "SUCCESS" if critic_assessment.success else "FAILURE"

        # 1. Store in Episodic Memory
        exp_id = self.episodic.add_experience(
            goal=task.title,
            result=result_str,
            lesson=lesson,
            task_id=task.task_id,
            cause=cause,
            fix=fix
        )

        # 2. Store fact in Semantic Memory if extracted
        if fact:
            self.semantic.add_fact(topic=skill_n, content=fact, source=f"task_{task.task_id}")

        # 3. Update Skill Memory
        self.skill.record_skill_level(
            name=skill_n,
            theoretical_level="medium" if critic_assessment.success else "low",
            practical_level="medium" if critic_assessment.success else "low"
        )

        # 4. Record knowledge gaps if discovered
        for gap in knowledge_gaps:
            gap_id = f"gap_{uuid.uuid4().hex[:8]}"
            self.db.execute_update(
                """INSERT INTO knowledge_gaps (id, topic, rationale, priority, status)
                   VALUES (?, ?, ?, ?, ?)""",
                (gap_id, gap, f"Discovered during reflection on task '{task.title}'", 1, "open")
            )

        logger.info(f"Reflection stored experience [{exp_id}] with lesson: '{lesson}'")
        return {
            "experience_id": exp_id,
            "lesson": lesson,
            "cause": cause,
            "fix": fix,
            "fact": fact,
            "skill": skill_n,
            "knowledge_gaps": knowledge_gaps
        }

    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return None

reflection = Reflection()
