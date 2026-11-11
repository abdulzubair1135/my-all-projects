"""
AUTO YT GENERATOR — Pipeline Stage Abstract Interfaces and Complete Stage Implementations.
"""

import json
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from app.constants import PipelineStage, StageStatus
from app.models.project import ProjectModel
from app.database import db
from app.logger import logger


class StageContext(BaseModel):
    """Execution context passed through every pipeline stage."""

    project: ProjectModel
    shared_data: Dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = False


class StageResult(BaseModel):
    """Result payload returned by a stage execution."""

    success: bool
    stage: PipelineStage
    status: StageStatus = StageStatus.COMPLETED
    data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None


class BaseStage(ABC):
    """Abstract Base Class for every pipeline stage."""

    def __init__(self, stage_enum: PipelineStage):
        self.stage_enum = stage_enum

    @abstractmethod
    def execute(self, context: StageContext) -> StageResult:
        """Executes stage logic and returns StageResult."""
        pass


# ── Pipeline Stage Implementations ─────────────────────────────────────────────

class ResearchStage(BaseStage):
    """Executes topic research and fact extraction."""

    def __init__(self):
        super().__init__(PipelineStage.RESEARCHING)

    def execute(self, context: StageContext) -> StageResult:
        from app.ai.research import ResearchEngine

        try:
            engine = ResearchEngine()
            research_result = engine.research_topic(
                topic=context.project.config.topic,
                tone=context.project.config.tone,
            )

            if context.project.project_dir:
                res_path = Path(context.project.project_dir) / "metadata" / "research.json"
                res_path.parent.mkdir(parents=True, exist_ok=True)
                with open(res_path, "w", encoding="utf-8") as f:
                    f.write(research_result.model_dump_json(indent=2))

            return StageResult(
                success=True,
                stage=self.stage_enum,
                data={"research": research_result},
            )
        except Exception as e:
            logger.exception(f"ResearchStage failed: {e}")
            return StageResult(
                success=False,
                stage=self.stage_enum,
                status=StageStatus.FAILED,
                error_message=str(e),
            )


class ScriptStage(BaseStage):
    """Executes 7-phase retention script generation."""

    def __init__(self):
        super().__init__(PipelineStage.SCRIPTING)

    def execute(self, context: StageContext) -> StageResult:
        from app.ai.script import ScriptEngine
        from app.ai.research import ResearchResult

        try:
            research: Optional[ResearchResult] = context.shared_data.get("research")
            if not research:
                from app.ai.research import ResearchEngine
                res_engine = ResearchEngine()
                research = res_engine.research_topic(
                    topic=context.project.config.topic,
                    tone=context.project.config.tone,
                )
                context.shared_data["research"] = research

            script_engine = ScriptEngine()
            script_result = script_engine.generate_script(context.project, research)

            if context.project.project_dir:
                script_path = Path(context.project.project_dir) / "metadata" / "script.json"
                script_path.parent.mkdir(parents=True, exist_ok=True)
                with open(script_path, "w", encoding="utf-8") as f:
                    f.write(script_result.model_dump_json(indent=2))

            return StageResult(
                success=True,
                stage=self.stage_enum,
                data={"script": script_result},
            )
        except Exception as e:
            logger.exception(f"ScriptStage failed: {e}")
            return StageResult(
                success=False,
                stage=self.stage_enum,
                status=StageStatus.FAILED,
                error_message=str(e),
            )


class ScenePlanningStage(BaseStage):
    """Converts script sections into granular 2D animation scenes with camera, props, and actions."""

    def __init__(self):
        super().__init__(PipelineStage.PLANNING)

    def execute(self, context: StageContext) -> StageResult:
        from app.ai.scene_planner import ScenePlannerEngine
        from app.models.script import ScriptModel

        try:
            script: Optional[ScriptModel] = context.shared_data.get("script")
            if not script:
                script_path = Path(context.project.project_dir or "") / "metadata" / "script.json"
                if script_path.exists():
                    with open(script_path, "r", encoding="utf-8") as f:
                        script = ScriptModel(**json.load(f))
                else:
                    script_stage = ScriptStage()
                    s_res = script_stage.execute(context)
                    if not s_res.success:
                        return s_res
                    script = s_res.data["script"]
                context.shared_data["script"] = script

            planner = ScenePlannerEngine()
            scene_plan = planner.plan_scenes(context.project, script)

            db.save_scenes(context.project.id, scene_plan.scenes)

            if context.project.project_dir:
                scenes_path = Path(context.project.project_dir) / "metadata" / "scenes.json"
                scenes_path.parent.mkdir(parents=True, exist_ok=True)
                with open(scenes_path, "w", encoding="utf-8") as f:
                    f.write(scene_plan.model_dump_json(indent=2))

            return StageResult(
                success=True,
                stage=self.stage_enum,
                data={"scene_plan": scene_plan, "scenes": scene_plan.scenes},
            )
        except Exception as e:
            logger.exception(f"ScenePlanningStage failed: {e}")
            return StageResult(
                success=False,
                stage=self.stage_enum,
                status=StageStatus.FAILED,
                error_message=str(e),
            )


