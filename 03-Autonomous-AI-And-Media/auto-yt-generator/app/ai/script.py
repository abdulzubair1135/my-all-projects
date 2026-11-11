"""
AUTO YT GENERATOR — Script Generation Engine.

Converts research into a high-retention YouTube documentary script following
the proven 7-stage narrative structure:
HOOK -> SETUP -> QUESTION -> EXPLANATION -> ESCALATION -> SURPRISING FACT -> CONCLUSION
"""

import json
from typing import Optional
from app.ai.provider import AIProvider
from app.ai.providers import get_ai_provider
from app.ai.research import ResearchResult
from app.models.script import ScriptModel, ScriptSection
from app.models.project import ProjectModel
from app.pipeline.cache import cache
from app.logger import logger


class ScriptEngine:
    """Generates structured, validated narration scripts with timestamps and visual cues."""

    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or get_ai_provider()

    def generate_script(self, project: ProjectModel, research: ResearchResult) -> ScriptModel:
        """Transforms research and project configuration into a full structured script."""
        cache_key = cache.generate_key(
            "script",
            {
                "topic": project.config.topic,
                "language": project.config.language,
                "style": project.config.style,
                "duration": project.config.duration_seconds,
            },
        )
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Loaded script for project '{project.id}' from cache.")
            return ScriptModel(**cached_data)

        system_prompt = (
            "You are a Master YouTube Scriptwriter and 2D Animation Director.\n"
            "You write highly engaging, retention-optimized scripts for cartoon/documentary videos.\n\n"
            "STRICT NARRATIVE STRUCTURE REQUIRED:\n"
            "1. HOOK: Immediate curiosity gap within first 5 seconds\n"
            "2. SETUP: Establish the world and baseline reality\n"
            "3. QUESTION: Raise the core mystery or mechanism\n"
            "4. EXPLANATION: Break down how the science/system works step-by-step\n"
            "5. ESCALATION: Raise the stakes or explain the worst-case scenario / tipping point\n"
            "6. SURPRISING FACT: Reveal a bizarre, counterintuitive, or little-known twist\n"
            "7. CONCLUSION: Memorable takeaway and philosophical punchline\n\n"
            "RULES:\n"
            "- Write in conversational, gripping language. Avoid boring academic jargon.\n"
            "- Provide vivid visual animation instructions for every section.\n"
            "- Provide audio/sound mood suggestions for each section.\n"
            "- Language requirement: Write narration strictly in the requested language code.\n"
        )

        research_context = (
            f"VERIFIED FACTS: {', '.join(research.verified_facts)}\n"
            f"ASSUMPTIONS: {', '.join(research.assumptions)}\n"
            f"HYPOTHETICALS: {', '.join(research.hypothetical_scenarios)}\n"
            f"ESTIMATES: {', '.join(research.estimates)}\n"
            f"KEY CONCEPTS: {', '.join(research.key_concepts)}"
        )

        prompt = (
            f"TOPIC: {project.config.topic}\n"
            f"LANGUAGE: {project.config.language}\n"
            f"STYLE: {project.config.style}\n"
            f"TARGET DURATION: {project.config.duration_seconds} seconds\n"
            f"VOICE STYLE: {project.config.voice_style}\n"
            f"TONE: {project.config.tone}\n\n"
            f"RESEARCH CONTEXT:\n{research_context}\n\n"
            "Generate the complete structured ScriptModel with all 7 narrative sections, estimated durations, "
            "and YouTube optimization metadata (title options, description, tags)."
        )

        logger.info(f"Generating script for project {project.id} ({project.config.topic}).")
        script: ScriptModel = self.provider.generate_structured(
            prompt=prompt,
            schema_cls=ScriptModel,
            system_prompt=system_prompt,
            temperature=0.4,
        )

        # Ensure project_id matches
        script.project_id = project.id

        cache.set(cache_key, "script", script.model_dump())
        return script
