"""
Storyboard Editor View for StickForge AI.
Interactive card-based editor for timed scenes, character actions, backgrounds, and camera movements.
"""

from __future__ import annotations
from typing import Optional, List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QComboBox,
    QDoubleSpinBox,
    QLineEdit,
    QMessageBox,
)

from app.storage.project_manager import ProjectData, SceneModel, SceneAction, CameraModel, get_project_manager
from app.ai.prompt_templates import SUPPORTED_ACTIONS, SUPPORTED_BACKGROUNDS
from app.ai.schema_validator import GeneratedStoryboard, SceneSpec, ActionSpec, CameraSpec, CharacterDef
from app.story.continuity_checker import check_continuity


class SceneCard(QFrame):
    """Visual card representing a single storyboard scene."""

    delete_requested = Signal(str)
    changed = Signal()

    def __init__(self, scene: SceneModel, parent=None):
        super().__init__(parent)
        self.scene = scene
        self.setProperty("class", "card")
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # Header: Scene # and Delete button
        hdr = QHBoxLayout()
        self.lbl_title = QLabel(f"Scene #{self.scene.sequence_order}: {self.scene.id}")
        self.lbl_title.setStyleSheet("font-weight: 700; color: #38BDF8;")
        hdr.addWidget(self.lbl_title)
        hdr.addStretch()

        btn_del = QPushButton("✕")
        btn_del.setFixedSize(26, 26)
        btn_del.setProperty("class", "btn-secondary")
        btn_del.clicked.connect(lambda: self.delete_requested.emit(self.scene.id))
        hdr.addWidget(btn_del)
        layout.addLayout(hdr)

        # Controls Row 1: Duration, Background, Action
        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Duration (s):"))
        self.spin_dur = QDoubleSpinBox()
        self.spin_dur.setRange(1.0, 60.0)
        self.spin_dur.setValue(self.scene.duration)
        self.spin_dur.valueChanged.connect(self._on_dur_changed)
        r1.addWidget(self.spin_dur)

        r1.addWidget(QLabel("Background:"))
        self.cb_bg = QComboBox()
        self.cb_bg.addItems(SUPPORTED_BACKGROUNDS)
        self.cb_bg.setCurrentText(self.scene.background)
        self.cb_bg.currentTextChanged.connect(self._on_bg_changed)
        r1.addWidget(self.cb_bg)

        r1.addWidget(QLabel("Action:"))
        self.cb_act = QComboBox()
        self.cb_act.addItems(SUPPORTED_ACTIONS)
        curr_act = self.scene.actions[0].action if self.scene.actions else "stand"
        self.cb_act.setCurrentText(curr_act)
        self.cb_act.currentTextChanged.connect(self._on_act_changed)
        r1.addWidget(self.cb_act)

        layout.addLayout(r1)

        # Controls Row 2: Camera Shot & Movement
        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Camera Shot:"))
        self.cb_shot = QComboBox()
        self.cb_shot.addItems(["medium", "wide", "close_up"])
        self.cb_shot.setCurrentText(self.scene.camera.shot)
        self.cb_shot.currentTextChanged.connect(self._on_camera_changed)
        r2.addWidget(self.cb_shot)

        r2.addWidget(QLabel("Movement:"))
        self.cb_move = QComboBox()
        self.cb_move.addItems(["static", "zoom_in", "zoom_out", "pan_left", "pan_right"])
        self.cb_move.setCurrentText(self.scene.camera.movement)
        self.cb_move.currentTextChanged.connect(self._on_camera_changed)
        r2.addWidget(self.cb_move)

        layout.addLayout(r2)

        # Controls Row 3: Narration Line
        r3 = QHBoxLayout()
        r3.addWidget(QLabel("Narration:"))
        self.edit_narr = QLineEdit(self.scene.narration)
        self.edit_narr.textChanged.connect(self._on_narr_changed)
        r3.addWidget(self.edit_narr)
        layout.addLayout(r3)

    def _on_dur_changed(self, val: float) -> None:
        self.scene.duration = val
        self.changed.emit()

    def _on_bg_changed(self, val: str) -> None:
        self.scene.background = val
        self.changed.emit()

    def _on_act_changed(self, val: str) -> None:
        if not self.scene.actions:
            self.scene.actions = [SceneAction(character_id="char_1", action=val)]
        else:
            self.scene.actions[0].action = val
        self.changed.emit()

    def _on_camera_changed(self) -> None:
        self.scene.camera.shot = self.cb_shot.currentText()
        self.scene.camera.movement = self.cb_move.currentText()
        self.changed.emit()

    def _on_narr_changed(self, text: str) -> None:
        self.scene.narration = text
        self.changed.emit()


