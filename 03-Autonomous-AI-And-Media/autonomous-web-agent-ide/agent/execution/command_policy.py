import shlex
import re
from typing import Tuple, List, Optional
from enum import Enum

class CommandCategory(str, Enum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    DANGEROUS = "DANGEROUS"
    BLOCKED = "BLOCKED"

# Explicit blocked binaries/commands
BLOCKED_EXECUTABLES = {
    "format", "diskpart", "mkfs", "dd", "fdisk",
    "shutdown", "reboot", "poweroff", "init",
    "sudo", "su", "runas", "takeown", "icacls",
    "reg", "regedit", "powershell_ise"
}

# Blocked subcommands or arguments
BLOCKED_PATTERNS = [
    re.compile(r"rm\s+-rf\s+(?:/|/\*|~|C:\\)", re.IGNORECASE),
    re.compile(r"del\s+/[a-z\s]*\s+[C-Z]:\\", re.IGNORECASE),
    re.compile(r"powershell.*-ExecutionPolicy\s+Bypass", re.IGNORECASE),
    re.compile(r"(?:cat|type|more|less)\s+.*(?:\.ssh|\.aws|\.gnupg|credentials|id_rsa)", re.IGNORECASE),
    re.compile(r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:", re.IGNORECASE), # Fork bomb
]

SAFE_BINARIES = {
    "npm", "npx", "yarn", "pnpm", "node",
    "python", "python3", "pytest", "pip",
    "git", "echo", "dir", "ls", "cat", "mkdir", "touch",
    "cargo", "go", "tsc", "vite"
}

CAUTION_BINARIES = {
    "curl", "wget", "docker", "docker-compose",
    "ssh", "scp", "nc", "netstat", "kill", "taskkill"
}

class CommandPolicyEngine:
    @classmethod
    def evaluate(cls, command_str: str) -> Tuple[CommandCategory, str]:
        """
        Evaluates a command string and returns its security category and reasoning.
        """
        if not command_str or not command_str.strip():
            return CommandCategory.BLOCKED, "Empty command is not allowed"

        cmd_clean = command_str.strip()

        # 1. Check blocked regex patterns
        for pattern in BLOCKED_PATTERNS:
            if pattern.search(cmd_clean):
                return CommandCategory.BLOCKED, f"Command contains forbidden destructive or security-bypassing pattern: {pattern.pattern}"

        # 2. Check for shell command chaining/injection operators if not quoted
        # Operators: &&, ||, ;, |, ``, $()
        has_chaining = bool(re.search(r"(?:&&|\|\||;|`|\$\(|\b\s*\|\s*\b)", cmd_clean))

        # 3. Parse executable name and tokens
        try:
            tokens = shlex.split(cmd_clean, posix=False)
        except Exception:
            tokens = cmd_clean.split()

        if not tokens:
            return CommandCategory.BLOCKED, "Could not parse command tokens"

        exe = tokens[0].lower().replace(".exe", "").replace(".cmd", "").replace(".bat", "")

        # Check blocked executables
        if exe in BLOCKED_EXECUTABLES:
            return CommandCategory.BLOCKED, f"Executable '{exe}' is strictly blocked for security"

        # If chaining is used, elevate to CAUTION or DANGEROUS unless safe
        if has_chaining:
            return CommandCategory.CAUTION, "Command contains chaining operators (&&, ||, ;, |)"

        # Check safe binaries
        if exe in SAFE_BINARIES:
            # Check for suspicious subcommands
            if exe == "npm" and len(tokens) > 1 and tokens[1] in ["publish", "unpublish"]:
                return CommandCategory.DANGEROUS, f"NPM operation '{tokens[1]}' is dangerous"
            if exe == "git" and len(tokens) > 1 and tokens[1] in ["push", "reset", "clean"]:
                return CommandCategory.CAUTION, f"Git '{tokens[1]}' operation requires caution"
            return CommandCategory.SAFE, f"Command '{exe}' is in safe allowlist"

        # Check caution binaries
        if exe in CAUTION_BINARIES:
            return CommandCategory.CAUTION, f"Command '{exe}' involves network or process management"

        # Default for unknown commands
        return CommandCategory.CAUTION, f"Executable '{exe}' is not recognized in default safe list"
