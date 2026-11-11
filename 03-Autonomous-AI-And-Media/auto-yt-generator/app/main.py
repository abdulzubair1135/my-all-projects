"""
AUTO YT GENERATOR — Command Line Interface.

Professional CLI for creating, inspecting, and generating automated video projects.
Works seamlessly with or without optional rich formatting and handles Windows cp1252 cleanly.
"""

import sys
import uuid
import json
from pathlib import Path

# Ensure root directory is always on python sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import click

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

from app.constants import (
    APP_NAME,
    APP_VERSION,
    VideoStyle,
    Language,
    PipelineStage,
    DEFAULT_DURATION,
    DEFAULT_FPS,
)
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
    AnimationStage,
    VideoRenderStage,
    OutputStage,
)
from app.animation.animator import scene_animator
from app.audio.music import music_generator
from app.quality.validator import quality_validator
from app.upload.youtube_uploader import youtube_uploader
from app.pipeline.batch import batch_generator
from app.logger import logger


def print_panel(text: str, title: str = ""):
    if HAS_RICH and console:
        console.print(Panel(text, title=title, border_style="cyan"))
    else:
        safe_title = title.encode("ascii", errors="replace").decode("ascii")
        safe_text = text.encode("ascii", errors="replace").decode("ascii")
        print(f"\n--- {safe_title} ---")
        print(safe_text)
        print("-" * (len(safe_title) + 8) + "\n")


@click.group()
@click.version_option(version=APP_VERSION, prog_name=APP_NAME)
def cli():
    """AUTO YT GENERATOR — AI & Procedural 2D YouTube Video Studio."""
    pass


@cli.command("info")
def show_info():
    """Displays system and environment configuration info."""
    info_text = (
        f"Application:        {APP_NAME} v{APP_VERSION}\n"
        f"Environment:        {settings.app.env}\n"
        f"AI Provider:        {settings.providers.ai_provider}\n"
        f"TTS Provider:       {settings.providers.tts_provider}\n"
        f"Music Provider:     {settings.providers.music_provider}\n"
        f"Default Resolution: {settings.video.default_resolution}\n"
        f"Projects Directory: {settings.paths.projects_dir}"
    )
    print_panel(info_text, title="System Information")


@cli.command("gui")
def launch_gui_cmd():
    """Launches the modern Desktop Graphical Studio interface (PyQt5)."""
    try:
        from app.gui.app import launch_gui
        print("Launching Desktop Graphical Studio...")
        launch_gui()
    except Exception as e:
        print(f"Failed to launch GUI: {e}")


@cli.command("new-project")
@click.option("--topic", "-t", required=True, help="Video topic or question (e.g. 'What if your brain stops?')")
@click.option(
    "--language",
    "-l",
    type=click.Choice([lang.value for lang in Language]),
    default=Language.ENGLISH.value,
    help="Language code",
)
@click.option(
    "--duration",
    "-d",
    type=int,
    default=DEFAULT_DURATION,
    help="Target duration in seconds",
)
@click.option(
    "--style",
    "-s",
    type=click.Choice([style.value for style in VideoStyle]),
    default=VideoStyle.DARK_CARTOON.value,
    help="Visual art style",
)
@click.option("--aspect", default="16:9", type=click.Choice(["16:9", "9:16"]), help="Aspect ratio (16:9 Widescreen or 9:16 Shorts/Reels)")
@click.option("--resolution", "-r", default="1920x1080", help="Video dimensions (e.g. 1920x1080 or 1080x1920)")
@click.option("--fps", type=int, default=DEFAULT_FPS, help="Frames per second")
@click.option("--voice", default="deep_narrator", help="Voice style preset")
@click.option("--music", default="dark_suspense", help="Music mood preset")
def new_project(topic, language, duration, style, aspect, resolution, fps, voice, music):
    """Creates a new automated video generator project in DB and filesystem."""
    project_id = str(uuid.uuid4())
    project_dir = Path(settings.paths.projects_dir) / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    if aspect == "9:16":
        resolution = "1080x1920"

    for sub in ["assets", "audio", "renders", "final", "thumbnail", "metadata"]:
        (project_dir / sub).mkdir(exist_ok=True)

    config = ProjectConfig(
        topic=topic,
        language=language,
        duration_seconds=duration,
        style=style,
        resolution=resolution,
        fps=fps,
        voice_style=voice,
        music_style=music,
    )

    project = ProjectModel(
        id=project_id,
        title=topic[:60],
        config=config,
        current_stage=PipelineStage.QUEUED,
        progress_percent=0.0,
        project_dir=str(project_dir),
    )

    db.create_project(project)

    created_info = (
        f"Project ID: {project_id}\n"
        f"Topic:      {topic}\n"
        f"Language:   {language}\n"
        f"Style:      {style}\n"
        f"Aspect:     {aspect} ({resolution})\n"
        f"Duration:   {duration}s\n"
        f"Directory:  {project_dir}"
    )
    print_panel(created_info, title="[+] Project Created Successfully")


