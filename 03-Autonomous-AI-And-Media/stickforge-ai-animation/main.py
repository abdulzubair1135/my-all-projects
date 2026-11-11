"""
main.py - End-to-End Automated Stickman Video Generator Pipeline

FCFS (First-Come, First-Served) orchestration pipeline:
1. Environment pre-check
2. Storyboard script generation via browser_bridge
3. Human-in-the-loop approval gate
4. FCFS scene asset generation (Audio -> Visual)
5. Headless video assembly (FFmpeg)
6. Self-verification & reporting
"""

from __future__ import annotations
import argparse
import os
import shutil
import sys
from pathlib import Path
from typing import List, Dict, Any

from app.core.logging_manager import setup_logging, get_logger
from app.video.ffmpeg_manager import probe_media
from browser_bridge import BrowserBridge
from engine import AudioEngine, VisualEngine, VideoAssembler

# Ensure safe UTF-8 terminal printing across Windows encodings
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

logger = get_logger("pipeline_main")


def print_banner():
    print("""
========================================================================
    STICKFORGE AI - AUTONOMOUS STICKMAN VIDEO GENERATION PIPELINE
========================================================================
""")


def run_environment_check() -> Dict[str, Any]:
    """Phase 1: Environment & AI Engines diagnostic check."""
    import urllib.request

    status = {
        "ffmpeg": False,
        "python": sys.version.split()[0],
        "cdp": False,
        "ollama": False,
        "comfyui": False,
        "sd_webui": False,
    }

    # FFmpeg check
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        py_scripts_ffmpeg = Path(sys.executable).parent / "Scripts" / "ffmpeg.exe"
        if py_scripts_ffmpeg.exists():
            ffmpeg_path = str(py_scripts_ffmpeg)
    status["ffmpeg"] = bool(ffmpeg_path)

    # DeepSeek CDP check
    bridge = BrowserBridge()
    status["cdp"] = bridge.is_cdp_available()

    # Ollama check
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=0.8) as resp:
            status["ollama"] = resp.status == 200
    except Exception:
        status["ollama"] = False

    # ComfyUI check (port 8188)
    try:
        with urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=0.8) as resp:
            status["comfyui"] = resp.status == 200
    except Exception:
        status["comfyui"] = False

    # SD WebUI check (port 7860)
    try:
        with urllib.request.urlopen("http://127.0.0.1:7860/sdapi/v1/progress", timeout=0.8) as resp:
            status["sd_webui"] = resp.status == 200
    except Exception:
        status["sd_webui"] = False

    print("\n[*] AI Studio System & Subsystems Diagnostic:")
    print(f"    • Python Runtime : {status['python']}")
    print(f"    • FFmpeg Engine  : {'[OK] Available' if status['ffmpeg'] else '[!] Missing'}")
    print(f"    • DeepSeek AI    : {'[CONNECTED] (Port 9222)' if status['cdp'] else '[OFFLINE] Connect via Option [2] in START.bat'}")
    print(f"    • Ollama (Qwen)  : {'[CONNECTED] (Port 11434)' if status['ollama'] else '[OFFLINE]'}")
    print(f"    • ComfyUI Server : {'[CONNECTED] (Port 8188)' if status['comfyui'] else '[OFFLINE] Start ComfyUI to use AI diffusion'}")
    print(f"    • SD WebUI/Forge : {'[CONNECTED] (Port 7860)' if status['sd_webui'] else '[OFFLINE] Start WebUI --api to use AI diffusion'}")
    print("------------------------------------------------------------------------")
    return status


