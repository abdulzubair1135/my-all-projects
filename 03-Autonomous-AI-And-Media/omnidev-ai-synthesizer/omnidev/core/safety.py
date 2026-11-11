import re
from typing import Tuple

class SafetyGuard:
    """
    Prevents execution of catastrophic or destructive system commands.
    """
    DANGEROUS_PATTERNS = [
        r"format\s+[a-zA-Z]:",
        r"rmdir\s+/[sS]\s+/[qQ]\s+[cC]:",
        r"del\s+/[sS]\s+/[qQ]\s+[cC]:\\windows",
        r"rm\s+-rf\s+/[^a-zA-Z0-9]*$",
        r"drop\s+database",
        r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;",  # fork bomb
    ]

    @classmethod
    def check_command(cls, command: str) -> Tuple[bool, str]:
        cmd_lower = command.lower().strip()
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, cmd_lower):
                return False, f"Command blocked by Safety Guard: contains dangerous pattern '{pattern}'"
        return True, "Safe"
