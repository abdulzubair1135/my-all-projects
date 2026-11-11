"""
FFmpeg and Media Probe Manager for StickForge AI.
Handles safe subprocess execution, media stream inspection, and encoding progress tracking.
"""

from __future__ import annotations
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

from app.core.logging_manager import get_logger

logger = get_logger("ffmpeg_manager")


def get_ffmpeg_binary() -> str:
    """Locate verified ffmpeg executable in PATH or Python scripts."""
    p = shutil.which("ffmpeg")
    if p:
        return p
    # Check Python scripts fallback
    py_ffmpeg = Path(sys.executable).parent / "Scripts" / "ffmpeg.exe"
    if py_ffmpeg.exists():
        return str(py_ffmpeg)
    # Check imageio_ffmpeg if available
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass
    raise RuntimeError("FFmpeg binary not found on this system.")


def probe_media(file_path: Path) -> Dict[str, Any]:
    """
    Inspect media file using ffmpeg -i and extract stream properties.
    Works reliably across all Windows machines even without standalone ffprobe.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Media file does not exist: {file_path}")

    ffmpeg_bin = get_ffmpeg_binary()
    cmd = [ffmpeg_bin, "-i", str(file_path)]

    # ffmpeg -i returns exit code 1 because no output file was specified, but outputs metadata in stderr
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    stderr_out = proc.stderr

    info: Dict[str, Any] = {
        "exists": True,
        "file_size_bytes": file_path.stat().st_size,
        "has_video": False,
        "has_audio": False,
        "duration": 0.0,
        "width": 0,
        "height": 0,
        "fps": 0.0,
        "codec_video": "",
        "codec_audio": "",
    }

    # Extract Duration: 00:00:15.30
    dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", stderr_out)
    if dur_match:
        h, m, s = dur_match.groups()
        info["duration"] = round(int(h) * 3600 + int(m) * 60 + float(s), 2)

    # Check Audio Stream
    audio_match = re.search(r"Stream #\d+:\d+.*Audio:\s*(\w+)", stderr_out)
    if audio_match:
        info["has_audio"] = True
        info["codec_audio"] = audio_match.group(1)

    # Check Video Stream: Stream #0:0: Video: h264, yuv420p, 1080x1920 [SAR 1:1 DAR 9:16], 30 fps
    video_match = re.search(
        r"Stream #\d+:\d+.*Video:\s*(\w+).*, (\d+)x(\d+).*?,\s*([\d\.]+)\s*(?:fps|tbr)",
        stderr_out,
    )
    if video_match:
        info["has_video"] = True
        info["codec_video"] = video_match.group(1)
        info["width"] = int(video_match.group(2))
        info["height"] = int(video_match.group(3))
        info["fps"] = float(video_match.group(4))

    return info


def run_ffmpeg_command(
    args: List[str],
    total_duration_seconds: Optional[float] = None,
    progress_callback: Optional[Callable[[float], None]] = None,
    timeout_seconds: int = 300,
) -> None:
    """
    Executes an FFmpeg command with progress tracking and explicit timeouts.
    Never uses shell=True to guarantee protection against command injection.
    """
    ffmpeg_bin = get_ffmpeg_binary()
    full_cmd = [ffmpeg_bin, "-y"] + args

    logger.debug(f"Executing FFmpeg command: {' '.join(full_cmd[:8])}...")

    process = subprocess.Popen(
        full_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        encoding="utf-8",
        errors="replace",
    )

    time_pattern = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")

    try:
        assert process.stderr is not None
        for line in process.stderr:
            if progress_callback and total_duration_seconds and total_duration_seconds > 0:
                match = time_pattern.search(line)
                if match:
                    h, m, s = match.groups()
                    current_time = int(h) * 3600 + int(m) * 60 + float(s)
                    pct = min(99.0, (current_time / total_duration_seconds) * 100.0)
                    progress_callback(pct)

        process.wait(timeout=timeout_seconds)

        if process.returncode != 0:
            err_msg = f"FFmpeg failed with exit code {process.returncode}"
            logger.error(err_msg)
            raise RuntimeError(err_msg)

        if progress_callback:
            progress_callback(100.0)

    except subprocess.TimeoutExpired:
        process.kill()
        raise TimeoutError(f"FFmpeg operation timed out after {timeout_seconds} seconds.")
