"""
Integration test for Phase 6 & 7: Audio synthesis, Subtitle generation,
FFmpeg encoding, video probe inspection, and thumbnail generation.
"""

from pathlib import Path
import pytest
from app.audio.tts_provider import MockTTSProvider
from app.audio.subtitle_generator import generate_subtitles_from_storyboard
from app.video.ffmpeg_manager import probe_media, run_ffmpeg_command
from app.video.compositor import VideoCompositor
from app.video.thumbnail_generator import ThumbnailGenerator
from app.ai.schema_validator import GeneratedStoryboard, CharacterDef, SceneSpec, ActionSpec


def test_mock_tts_synthesis(tmp_path):
    tts = MockTTSProvider()
    wav_file = tmp_path / "test_speech.wav"
    dur = tts.synthesize("Rahul starts his adventure across the bridge.", wav_file)
    assert dur > 1.0
    assert wav_file.exists()
    assert wav_file.stat().st_size > 1000


def test_subtitle_generation(tmp_path):
    sb = GeneratedStoryboard(
        project_id="test_sub_proj",
        title="Subtitle Story",
        characters=[CharacterDef(id="hero", name="Hero")],
        scenes=[
            SceneSpec(id="s1", sequence_order=1, duration=3.0, narration="First scene narration line."),
            SceneSpec(id="s2", sequence_order=2, duration=4.0, narration="Second scene narration line."),
        ]
    )
    srt_file = tmp_path / "test.srt"
    cues = generate_subtitles_from_storyboard(sb, srt_file, aspect_ratio="9:16")
    assert len(cues) == 2
    assert srt_file.exists()
    content = srt_file.read_text(encoding="utf-8")
    assert "00:00:00,000 --> 00:00:03,000" in content
    assert "First scene narration line." in content


def test_end_to_end_video_render_and_probe(tmp_path):
    """
    Renders an actual 1-second test stickman animation MP4 using FFmpeg,
    then inspects the file with FFprobe/ffmpeg to verify stream properties.
    """
    work_dir = tmp_path / "render_work"
    output_mp4 = tmp_path / "final_test_video.mp4"

    sb = GeneratedStoryboard(
        project_id="proj_render_test",
        title="Render Acceptance Test",
        aspect_ratio="9:16",
        characters=[CharacterDef(id="hero", name="Rahul", color="#38BDF8")],
        scenes=[
            SceneSpec(
                id="scene_001",
                sequence_order=1,
                duration=1.2,  # Short deterministic render for fast testing
                background="classroom",
                narration="Rahul is sitting and thinking.",
                actions=[ActionSpec(character_id="hero", action="sit")],
            )
        ]
    )

    compositor = VideoCompositor(
        width=540,
        height=960,
        fps=15,
        tts_provider=MockTTSProvider(),
    )

    rendered_path = compositor.render_project_to_mp4(
        storyboard=sb,
        work_dir=work_dir,
        output_mp4_path=output_mp4,
    )

    assert rendered_path.exists()
    assert rendered_path.stat().st_size > 5000

    # Inspect media stream with probe
    info = probe_media(rendered_path)
    assert info["has_video"] is True
    assert info["has_audio"] is True
    assert info["width"] == 540
    assert info["height"] == 960
    assert info["duration"] > 0.8
    assert info["codec_video"] == "h264"


def test_thumbnail_generator(tmp_path):
    sb = GeneratedStoryboard(
        project_id="thumb_proj",
        title="Epic Stickman Quest",
        characters=[CharacterDef(id="hero", name="Rahul")],
        scenes=[SceneSpec(id="s1", sequence_order=1, duration=2.0, background="forest")]
    )
    thumb_path = tmp_path / "cover.jpg"
    gen = ThumbnailGenerator(width=540, height=960)
    gen.generate(sb, thumb_path)
    assert thumb_path.exists()
    assert thumb_path.stat().st_size > 2000
