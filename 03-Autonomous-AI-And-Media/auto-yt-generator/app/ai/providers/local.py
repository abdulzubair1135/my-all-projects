"""
AUTO YT GENERATOR — Local Offline Fallback AI Provider.

Generates realistic structured research, scripts, and scene plans algorithmically.
Allows the full pipeline to run reliably in testing, CI/CD, and offline environments.
"""

import json
import re
from typing import Optional, Type, Dict, Any
from pydantic import BaseModel
from app.ai.provider import AIProvider
from app.logger import logger


class LocalAIProvider(AIProvider):
    """Offline deterministic AI provider for development and testing."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = "local-rule-engine"):
        super().__init__(api_key=api_key, model_name=model_name)

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        logger.info("LocalAIProvider generating text (offline rule engine).")
        return f"Generated response for: {prompt[:100]}..."

    def generate_structured(
        self,
        prompt: str,
        schema_cls: Type[BaseModel],
        system_prompt: Optional[str] = None,
        temperature: float = 0.5,
    ) -> BaseModel:
        logger.info(f"LocalAIProvider generating structured JSON for schema: {schema_cls.__name__}")

        # Extract topic from prompt
        topic_match = re.search(r"TOPIC:\s*(.*?)(?:\n|$)", prompt, re.IGNORECASE)
        topic = topic_match.group(1).strip() if topic_match else "Human Biology & Nature"

        schema_name = schema_cls.__name__

        if schema_name == "ResearchResult":
            data = {
                "topic": topic,
                "summary": f"A comprehensive scientific breakdown of what happens during '{topic}'.",
                "verified_facts": [
                    f"The fundamental mechanism underlying {topic} involves primary biological or physical systems.",
                    "Cells require continuous oxygen and glucose delivery to maintain metabolic homeostasis.",
                    "Within 10 to 30 seconds of cessation, electrical activity begins to alter dramatically.",
                    "Irreversible cellular degradation typically begins after 4 to 6 minutes without restoration.",
                ],
                "assumptions": [
                    "Standard environmental temperature and normal baseline physiological conditions.",
                    "No immediate medical intervention or artificial life support applied.",
                ],
                "hypothetical_scenarios": [
                    "What happens if consciousness persists for several seconds after the event?",
                    "What if environmental cooling slows down cellular decay rates?",
                ],
                "estimates": [
                    "Approximate timeline: 0s shock, 10s loss of consciousness, 3-5 mins critical window.",
                    "Roughly 86 billion neurons are affected simultaneously.",
                ],
                "key_concepts": ["Metabolism", "Ischemia", "Consciousness", "Cellular Apoptosis", "Recovery Window"],
            }
            return schema_cls(**data)

        elif schema_name == "ScriptModel":
            data = {
                "project_id": "local-generated",
                "title": f"What Really Happens When {topic}?",
                "hook": f"What if everything you knew about {topic} changed in a single second?",
                "target_duration_sec": 300,
                "total_estimated_duration_sec": 180.0,
                "sections": [
                    {
                        "section_type": "hook",
                        "title": "The First Shock",
                        "narration_text": f"Imagine this: in a single instant, {topic}. What happens next is far weirder than you think.",
                        "estimated_duration_sec": 15.0,
                        "visual_intent": "Dramatic zoom on a silhouetted character as the environment freezes.",
                        "sound_intent": "Deep sub bass drop and clock ticking stopped abruptly.",
                    },
                    {
                        "section_type": "setup",
                        "title": "The Immediate Cascade",
                        "narration_text": "Within the first ten seconds, the primary power grid shuts down. Sensors stop reporting, and normal systems begin to freeze.",
                        "estimated_duration_sec": 30.0,
                        "visual_intent": "Cut to internal schematic showing glowing energy lines flickering out.",
                        "sound_intent": "Low electrical hum powering down.",
                    },
                    {
                        "section_type": "question",
                        "title": "The Hidden Mechanism",
                        "narration_text": "Why does this happen so fast? The answer comes down to one critical ingredient that runs out almost immediately.",
                        "estimated_duration_sec": 25.0,
                        "visual_intent": "Magnified microscopic view of molecules colliding and depleting.",
                        "sound_intent": "Subtle mysterious chime melody.",
                    },
                    {
                        "section_type": "explanation",
                        "title": "How The System Fails",
                        "narration_text": "Without continuous replenishment, cells cannot maintain their chemical balance. Ion channels fail, leading to an uncontrolled cascade.",
                        "estimated_duration_sec": 40.0,
                        "visual_intent": "Character stumbling in dark room as shadows stretch.",
                        "sound_intent": "Tense rhythmic percussion building slowly.",
                    },
                    {
                        "section_type": "escalation",
                        "title": "The Point of No Return",
                        "narration_text": "By minute three, the damage shifts from temporary pause to permanent structural collapse.",
                        "estimated_duration_sec": 35.0,
                        "visual_intent": "Red warning pulses illuminate the scene with frantic camera shake.",
                        "sound_intent": "Accelerating heartbeat effect with high-pass filter.",
                    },
                    {
                        "section_type": "surprising_fact",
                        "title": "The Bizarre Exception",
                        "narration_text": "Curiously, not all parts shut down together. Certain stubborn cells continue operating for hours, completely unaware the main system is gone.",
                        "estimated_duration_sec": 20.0,
                        "visual_intent": "Surprised character staring at a single glowing particle surviving in darkness.",
                        "sound_intent": "Glitch effect followed by strange eerie synth.",
                    },
                    {
                        "section_type": "conclusion",
                        "title": "The Final Verdict",
                        "narration_text": "It turns out the boundary between running and stopping is far more complex than simple on and off switches.",
                        "estimated_duration_sec": 15.0,
                        "visual_intent": "Slow zoom out to starry night sky with contemplative character silhouette.",
                        "sound_intent": "Warm atmospheric synth wash fading to silence.",
                    },
                ],
                "facts_used": ["Immediate energy depletion", "Differential cell survival timeframes"],
                "hypothetical_scenarios": ["Complete sudden shutdown"],
                "youtube_title_options": [
                    f"What If {topic}? (The Terrifying Reality)",
                    f"The Exact Timeline When {topic}",
                    f"Why {topic} Is Weirder Than You Think",
                ],
                "youtube_description": f"In this video, we explore the scientific timeline of what happens during '{topic}', explaining the exact mechanisms and surprising facts.",
                "youtube_tags": ["science", "documentary", "what if", "timeline", "educational", "animation"],
            }
            return schema_cls(**data)

        elif schema_name == "ScenePlan":
            scenes = [
                {
                    "scene_index": 1,
                    "section_ref": "hook",
                    "duration_sec": 15.0,
                    "narration_text": f"Imagine this: in a single instant, {topic}. What happens next is far weirder than you think.",
                    "background_id": "bedroom_dark",
                    "characters": ["character_main"],
                    "props": ["bed", "clock"],
                    "actions": [
                        {
                            "entity_id": "character_main",
                            "action": "sleep",
                            "expression": "neutral",
                            "start_time_sec": 0.0,
                            "duration_sec": 7.0,
                            "position_x_percent": 50.0,
                            "position_y_percent": 60.0,
                            "scale": 1.0,
                        },
                        {
                            "entity_id": "character_main",
                            "action": "shocked",
                            "expression": "shocked",
                            "start_time_sec": 7.0,
                            "duration_sec": 8.0,
                            "position_x_percent": 50.0,
                            "position_y_percent": 55.0,
                            "scale": 1.1,
                        },
                    ],
                    "camera": {
                        "type": "slow_zoom_in",
                        "zoom_start": 1.0,
                        "zoom_end": 1.25,
                        "focus_target": "character_main",
                    },
                    "effects": ["vignette", "film_grain"],
                    "sfx": ["clock_ticking", "sub_bass_drop"],
                    "mood": "suspense",
                    "subtitle_text": f"Imagine this: in a single instant, {topic}.",
                },
                {
                    "scene_index": 2,
                    "section_ref": "setup",
                    "duration_sec": 30.0,
                    "narration_text": "Within the first ten seconds, the primary power grid shuts down. Sensors stop reporting, and normal systems begin to freeze.",
                    "background_id": "brain_interior",
                    "characters": ["character_neuron"],
                    "props": ["synapse_nodes", "energy_beam"],
                    "actions": [
                        {
                            "entity_id": "character_neuron",
                            "action": "idle",
                            "expression": "confused",
                            "start_time_sec": 0.0,
                            "duration_sec": 30.0,
                            "position_x_percent": 45.0,
                            "position_y_percent": 50.0,
                            "scale": 1.2,
                        }
                    ],
                    "camera": {
                        "type": "pan_left",
                        "zoom_start": 1.1,
                        "zoom_end": 1.1,
                        "focus_target": "synapse_nodes",
                    },
                    "effects": ["electric_pulse_fading"],
                    "sfx": ["power_down_hum", "glitch"],
                    "mood": "dark",
                    "subtitle_text": "Within the first ten seconds, the primary power grid shuts down.",
                },
                {
                    "scene_index": 3,
                    "section_ref": "question",
                    "duration_sec": 25.0,
                    "narration_text": "Why does this happen so fast? The answer comes down to one critical ingredient that runs out almost immediately.",
                    "background_id": "laboratory_microscopic",
                    "characters": ["character_scientist"],
                    "props": ["microscope", "molecule_diagram"],
                    "actions": [
                        {
                            "entity_id": "character_scientist",
                            "action": "talk",
                            "expression": "confused",
                            "start_time_sec": 0.0,
                            "duration_sec": 25.0,
                            "position_x_percent": 60.0,
                            "position_y_percent": 50.0,
                            "scale": 1.0,
                        }
                    ],
                    "camera": {
                        "type": "slow_zoom_in",
                        "zoom_start": 1.0,
                        "zoom_end": 1.15,
                        "focus_target": "molecule_diagram",
                    },
                    "effects": ["floating_particles"],
                    "sfx": ["mysterious_chime"],
                    "mood": "mysterious",
                    "subtitle_text": "Why does this happen so fast?",
                },
                {
                    "scene_index": 4,
                    "section_ref": "explanation",
                    "duration_sec": 40.0,
                    "narration_text": "Without continuous replenishment, cells cannot maintain their chemical balance. Ion channels fail, leading to an uncontrolled cascade.",
                    "background_id": "cellular_landscape",
                    "characters": ["character_main"],
                    "props": ["ion_gate", "calcium_particles"],
                    "actions": [
                        {
                            "entity_id": "character_main",
                            "action": "scared",
                            "expression": "scared",
                            "start_time_sec": 0.0,
                            "duration_sec": 40.0,
                            "position_x_percent": 50.0,
                            "position_y_percent": 50.0,
                            "scale": 1.0,
                        }
                    ],
                    "camera": {
                        "type": "shake",
                        "zoom_start": 1.0,
                        "zoom_end": 1.2,
                        "focus_target": "character_main",
                    },
                    "effects": ["cellular_decay_tint"],
                    "sfx": ["tense_heartbeat", "chemical_bubble"],
                    "mood": "suspense",
                    "subtitle_text": "Without continuous replenishment, cells cannot maintain their balance.",
                },
                {
                    "scene_index": 5,
                    "section_ref": "escalation",
                    "duration_sec": 35.0,
                    "narration_text": "By minute three, the damage shifts from temporary pause to permanent structural collapse.",
                    "background_id": "emergency_room_dark",
                    "characters": ["character_main"],
                    "props": ["heart_monitor", "clock_ticking"],
                    "actions": [
                        {
                            "entity_id": "character_main",
                            "action": "dead",
                            "expression": "sad",
                            "start_time_sec": 0.0,
                            "duration_sec": 35.0,
                            "position_x_percent": 50.0,
                            "position_y_percent": 65.0,
                            "scale": 1.0,
                        }
                    ],
                    "camera": {
                        "type": "tilt_up",
                        "zoom_start": 1.2,
                        "zoom_end": 1.0,
                        "focus_target": "heart_monitor",
                    },
                    "effects": ["red_warning_flash", "heavy_vignette"],
                    "sfx": ["flatline_beep", "dramatic_hit"],
                    "mood": "horror",
                    "subtitle_text": "By minute three, the damage shifts to permanent structural collapse.",
                },
                {
                    "scene_index": 6,
                    "section_ref": "surprising_fact",
                    "duration_sec": 20.0,
                    "narration_text": "Curiously, not all parts shut down together. Certain stubborn cells continue operating for hours, completely unaware the main system is gone.",
                    "background_id": "abstract_space",
                    "characters": ["character_survivor_cell"],
                    "props": ["isolated_glow"],
                    "actions": [
                        {
                            "entity_id": "character_survivor_cell",
                            "action": "idle",
                            "expression": "happy",
                            "start_time_sec": 0.0,
                            "duration_sec": 20.0,
                            "position_x_percent": 50.0,
                            "position_y_percent": 50.0,
                            "scale": 1.3,
                        }
                    ],
                    "camera": {
                        "type": "slow_zoom_out",
                        "zoom_start": 1.4,
                        "zoom_end": 1.0,
                        "focus_target": "character_survivor_cell",
                    },
                    "effects": ["mystic_glow", "starfield"],
                    "sfx": ["eerie_synth_riser", "sparkle_glitch"],
                    "mood": "mysterious",
                    "subtitle_text": "Certain stubborn cells continue operating for hours.",
                },
                {
                    "scene_index": 7,
                    "section_ref": "conclusion",
                    "duration_sec": 15.0,
                    "narration_text": "It turns out the boundary between running and stopping is far more complex than simple on and off switches.",
                    "background_id": "night_landscape_stars",
                    "characters": ["character_main"],
                    "props": ["silhouette_cliff"],
                    "actions": [
                        {
                            "entity_id": "character_main",
                            "action": "stand",
                            "expression": "neutral",
                            "start_time_sec": 0.0,
                            "duration_sec": 15.0,
                            "position_x_percent": 50.0,
                            "position_y_percent": 55.0,
                            "scale": 0.9,
                        }
                    ],
                    "camera": {
                        "type": "slow_zoom_out",
                        "zoom_start": 1.1,
                        "zoom_end": 0.9,
                        "focus_target": "night_landscape_stars",
                    },
                    "effects": ["ambient_glow", "cinematic_letterbox"],
                    "sfx": ["warm_ambient_wash", "whoosh_fadeout"],
                    "mood": "emotional",
                    "subtitle_text": "The boundary between running and stopping is far more complex than we think.",
                },
            ]

            total_duration = sum(s["duration_sec"] for s in scenes)
            data = {
                "project_id": "local-generated",
                "total_scenes": len(scenes),
                "total_duration_sec": total_duration,
                "scenes": scenes,
            }
            return schema_cls(**data)

        # Generic default mock if another schema passed
        return schema_cls()