@cli.command("list-projects")
def list_projects():
    """Lists all created projects."""
    projects = db.list_projects()
    if not projects:
        print("No projects found. Create one with `new-project`.")
        return

    if HAS_RICH and console:
        table = Table(title="AUTO YT Projects", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=36)
        table.add_column("Topic", style="cyan", max_width=40)
        table.add_column("Style", style="green")
        table.add_column("Lang", style="blue")
        table.add_column("Duration", justify="right")
        table.add_column("Stage", style="bold yellow")
        table.add_column("Progress", justify="right")

        for p in projects:
            table.add_row(
                p.id,
                p.topic,
                p.style,
                p.language,
                f"{p.duration_seconds}s",
                p.current_stage,
                f"{p.progress_percent:.0f}%",
            )
        console.print(table)
    else:
        print("\n" + "=" * 80)
        print(f"{'ID':<38} | {'TOPIC':<25} | {'STAGE':<12} | {'PROGRESS'}")
        print("=" * 80)
        for p in projects:
            print(f"{p.id:<38} | {p.topic[:25]:<25} | {p.current_stage:<12} | {p.progress_percent:.0f}%")
        print("=" * 80 + "\n")


@cli.command("show-project")
@click.argument("project_id")
def show_project(project_id):
    """Inspects full details of a specific project."""
    project = db.get_project(project_id)
    if not project:
        print(f"Error: Project '{project_id}' not found.")
        sys.exit(1)

    details = (
        f"ID:            {project.id}\n"
        f"Title:         {project.title}\n"
        f"Topic:         {project.config.topic}\n"
        f"Language:      {project.config.language}\n"
        f"Style:         {project.config.style}\n"
        f"Duration:      {project.config.duration_seconds} seconds\n"
        f"Resolution:    {project.config.resolution} @ {project.config.fps}fps\n"
        f"Current Stage: {project.current_stage}\n"
        f"Progress:      {project.progress_percent}%\n"
        f"Directory:     {project.project_dir}\n"
        f"Error:         {project.error_message or 'None'}\n"
        f"Created At:    {project.created_at.isoformat()}"
    )
    print_panel(details, title=f"Project: {project.id}")


@cli.command("generate-script")
@click.argument("project_id")
def generate_script_cmd(project_id):
    """Executes AI Research & Script generation stages for a project."""
    project = db.get_project(project_id)
    if not project:
        print(f"Error: Project '{project_id}' not found.")
        sys.exit(1)

    orchestrator = PipelineOrchestrator([
        ResearchStage(),
        ScriptStage(),
    ])

    print(f"Starting AI Research & Script Generation for '{project.config.topic}'...")
    job = orchestrator.run_pipeline(project)

    if job.status.value == "COMPLETED":
        script_file = Path(project.project_dir) / "metadata" / "script.json"
        if script_file.exists():
            with open(script_file, "r", encoding="utf-8") as f:
                script_data = json.load(f)

            summary = (
                f"Title: {script_data.get('title')}\n"
                f"Hook:  {script_data.get('hook')}\n"
                f"Total Sections: {len(script_data.get('sections', []))}\n"
                f"Estimated Duration: {script_data.get('total_estimated_duration_sec')}s\n"
                f"Saved to: {script_file}"
            )
            print_panel(summary, title="[OK] Script Generated Successfully")
    else:
        print(f"Failed to generate script. Check logs for details.")


