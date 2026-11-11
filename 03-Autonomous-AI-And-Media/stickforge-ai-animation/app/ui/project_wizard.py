"""
Project Wizard for StickForge AI.
Guided dialog for configuring new stickman animation video projects.
"""

from __future__ import annotations
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QPushButton,
    QFormLayout,
    QGroupBox,
)

from app.storage.project_manager import get_project_manager, ProjectData


class ProjectWizardDialog(QDialog):
    """Modal wizard for creating new projects."""

    project_created = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Animation Project — StickForge AI")
        self.resize(520, 480)
        self.project_manager = get_project_manager()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("New Project Wizard")
        title.setStyleSheet("font-size: 18px; font-weight: 700; color: #38BDF8;")
        layout.addWidget(title)

        grp = QGroupBox("Project Settings")
        form = QFormLayout(grp)

        self.edit_name = QLineEdit("My Stickman Adventure")
        form.addRow("Project Name:", self.edit_name)

        self.edit_topic = QLineEdit("Friendship and Determination")
        self.edit_topic.setPlaceholderText("e.g. Marathon race, Haunted exam hall, Cricket match")
        form.addRow("Story Topic / Idea:", self.edit_topic)

        self.cb_genre = QComboBox()
        self.cb_genre.addItems([
            "comedy", "suspense", "horror", "mystery",
            "motivational", "educational", "action", "life_lessons"
        ])
        form.addRow("Genre:", self.cb_genre)

        self.cb_language = QComboBox()
        self.cb_language.addItems(["hinglish", "english", "hindi"])
        form.addRow("Language:", self.cb_language)

        self.cb_aspect = QComboBox()
        self.cb_aspect.addItems(["9:16 (Shorts & Reels)", "16:9 (YouTube Landscape)"])
        form.addRow("Aspect Ratio:", self.cb_aspect)

        self.spin_duration = QSpinBox()
        self.spin_duration.setRange(5, 180)
        self.spin_duration.setValue(30)
        self.spin_duration.setSuffix(" seconds")
        form.addRow("Target Duration:", self.spin_duration)

        self.spin_chars = QSpinBox()
        self.spin_chars.setRange(1, 4)
        self.spin_chars.setValue(1)
        form.addRow("Number of Characters:", self.spin_chars)

        layout.addWidget(grp)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setProperty("class", "btn-secondary")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_create = QPushButton("Create Project")
        btn_create.setProperty("class", "btn-primary")
        btn_create.clicked.connect(self._create_project)
        btn_layout.addWidget(btn_create)

        layout.addLayout(btn_layout)

    def _create_project(self) -> None:
        name = self.edit_name.text().strip() or "Untitled Animation"
        topic = self.edit_topic.text().strip()
        genre = self.cb_genre.currentText()
        language = self.cb_language.currentText()
        aspect = "9:16" if "9:16" in self.cb_aspect.currentText() else "16:9"
        duration = float(self.spin_duration.value())

        proj = self.project_manager.create_project(
            name=name,
            topic=topic,
            genre=genre,
            language=language,
            duration_target=duration,
            aspect_ratio=aspect,
        )
        self.project_created.emit(proj.id)
        self.accept()
