"""
Project Manager for StickForge AI.
Handles project bundles (.sfproj), serialization, atomic disk saving, and recovery.
"""

from __future__ import annotations
import json
import os
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.config import PROJECTS_DIR
from app.core.logging_manager import get_logger
from app.storage.repositories import ProjectRepository

logger = get_logger("project_manager")


class CharacterModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = "Hero"
    style: str = "classic_stickman"
    color: str = "#FFFFFF"
    line_thickness: int = 4
    voice_id: str = "en-US-ChristopherNeural"
    proportions: Dict[str, float] = Field(
        default_factory=lambda: {
            "head_radius": 24.0,
            "torso_length": 65.0,
            "upper_arm_length": 35.0,
            "lower_arm_length": 32.0,
            "upper_leg_length": 42.0,
            "lower_leg_length": 40.0,
        }
    )


class SceneAction(BaseModel):
    character_id: str
    action: str = "stand"  # stand, walk, run, jump, sit, wave, etc.
    parameters: Dict[str, Any] = Field(default_factory=dict)


class CameraModel(BaseModel):
    shot: str = "medium"  # wide, medium, close_up
    movement: str = "static"  # static, pan_left, pan_right, zoom_in, zoom_out
    speed: float = 1.0


class SceneModel(BaseModel):
    id: str = Field(default_factory=lambda: f"scene_{uuid.uuid4().hex[:6]}")
    sequence_order: int = 1
    duration: float = 5.0
    background: str = "white"
    narration: str = ""
    dialogue: str = ""
    camera: CameraModel = Field(default_factory=CameraModel)
    actions: List[SceneAction] = Field(default_factory=list)
    sound_effects: List[Dict[str, Any]] = Field(default_factory=list)
    transition: str = "none"


class ProjectData(BaseModel):
    id: str = Field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:8]}")
    name: str = "Untitled Animation"
    topic: str = ""
    genre: str = "comedy"
    language: str = "hinglish"
    duration_target: float = 30.0
    aspect_ratio: str = "9:16"  # 9:16 (Shorts/Reels) or 16:9
    characters: List[CharacterModel] = Field(default_factory=list)
    scenes: List[SceneModel] = Field(default_factory=list)
    script_text: str = ""
    version: int = 1


class ProjectManager:
    """Manages project persistence, atomic saves, and directory structures."""

    def __init__(self, projects_dir: Path = PROJECTS_DIR):
        self.projects_dir = projects_dir
        self.repo = ProjectRepository()

    def create_project(
        self,
        name: str,
        topic: str = "",
        genre: str = "comedy",
        language: str = "hinglish",
        duration_target: float = 30.0,
        aspect_ratio: str = "9:16",
    ) -> ProjectData:
        """Create a new project bundle directory and initial project file."""
        proj_id = f"proj_{uuid.uuid4().hex[:8]}"
        project = ProjectData(
            id=proj_id,
            name=name,
            topic=topic,
            genre=genre,
            language=language,
            duration_target=duration_target,
            aspect_ratio=aspect_ratio,
            characters=[CharacterModel(id="char_1", name="Rahul")],
            scenes=[
                SceneModel(
                    id="scene_001",
                    sequence_order=1,
                    duration=5.0,
                    background="classroom",
                    narration="Rahul ke paas paise nahi the, lekin uske sapne bahut bade the.",
                    actions=[SceneAction(character_id="char_1", action="sit")],
                )
            ],
        )

        # Save to disk and register in DB
        self.save_project(project)
        self.repo.create(
            {
                "id": project.id,
                "name": project.name,
                "topic": project.topic,
                "genre": project.genre,
                "language": project.language,
                "duration_target": project.duration_target,
                "aspect_ratio": project.aspect_ratio,
                "status": "draft",
                "file_path": str(self.get_project_file_path(project.id)),
            }
        )
        logger.info(f"Project '{name}' ({proj_id}) created successfully.")
        return project

    def get_project_dir(self, project_id: str) -> Path:
        d = self.projects_dir / project_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def get_project_file_path(self, project_id: str) -> Path:
        return self.get_project_dir(project_id) / "project.sfproj"

    def save_project(self, project: ProjectData) -> Path:
        """Save project atomically using temporary file swap."""
        filepath = self.get_project_file_path(project.id)
        temp_file = filepath.with_suffix(".tmp")

        data = project.model_dump()
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Atomic replacement
        if temp_file.exists():
            temp_file.replace(filepath)

        # Update database record
        self.repo.update(
            project.id,
            {
                "name": project.name,
                "topic": project.topic,
                "genre": project.genre,
                "language": project.language,
                "duration_target": project.duration_target,
                "aspect_ratio": project.aspect_ratio,
            },
        )
        logger.debug(f"Project {project.id} saved atomically.")
        return filepath

    def load_project(self, project_id: str) -> Optional[ProjectData]:
        """Load and validate project by ID with corruption fallback."""
        filepath = self.get_project_file_path(project_id)
        if not filepath.exists():
            # Check if temp file exists due to crash
            temp_file = filepath.with_suffix(".tmp")
            if temp_file.exists():
                logger.warning(f"Recovering project {project_id} from incomplete temp save.")
                temp_file.replace(filepath)
            else:
                logger.error(f"Project file not found: {filepath}")
                return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ProjectData.model_validate(data)
        except Exception as e:
            logger.error(f"Failed to parse project file {filepath}: {e}", exc_info=True)
            return None

    def duplicate_project(self, project_id: str, new_name: str) -> Optional[ProjectData]:
        """Duplicate an existing project under a new ID and title."""
        original = self.load_project(project_id)
        if not original:
            return None
        clone = original.model_copy(deep=True)
        clone.id = f"proj_{uuid.uuid4().hex[:8]}"
        clone.name = new_name
        self.save_project(clone)
        self.repo.create(
            {
                "id": clone.id,
                "name": clone.name,
                "topic": clone.topic,
                "genre": clone.genre,
                "language": clone.language,
                "duration_target": clone.duration_target,
                "aspect_ratio": clone.aspect_ratio,
                "status": "draft",
                "file_path": str(self.get_project_file_path(clone.id)),
            }
        )
        return clone


# Global project manager singleton
_project_manager: Optional[ProjectManager] = None


def get_project_manager() -> ProjectManager:
    global _project_manager
    if _project_manager is None:
        _project_manager = ProjectManager()
    return _project_manager
