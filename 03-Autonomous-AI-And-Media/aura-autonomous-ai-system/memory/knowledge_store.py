"""
AURA Unified Knowledge Store.
Provides single-point memory query interface with threshold evaluation before external research.
"""

from typing import Dict, Any, List, Optional
from memory.semantic_memory import SemanticMemory, semantic_memory
from memory.episodic_memory import EpisodicMemory, episodic_memory
from memory.procedural_memory import ProceduralMemory, procedural_memory
from memory.skill_memory import SkillMemory, skill_memory
from memory.knowledge_graph import KnowledgeGraph, knowledge_graph
from memory.self_model import SelfModel, self_model
from core.logger import setup_logger

logger = setup_logger("KnowledgeStore")

class KnowledgeStore:
    def __init__(
        self,
        semantic: Optional[SemanticMemory] = None,
        episodic: Optional[EpisodicMemory] = None,
        procedural: Optional[ProceduralMemory] = None,
        skills: Optional[SkillMemory] = None,
        graph: Optional[KnowledgeGraph] = None,
        self_m: Optional[SelfModel] = None
    ):
        self.semantic = semantic or semantic_memory
        self.episodic = episodic or episodic_memory
        self.procedural = procedural or procedural_memory
        self.skills = skills or skill_memory
        self.graph = graph or knowledge_graph
        self.self_m = self_m or self_model

    def query_memory(self, question: str, threshold: float = 0.4) -> Dict[str, Any]:
        """
        Queries all memory types for relevance.
        Returns result dict with `sufficient` flag indicating if memory answer exists.
        """
        logger.info(f"Querying knowledge store for: '{question}'")

        facts = self.semantic.search_facts(question, top_k=3)
        experiences = self.episodic.search_experiences(question, top_k=3)

        # Check max similarity score
        max_sim = 0.0
        if facts:
            max_sim = max(max_sim, max(f.get("similarity", 0.0) for f in facts))
        if experiences:
            max_sim = max(max_sim, max(e.get("similarity", 0.0) for e in experiences))

        sufficient = max_sim >= threshold

        return {
            "query": question,
            "sufficient": sufficient,
            "max_similarity": max_sim,
            "facts": facts,
            "experiences": experiences
        }

knowledge_store = KnowledgeStore()
