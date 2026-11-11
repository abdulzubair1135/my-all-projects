"""
UI tests for StickForge AI Main Window and views.
"""

import pytest
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_main_window_initialization(qapp):
    window = MainWindow()
    assert window.windowTitle().startswith("StickForge AI")
    assert "dashboard" in window.views
    assert "settings" in window.views
    assert "diagnostics" in window.views

    # Test navigation
    window.navigate_to("settings")
    assert window.content_stack.currentWidget() == window.views["settings"]

    window.navigate_to("dashboard")
    assert window.content_stack.currentWidget() == window.views["dashboard"]

    window.close()
