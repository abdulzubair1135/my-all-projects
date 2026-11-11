"""
Dashboard View for StickForge AI.
Displays quick actions, recent projects, system health, and task status.
"""

from __future__ import annotations
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QGridLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

from app.storage.repositories import ProjectRepository, RenderJobRepository
from app.core.resource_manager import get_resource_manager


class DashboardView(QWidget):
    """Studio home dashboard."""

    create_project_requested = Signal()
    open_project_requested = Signal(str)
    navigate_requested = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.project_repo = ProjectRepository()
        self.render_repo = RenderJobRepository()
        self.resource_mgr = get_resource_manager()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header with Title and Create Project Action
        header_layout = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: 700; color: #F8FAFC;")
        subtitle = QLabel("Welcome to StickForge AI — Stickman Video Creation Studio")
        subtitle.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header_layout.addLayout(title_box)

        header_layout.addStretch()

        btn_new = QPushButton("+ Create Project")
        btn_new.setProperty("class", "btn-primary")
        btn_new.setMinimumHeight(40)
        btn_new.clicked.connect(self.create_project_requested.emit)
        header_layout.addWidget(btn_new)

        layout.addLayout(header_layout)

        # Status Cards Grid
        grid = QGridLayout()
        grid.setSpacing(16)

        # Card 1: Browser & DeepSeek Status
        self.card_browser = self._create_card(
            "DeepSeek Browser", "Ready / Connected", "Dedicated profile initialized."
        )
        grid.addWidget(self.card_browser, 0, 0)

        # Card 2: AI Pipeline
        self.card_ai = self._create_card(
            "AI Director", "Idle", "Awaiting story instructions."
        )
        grid.addWidget(self.card_ai, 0, 1)

        # Card 3: System Resources
        stats = self.resource_mgr.get_system_stats()
        self.card_sys = self._create_card(
            "System & GPU",
            f"RAM: {stats['ram_available_gb']} GB Free",
            f"GPU: {stats['gpu']}",
        )
        grid.addWidget(self.card_sys, 0, 2)

        layout.addLayout(grid)

        # Recent Projects Section
        recents_header = QHBoxLayout()
        recents_title = QLabel("Recent Projects")
        recents_title.setStyleSheet("font-size: 16px; font-weight: 600; color: #F1F5F9;")
        recents_header.addWidget(recents_title)
        recents_header.addStretch()
        layout.addLayout(recents_header)

        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(6)
        self.projects_table.setHorizontalHeaderLabels(
            ["Title", "Topic", "Genre", "Duration", "Last Updated", "Actions"]
        )
        self.projects_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.projects_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.projects_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.projects_table.setStyleSheet("background-color: #18191E; border: 1px solid #2D3039;")
        layout.addWidget(self.projects_table)

        self.refresh()

    def _create_card(self, title_text: str, value_text: str, detail_text: str) -> QFrame:
        card = QFrame()
        card.setProperty("class", "card")
        c_layout = QVBoxLayout(card)
        c_layout.setSpacing(4)

        lbl_title = QLabel(title_text)
        lbl_title.setProperty("class", "card-subtitle")
        lbl_val = QLabel(value_text)
        lbl_val.setStyleSheet("font-size: 18px; font-weight: 700; color: #38BDF8;")
        lbl_detail = QLabel(detail_text)
        lbl_detail.setProperty("class", "card-subtitle")

        c_layout.addWidget(lbl_title)
        c_layout.addWidget(lbl_val)
        c_layout.addWidget(lbl_detail)
        return card

    def refresh(self) -> None:
        """Reload recent projects from SQLite."""
        projects = self.project_repo.list_all(limit=10)
        self.projects_table.setRowCount(len(projects))
        for row, proj in enumerate(projects):
            self.projects_table.setItem(row, 0, QTableWidgetItem(proj.get("name", "")))
            self.projects_table.setItem(row, 1, QTableWidgetItem(proj.get("topic", "") or "—"))
            self.projects_table.setItem(row, 2, QTableWidgetItem(proj.get("genre", "comedy")))
            self.projects_table.setItem(
                row, 3, QTableWidgetItem(f"{proj.get('duration_target', 30)}s")
            )
            self.projects_table.setItem(row, 4, QTableWidgetItem(str(proj.get("updated_at", ""))))

            btn_open = QPushButton("Open")
            btn_open.setProperty("class", "btn-secondary")
            proj_id = proj.get("id")
            btn_open.clicked.connect(lambda checked=False, pid=proj_id: self.open_project_requested.emit(pid))
            self.projects_table.setCellWidget(row, 5, btn_open)
