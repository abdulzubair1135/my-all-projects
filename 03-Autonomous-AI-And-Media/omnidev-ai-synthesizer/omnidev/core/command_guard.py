import re
from pathlib import Path
from typing import Tuple, Optional
import config

class CommandGuard:
    """
    Security and Sandboxing Guard for OmniDev.
    """
    DANGEROUS_COMMANDS = [
        r"\brm\s+-rf\s+/",
        r"\bformat\b",
        r"\bdel\s+/[sS]\s+/[qQ]\s+[cC]:\\",
        r"\bshutdown\b",
        r"\breboot\b",
        r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;",
        r"\bmkfs\b",
        r"\bdd\s+if=",
        r"\bdrop\s+database\b",
        r"\btruncate\s+table\b",
        r"\bgit\s+push\s+.*--force\b"
    ]

    @classmethod
    def check_command_safety(cls, command: str) -> Tuple[bool, str]:
        cmd_clean = command.strip()
        for pattern in cls.DANGEROUS_COMMANDS:
            if re.search(pattern, cmd_clean, re.IGNORECASE):
                return False, f"Command blocked: prohibited pattern '{pattern}'"
        return True, "Safe"

    @classmethod
    def validate_path_sandbox(cls, target_path: Path, base_dir: Optional[Path] = None) -> Tuple[bool, Path, str]:
        sandbox_base = (base_dir or config.WORKSPACE_DIR).resolve()
        try:
            resolved_target = (sandbox_base / target_path).resolve()
            if not str(resolved_target).startswith(str(sandbox_base)):
                return False, resolved_target, f"Path escape blocked: '{target_path}' outside '{sandbox_base}'"
            return True, resolved_target, "Valid"
        except Exception as e:
            return False, target_path, f"Path error: {e}"

    @classmethod
    def redact_secrets(cls, text: str) -> str:
        redacted = text
        redacted = re.sub(r"(?i)(api[_-]?key|secret|password|passwd|auth[_-]?token|bearer|private[_-]?key)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{8,})['\"]?", r"\1: [REDACTED_SECRET]", redacted)
        redacted = re.sub(r"ghp_[a-zA-Z0-9]{36}", "[REDACTED_GITHUB_TOKEN]", redacted)
        redacted = re.sub(r"AIza[0-9A-Za-z-_]{35}", "[REDACTED_GOOGLE_KEY]", redacted)
        redacted = re.sub(r"sk-[a-zA-Z0-9]{20,}", "[REDACTED_OPENAI_KEY]", redacted)
        return redacted
