"""
AURA Curiosity Engine Module.
Autonomously generates next candidate learning topics based on knowledge gaps, concept relationships, and self-model awareness.
"""

from typing import List, Dict, Any, Optional
from learning.knowledge_gap import KnowledgeGapEngine, knowledge_gap_engine
from memory.knowledge_graph import KnowledgeGraph, knowledge_graph
from memory.self_model import SelfModel, self_model
from brain.model_adapter import ModelAdapter, model_adapter
from core.model_router import ModelRouter, model_router
from core.logger import setup_logger

logger = setup_logger("CuriosityEngine")

class CuriosityEngine:
    def __init__(
        self,
        gap_inst: Optional[KnowledgeGapEngine] = None,
        graph_inst: Optional[KnowledgeGraph] = None,
        self_inst: Optional[SelfModel] = None,
        adapter: Optional[ModelAdapter] = None,
        router: Optional[ModelRouter] = None
    ):
        self.gaps = gap_inst or knowledge_gap_engine
        self.graph = graph_inst or knowledge_graph
        self.self_m = self_inst or self_model
        self.adapter = adapter or model_adapter
        self.router = router or model_router

    def propose_next_learning_topic(self) -> Dict[str, Any]:
        """
        Analyzes internal state and proposes a candidate learning topic with rationale and priority.
        """
        logger.info("CuriosityEngine evaluating next topic candidate...")

        # 1. Check open knowledge gaps first
        open_gaps = self.gaps.get_open_gaps(limit=1)
        if open_gaps:
            gap = open_gaps[0]
            logger.info(f"Curiosity selected topic from knowledge gap: '{gap['topic']}'")
            return {
                "topic": gap["topic"],
                "rationale": gap.get("rationale") or f"Resolved open knowledge gap in '{gap['topic']}'",
                "source": "knowledge_gap",
                "priority": gap.get("priority", 1),
                "gap_id": gap["id"]
            }

        # 2. Check concept graph subtopics or prerequisites of known concepts
        summary = self.self_m.get_self_summary()
        known = summary.get("known_topics", [])
        if known:
            last_known = known[0]
            subtopics = self.graph.get_subtopics(last_known)
            if subtopics:
                next_topic = subtopics[0]
                logger.info(f"Curiosity selected subtopic '{next_topic}' of known concept '{last_known}'")
                return {
                    "topic": next_topic,
                    "rationale": f"Explores subtopic of known concept '{last_known}'",
                    "source": "knowledge_graph",
                    "priority": 2
                }

        # 3. Fallback: Generate curious topic using local LLM
        prompt = f"""You are the AURA Autonomous Curiosity Engine.
Analyze current known topics: {known or ['Python', 'Networking', 'AsyncIO']}

Propose 1 useful, practical software engineering or computer science topic to learn next.
Return ONLY a valid JSON object matching this schema:
{{
  "topic": "Topic title",
  "rationale": "Why this topic is useful to learn next",
  "priority": 1
}}
"""
        model = self.router.select_model(task_complexity="fast")
        response = self.adapter.generate(prompt, model=model, temperature=0.3)
        parsed = self._parse_json(response)

        if parsed and "topic" in parsed:
            return {
                "topic": parsed["topic"],
                "rationale": parsed.get("rationale", "Autonomous curiosity proposal."),
                "source": "curiosity_llm",
                "priority": parsed.get("priority", 1)
            }

        return {
            "topic": "Python AsyncIO and Concurrency Fundamentals",
            "rationale": "Default autonomous curiosity topic.",
            "source": "default_curiosity",
            "priority": 1
        }

    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        import json, re
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return None

curiosity_engine = CuriosityEngine()
