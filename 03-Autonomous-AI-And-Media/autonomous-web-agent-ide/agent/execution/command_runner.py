import asyncio
import time
import os
import sys
import subprocess
from typing import Dict, Any, Optional, Callable

MAX_OUTPUT_BYTES = 100 * 1024  # 100 KB limit to prevent OOM/flooding

class CommandResult:
    def __init__(self, exit_code: int, stdout: str, stderr: str, duration_ms: int):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.duration_ms = duration_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms
        }

def _run_subprocess_sync(command: str, cwd: str, timeout: int, env: Dict[str, str]) -> CommandResult:
    start_time = time.time()
    # Force UTF-8 environment
    merged_env = os.environ.copy()
    merged_env["PYTHONIOENCODING"] = "utf-8"
    merged_env["LANG"] = "en_US.UTF-8"
    if env:
        merged_env.update(env)

    try:
        proc = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            env=merged_env
        )
        duration_ms = int((time.time() - start_time) * 1000)
        return CommandResult(
            exit_code=proc.returncode,
            stdout=(proc.stdout or "")[:MAX_OUTPUT_BYTES],
            stderr=(proc.stderr or "")[:MAX_OUTPUT_BYTES],
            duration_ms=duration_ms
        )
    except subprocess.TimeoutExpired as e:
        duration_ms = int((time.time() - start_time) * 1000)
        stdout_text = (e.stdout.decode("utf-8", errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or ""))
        stderr_text = (e.stderr.decode("utf-8", errors="replace") if isinstance(e.stderr, bytes) else (e.stderr or ""))
        return CommandResult(
            exit_code=124,
            stdout=stdout_text[:MAX_OUTPUT_BYTES],
            stderr=f"{stderr_text}\n[Command timed out after {timeout} seconds]"[:MAX_OUTPUT_BYTES],
            duration_ms=duration_ms
        )
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return CommandResult(
            exit_code=1,
            stdout="",
            stderr=str(e),
            duration_ms=duration_ms
        )

class CommandRunner:
    @staticmethod
    async def run(
        command: str,
        cwd: str,
        timeout: int = 120,
        env: Optional[Dict[str, str]] = None,
        on_stdout: Optional[Callable[[str], None]] = None,
        on_stderr: Optional[Callable[[str], None]] = None
    ) -> CommandResult:
        merged_env = os.environ.copy()
        merged_env["PYTHONIOENCODING"] = "utf-8"
        if env:
            merged_env.update(env)

        result = await asyncio.to_thread(_run_subprocess_sync, command, cwd, timeout, merged_env)
        if on_stdout and result.stdout:
            on_stdout(result.stdout)
        if on_stderr and result.stderr:
            on_stderr(result.stderr)
        return result