class AssetGenerationStage(BaseStage):
    """Procedurally generates all required character sprites, 1080p backgrounds, and props."""

    def __init__(self):
        super().__init__(PipelineStage.GENERATING_ASSETS)

    def execute(self, context: StageContext) -> StageResult:
        from app.assets.manager import asset_manager
        from app.models.scene import ScenePlan

        try:
            scene_plan: Optional[ScenePlan] = context.shared_data.get("scene_plan")
            if not scene_plan:
                scenes = db.get_scenes(context.project.id)
                if not scenes:
                    planning_stage = ScenePlanningStage()
                    p_res = planning_stage.execute(context)
                    if not p_res.success:
                        return p_res
                    scene_plan = p_res.data["scene_plan"]
                else:
                    scene_plan = ScenePlan(
                        project_id=context.project.id,
                        total_scenes=len(scenes),
                        total_duration_sec=sum(s.duration_sec for s in scenes),
                        scenes=scenes,
                    )
                context.shared_data["scene_plan"] = scene_plan

            logger.info(f"Generating visual assets for {len(scene_plan.scenes)} scenes...")
            assets_dict = asset_manager.generate_all_scene_assets(
                scene_plan=scene_plan,
                project_dir=context.project.project_dir,
            )

            return StageResult(
                success=True,
                stage=self.stage_enum,
                data={"assets": assets_dict},
            )
        except Exception as e:
            logger.exception(f"AssetGenerationStage failed: {e}")
            return StageResult(
                success=False,
                stage=self.stage_enum,
                status=StageStatus.FAILED,
                error_message=str(e),
            )


class VoiceGenerationStage(BaseStage):
    """Synthesizes voiceover audio for each scene and synchronizes scene durations."""

    def __init__(self):
        super().__init__(PipelineStage.GENERATING_AUDIO)

    def execute(self, context: StageContext) -> StageResult:
        from app.audio.voice import voice_engine

        try:
            scenes = db.get_scenes(context.project.id)
            if not scenes:
                plan_stage = ScenePlanningStage()
                res = plan_stage.execute(context)
                if not res.success:
                    return res
                scenes = res.data["scenes"]

            audio_dir = Path(context.project.project_dir or "") / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Generating voiceover audio for {len(scenes)} scenes...")
            audio_files: List[str] = []

            for s in scenes:
                if s.narration_text:
                    out_path = str(audio_dir / f"narration_scene_{s.scene_index:02d}.mp3")
                    audio_path, duration = voice_engine.generate_narration(
                        text=s.narration_text,
                        output_path=out_path,
                        language=context.project.config.language,
                    )
                    s.audio_file = audio_path
                    s.duration_sec = max(s.duration_sec, duration + 0.5)
                    audio_files.append(audio_path)

            db.save_scenes(context.project.id, scenes)

            return StageResult(
                success=True,
                stage=self.stage_enum,
                data={"audio_files": audio_files, "scenes": scenes},
            )
        except Exception as e:
            logger.exception(f"VoiceGenerationStage failed: {e}")
            return StageResult(
                success=False,
                stage=self.stage_enum,
                status=StageStatus.FAILED,
                error_message=str(e),
            )


class AudioMixStage(BaseStage):
    """Generates procedural background music, SFX, and mixes with voiceover ducking."""

    def __init__(self):
        super().__init__(PipelineStage.MIXING)

    def execute(self, context: StageContext) -> StageResult:
        from app.audio.music import music_generator
        from app.audio.sfx import sfx_generator
        from app.audio.mixer import audio_mixer

        try:
            scenes = db.get_scenes(context.project.id)
            if not scenes:
                plan_stage = ScenePlanningStage()
                res = plan_stage.execute(context)
                if not res.success:
                    return res
                scenes = res.data["scenes"]

            total_duration = sum(s.duration_sec for s in scenes)
            audio_dir = Path(context.project.project_dir or "") / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)

            music_path = str(audio_dir / "bg_music.wav")
            music_generator.generate_music(
                duration_sec=total_duration,
                output_path=music_path,
                style=context.project.config.music_style,
            )

            master_audio_path = str(audio_dir / "master_audio.wav")
            audio_mixer.mix_project_audio(
                scenes=scenes,
                music_path=music_path,
                output_path=master_audio_path,
                ducking_ratio=0.25,
            )

            return StageResult(
                success=True,
                stage=self.stage_enum,
                data={"master_audio": master_audio_path, "music": music_path},
            )
        except Exception as e:
            logger.exception(f"AudioMixStage failed: {e}")
            return StageResult(
                success=False,
                stage=self.stage_enum,
                status=StageStatus.FAILED,
                error_message=str(e),
            )