class StoryboardEditorView(QWidget):
    """Main Storyboard editor with scrollable scene cards."""

    render_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project: Optional[ProjectData] = None
        self.cards: List[SceneCard] = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Storyboard & Scene Choreographer")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #F8FAFC;")
        sub = QLabel("Configure scene durations, stickman actions, backgrounds, and camera movements.")
        sub.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(title)
        title_box.addWidget(sub)
        hdr.addLayout(title_box)
        hdr.addStretch()

        self.btn_validate = QPushButton("Check Continuity")
        self.btn_validate.setProperty("class", "btn-secondary")
        self.btn_validate.clicked.connect(self._validate_continuity)
        hdr.addWidget(self.btn_validate)

        btn_add = QPushButton("+ Add Scene")
        btn_add.setProperty("class", "btn-secondary")
        btn_add.clicked.connect(self._add_scene)
        hdr.addWidget(btn_add)

        btn_save = QPushButton("Save Storyboard")
        btn_save.setProperty("class", "btn-secondary")
        btn_save.clicked.connect(self._save_storyboard)
        hdr.addWidget(btn_save)

        btn_to_render = QPushButton("🎬 Render Final Video (MP4) ->")
        btn_to_render.setProperty("class", "btn-primary")
        btn_to_render.clicked.connect(self._go_to_render)
        hdr.addWidget(btn_to_render)

        layout.addLayout(hdr)

        # Scroll Area for Scene Cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(12)
        self.cards_layout.addStretch()

        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll)

    def load_project(self, project: ProjectData) -> None:
        self.project = project
        self._render_cards()

    def _render_cards(self) -> None:
        # Clear existing
        for c in self.cards:
            self.cards_layout.removeWidget(c)
            c.deleteLater()
        self.cards.clear()

        if not self.project:
            return

        for idx, scene in enumerate(self.project.scenes):
            scene.sequence_order = idx + 1
            card = SceneCard(scene)
            card.delete_requested.connect(self._delete_scene)
            card.changed.connect(self._on_card_changed)
            # Insert before the stretch item
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
            self.cards.append(card)

    def _add_scene(self) -> None:
        if not self.project:
            return
        new_scene = SceneModel(
            id=f"scene_{len(self.project.scenes) + 1:03d}",
            sequence_order=len(self.project.scenes) + 1,
            duration=5.0,
            background="classroom",
            narration="New scene narration...",
            actions=[SceneAction(character_id="char_1", action="stand")],
        )
        self.project.scenes.append(new_scene)
        self._render_cards()

    def _delete_scene(self, scene_id: str) -> None:
        if not self.project or len(self.project.scenes) <= 1:
            QMessageBox.warning(self, "Cannot Delete", "Storyboard must have at least one scene.")
            return
        self.project.scenes = [s for s in self.project.scenes if s.id != scene_id]
        self._render_cards()

    def _on_card_changed(self) -> None:
        # Autosave dirty state if needed
        pass

    def _save_storyboard(self) -> None:
        if self.project:
            get_project_manager().save_project(self.project)
            QMessageBox.information(self, "Saved", "Storyboard updated successfully.")

    def _go_to_render(self) -> None:
        if self.project:
            get_project_manager().save_project(self.project)
        self.render_requested.emit()

    def _validate_continuity(self) -> None:
        if not self.project:
            return
        # Convert to GeneratedStoryboard model
        sb = GeneratedStoryboard(
            schema_version=1,
            project_id=self.project.id,
            title=self.project.name,
            aspect_ratio=self.project.aspect_ratio,
            characters=[
                CharacterDef(id=c.id, name=c.name, color=c.color)
                for c in self.project.characters
            ],
            scenes=[
                SceneSpec(
                    id=s.id,
                    sequence_order=s.sequence_order,
                    duration=s.duration,
                    background=s.background,
                    narration=s.narration,
                    actions=[ActionSpec(character_id=a.character_id, action=a.action) for a in s.actions],
                    camera=CameraSpec(shot=s.camera.shot, movement=s.camera.movement),
                )
                for s in self.project.scenes
            ],
        )

        rep = check_continuity(sb, self.project.duration_target)
        if rep.is_valid:
            msg = "Continuity check passed!\nAll character IDs, durations, and actions are valid."
            if rep.warnings:
                msg += "\n\nWarnings:\n" + "\n".join(rep.warnings)
            QMessageBox.information(self, "Continuity Verified", msg)
        else:
            QMessageBox.critical(
                self,
                "Continuity Errors Found",
                "Please fix the following issues:\n" + "\n".join(rep.errors),
            )
