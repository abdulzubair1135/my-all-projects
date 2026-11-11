"""
Unit tests for StickForge AI Phase 1 Core Foundation.
Tests configuration, database schema, project manager, task manager, and event bus.
"""

import os
import shutil
import tempfile
from pathlib import Path
import pytest

from app.core.config import AppConfig
from app.core.logging_manager import setup_logging, get_logger, InMemoryLogHandler
from app.core.event_bus import EventBus
from app.core.task_manager import TaskManager, TaskState
from app.storage.database import Database
from app.storage.repositories import ProjectRepository, CheckpointRepository
from app.storage.project_manager import ProjectManager, ProjectData, CharacterModel, SceneModel


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


def test_app_config_serialization(temp_dir):
    cfg_file = temp_dir / "config.json"
    cfg = AppConfig()
    cfg.video.default_fps = 60
    cfg.tts.default_provider = "pyttsx3"
    cfg.save(cfg_file)

    loaded = AppConfig.load(cfg_file)
    assert loaded.video.default_fps == 60
    assert loaded.tts.default_provider == "pyttsx3"
    assert loaded.browser.headless is False  # Must be visible by default


def test_database_initialization_and_crud(temp_dir):
    db_file = temp_dir / "test.db"
    db = Database(db_file)
    db.initialize()

    repo = ProjectRepository(db)
    proj_id = "test_p1"
    repo.create({
        "id": proj_id,
        "name": "Unit Test Project",
        "topic": "Stickman Hero",
        "genre": "action",
        "language": "hinglish",
        "duration_target": 25.0,
        "aspect_ratio": "9:16",
        "status": "draft",
        "file_path": "/fake/path"
    })

    fetched = repo.get(proj_id)
    assert fetched is not None
    assert fetched["name"] == "Unit Test Project"
    assert fetched["genre"] == "action"

    repo.update(proj_id, {"status": "rendered"})
    updated = repo.get(proj_id)
    assert updated["status"] == "rendered"

    repo.delete(proj_id)
    assert repo.get(proj_id) is None


def test_project_manager_atomic_save(temp_dir):
    mgr = ProjectManager(projects_dir=temp_dir)
    project = mgr.create_project(
        name="Atomic Test",
        topic="Testing",
        genre="comedy",
        language="english",
        duration_target=15.0,
    )

    loaded = mgr.load_project(project.id)
    assert loaded is not None
    assert loaded.name == "Atomic Test"
    assert len(loaded.scenes) == 1

    # Modify and save
    loaded.name = "Renamed Atomic Test"
    loaded.scenes.append(SceneModel(id="sc_2", sequence_order=2, duration=4.0))
    mgr.save_project(loaded)

    reloaded = mgr.load_project(project.id)
    assert reloaded.name == "Renamed Atomic Test"
    assert len(reloaded.scenes) == 2


def test_task_manager_transitions_and_checkpoints(temp_dir):
    db_file = temp_dir / "test_tasks.db"
    db = Database(db_file)
    db.initialize()

    tm = TaskManager()
    tm.checkpoint_repo = CheckpointRepository(db)

    job = tm.create_job(project_id="proj_xyz", task_type="ai_generation")
    assert job.state == TaskState.PENDING

    tm.transition(job.id, TaskState.RUNNING, progress=25.0)
    assert tm.get_job(job.id).state == TaskState.RUNNING
    assert tm.get_job(job.id).progress == 25.0

    # Save and reload checkpoint
    tm.save_checkpoint(job.id, "step_story_prompt", {"prompt_tokens": 120, "partial_story": "Rahul arrives"})
    cp = tm.load_checkpoint(job.id)
    assert cp is not None
    assert cp["step_name"] == "step_story_prompt"
    assert cp["state_data"]["partial_story"] == "Rahul arrives"

    # Transition to completed
    tm.transition(job.id, TaskState.COMPLETED, progress=100.0)
    assert tm.get_job(job.id).state == TaskState.COMPLETED


def test_event_bus():
    bus = EventBus()
    received = []

    def handler(message, code):
        received.append((message, code))

    bus.subscribe("test_topic", handler)
    bus.publish("test_topic", message="hello", code=200)

    assert len(received) == 1
    assert received[0] == ("hello", 200)

    bus.unsubscribe("test_topic", handler)
    bus.publish("test_topic", message="world", code=201)
    assert len(received) == 1