class AnimationStage(BaseStage):
    """Renders 2D animated keyframes and composite sequences for all scenes."""

    def __init__(self):
        super().__init__(PipelineStage.ANIMATING)

    def execute(self, context: StageContext) -> StageResult:
        from app.animation.animator import scene_animator

        try:
            scenes = db.get_scenes(context.project.id)
            if not scenes:
                plan_stage = ScenePlanningStage()
                res = plan_stage.execute(context)
                if not res.success:
                    return res
                scenes = res.data["scenes"]

            rendered_preview_frames: List[str] = []
            renders_dir = Path(context.project.project_dir or "") / "renders"
            renders_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Animating {len(scenes)} scenes for project {context.project.id}...")
            for s in scenes:
                mid_t = s.duration_sec / 2.0
                frame_img = scene_animator.render_scene_frame(
                    scene=s,
                    time_sec=mid_t,
                    project_dir=context.project.project_dir,
                )
                preview_path = renders_dir / f"preview_scene_{s.scene_index:02d}.png"
                frame_img.save(preview_path, "PNG")
                rendered_preview_frames.append(str(preview_path))

            return StageResult(
                success=True,
                stage=self.stage_enum,
                data={"preview_frames": rendered_preview_frames, "scenes_animated": len(scenes)},
            )
        except Exception as e:
            logger.exception(f"AnimationStage failed: {e}")
            return StageResult(
                success=False,
                stage=self.stage_enum,
                status=StageStatus.FAILED,
                error_message=str(e),
            )


class VideoRenderStage(BaseStage):
    """Encodes the final 1080p MP4 video with synchronized audio and burned subtitles."""

    def __init__(self):
        super().__init__(PipelineStage.RENDERING)

    def execute(self, context: StageContext) -> StageResult:
        from app.video.renderer import video_renderer

        try:
            scenes = db.get_scenes(context.project.id)
            if not scenes:
                plan_stage = ScenePlanningStage()
                res = plan_stage.execute(context)
                if not res.success:
                    return res
                scenes = res.data["scenes"]

            audio_path = str(Path(context.project.project_dir or "") / "audio" / "master_audio.wav")
            if not Path(audio_path).exists():
                mix_stage = AudioMixStage()
                m_res = mix_stage.execute(context)
                if m_res.success:
                    audio_path = m_res.data["master_audio"]

            logger.info(f"Rendering final 1080p MP4 video for project {context.project.id}...")
            final_mp4 = video_renderer.render_project_video(
                project=context.project,
                scenes=scenes,
                master_audio_path=audio_path,
                fps=context.project.config.fps,
                burn_subtitles=True,
            )

            context.project.output_video_path = final_mp4

            return StageResult(
                success=True,
                stage=self.stage_enum,
                data={"video_path": final_mp4, "duration": sum(s.duration_sec for s in scenes)},
            )
        except Exception as e:
            logger.exception(f"VideoRenderStage failed: {e}")
            return StageResult(
                success=False,
                stage=self.stage_enum,
                status=StageStatus.FAILED,
                error_message=str(e),
            )


class OutputStage(BaseStage):
    """Generates YouTube thumbnail, titles, description, tags, chapters, and validation report."""

    def __init__(self):
        super().__init__(PipelineStage.VALIDATING)

    def execute(self, context: StageContext) -> StageResult:
        from app.output.thumbnail import thumbnail_generator
        from app.output.metadata import metadata_generator
        from app.quality.validator import quality_validator
        from app.models.script import ScriptModel

        try:
            scenes = db.get_scenes(context.project.id)

            # Load script
            script_path = Path(context.project.project_dir or "") / "metadata" / "script.json"
            if script_path.exists():
                with open(script_path, "r", encoding="utf-8") as f:
                    script = ScriptModel(**json.load(f))
            else:
                script = ScriptModel(
                    project_id=context.project.id,
                    title=context.project.config.topic,
                    hook=context.project.config.topic,
                    target_duration_sec=context.project.config.duration_seconds,
                    total_estimated_duration_sec=sum(s.duration_sec for s in scenes),
                    sections=[],
                )

            # 1. Generate Thumbnail
            thumb_path = thumbnail_generator.generate_thumbnail(
                project=context.project,
                script=script,
            )
            context.project.thumbnail_path = thumb_path

            # 2. Generate YouTube Publishing Metadata & Chapters
            report_data = metadata_generator.generate_all_metadata(
                project=context.project,
                script=script,
                scenes=scenes,
            )

            # 3. Perform Quality Audit & Retention Scorecard
            quality_report = quality_validator.validate_project(context.project, scenes=scenes)

            from app.quality.retention import retention_audit_engine
            from app.models.scene import ScenePlan
            scene_plan = ScenePlan(
                project_id=context.project.id,
                total_scenes=len(scenes),
                total_duration_sec=sum(s.duration_sec for s in scenes),
                scenes=scenes,
            )
            retention_report = retention_audit_engine.audit_scene_plan(scene_plan)

            if context.project.project_dir:
                ret_path = Path(context.project.project_dir) / "metadata" / "retention_report.json"
                with open(ret_path, "w", encoding="utf-8") as f:
                    json.dump(retention_report, f, indent=2)

            return StageResult(
                success=True,
                stage=self.stage_enum,
                data={
                    "thumbnail": thumb_path,
                    "metadata": report_data,
                    "quality_report": quality_report,
                    "retention_report": retention_report,
                },
            )
        except Exception as e:
            logger.exception(f"OutputStage failed: {e}")
            return StageResult(
                success=False,
                stage=self.stage_enum,
                status=StageStatus.FAILED,
                error_message=str(e),
            )