def human_approval_gate(scenes: List[Dict[str, Any]], auto_approve: bool = False) -> List[Dict[str, Any]]:
    """Phase 2: Human-in-the-Loop Approval Gate."""
    print("\n[+] GENERATED SCENE STORYBOARD:")
    for s in scenes:
        print(f"\n    [Scene #{s['scene_id']}] (~{s['estimated_seconds']:.1f}s)")
        print(f"    Visual   : {s['visual_prompt']}")
        print(f"    Voiceover: {s['voiceover']}")

    if auto_approve:
        print("\n[*] Auto-approval flag detected. Proceeding with asset generation...")
        return scenes

    while True:
        try:
            choice = input("\n[?] Approve this script storyboard? (y/n/e for manual edit): ").strip().lower()
        except EOFError:
            print("[*] Non-interactive environment detected. Auto-approving...")
            return scenes

        if choice in ["y", "yes"]:
            return scenes
        elif choice in ["e", "edit"]:
            print("[*] Entering quick manual edit mode:")
            for s in scenes:
                new_v = input(f"Edit voiceover for Scene #{s['scene_id']} (press Enter to keep): ").strip()
                if new_v:
                    s["voiceover"] = new_v
            return scenes
        elif choice in ["n", "no"]:
            print("[*] Storyboard rejected. Please enter updated topic prompt or press Ctrl+C to abort.")
            return []
        else:
            print("Please enter 'y' to approve, 'n' to regenerate, or 'e' to edit.")


def run_pipeline(
    topic: str = "computer crash and sudden blue screen",
    language: str = "hinglish",
    duration: int = 20,
    width: int = 1080,
    height: int = 1920,
    auto_approve: bool = False,
    keep_temp: bool = False,
    output_filename: str = "final_stickman_story.mp4",
) -> Path:
    """Orchestrates Phase 1 through Phase 5 in strict FCFS sequence."""
    setup_logging()
    print_banner()

    # Phase 1: Environment Check
    env_status = run_environment_check()

    # Workspace directories
    temp_dir = Path("./temp").resolve()
    temp_dir.mkdir(parents=True, exist_ok=True)
    output_dir = Path("./output").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    final_output_path = output_dir / output_filename

    # Phase 2: Script Generation Loop
    bridge = BrowserBridge()
    scenes = []
    while not scenes:
        print(f"\n[*] Requesting storyboard script for topic: '{topic}'...")
        scenes = bridge.generate_storyboard(topic=topic, language=language, duration=duration)
        scenes = human_approval_gate(scenes, auto_approve=auto_approve)
        if not scenes:
            topic = input("Enter new topic prompt: ").strip() or topic

    # Phase 3: FCFS Asset Generation Pipeline
    print("\n========================================================================")
    print("   PHASE 3: FCFS ASSET GENERATION (Voiceover & Stickman Visuals)")
    print("========================================================================")

    audio_engine = AudioEngine()
    visual_engine = VisualEngine(width=width, height=height)
    video_assembler = VideoAssembler(fps=24, width=width, height=height)

    scene_clips: List[Path] = []
    total_audio_duration = 0.0

    for item in scenes:
        s_id = item["scene_id"]
        print(f"\n[>>>] Processing Scene #{s_id}/{len(scenes)} in FCFS sequence:")

        # 1. Audio Generation (Voiceover)
        audio_path = temp_dir / f"audio_scene_{s_id}.mp3"
        exact_duration = audio_engine.synthesize_scene_audio(
            text=item["voiceover"],
            output_path=audio_path,
            language=language,
        )
        total_audio_duration += exact_duration
        print(f"      [1/3 Audio]  Generated: {audio_path.name} | Exact Duration: {exact_duration:.2f}s")

        # 2. Image Generation (Stickman Visual)
        frame_path = temp_dir / f"frame_scene_{s_id}.png"
        visual_engine.generate_scene_frame(
            visual_prompt=item["visual_prompt"],
            output_path=frame_path,
        )
        print(f"      [2/3 Visual] Generated: {frame_path.name} ({width}x{height})")

        # 3. Individual Scene Clip Render (AI-Directed Action & Word Sync)
        clip_path = temp_dir / f"clip_scene_{s_id}.mp4"
        video_assembler.render_scene_clip(
            image_path=frame_path,
            audio_path=audio_path,
            duration=exact_duration,
            output_clip_path=clip_path,
            voiceover=item.get("voiceover", ""),
            camera_action=item.get("camera_action", "zoom_in"),
            cue_word=item.get("cue_word", ""),
        )
        scene_clips.append(clip_path)
        print(f"      [3/3 Clip]   Rendered: {clip_path.name}")

    # Phase 4: Headless Video Stitching & Assembly
    print("\n========================================================================")
    print("   PHASE 4: HEADLESS VIDEO STITCHING & MULTIPLEXING")
    print("========================================================================")
    print(f"[*] Concatenating {len(scene_clips)} scene clips into unified video...")

    video_assembler.concatenate_scene_clips(scene_clips, final_output_path)
    print(f"[OK] Final assembly complete: {final_output_path.name}")

    # Phase 5: Self-Verification & Automated Testing
    print("\n========================================================================")
    print("   PHASE 5: SELF-VERIFICATION & QUALITY AUDIT")
    print("========================================================================")

    if not final_output_path.exists():
        raise FileNotFoundError(f"Verification Failed: Output video does not exist: {final_output_path}")

    file_size_bytes = final_output_path.stat().st_size
    info = probe_media(final_output_path)
    measured_duration = info.get("duration", 0.0)

    print(f"[*] Verified Output File: {final_output_path.resolve()}")
    print(f"    • File Size: {file_size_bytes / 1024:.1f} KB")
    print(f"    • Total Duration: {measured_duration:.2f}s (Audio Sum: {total_audio_duration:.2f}s)")
    print(f"    • Video Stream: {info.get('codec_video')} ({info.get('width')}x{info.get('height')}) @ {info.get('fps')} FPS")
    print(f"    • Audio Stream: {info.get('codec_audio')}")

    if file_size_bytes < 500 * 1024:
        raise ValueError(f"Verification Failed: File size is {file_size_bytes / 1024:.1f} KB, expected > 500 KB.")

    if not info.get("has_video") or not info.get("has_audio"):
        raise ValueError("Verification Failed: Missing video or audio stream in rendered output.")

    # Cleanup temp files unless requested to keep
    if not keep_temp:
        print("\n[*] Cleaning up temporary scene assets...")
        shutil.rmtree(temp_dir, ignore_errors=True)
    else:
        print(f"\n[*] Keeping temporary assets in: {temp_dir}")

    print("\n========================================================================")
    print("   PIPELINE STATUS: 100% SUCCESS — READY FOR DISTRIBUTION")
    print("========================================================================")
    print(f"Scene Count     : {len(scenes)}")
    print(f"Total Duration  : {measured_duration:.2f} seconds")
    print(f"Final MP4 Path  : {final_output_path.resolve()}")
    print("========================================================================\n")

    # Automatically launch video player on Windows if in interactive mode
    try:
        if sys.platform == "win32" and not auto_approve:
            os.startfile(str(final_output_path.resolve()))
    except Exception:
        pass

    return final_output_path


