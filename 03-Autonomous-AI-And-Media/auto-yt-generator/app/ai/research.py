"""
AUTO YT GENERATOR — Research Engine.

Performs topic concept analysis and separates:
- Verified scientific facts
- Underlying assumptions
- Hypothetical scenarios
- Numerical estimates / timelines
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from app.ai.provider import AIProvider
from app.ai.providers import get_ai_provider
from app.pipeline.cache import cache
from app.logger import logger


class ResearchResult(BaseModel):
    """Structured research data model for topic grounding."""

    topic: str
    summary: str
    verified_facts: List[str] = Field(default_factory=list, description="Direct scientific/factual realities")
    assumptions: List[str] = Field(default_factory=list, description="Baseline conditions assumed")
    hypothetical_scenarios: List[str] = Field(default_factory=list, description="What-if thought experiments")
    estimates: List[str] = Field(default_factory=list, description="Estimated numbers, durations, rates")
    key_concepts: List[str] = Field(default_factory=list, description="Core keywords and mechanisms")


class ResearchEngine:
    """Extracts factual concepts and narrative foundations for any video topic."""

    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or get_ai_provider()

    def research_topic(self, topic: str, tone: str = "scientific_mysterious") -> ResearchResult:
        """Executes research on topic using caching and structured schema enforcement."""
        cache_key = cache.generate_key("research", {"topic": topic, "tone": tone})
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Loaded research for topic '{topic}' from cache.")
            return ResearchResult(**cached_data)

        system_prompt = (
            "You are a Senior Science Researcher and Fact-Checker for high-retention educational documentaries.\n"
            "Your job is to thoroughly break down the given topic.\n"
            "CRITICAL: You must strictly separate verified facts from hypothetical scenarios and assumptions.\n"
            "Do NOT present speculative theories as established scientific facts."
        )

        prompt = (
            f"TOPIC: {topic}\n"
            f"TONE: {tone}\n\n"
            "Provide a comprehensive, scientifically rigorous research breakdown covering:\n"
            "1. Verified biological/physical mechanisms\n"
            "2. Baseline assumptions\n"
            "3. Hypothetical scenarios or thought experiments\n"
            "4. Quantifiable estimates and timelines (e.g. 0s, 10s, 3m, etc.)\n"
            "5. Core educational keywords/concepts."
        )

        logger.info(f"Researching topic: '{topic}' with tone: '{tone}'")
        result: ResearchResult = self.provider.generate_structured(
            prompt=prompt,
            schema_cls=ResearchResult,
            system_prompt=system_prompt,
            temperature=0.3,
        )

        cache.set(cache_key, "research", result.model_dump())
        return result
