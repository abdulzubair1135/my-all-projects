"""
AURA Logging System.
Provides structured logging for all AURA components with Windows Unicode handling.
"""

import logging
import sys
import io
from pathlib import Path
from typing import Optional
from config import config

def setup_logger(name: str = "AURA", log_file: Optional[Path] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    log_level = getattr(logging, config.log_level.upper(), logging.INFO)
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Safe Console Handler for Windows (UTF-8 encoding wrapper)
    try:
        if sys.platform == "win32" and hasattr(sys.stdout, "buffer"):
            safe_stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            console_handler = logging.StreamHandler(safe_stdout)
        else:
            console_handler = logging.StreamHandler(sys.stdout)
    except Exception:
        console_handler = logging.StreamHandler(sys.stdout)

    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)

    # File Handler
    if log_file is None:
        log_file = config.storage.logs_dir / "aura.log"

    try:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to setup file handler for logger {name}: {e}", file=sys.stderr)

    return logger

logger = setup_logger("AURA")
