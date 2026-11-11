"""
Comprehensive Unit Tests for AI Video Production Engine Upgrade.

Tests all 16 layers:
- SemanticDirector, ActingDirector, CameraDirector
- 2D CharacterRig puppet & 14-Viseme Lip Sync
- InfographicsEngine, BRollEngine, TransitionEngine
- DynamicCaptionsEngine, RetentionAuditEngine, QualityMemory
"""

import unittest
from PIL import Image

from app.director.semantic import semantic_director
from app.director.acting import acting_director
from app.director.camera import camera_director
from app.assets.rig import character_rig
from app.audio.viseme import viseme_engine
from app.motion.infographics import infographics_engine
from app.motion.broll import broll_engine
from app.motion.transitions import transition_engine
from app.video.dynamic_captions import dynamic_captions_engine
from app.quality.retention import retention_audit_engine
from app.quality.memory import quality_memory
from app.models.scene import ScenePlan, SceneModel, SceneAction, CameraConfig, InfographicConfig


class TestDirectorAndProductionUpgrade(unittest.TestCase):
    def test_semantic_director(self):
        cue = semantic_director.analyze_narration_beat("The human brain consumes 20 percent of total energy!", section_name="hook")
        self.assertIn(cue.emotion, ["curiosity", "shock", "awe", "neutral"])
        self.assertEqual(cue.intent, "hook")
        self.assertGreater(cue.importance, 0.7)

        # Infographic detection
        is_info, cfg = semantic_director.detect_infographic_opportunity("The human brain uses 20 percent of your daily calories.")
        self.assertTrue(is_info)
        self.assertIsNotNone(cfg)
        self.assertEqual(cfg.stat_number, 20.0)

    def test_acting_director(self):
        cue = semantic_director.analyze_narration_beat("Suddenly the power shut down completely!", section_name="escalation")
        action = acting_director.direct_acting_performance(semantic=cue, character_id="char_1", duration_sec=4.0)
        self.assertIn(action.expression, ["scared", "shocked", "neutral"])
        self.assertGreater(action.duration_sec, 0.5)

    def test_camera_director(self):
        cue = semantic_director.analyze_narration_beat("Why does this mysterious phenomenon happen?", section_name="question")
        cam = camera_director.direct_camera_for_scene(cue)
        self.assertIsNotNone(cam.type)
        self.assertGreaterEqual(cam.zoom_start, 1.0)
        self.assertIsNotNone(cam.parallax)

    def test_character_puppet_rig(self):
        frame = character_rig.render_puppet_frame(
            time_sec=1.5,
            gesture="point_right",
            expression="shocked",
            gaze="right",
            viseme="A",
            has_glasses=True,
        )
        self.assertEqual(frame.size, (512, 768))

    def test_viseme_lip_sync(self):
        viseme = viseme_engine.get_viseme_at_time(audio_path=None, time_sec=0.5, is_talking=True)
        self.assertIn(viseme, viseme_engine.VISEME_SEQUENCE)

    def test_infographics_engine(self):
        cfg = InfographicConfig(
            type="stats_counter",
            title="BRAIN POWER",
            stat_number=20.0,
            stat_suffix="%",
            description="Consumes massive metabolic energy",
        )
        frame = infographics_engine.render_infographic_frame(config=cfg, time_sec=1.0, duration_sec=3.0)
        self.assertEqual(frame.size, (1920, 1080))

    def test_broll_engine(self):
        frame = broll_engine.render_broll_frame(broll_type="neural_synapses", time_sec=2.0)
        self.assertEqual(frame.size, (1920, 1080))

    def test_transition_engine(self):
        fa = Image.new("RGBA", (1920, 1080), (20, 20, 20, 255))
        fb = Image.new("RGBA", (1920, 1080), (100, 100, 200, 255))
        blended = transition_engine.apply_transition(fa, fb, progress=0.5, transition_type="zoom")
        self.assertEqual(blended.size, (1920, 1080))

    def test_dynamic_captions(self):
        frame = Image.new("RGBA", (1920, 1080), (10, 10, 15, 255))
        cap = dynamic_captions_engine.render_karaoke_caption(
            frame=frame,
            text="WHAT HAPPENS IF THE BRAIN STOPS",
            time_sec=1.2,
            duration_sec=3.0,
        )
        self.assertEqual(cap.size, (1920, 1080))

    def test_retention_audit_and_memory(self):
        plan = ScenePlan(
            project_id="test_audit",
            total_scenes=2,
            total_duration_sec=6.0,
            scenes=[
                SceneModel(
                    scene_index=1,
                    duration_sec=3.0,
                    narration_text="Hook scene line",
                    background_id="bedroom_dark",
                    actions=[SceneAction(entity_id="c1", duration_sec=3.0)],
                    camera=CameraConfig(),
                ),
                SceneModel(
                    scene_index=2,
                    duration_sec=3.0,
                    narration_text="Second explanation line",
                    background_id="brain_interior",
                    is_cutaway=True,
                    infographic=InfographicConfig(title="INFO"),
                    actions=[SceneAction(entity_id="c1", duration_sec=3.0)],
                    camera=CameraConfig(),
                ),
            ],
        )
        report = retention_audit_engine.audit_scene_plan(plan)
        self.assertIn("overall_score", report)
        self.assertGreater(report["overall_score"], 50)
        self.assertIn("category_scores", report)

        # Quality memory check
        self.assertIn("min_quality_score_target", quality_memory.rules)


if __name__ == "__main__":
    unittest.main()
