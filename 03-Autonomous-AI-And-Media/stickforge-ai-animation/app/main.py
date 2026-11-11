"""
Main entry point for StickForge AI desktop application.
"""

from __future__ import annotations
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

# Ensure project root is in sys.path
PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from app.core.logging_manager import setup_logging, get_logger
from app.bootstrap import run_preflight_checks
from app.ui.main_window import MainWindow

logger = get_logger("main")


def main() -> int:
    setup_logging()
    logger.info("Initializing StickForge AI...")

    # Run non-blocking preflight verification
    preflight = run_preflight_checks()
    for component, info in preflight.items():
        if info.get("status") == "ERROR":
            logger.error(f"Preflight error in {component}: {info.get('message')}")

    # Set DPI awareness for high-resolution displays
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("StickForge AI")
    app.setOrganizationName("StickForge")

    window = MainWindow()
    window.show()

    logger.info("StickForge AI main window displayed.")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
