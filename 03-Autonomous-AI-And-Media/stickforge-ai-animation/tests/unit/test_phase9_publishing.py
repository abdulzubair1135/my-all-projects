"""
Tests for Phase 9 & 10: YouTube and Instagram Publishing Adapters, Smart Repurposer, and Scheduler.
"""

from pathlib import Path
import pytest
from pydantic import ValidationError
from app.publishing.base_publisher import PublishingMetadata
from app.publishing.youtube_publisher import YouTubePublisher
from app.publishing.instagram_publisher import InstagramPublisher
from app.publishing.publishing_scheduler import SmartRepurposer, PublishingScheduler
from app.storage.repositories import ProjectRepository


def test_smart_repurposer():
    title = "The Great Marathon"
    premise = "Rahul runs against all odds."
    narr = "Rahul kept running."

    yt_meta = SmartRepurposer.generate_youtube_shorts_metadata(title, premise, narr)
    assert "#Shorts" in yt_meta.title
    assert "Shorts" in yt_meta.tags

    ig_meta = SmartRepurposer.generate_instagram_reels_metadata(title, premise, narr)
    assert "#reels" in ig_meta.description
    assert len(ig_meta.tags) > 0


def test_youtube_publisher_validation(tmp_path):
    pub = YouTubePublisher(simulate_mode=True)
    fake_video = tmp_path / "dummy.mp4"
    fake_video.write_bytes(b"dummy")

    # Pydantic schema validation on 100 char limit
    with pytest.raises(ValidationError):
        PublishingMetadata(title="A" * 105)

    # Empty title validation via publisher
    meta = PublishingMetadata.model_construct(title="")
    errs = pub.validate_media_and_metadata(fake_video, meta)
    assert any("empty" in e for e in errs)


def test_publishing_scheduler_simulated_execution(tmp_path):
    scheduler = PublishingScheduler()
    proj_repo = ProjectRepository()

    import uuid
    # Register project first to satisfy SQLite FOREIGN KEY
    proj_id = f"pub_sched_test_{uuid.uuid4().hex[:8]}"
    proj_repo.create({
        "id": proj_id,
        "name": "Sched Test Project",
        "topic": "Running",
        "genre": "action",
        "language": "hinglish",
        "duration_target": 10.0,
        "aspect_ratio": "9:16",
        "status": "draft",
        "file_path": str(tmp_path / "p.sfproj"),
    })

    from app.video.compositor import VideoCompositor
    from app.ai.schema_validator import GeneratedStoryboard, CharacterDef, SceneSpec
    from app.audio.tts_provider import MockTTSProvider

    sb = GeneratedStoryboard(
        project_id=proj_id,
        title="Sched Test",
        characters=[CharacterDef(id="h", name="H")],
        scenes=[SceneSpec(id="s1", sequence_order=1, duration=3.5, narration="Testing scheduler.")]
    )
    test_mp4 = tmp_path / "sched_test.mp4"
    comp = VideoCompositor(width=540, height=960, fps=15, tts_provider=MockTTSProvider())
    comp.render_project_to_mp4(sb, tmp_path / "work", test_mp4)

    meta = PublishingMetadata(title="Scheduler Video Test", description="Testing upload")
    job_id = scheduler.schedule_job(
        project_id=proj_id,
        platform="youtube",
        media_path=test_mp4,
        metadata=meta,
    )
    assert job_id.startswith("pub_")

    # Execute
    res = scheduler.execute_job_now(job_id)
    assert res.success is True
    assert res.platform == "youtube"
    assert res.video_id is not None
    assert res.is_simulated is True