@cli.command("generate-scenes")
@click.argument("project_id")
def generate_scenes_cmd(project_id):
    """Executes Scene Planning & Storyboard generation stages for a project."""
    project = db.get_project(project_id)
    if not project:
        print(f"Error: Project '{project_id}' not found.")
        sys.exit(1)

    orchestrator = PipelineOrchestrator([
        ResearchStage(),
        ScriptStage(),
        ScenePlanningStage(),
    ])

    print(f"Starting Storyboard & Scene Planning for '{project.config.topic}'...")
    job = orchestrator.run_pipeline(project)

    if job.status.value == "COMPLETED":
        scenes = db.get_scenes(project.id)
        summary = (
            f"Project: {project.config.topic}\n"
            f"Total Scenes Planned: {len(scenes)}\n"
            f"Total Duration: {sum(s.duration_sec for s in scenes):.1f}s\n"
            f"Saved to: SQLite DB & {project.project_dir}/metadata/scenes.json"
        )
        print_panel(summary, title="[OK] Storyboard & Scenes Generated Successfully")
    else:
        print(f"Failed to generate scenes. Check logs for details.")


@cli.command("show-scenes")
@click.argument("project_id")
def show_scenes_cmd(project_id):
    """Displays the storyboard scene plan for a project."""
    scenes = db.get_scenes(project_id)
    if not scenes:
        print(f"No scenes found for project '{project_id}'. Run `generate-scenes` first.")
        return

    print(f"\n================ Storyboard Scenes for Project {project_id} ================\n")
    for s in scenes:
        actions_str = ", ".join([f"{a.entity_id}:{a.action}({a.expression})" for a in s.actions]) or "None"
        sfx_str = ", ".join(s.sfx) or "None"
        effects_str = ", ".join(s.effects) or "None"
        chars_str = ", ".join(s.characters) or "None"
        props_str = ", ".join(s.props) or "None"

        scene_card = (
            f"Scene #{s.scene_index} [{s.section_ref or 'scene'}] ({s.duration_sec}s | Mood: {s.mood})\n"
            f"  Background:  {s.background_id}\n"
            f"  Characters:  {chars_str}\n"
            f"  Props:       {props_str}\n"
            f"  Actions:     {actions_str}\n"
            f"  Camera:      {s.camera.type} (zoom {s.camera.zoom_start} -> {s.camera.zoom_end})\n"
            f"  VFX:         {effects_str}\n"
            f"  SFX:         {sfx_str}\n"
            f"  Narration:   \"{s.narration_text[:80]}...\""
        )
        print_panel(scene_card, title=f"Scene {s.scene_index}")


@cli.command("generate-assets")
@click.argument("project_id")
def generate_assets_cmd(project_id):
    """Generates all 2D character poses, 1080p backgrounds, and props for a project."""
    project = db.get_project(project_id)
    if not project:
        print(f"Error: Project '{project_id}' not found.")
        sys.exit(1)

    orchestrator = PipelineOrchestrator([
        ResearchStage(),
        ScriptStage(),
        ScenePlanningStage(),
        AssetGenerationStage(),
    ])

    print(f"Generating 2D Character Poses, 1080p Backgrounds & Props for '{project.config.topic}'...")
    job = orchestrator.run_pipeline(project)

    if job.status.value == "COMPLETED":
        asset_folder = Path(project.project_dir) / "assets"
        asset_files = list(asset_folder.glob("*.png")) if asset_folder.exists() else []

        summary = (
            f"Project: {project.config.topic}\n"
            f"Total Generated Assets: {len(asset_files)}\n"
            f"Asset Folder: {asset_folder}\n"
            f"Types Generated: 1080p Backgrounds, Character Poses, Props"
        )
        print_panel(summary, title="[OK] Assets Generated Successfully")
    else:
        print("Failed to generate assets. Check logs for details.")


