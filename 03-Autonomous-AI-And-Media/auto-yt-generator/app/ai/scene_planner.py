"""
AUTO YT GENERATOR — AI Scene Planner & Storyboard Director Engine.

Converts 7-phase retention scripts into professional storyboard scene beats using:
- SemanticDirector (emotion, intent, and keyword extraction)
- ActingDirector (expressive character staging, gestures, and gaze)
- CameraDirector (shot framing, zoom curves, and parallax depth)
- Infographic & B-Roll Cutaway detection
"""

import json
from typing import Optional, List
from app.ai.provider import AIProvider
from app.ai.providers import get_ai_provider
from app.models.project import ProjectModel
from app.models.script import ScriptModel
from app.models.scene import ScenePlan, SceneModel, SceneAction, CameraConfig, ShotType
from app.director.semantic import semantic_director
from app.director.acting import acting_director
from app.director.camera import camera_director
from app.pipeline.cache import cache
from app.logger import logger


class ScenePlannerEngine:
    """Converts narration script sections into actionable 2D animation scene plans."""

    def __init__(self, provider: Optional[AIProvider] = None):
        self.provider = provider or get_ai_provider()

    def plan_scenes(self, project: ProjectModel, script: ScriptModel) -> ScenePlan:
        """Transforms a ScriptModel into a granular, semantic ScenePlan storyboard."""
        cache_key = cache.generate_key(
            "scene_plan_v2",
            {
                "project_id": project.id,
                "script_title": script.title,
                "sections_count": len(script.sections),
                "style": project.config.style,
            },
        )
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Loaded scene plan for project '{project.id}' from cache.")
            return ScenePlan(**cached_data)

        logger.info(f"Directing storyboard scenes for project {project.id} ({len(script.sections)} sections)...")

        planned_scenes: List[SceneModel] = []
        scene_idx = 1

        for s in script.sections:
            narration = s.narration_text or s.title
            duration = max(3.0, float(s.estimated_duration_sec))

            # 1. Semantic Analysis
            semantic_cue = semantic_director.analyze_narration_beat(narration, section_name=s.section_type)

            # 2. Check for Infographic Cutaway Opportunity
            has_cutaway, infographic_cfg = semantic_director.detect_infographic_opportunity(narration)

            # 3. Camera Direction
            cam_cfg = camera_director.direct_camera_for_scene(semantic_cue, is_cutaway=has_cutaway)

            # 4. Acting Direction
            char_id = "main_character"
            acting_action = acting_director.direct_acting_performance(
                semantic=semantic_cue,
                character_id=char_id,
                duration_sec=duration,
                is_infographic_present=has_cutaway,
            )

            # 5. Determine Background & Props
            bg_id = "bedroom_dark"
            props = []
            if "brain" in project.config.topic.lower() or "brain" in narration.lower():
                bg_id = "brain_interior" if s.section_type in ["explanation", "escalation", "surprising_fact"] else "bedroom_dark"
                props = ["energy_beam"] if bg_id == "brain_interior" else ["clock"]
            elif "company" in project.config.topic.lower() or "billion" in project.config.topic.lower():
                bg_id = "laboratory" if s.section_type in ["explanation", "escalation"] else "bedroom_dark"
                props = ["glowing_orb"]

            # 6. Contextual SFX & VFX Overlays
            effects = ["vignette", "film_grain"]
            sfx = ["whoosh"]
            if semantic_cue.emotion in ["fear", "shock"]:
                effects.extend(["heartbeat_pulse", "glitch"])
                sfx.extend(["heartbeat", "impact"])
            elif semantic_cue.intent == "question":
                sfx.append("clock_ticking")

            scene_item = SceneModel(
                scene_index=scene_idx,
                section_ref=s.section_type,
                duration_sec=duration,
                narration_text=narration,
                is_cutaway=has_cutaway,
                infographic=infographic_cfg,
                background_id=bg_id,
                characters=[char_id] if not has_cutaway or acting_action.position_x_percent < 40 else [char_id],
                props=props,
                actions=[acting_action],
                camera=cam_cfg,
                semantic=semantic_cue,
                effects=effects,
                sfx=sfx,
                mood=semantic_cue.emotion,
                subtitle_text=narration,
            )

            planned_scenes.append(scene_item)
            scene_idx += 1

        total_dur = sum(sc.duration_sec for sc in planned_scenes)
        scene_plan = ScenePlan(
            project_id=project.id,
            total_scenes=len(planned_scenes),
            total_duration_sec=total_dur,
            scenes=planned_scenes,
        )

        cache.set(cache_key, "scene_plan_v2", scene_plan.model_dump())
        logger.info(f"Storyboard planning complete: {len(planned_scenes)} scenes directed.")
        return scene_plan


# Default scene planner engine instance
scene_planner_engine = ScenePlannerEngine()
