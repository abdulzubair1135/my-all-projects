"""
Animation Editor View for StickForge AI.
Interactive frame scrubber, motion parameter tuner, and live canvas player.
"""

from __future__ import annotations
import io
from typing import Optional, Dict
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSlider,
    QGroupBox,
    QFormLayout,
    QSplitter,
)

from PIL import Image
from app.storage.project_manager import ProjectData
from app.animation.scene_renderer import SceneRenderer
from app.ai.schema_validator import SceneSpec, CharacterDef, ActionSpec, CameraSpec
from app.ai.prompt_templates import SUPPORTED_ACTIONS


class AnimationEditorView(QWidget):
    """Animation parameter fine-tuner and frame scrubber."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project: Optional[ProjectData] = None
        self.renderer = SceneRenderer(width=450, height=800, fps=24)
        self.current_scene_idx = 0
        self.current_frame = 0
        self.is_playing = False

        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self._step_frame)

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Animation & Motion Editor")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #F8FAFC;")
        sub = QLabel("Fine-tune stickman keyframes, speeds, directions, and scrub live frames.")
        sub.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(title)
        title_box.addWidget(sub)
        hdr.addLayout(title_box)
        hdr.addStretch()
        layout.addLayout(hdr)

        splitter = QSplitter(Qt.Horizontal)

        # Left Controls
        ctrl_grp = QGroupBox("Motion Parameters")
        form = QFormLayout(ctrl_grp)

        self.cb_scene = QComboBox()
        self.cb_scene.currentIndexChanged.connect(self._on_scene_changed)
        form.addRow("Active Scene:", self.cb_scene)

        self.cb_action = QComboBox()
        self.cb_action.addItems(SUPPORTED_ACTIONS)
        self.cb_action.currentTextChanged.connect(self._on_action_changed)
        form.addRow("Stickman Action:", self.cb_action)

        self.cb_direction = QComboBox()
        self.cb_direction.addItems(["right", "left"])
        self.cb_direction.currentTextChanged.connect(self._on_direction_changed)
        form.addRow("Facing Direction:", self.cb_direction)

        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_speed.setRange(5, 25)
        self.slider_speed.setValue(10)
        self.slider_speed.valueChanged.connect(self._render_active_frame)
        form.addRow("Motion Speed:", self.slider_speed)

        splitter.addWidget(ctrl_grp)

        # Right Live Canvas & Scrubber
        preview_grp = QGroupBox("Scene Frame Scrubber")
        p_layout = QVBoxLayout(preview_grp)

        self.lbl_canvas = QLabel()
        self.lbl_canvas.setAlignment(Qt.AlignCenter)
        self.lbl_canvas.setMinimumSize(320, 520)
        self.lbl_canvas.setStyleSheet("background-color: #0F1015; border: 1px solid #27272A; border-radius: 8px;")
        p_layout.addWidget(self.lbl_canvas)

        # Play / Pause & Scrubber bar
        bar = QHBoxLayout()
        self.btn_play = QPushButton("▶ Play")
        self.btn_play.setProperty("class", "btn-primary")
        self.btn_play.clicked.connect(self._toggle_playback)
        bar.addWidget(self.btn_play)

        self.slider_scrubber = QSlider(Qt.Horizontal)
        self.slider_scrubber.setRange(0, 100)
        self.slider_scrubber.valueChanged.connect(self._on_scrubber_changed)
        bar.addWidget(self.slider_scrubber)

        self.lbl_frame_counter = QLabel("0 / 0")
        bar.addWidget(self.lbl_frame_counter)

        p_layout.addLayout(bar)
        splitter.addWidget(preview_grp)

        splitter.setSizes([340, 540])
        layout.addWidget(splitter)

    def load_project(self, project: ProjectData) -> None:
        self.project = project
        self.cb_scene.clear()
        for idx, s in enumerate(project.scenes):
            self.cb_scene.addItem(f"Scene #{idx+1} ({s.id})")
        if project.scenes:
            self.cb_scene.setCurrentIndex(0)

    def _on_scene_changed(self, idx: int) -> None:
        if not self.project or idx < 0 or idx >= len(self.project.scenes):
            return
        self.current_scene_idx = idx
        scene = self.project.scenes[idx]
        if scene.actions:
            self.cb_action.setCurrentText(scene.actions[0].action)
        num_frames = max(1, int(scene.duration * 24))
        self.slider_scrubber.setRange(0, num_frames - 1)
        self.current_frame = 0
        self.slider_scrubber.setValue(0)
        self._render_active_frame()

    def _on_action_changed(self, act: str) -> None:
        if self.project and self.project.scenes:
            scene = self.project.scenes[self.current_scene_idx]
            if scene.actions:
                scene.actions[0].action = act
            self._render_active_frame()

    def _on_direction_changed(self, d: str) -> None:
        if self.project and self.project.scenes:
            scene = self.project.scenes[self.current_scene_idx]
            if scene.actions:
                scene.actions[0].parameters["direction"] = d
            self._render_active_frame()

    def _on_scrubber_changed(self, val: int) -> None:
        self.current_frame = val
        self._render_active_frame()

    def _toggle_playback(self) -> None:
        if self.is_playing:
            self.play_timer.stop()
            self.btn_play.setText("▶ Play")
            self.is_playing = False
        else:
            self.play_timer.start(int(1000 / 24))
            self.btn_play.setText("⏸ Pause")
            self.is_playing = True

    def _step_frame(self) -> None:
        max_f = self.slider_scrubber.maximum()
        self.current_frame = (self.current_frame + 1) % (max_f + 1)
        self.slider_scrubber.setValue(self.current_frame)

    def _render_active_frame(self) -> None:
        if not self.project or not self.project.scenes:
            return
        scene_model = self.project.scenes[self.current_scene_idx]
        num_frames = max(1, int(scene_model.duration * 24))
        self.lbl_frame_counter.setText(f"{self.current_frame + 1} / {num_frames}")

        # Convert SceneModel to SceneSpec
        speed_factor = self.slider_speed.value() / 10.0
        act_name = self.cb_action.currentText()
        direction = self.cb_direction.currentText()

        spec = SceneSpec(
            id=scene_model.id,
            sequence_order=scene_model.sequence_order,
            duration=scene_model.duration,
            background=scene_model.background,
            actions=[
                ActionSpec(
                    character_id="hero",
                    action=act_name,
                    parameters={"speed": speed_factor, "direction": direction},
                )
            ],
            camera=CameraSpec(shot=scene_model.camera.shot, movement=scene_model.camera.movement),
        )

        chars = {
            "hero": CharacterDef(
                id="hero",
                name=self.project.characters[0].name if self.project.characters else "Rahul",
                color=self.project.characters[0].color if self.project.characters else "#38BDF8",
            )
        }

        img = self.renderer.render_frame(spec, chars, self.current_frame, num_frames)

        # Scale to canvas size
        img_resized = img.resize((320, 520), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img_resized.save(buf, format="PNG")
        qimg = QImage.fromData(buf.getvalue())
        self.lbl_canvas.setPixmap(QPixmap.fromImage(qimg))