def main():
    parser = argparse.ArgumentParser(description="End-to-End Automated Stickman Video Generator")
    parser.add_argument("--topic", type=str, default="", help="Story topic prompt")
    parser.add_argument("--lang", type=str, default="hinglish", help="Language style (hinglish, english, hindi)")
    parser.add_argument("--duration", type=int, default=20, help="Target duration in seconds")
    parser.add_argument("--width", type=int, default=1080, help="Video width (default 1080)")
    parser.add_argument("--height", type=int, default=1920, help="Video height (default 1920 for Shorts/Reels)")
    parser.add_argument("--auto-approve", "-y", action="store_true", help="Bypass manual approval prompt for automated pipelines")
    parser.add_argument("--keep-temp", action="store_true", help="Preserve temporary scene audios and frames")
    parser.add_argument("--output", type=str, default="final_stickman_story.mp4", help="Output filename")

    args = parser.parse_args()

    topic = args.topic.strip()
    if not topic:
        print("\n========================================================================")
        print("   🎬 STICKFORGE AI — CREATE YOUR STICKMAN VIDEO")
        print("========================================================================")
        try:
            user_input = input("[?] Enter video topic (or press Enter for 'funny cricket match'): ").strip()
            topic = user_input if user_input else "funny cricket match"
        except (EOFError, KeyboardInterrupt):
            topic = "funny cricket match"

    run_pipeline(
        topic=topic,
        language=args.lang,
        duration=args.duration,
        width=args.width,
        height=args.height,
        auto_approve=args.auto_approve,
        keep_temp=args.keep_temp,
        output_filename=args.output,
    )


if __name__ == "__main__":
    main()