@cli.command("generate-voice")
@click.argument("project_id")
def generate_voice_cmd(project_id):
    """Synthesizes voiceover audio for each scene in a project."""
    project = db.get_project(project_id)
    if not project:
        print(f"Error: Project '{project_id}' not found.")
        sys.exit(1)

    orchestrator = PipelineOrchestrator([
        ResearchStage(),
        ScriptStage(),
        ScenePlanningStage(),
        VoiceGenerationStage(),
    ])

    print(f"Synthesizing Voiceover Audio for '{project.config.topic}'...")
    job = orchestrator.run_pipeline(project)

    if job.status.value == "COMPLETED":
        audio_folder = Path(project.project_dir) / "audio"
        audio_files = list(audio_folder.glob("*.*")) if audio_folder.exists() else []

        summary = (
            f"Project: {project.config.topic}\n"
            f"Total Voice Clips Generated: {len(audio_files)}\n"
            f"Audio Directory: {audio_folder}\n"
            f"Language: {project.config.language}"
        )
        print_panel(summary, title="[OK] Voiceover Audio Generated Successfully")
    else:
        print("Failed to generate voiceover. Check logs for details.")


@cli.command("mix-audio")
@click.argument("project_id")
def mix_audio_cmd(project_id):
    """Generates procedural music and mixes master audio with automated voice ducking."""
    project = db.get_project(project_id)
    if not project:
        print(f"Error: Project '{project_id}' not found.")
        sys.exit(1)

    orchestrator = PipelineOrchestrator([
        ResearchStage(),
        ScriptStage(),
        ScenePlanningStage(),
        VoiceGenerationStage(),
        AudioMixStage(),
    ])

    print(f"Mixing Master Audio with Dynamic Voice Ducking for '{project.config.topic}'...")
    job = orchestrator.run_pipeline(project)

    if job.status.value == "COMPLETED":
        master_audio = Path(project.project_dir) / "audio" / "master_audio.wav"
        bg_music = Path(project.project_dir) / "audio" / "bg_music.wav"

        summary = (
            f"Project: {project.config.topic}\n"
            f"Master Mixed Audio: {master_audio}\n"
            f"Background Score:   {bg_music}\n"
            f"Features: Procedural 808 Bass, Drums, Melody, Voice Ducking (-12dB active)"
        )
        print_panel(summary, title="[OK] Master Audio Mixed Successfully")
    else:
        print("Failed to mix audio. Check logs for details.")


@cli.command("generate-phonk")
@click.option("--output", "-o", default="phonk_beat.wav", help="Output WAV filename")
@click.option("--duration", "-d", default=30.0, type=float, help="Track duration in seconds")
@click.option("--bpm", default=145, type=int, help="Beats per minute")
def generate_phonk_cmd(output, duration, bpm):
    """Standalone Phonk / Music Generator mode."""
    print(f"Generating Phonk Track ({duration}s @ {bpm} BPM)...")
    out_path = music_generator.generate_music(
        duration_sec=duration,
        output_path=output,
        style="phonk",
        bpm=bpm,
    )
    print_panel(f"Phonk Track Rendered: {out_path}\nBPM: {bpm}\nDuration: {duration}s", title="[OK] Phonk Generator")


@cli.command("render-video")
@click.argument("project_id")
@click.option("--fps", default=30, type=int, help="Video frames per second (e.g. 30 or 60)")
def render_video_cmd(project_id, fps):
    """Executes full automated pipeline and exports final 1080p MP4 with audio & subtitles."""
    project = db.get_project(project_id)
    if not project:
        print(f"Error: Project '{project_id}' not found.")
        sys.exit(1)

    project.config.fps = fps

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

    print(f"Rendering Full 1080p MP4 Video for '{project.config.topic}'...")
    job = orchestrator.run_pipeline(project)

    if job.status.value == "COMPLETED":
        final_mp4 = Path(project.project_dir) / "final" / "video.mp4"
        srt_file = Path(project.project_dir) / "final" / "subtitles.srt"
        thumb_file = Path(project.project_dir) / "final" / "thumbnail.png"

        summary = (
            f"Project:          {project.config.topic}\n"
            f"Final MP4 Video:  {final_mp4}\n"
            f"Subtitles (SRT):  {srt_file}\n"
            f"Thumbnail:        {thumb_file}\n"
            f"Metadata Folder:  {project.project_dir}/final\n"
            f"Status:           100% COMPLETE & YOUTUBE READY"
        )
        print_panel(summary, title="[OK] Final Video & Metadata Completed Successfully!")
    else:
        print("Failed to render video. Check logs for details.")


