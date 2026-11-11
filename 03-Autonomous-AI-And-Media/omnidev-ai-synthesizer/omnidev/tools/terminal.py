import asyncio
import subprocess
import time
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class CommandResult:
    command: str
    stdout: str
    stderr: str
    exit_code: int
    duration: float

    @property
    def is_success(self) -> bool:
        return self.exit_code == 0

def decode_output(data: bytes) -> str:
    if not data:
        return ""
    for enc in ("utf-8", "cp1252", "latin-1", "gbk", "shift_jis"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")

def run_terminal_command_sync(
    command: str,
    cwd: Optional[str | Path] = None,
    timeout: int = 120,
    shell: bool = True
) -> CommandResult:
    """
    Executes a shell command synchronously and captures stdout, stderr, and exit code.
    """
    start_time = time.time()
    work_dir = str(cwd) if cwd else os.getcwd()

    try:
        process = subprocess.Popen(
            command,
            cwd=work_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=shell,
        )
        stdout_bytes, stderr_bytes = process.communicate(timeout=timeout)
        duration = time.time() - start_time

        return CommandResult(
            command=command,
            stdout=decode_output(stdout_bytes),
            stderr=decode_output(stderr_bytes),
            exit_code=process.returncode,
            duration=duration,
        )
    except subprocess.TimeoutExpired:
        process.kill()
        stdout_bytes, stderr_bytes = process.communicate()
        duration = time.time() - start_time
        return CommandResult(
            command=command,
            stdout=decode_output(stdout_bytes),
            stderr=f"Command timed out after {timeout} seconds.\n" + decode_output(stderr_bytes),
            exit_code=-1,
            duration=duration,
        )
    except Exception as e:
        duration = time.time() - start_time
        return CommandResult(
            command=command,
            stdout="",
            stderr=f"Failed to execute command: {str(e)}",
            exit_code=-1,
            duration=duration,
        )

async def run_terminal_command(
    command: str,
    cwd: Optional[str | Path] = None,
    timeout: int = 120,
    shell: bool = True
) -> CommandResult:
    """
    Async wrapper for executing a terminal command.
    """
    return await asyncio.to_thread(run_terminal_command_sync, command, cwd, timeout, shell)
