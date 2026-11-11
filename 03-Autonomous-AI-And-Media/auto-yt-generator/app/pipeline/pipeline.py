"""
AUTO YT GENERATOR — Pipeline Orchestrator.

Executes sequential stages (Research -> Script -> Scenes -> Assets -> Audio -> Animation -> Compositing -> QC -> Render)
with robust error tracking, retry policies, and database state updates.
"""

import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.constants import PipelineStage, StageStatus
from app.models.project import ProjectModel
from app.models.job import JobModel, StageLog
from app.pipeline.stages import BaseStage, StageContext, StageResult
from app.database import db
from app.logger import logger


class PipelineOrchestrator:
    """Manages the lifecycle and execution flow of video generation pipelines."""

    def __init__(self, stages: Optional[List[BaseStage]] = None):
        self.stages: List[BaseStage] = stages or []

    def register_stage(self, stage: BaseStage) -> None:
        """Appends a new executable stage to the pipeline sequence."""
        self.stages.append(stage)

    def run_pipeline(
        self,
        project: ProjectModel,
        start_from_stage: Optional[PipelineStage] = None,
        dry_run: bool = False,
    ) -> JobModel:
        """Executes all registered stages sequentially for the given project."""
        job_id = f"job_{project.id}_{int(time.time())}"
        job = JobModel(
            job_id=job_id,
            project_id=project.id,
            current_stage=PipelineStage.QUEUED,
            status=StageStatus.RUNNING,
            overall_progress=0.0,
        )

        context = StageContext(project=project, dry_run=dry_run)
        total_stages = len(self.stages)
        logger.info(f"Starting pipeline job {job_id} for project {project.id} with {total_stages} stages.")

        skip = start_from_stage is not None
        for index, stage in enumerate(self.stages):
            if skip:
                if stage.stage_enum == start_from_stage:
                    skip = False
                else:
                    logger.debug(f"Skipping stage {stage.stage_enum.value} as per start_from_stage policy.")
                    continue

            stage_name = stage.stage_enum.value
            logger.info(f"Executing stage [{index + 1}/{total_stages}]: {stage_name}")

            # Record stage start
            stage_log = StageLog(
                stage_name=stage_name,
                status=StageStatus.RUNNING,
                start_time=datetime.utcnow(),
            )
            job.current_stage = stage.stage_enum
            job.stage_logs.append(stage_log)

            # Update DB project stage
            progress_percent = (index / total_stages) * 100.0
            db.update_project_stage(project.id, stage.stage_enum, progress_percent)

            start_t = time.time()
            try:
                result: StageResult = stage.execute(context)
                elapsed = time.time() - start_t

                stage_log.end_time = datetime.utcnow()
                stage_log.duration_seconds = elapsed

                if result.success:
                    stage_log.status = StageStatus.COMPLETED
                    context.shared_data.update(result.data)
                    logger.info(f"Stage {stage_name} completed successfully in {elapsed:.2f}s.")
                else:
                    stage_log.status = StageStatus.FAILED
                    stage_log.error_message = result.error_message
                    job.status = StageStatus.FAILED
                    db.update_project_stage(
                        project.id,
                        PipelineStage.FAILED,
                        progress_percent,
                        error_message=result.error_message,
                    )
                    logger.error(f"Stage {stage_name} failed: {result.error_message}")
                    return job

            except Exception as e:
                elapsed = time.time() - start_t
                stage_log.end_time = datetime.utcnow()
                stage_log.duration_seconds = elapsed
                stage_log.status = StageStatus.FAILED
                stage_log.error_message = str(e)
                job.status = StageStatus.FAILED
                db.update_project_stage(
                    project.id,
                    PipelineStage.FAILED,
                    progress_percent,
                    error_message=str(e),
                )
                logger.exception(f"Unhandled exception in stage {stage_name}: {e}")
                return job

        # All stages completed
        job.current_stage = PipelineStage.COMPLETED
        job.status = StageStatus.COMPLETED
        job.overall_progress = 100.0
        db.update_project_stage(project.id, PipelineStage.COMPLETED, 100.0)
        logger.info(f"Pipeline job {job_id} successfully completed for project {project.id}!")
        return job
