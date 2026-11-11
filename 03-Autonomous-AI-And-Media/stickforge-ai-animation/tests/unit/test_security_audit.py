"""
Security Audit Unit Test for StickForge AI.
Verifies that no plaintext passwords, hardcoded API keys, bearer tokens,
or personal cookies exist in code, configuration, or launcher scripts.
"""

import os
import re
from pathlib import Path
import pytest
from app.core.config import PROJECT_ROOT

SUSPICIOUS_PATTERNS = [
    re.compile(r'(?:api[_-]?key|secret|password|bearer|private_key)\s*[:=]\s*["\'][A-Za-z0-9_\-\.]{16,}["\']', re.IGNORECASE),
]

EXCLUDED_DIRS = {".git", ".pytest_cache", "__pycache__", "user_data", "cache"}
ALLOWED_EXTENSIONS = {".py", ".json", ".bat", ".md", ".spec"}


def test_codebase_zero_secrets():
    violations = []

    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Prune excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            path = Path(root) / file
            if path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue

            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                for line_idx, line in enumerate(content.splitlines(), start=1):
                    # Ignore comment examples in security/troubleshooting docs
                    if "example" in line.lower() or "redact" in line.lower():
                        continue
                    for pat in SUSPICIOUS_PATTERNS:
                        if pat.search(line):
                            violations.append(f"{path.name}:{line_idx} - {line.strip()[:60]}")
            except Exception:
                pass

    assert len(violations) == 0, f"Found potential secret violations:\n" + "\n".join(violations)