@cli.command("batch-generate")
@click.option("--file", "-f", required=True, help="Path to text file containing video topics (one per line)")
@click.option("--style", default="dark_cartoon", help="Visual art style")
@click.option("--language", default="en", help="Language code")
@click.option("--duration", default=180, type=int, help="Duration in seconds")
@click.option("--fps", default=15, type=int, help="FPS")
def batch_generate_cmd(file, style, language, duration, fps):
    """Generates multiple complete YouTube videos in batch from a topics file."""
    print(f"Starting Batch Production from '{file}'...")
    results = batch_generator.run_batch_from_file(
        topics_file=file,
        style=style,
        language=language,
        duration_sec=duration,
        fps=fps,
    )
    print_panel(f"Batch completed for {len(results)} videos!\nOutput details in database.", title="[OK] Batch Video Production Complete")


@cli.command("upload-youtube")
@click.argument("project_id")
@click.option("--privacy", default="unlisted", type=click.Choice(["public", "unlisted", "private"]), help="Privacy status")
def upload_youtube_cmd(project_id, privacy):
    """Directly uploads project video, thumbnail, and metadata to YouTube."""
    project = db.get_project(project_id)
    if not project:
        print(f"Error: Project '{project_id}' not found.")
        sys.exit(1)

    print(f"Uploading '{project.config.topic}' to YouTube ({privacy})...")
    res = youtube_uploader.upload_project_video(project, privacy_status=privacy)
    print_panel(
        f"Video URL: {res.get('video_url')}\nStatus: {res.get('status')}\nNote: {res.get('note', '')}",
        title="[OK] YouTube Upload Result",
    )


@cli.command("generate-all")
@click.argument("project_id")
@click.option("--fps", default=30, type=int, help="Frames per second")
def generate_all_cmd(project_id, fps):
    """1-Click Master Generator: Runs all 8 stages from topic to finished YouTube MP4."""
    project = db.get_project(project_id)
    if not project:
        print(f"Error: Project '{project_id}' not found.")
        sys.exit(1)

    project.config.fps = fps

    orchestrator = PipelineOrchestrator([
        ResearchStage(),
        ScriptStage(),
        ScenePlanningStage(),
        AssetGenerationStage(),
        VoiceGenerationStage(),
        AudioMixStage(),
        AnimationStage(),
        VideoRenderStage(),
        OutputStage(),
    ])

    print(f"Starting 1-Click Master Generator for '{project.config.topic}'...")
    job = orchestrator.run_pipeline(project)

    if job.status.value == "COMPLETED":
        final_mp4 = Path(project.project_dir) / "final" / "video.mp4"
        thumb_file = Path(project.project_dir) / "final" / "thumbnail.png"
        summary = (
            f"Project:   {project.config.topic}\n"
            f"Video:     {final_mp4}\n"
            f"Thumbnail: {thumb_file}\n"
            f"All Assets, Voiceover, Music, SFX & Metadata Generated!"
        )
        print_panel(summary, title="[OK] Full 1-Click Generation Finished!")


@cli.command("validate-project")
@click.argument("project_id")
def validate_project_cmd(project_id):
    """Runs quality audit checklist on a project."""
    project = db.get_project(project_id)
    if not project:
        print(f"Error: Project '{project_id}' not found.")
        sys.exit(1)

    report = quality_validator.validate_project(project)
    print_panel(
        f"Passed: {report['passed']}\nErrors: {len(report['errors'])}\nWarnings: {len(report['warnings'])}\nDetails saved in final/quality_report.json",
        title="Quality Control Audit",
    )


@cli.command("delete-project")
@click.argument("project_id")
def delete_project(project_id):
    """Deletes a project from the database."""
    success = db.delete_project(project_id)
    if success:
        print(f"Project {project_id} deleted successfully.")
    else:
        print(f"Error: Project {project_id} not found.")


if __name__ == "__main__":
    cli()
