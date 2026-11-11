"""
AUTO YT GENERATOR — Structured Logging Module.

Provides standard JSON/colored logging with rotation and module context.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(
    name: str = "auto_yt",
    log_dir: str = "logs",
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
) -> logging.Logger:
    """Configures and returns a logger instance with console and rotating file output."""
    logger = logging.getLogger(name)
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    # Prevent duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    # Ensure log directory exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_file = Path(log_dir) / "application.log"

    # Formatter
    file_format = logging.Formatter(
        '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "module": "%(module)s", "line": %(lineno)d, "message": "%(message)s"}'
    )
    console_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)-7s] (%(module)s) %(message)s",
        datefmt="%H:%M:%S",
    )

    # File Handler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(file_format)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    return logger


# Default logger instance
logger = setup_logger()
