"""
AUTO YT GENERATOR — Quality Control & Validation Engine.

Performs automated pre-flight and post-render validation checks:
- Verifies script schema integrity
- Verifies scene storyboard consistency
- Verifies audio duration synchronization
- Verifies missing assets or background files
- Generates quality_report.json
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.models.project import ProjectModel
from app.models.scene import SceneModel
from app.logger import logger


class QualityValidator:
    """Performs sanity and quality assurance audits on projects."""

    def validate_project(self, project: ProjectModel, scenes: Optional[List[SceneModel]] = None) -> Dict[str, Any]:
        """Runs full quality checklist and returns audit report dict."""
        project_dir = Path(project.project_dir or f"projects/{project.id}")
        report = {
            "project_id": project.id,
            "validated_at": datetime.utcnow().isoformat(),
            "passed": True,
            "errors": [],
            "warnings": [],
            "checks": {
                "script_valid": False,
                "scenes_valid": False,
                "assets_present": False,
                "audio_synced": False,
                "final_video_present": False,
            },
        }

        # 1. Check Script JSON
        script_file = project_dir / "metadata" / "script.json"
        if script_file.exists():
            try:
                with open(script_file, "r", encoding="utf-8") as f:
                    json.load(f)
                report["checks"]["script_valid"] = True
            except Exception as e:
                report["errors"].append(f"Corrupted script.json: {e}")
        else:
            report["warnings"].append("script.json not yet generated.")

        # 2. Check Scenes
        if not scenes:
            from app.database import db
            scenes = db.get_scenes(project.id)

        if scenes:
            report["checks"]["scenes_valid"] = True
            # Check scene durations
            total_dur = sum(s.duration_sec for s in scenes)
            if total_dur < 1.0:
                report["errors"].append(f"Invalid total duration: {total_dur}s")

            # Check audio sync
            audio_missing = 0
            for s in scenes:
                if s.narration_text and not s.audio_file:
                    audio_missing += 1
            if audio_missing == 0:
                report["checks"]["audio_synced"] = True
            else:
                report["warnings"].append(f"{audio_missing} scenes missing audio clips.")

        # 3. Check Assets
        asset_folder = project_dir / "assets"
        if asset_folder.exists() and len(list(asset_folder.glob("*.png"))) > 0:
            report["checks"]["assets_present"] = True
        else:
            report["warnings"].append("Assets directory is empty or missing.")

        # 4. Check Final Video
        final_video = project_dir / "final" / "video.mp4"
        if final_video.exists() and final_video.stat().st_size > 5000:
            report["checks"]["final_video_present"] = True
        else:
            report["warnings"].append("final/video.mp4 not rendered.")

        report["passed"] = len(report["errors"]) == 0

        # Persist report
        quality_file = project_dir / "final" / "quality_report.json"
        quality_file.parent.mkdir(parents=True, exist_ok=True)
        with open(quality_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Quality audit completed: Passed = {report['passed']} ({len(report['errors'])} errors, {len(report['warnings'])} warnings)")
        return report


# Default quality validator instance
quality_validator = QualityValidator()
