"""
AUTO YT GENERATOR — Batch Video Production Engine.

Generates multiple full YouTube videos from a topic list text file automatically.
"""

import uuid
from pathlib import Path
from typing import List, Dict, Any

from app.config import settings
from app.database import db
from app.models.project import ProjectModel, ProjectConfig
from app.pipeline.pipeline import PipelineOrchestrator
from app.pipeline.stages import (
    ResearchStage,
    ScriptStage,
    ScenePlanningStage,
    AssetGenerationStage,
    VoiceGenerationStage,
    AudioMixStage,
    VideoRenderStage,
    OutputStage,
)
from app.logger import logger


class BatchGenerator:
    """Manages batch automated video generation for multiple topics."""

    def run_batch_from_file(
        self,
        topics_file: str,
        style: str = "dark_cartoon",
        language: str = "en",
        duration_sec: int = 180,
        fps: int = 15,
    ) -> List[Dict[str, Any]]:
        """Reads topic file and produces videos sequentially."""
        file_path = Path(topics_file)
        if not file_path.exists():
            raise FileNotFoundError(f"Topics file not found: {topics_file}")

        with open(file_path, "r", encoding="utf-8") as f:
            topics = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        logger.info(f"Starting batch production for {len(topics)} topics...")
        results = []

        orchestrator = PipelineOrchestrator([
            ResearchStage(),
            ScriptStage(),
            ScenePlanningStage(),
            AssetGenerationStage(),
            VoiceGenerationStage(),
            AudioMixStage(),
            VideoRenderStage(),
            OutputStage(),
        ])

        for i, topic in enumerate(topics, 1):
            logger.info(f"--- Processing Batch [{i}/{len(topics)}]: '{topic}' ---")
            project_id = str(uuid.uuid4())
            project_dir = Path(settings.paths.projects_dir) / project_id
            project_dir.mkdir(parents=True, exist_ok=True)
            for sub in ["assets", "audio", "renders", "final", "thumbnail", "metadata"]:
                (project_dir / sub).mkdir(exist_ok=True)

            config = ProjectConfig(
                topic=topic,
                language=language,
                duration_seconds=duration_sec,
                style=style,
                resolution="1920x1080",
                fps=fps,
            )
            project = ProjectModel(
                id=project_id,
                title=topic[:60],
                config=config,
                project_dir=str(project_dir),
            )
            db.create_project(project)

            try:
                job = orchestrator.run_pipeline(project)
                results.append({
                    "topic": topic,
                    "project_id": project_id,
                    "status": job.status.value,
                    "video_path": str(project_dir / "final" / "video.mp4"),
                    "thumbnail_path": str(project_dir / "final" / "thumbnail.png"),
                })
            except Exception as e:
                logger.error(f"Batch item failed for '{topic}': {e}")
                results.append({
                    "topic": topic,
                    "project_id": project_id,
                    "status": "FAILED",
                    "error": str(e),
                })

        return results


# Default batch generator instance
batch_generator = BatchGenerator()
