"""
Logging manager for StickForge AI.
Features:
- Structured logging with timestamps, module names, job IDs.
- Automatic redaction of sensitive credentials (API keys, Bearer tokens, cookies).
- Rotating file handler in logs/ directory.
- Thread-safe memory buffer for UI Diagnostics viewer.
"""

from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
import os
import re
from pathlib import Path
from typing import List, Optional
from collections import deque
from app.core.config import LOGS_DIR


# Patterns to redact
REDACTION_PATTERNS = [
    re.compile(r"(api[_-]?key[\s:=]+)(['\"]?[\w\-]{8,}['\"]?)", re.IGNORECASE),
    re.compile(r"(bearer\s+)([\w\-_\.]{12,})", re.IGNORECASE),
    re.compile(r"(token[\s:=]+)(['\"]?[\w\-]{8,}['\"]?)", re.IGNORECASE),
    re.compile(r"(password[\s:=]+)(['\"]?[^'\"\s]{4,}['\"]?)", re.IGNORECASE),
    re.compile(r"(secret[\s:=]+)(['\"]?[\w\-]{8,}['\"]?)", re.IGNORECASE),
    re.compile(r"(cookie[\s:=]+)(['\"]?[^'\"\n]+['\"]?)", re.IGNORECASE),
]


class RedactingFormatter(logging.Formatter):
    """Custom formatter that masks sensitive strings."""

    def format(self, record: logging.LogRecord) -> str:
        orig = super().format(record)
        msg = orig
        for pattern in REDACTION_PATTERNS:
            msg = pattern.sub(r"\1[REDACTED]", msg)
        return msg


class InMemoryLogHandler(logging.Handler):
    """Stores the latest N logs for instant UI display."""

    def __init__(self, capacity: int = 500):
        super().__init__()
        self.buffer: deque[str] = deque(maxlen=capacity)

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.buffer.append(msg)
        except Exception:
            self.handleError(record)

    def get_logs(self) -> List[str]:
        return list(self.buffer)

    def clear(self) -> None:
        self.buffer.clear()


# Global memory handler instance
_memory_handler: Optional[InMemoryLogHandler] = None
_logger_initialized: bool = False


def setup_logging(level: int = logging.INFO) -> None:
    """Initialize application logging."""
    global _memory_handler, _logger_initialized
    if _logger_initialized:
        return

    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOGS_DIR / "stickforge.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    formatter = RedactingFormatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1. Rotating file handler (max 10MB per file, 5 backups)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    root_logger.addHandler(file_handler)

    # 2. Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    root_logger.addHandler(console_handler)

    # 3. In-memory buffer for UI
    _memory_handler = InMemoryLogHandler(capacity=1000)
    _memory_handler.setFormatter(formatter)
    _memory_handler.setLevel(level)
    root_logger.addHandler(_memory_handler)

    # 4. Silence noisy third-party libraries from polluting diagnostic logs
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)
    logging.getLogger("comtypes").setLevel(logging.ERROR)
    logging.getLogger("comtypes.client._generate").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    _logger_initialized = True
    logging.getLogger("stickforge").info("StickForge AI logging system initialized.")


def get_logger(name: str) -> logging.Logger:
    """Convenience getter for namespaced loggers."""
    if not _logger_initialized:
        setup_logging()
    return logging.getLogger(f"stickforge.{name}")


def get_recent_logs() -> List[str]:
    """Retrieve recent logs from the in-memory ring buffer."""
    if _memory_handler:
        return _memory_handler.get_logs()
    return []


def clear_all_logs() -> None:
    """Clear memory ring buffer and truncate log file."""
    if _memory_handler:
        _memory_handler.clear()
    log_file = LOGS_DIR / "stickforge.log"
    if log_file.exists():
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("")
        except Exception:
            pass
