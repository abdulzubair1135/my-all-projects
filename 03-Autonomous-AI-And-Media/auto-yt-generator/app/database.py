"""
AUTO YT GENERATOR — SQLite Database Layer.

Handles storage for projects, scenes, assets, jobs, and render status with auto-migration.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.constants import DB_FILE, PipelineStage
from app.models.project import ProjectModel, ProjectConfig, ProjectSummary
from app.models.scene import SceneModel, CameraConfig, SceneAction
from app.logger import logger


class Database:
    """SQLite Database manager with automated schema creation, migrations, and CRUD."""

    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create tables and apply automated column migrations if missing."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Projects Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    language TEXT NOT NULL,
                    duration_seconds INTEGER NOT NULL,
                    style TEXT NOT NULL,
                    resolution TEXT NOT NULL,
                    fps INTEGER NOT NULL,
                    voice_style TEXT,
                    music_style TEXT,
                    tone TEXT,
                    current_stage TEXT NOT NULL,
                    progress_percent REAL NOT NULL,
                    error_message TEXT,
                    project_dir TEXT,
                    output_video_path TEXT,
                    thumbnail_path TEXT,
                    config_json TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP
                )
            """)

            # Scenes Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scenes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    scene_index INTEGER NOT NULL,
                    section_ref TEXT,
                    duration_sec REAL NOT NULL,
                    narration_text TEXT,
                    background_id TEXT NOT NULL,
                    characters_json TEXT,
                    props_json TEXT,
                    actions_json TEXT,
                    camera_json TEXT,
                    effects_json TEXT,
                    sfx_json TEXT,
                    mood TEXT,
                    audio_file TEXT,
                    subtitle_text TEXT,
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    UNIQUE(project_id, scene_index)
                )
            """)

            # Assets Catalog Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    asset_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    is_procedural INTEGER NOT NULL,
                    metadata_json TEXT,
                    created_at TIMESTAMP NOT NULL
                )
            """)

            # Pipeline Jobs Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    current_stage TEXT NOT NULL,
                    status TEXT NOT NULL,
                    overall_progress REAL NOT NULL,
                    stage_logs_json TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
            """)

            # Cache Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    cache_key TEXT PRIMARY KEY,
                    stage TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP
                )
            """)

            # Migration check: Ensure newly added columns exist in existing SQLite databases
            cursor.execute("PRAGMA table_info(scenes)")
            existing_columns = [row["name"] for row in cursor.fetchall()]
            if "section_ref" not in existing_columns:
                cursor.execute("ALTER TABLE scenes ADD COLUMN section_ref TEXT")
            if "subtitle_text" not in existing_columns:
                cursor.execute("ALTER TABLE scenes ADD COLUMN subtitle_text TEXT")

            conn.commit()
            logger.debug("Database initialized successfully.")

    # ── Project CRUD ──────────────────────────────────────────────────────────

    def create_project(self, project: ProjectModel) -> ProjectModel:
        """Insert a new project record."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO projects (
                    id, title, topic, language, duration_seconds, style,
                    resolution, fps, voice_style, music_style, tone,
                    current_stage, progress_percent, error_message,
                    project_dir, output_video_path, thumbnail_path,
                    config_json, created_at, updated_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    project.id,
                    project.title,
                    project.config.topic,
                    project.config.language,
                    project.config.duration_seconds,
                    project.config.style,
                    project.config.resolution,
                    project.config.fps,
                    project.config.voice_style,
                    project.config.music_style,
                    project.config.tone,
                    project.current_stage,
                    project.progress_percent,
                    project.error_message,
                    project.project_dir,
                    project.output_video_path,
                    project.thumbnail_path,
                    project.config.model_dump_json(),
                    project.created_at.isoformat(),
                    project.updated_at.isoformat(),
                    project.completed_at.isoformat() if project.completed_at else None,
                ),
            )
            conn.commit()
            logger.info(f"Project created in DB: {project.id} ({project.config.topic})")
        return project

    def get_project(self, project_id: str) -> Optional[ProjectModel]:
        """Fetch full project details by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
            row = cursor.fetchone()
            if not row:
                return None

            config_data = json.loads(row["config_json"])
            return ProjectModel(
                id=row["id"],
                title=row["title"],
                config=ProjectConfig(**config_data),
                current_stage=PipelineStage(row["current_stage"]),
                progress_percent=row["progress_percent"],
                error_message=row["error_message"],
                project_dir=row["project_dir"],
                output_video_path=row["output_video_path"],
                thumbnail_path=row["thumbnail_path"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
            )

    def list_projects(self) -> List[ProjectSummary]:
        """List all projects in descending creation order."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
            rows = cursor.fetchall()
            summaries = []
            for row in rows:
                summaries.append(
                    ProjectSummary(
                        id=row["id"],
                        title=row["title"],
                        topic=row["topic"],
                        style=row["style"],
                        language=row["language"],
                        duration_seconds=row["duration_seconds"],
                        current_stage=row["current_stage"],
                        progress_percent=row["progress_percent"],
                        created_at=datetime.fromisoformat(row["created_at"]),
                    )
                )
            return summaries

    def update_project_stage(
        self,
        project_id: str,
        stage: PipelineStage,
        progress_percent: float,
        error_message: Optional[str] = None,
    ) -> None:
        """Update current stage and progress percentage for a project."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE projects
                SET current_stage = ?, progress_percent = ?, error_message = ?, updated_at = ?
                WHERE id = ?
            """,
                (
                    stage.value,
                    progress_percent,
                    error_message,
                    datetime.utcnow().isoformat(),
                    project_id,
                ),
            )
            conn.commit()

    def delete_project(self, project_id: str) -> bool:
        """Delete a project and related records from database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ── Scene CRUD ────────────────────────────────────────────────────────────

    def save_scenes(self, project_id: str, scenes: List[SceneModel]) -> None:
        """Inserts or replaces a list of scenes for a given project."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Clean old scenes for project
            cursor.execute("DELETE FROM scenes WHERE project_id = ?", (project_id,))

            for scene in scenes:
                cursor.execute(
                    """
                    INSERT INTO scenes (
                        project_id, scene_index, section_ref, duration_sec, narration_text,
                        background_id, characters_json, props_json, actions_json,
                        camera_json, effects_json, sfx_json, mood, audio_file, subtitle_text
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        project_id,
                        scene.scene_index,
                        scene.section_ref,
                        scene.duration_sec,
                        scene.narration_text,
                        scene.background_id,
                        json.dumps(scene.characters),
                        json.dumps(scene.props),
                        json.dumps([a.model_dump() for a in scene.actions]),
                        scene.camera.model_dump_json(),
                        json.dumps(scene.effects),
                        json.dumps(scene.sfx),
                        scene.mood,
                        scene.audio_file,
                        scene.subtitle_text,
                    ),
                )
            conn.commit()
            logger.info(f"Saved {len(scenes)} storyboard scenes to DB for project {project_id}.")

    def get_scenes(self, project_id: str) -> List[SceneModel]:
        """Retrieves all scenes for a project sorted by scene_index."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scenes WHERE project_id = ? ORDER BY scene_index ASC", (project_id,))
            rows = cursor.fetchall()
            scenes = []
            for row in rows:
                actions_data = json.loads(row["actions_json"] or "[]")
                actions = [SceneAction(**a) for a in actions_data]
                camera_data = json.loads(row["camera_json"] or "{}")

                scenes.append(
                    SceneModel(
                        scene_index=row["scene_index"],
                        section_ref=row["section_ref"],
                        duration_sec=row["duration_sec"],
                        narration_text=row["narration_text"] or "",
                        background_id=row["background_id"],
                        characters=json.loads(row["characters_json"] or "[]"),
                        props=json.loads(row["props_json"] or "[]"),
                        actions=actions,
                        camera=CameraConfig(**camera_data),
                        effects=json.loads(row["effects_json"] or "[]"),
                        sfx=json.loads(row["sfx_json"] or "[]"),
                        mood=row["mood"] or "suspense",
                        audio_file=row["audio_file"],
                        subtitle_text=row["subtitle_text"],
                    )
                )
            return scenes


# Default database instance
db = Database()
