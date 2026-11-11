"""
End-to-End (E2E) Acceptance Test for StickForge AI.
Verifies the complete creation, animation, voice synthesis, video export, thumbnail, and publishing lifecycle.
"""

from pathlib import Path
import pytest

from app.storage.project_manager import ProjectManager, CharacterModel
from app.ai.ai_provider import MockAIProvider
from app.story.continuity_checker import check_continuity
from app.audio.tts_provider import MockTTSProvider
from app.audio.subtitle_generator import generate_subtitles_from_storyboard
from app.video.compositor import VideoCompositor
from app.video.thumbnail_generator import ThumbnailGenerator
from app.video.ffmpeg_manager import probe_media
from app.publishing.base_publisher import PublishingMetadata
from app.publishing.publishing_scheduler import PublishingScheduler, SmartRepurposer


def test_full_stickforge_studio_pipeline(tmp_path):
    # 1. Create project via ProjectManager
    pm = ProjectManager(projects_dir=tmp_path / "projects")
    project = pm.create_project(
        name="Acceptance Marathon",
        topic="Marathon Victory",
        genre="motivational",
        language="hinglish",
        duration_target=6.0,
        aspect_ratio="9:16",
    )
    assert project.id.startswith("proj_")
    assert project.name == "Acceptance Marathon"

    # 2. Generate Story Script via AI Provider
    ai = MockAIProvider()
    script = ai.generate_story(
        topic=project.topic,
        genre=project.genre,
        language=project.language,
        duration_target=project.duration_target,
        character_count=1,
    )
    assert len(script.beats) >= 3
    assert len(script.full_narration) > 10

    # 3. Decompose to Storyboard
    storyboard = ai.generate_storyboard(
        project_id=project.id,
        script=script,
        aspect_ratio=project.aspect_ratio,
    )
    assert len(storyboard.scenes) >= 3

    # 4. Validate Continuity
    report = check_continuity(storyboard, target_duration=project.duration_target)
    assert report.is_valid is True

    # 5. Customize Character
    storyboard.characters[0].color = "#0284C7"
    storyboard.characters[0].name = "Champion Rahul"

    # 6. Generate Subtitles
    srt_path = tmp_path / "subtitles.srt"
    cues = generate_subtitles_from_storyboard(storyboard, srt_path, storyboard.aspect_ratio)
    assert srt_path.exists()
    assert len(cues) == len(storyboard.scenes)

    # 7. Render Final MP4 Video using Compositor & FFmpeg
    output_mp4 = tmp_path / "final_video.mp4"
    work_dir = tmp_path / "work"
    compositor = VideoCompositor(
        width=540,
        height=960,
        fps=15,
        tts_provider=MockTTSProvider(),
    )

    rendered_video = compositor.render_project_to_mp4(
        storyboard=storyboard,
        work_dir=work_dir,
        output_mp4_path=output_mp4,
    )
    assert rendered_video.exists()

    # 8. Probe Media
    probe_info = probe_media(rendered_video)
    assert probe_info["has_video"] is True
    assert probe_info["has_audio"] is True
    assert probe_info["width"] == 540
    assert probe_info["height"] == 960
    assert probe_info["duration"] > 2.0

    # 9. Generate Thumbnail
    thumb_path = tmp_path / "thumbnail.jpg"
    thumb_gen = ThumbnailGenerator(width=540, height=960)
    thumb_gen.generate(storyboard, thumb_path)
    assert thumb_path.exists()
    assert thumb_path.stat().st_size > 1000

    # 10. Smart Repurposing & Publishing
    meta = SmartRepurposer.generate_youtube_shorts_metadata(
        title=storyboard.title,
        premise=script.premise,
        full_narration=script.full_narration,
    )
    scheduler = PublishingScheduler()
    job_id = scheduler.schedule_job(
        project_id=project.id,
        platform="youtube",
        media_path=rendered_video,
        metadata=meta,
    )
    pub_result = scheduler.execute_job_now(job_id)
    assert pub_result.success is True
    assert pub_result.video_id is not None

    # 11. Reopen and verify Project state
    reloaded = pm.load_project(project.id)
    assert reloaded is not None
    assert reloaded.name == project.name
