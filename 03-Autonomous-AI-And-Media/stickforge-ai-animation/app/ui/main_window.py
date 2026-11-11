"""
Main Application Window for StickForge AI.
Container with sidebar navigation, view stack, project lifecycle management, and status bar.
"""

from __future__ import annotations
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QPushButton,
    QLabel,
    QFrame,
    QStatusBar,
    QButtonGroup,
    QMessageBox,
)

from app.ui.theme import DARK_THEME_QSS
from app.ui.dashboard import DashboardView
from app.ui.project_wizard import ProjectWizardDialog
from app.ui.story_studio import StoryStudioView
from app.ui.storyboard_editor import StoryboardEditorView
from app.ui.character_studio import CharacterStudioView
from app.ui.animation_editor import AnimationEditorView
from app.ui.voice_studio import VoiceStudioView
from app.ui.timeline_editor import TimelineEditorView
from app.ui.publishing_hub import PublishingHubView
from app.ui.diagnostics import DiagnosticsView
from app.ui.settings import SettingsView

from app.storage.project_manager import get_project_manager, ProjectData
from app.core.logging_manager import get_logger
from app.core.event_bus import get_event_bus

logger = get_logger("main_window")


class MainWindow(QMainWindow):
    """StickForge AI Primary Desktop Window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("StickForge AI — Stickman Video Studio")
        self.resize(1340, 880)
        self.setMinimumSize(1024, 680)
        self.setStyleSheet(DARK_THEME_QSS)

        self.project_manager = get_project_manager()
        self.active_project: Optional[ProjectData] = None
        self.views = {}

        self._init_ui()
        self._subscribe_events()

    def _init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        root_layout = QHBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Left Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("SidebarFrame")
        s_layout = QVBoxLayout(sidebar)
        s_layout.setContentsMargins(0, 0, 0, 16)
        s_layout.setSpacing(4)

        lbl_logo = QLabel("STICKFORGE AI")
        lbl_logo.setObjectName("SidebarHeader")
        s_layout.addWidget(lbl_logo)

        self.nav_btn_group = QButtonGroup(self)
        self.nav_btn_group.setExclusive(True)

        nav_items = [
            ("dashboard", "Dashboard"),
            ("story", "Story Studio"),
            ("storyboard", "Storyboard Editor"),
            ("character", "Character Studio"),
            ("animation", "Animation Editor"),
            ("voice", "Voice Studio"),
            ("timeline", "Timeline & Preview"),
            ("publishing", "Publishing Hub"),
            ("settings", "Settings"),
            ("diagnostics", "Diagnostics"),
        ]

        self.nav_buttons = {}
        for index, (key, title) in enumerate(nav_items):
            btn = QPushButton(title)
            btn.setProperty("class", "nav-btn")
            btn.setCheckable(True)
            self.nav_btn_group.addButton(btn, index)
            s_layout.addWidget(btn)
            self.nav_buttons[key] = btn
            btn.clicked.connect(lambda checked=False, k=key: self.navigate_to(k))

        s_layout.addStretch()

        # Active Project Indicator in sidebar bottom
        self.lbl_active_proj = QLabel("No Project Loaded")
        self.lbl_active_proj.setStyleSheet(
            "color: #64748B; font-size: 11px; padding: 10px 16px; border-top: 1px solid #27272A;"
        )
        s_layout.addWidget(self.lbl_active_proj)

        root_layout.addWidget(sidebar)

        # 2. Main Content Stack
        self.content_stack = QStackedWidget()
        self.content_stack.setObjectName("ContentArea")
        root_layout.addWidget(self.content_stack)

        # Setup Views
        self._setup_views()

        # 3. Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("StickForge AI ready. Ready for creation.")

        # Default to Dashboard
        self.navigate_to("dashboard")

    def _setup_views(self) -> None:
        # Dashboard
        self.dashboard_view = DashboardView()
        self.dashboard_view.open_project_requested.connect(self.load_project_by_id)
        self.dashboard_view.create_project_requested.connect(self._create_new_project_dialog)
        self._register_view("dashboard", self.dashboard_view)

        # Story Studio
        self.story_view = StoryStudioView()
        self.story_view.storyboard_ready.connect(lambda: self.navigate_to("storyboard"))

        def _on_story_render_requested():
            self.navigate_to("timeline")
            if hasattr(self.timeline_view, "_start_render"):
                self.timeline_view._start_render()

        self.story_view.render_ready.connect(_on_story_render_requested)
        self._register_view("story", self.story_view)

        # Storyboard Editor
        self.storyboard_view = StoryboardEditorView()
        self.storyboard_view.render_requested.connect(lambda: self.navigate_to("timeline"))
        self._register_view("storyboard", self.storyboard_view)

        # Character Studio
        self.character_view = CharacterStudioView()
        self._register_view("character", self.character_view)

        # Animation Editor
        self.animation_view = AnimationEditorView()
        self._register_view("animation", self.animation_view)

        # Voice Studio
        self.voice_view = VoiceStudioView()
        self._register_view("voice", self.voice_view)

        # Timeline Editor
        self.timeline_view = TimelineEditorView()
        self._register_view("timeline", self.timeline_view)

        # Publishing Hub
        self.publishing_view = PublishingHubView()
        self._register_view("publishing", self.publishing_view)

        # Settings & Diagnostics
        self.settings_view = SettingsView()
        self._register_view("settings", self.settings_view)

        self.diagnostics_view = DiagnosticsView()
        self._register_view("diagnostics", self.diagnostics_view)

    def _register_view(self, key: str, widget: QWidget) -> None:
        self.views[key] = widget
        self.content_stack.addWidget(widget)

    def navigate_to(self, key: str) -> None:
        if key in self.views:
            # Sync active project with view before switching
            if self.active_project and hasattr(self.views[key], "load_project"):
                self.views[key].load_project(self.active_project)

            self.content_stack.setCurrentWidget(self.views[key])
            if key in self.nav_buttons:
                self.nav_buttons[key].setChecked(True)
            self.status_bar.showMessage(f"Navigated to {key.replace('_', ' ').capitalize()}")

    def set_active_project(self, project: ProjectData) -> None:
        self.active_project = project
        self.lbl_active_proj.setText(f"Project: {project.name}")
        self.lbl_active_proj.setStyleSheet(
            "color: #38BDF8; font-size: 11px; padding: 10px 16px; font-weight: 600;"
        )
        self.setWindowTitle(f"StickForge AI — [{project.name}]")
        self.status_bar.showMessage(f"Loaded project: {project.name}")

        # Propagate to loaded views
        for view in self.views.values():
            if hasattr(view, "load_project"):
                view.load_project(project)

    def load_project_by_id(self, project_id: str) -> None:
        proj = self.project_manager.load_project(project_id)
        if proj:
            self.set_active_project(proj)
            self.navigate_to("story")

    def _create_new_project_dialog(self) -> None:
        dialog = ProjectWizardDialog(self)
        dialog.project_created.connect(self.load_project_by_id)
        dialog.exec()
        self.dashboard_view.refresh()

    def _subscribe_events(self) -> None:
        bus = get_event_bus()
        bus.subscribe(
            "task_state_changed",
            lambda job_id, new_state, progress, error, **kwargs: self.status_bar.showMessage(
                f"Task {job_id}: {new_state} ({progress:.1f}%)"
            ),
        )

    def closeEvent(self, event) -> None:
        if hasattr(self, "diagnostics_view"):
            self.diagnostics_view.stop_timer()
        event.accept()
