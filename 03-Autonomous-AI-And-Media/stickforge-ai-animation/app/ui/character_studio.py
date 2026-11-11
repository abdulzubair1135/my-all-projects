"""
Character Studio View for StickForge AI.
Interactive character designer with real-time pose preview canvas, color picker, and voice assignment.
"""

from __future__ import annotations
import io
from typing import Optional, List
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QColorDialog,
    QSlider,
    QFormLayout,
    QGroupBox,
    QListWidget,
    QSplitter,
    QMessageBox,
)

from PIL import Image, ImageDraw
from app.storage.project_manager import ProjectData, CharacterModel, get_project_manager
from app.animation.skeleton import StickmanSkeleton, SkeletonProportions
from app.animation.pose import POSE_STAND, POSE_WAVE_1, POSE_WALK_1, POSE_RUN_1, POSE_HAPPY, POSE_SAD, POSE_FIGHT_PUNCH
from app.animation.background_renderer import hex_to_rgb


class CharacterStudioView(QWidget):
    """Character customization and pose inspection studio."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project: Optional[ProjectData] = None
        self.active_char: Optional[CharacterModel] = None
        self.skeleton = StickmanSkeleton()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Character Studio")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #F8FAFC;")
        sub = QLabel("Customize stickman characters, colors, proportions, and test keyframe poses.")
        sub.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(title)
        title_box.addWidget(sub)
        hdr.addLayout(title_box)
        hdr.addStretch()

        btn_add = QPushButton("+ Add Character")
        btn_add.setProperty("class", "btn-secondary")
        btn_add.clicked.connect(self._add_character)
        hdr.addWidget(btn_add)

        btn_save = QPushButton("Save Characters")
        btn_save.setProperty("class", "btn-primary")
        btn_save.clicked.connect(self._save_characters)
        hdr.addWidget(btn_save)

        layout.addLayout(hdr)

        # Main Splitter: Left character list, Middle properties, Right live preview
        splitter = QSplitter(Qt.Horizontal)

        # 1. Characters List
        left_grp = QGroupBox("Project Characters")
        left_layout = QVBoxLayout(left_grp)
        self.char_list = QListWidget()
        self.char_list.currentRowChanged.connect(self._on_char_selected)
        left_layout.addWidget(self.char_list)
        splitter.addWidget(left_grp)

        # 2. Properties Form
        prop_grp = QGroupBox("Character Attributes")
        form = QFormLayout(prop_grp)

        self.edit_name = QLineEdit()
        self.edit_name.textChanged.connect(self._on_name_changed)
        form.addRow("Character Name:", self.edit_name)

        # Color picker
        color_layout = QHBoxLayout()
        self.btn_color = QPushButton("Pick Color")
        self.btn_color.setProperty("class", "btn-secondary")
        self.btn_color.clicked.connect(self._pick_color)
        self.lbl_color_preview = QLabel("   #38BDF8   ")
        self.lbl_color_preview.setStyleSheet("background-color: #38BDF8; color: #000; border-radius: 4px; padding: 4px;")
        color_layout.addWidget(self.btn_color)
        color_layout.addWidget(self.lbl_color_preview)
        form.addRow("Stick Color:", color_layout)

        # Proportions Sliders
        self.slider_head = QSlider(Qt.Horizontal)
        self.slider_head.setRange(16, 40)
        self.slider_head.setValue(24)
        self.slider_head.valueChanged.connect(self._update_preview)
        form.addRow("Head Size:", self.slider_head)

        self.slider_torso = QSlider(Qt.Horizontal)
        self.slider_torso.setRange(40, 100)
        self.slider_torso.setValue(65)
        self.slider_torso.valueChanged.connect(self._update_preview)
        form.addRow("Torso Length:", self.slider_torso)

        self.cb_pose = QComboBox()
        self.cb_pose.addItems(["Stand", "Wave", "Walk", "Run", "Happy", "Sad", "Punch"])
        self.cb_pose.currentTextChanged.connect(self._update_preview)
        form.addRow("Test Pose:", self.cb_pose)

        splitter.addWidget(prop_grp)

        # 3. Live Preview Canvas
        preview_grp = QGroupBox("Live Stickman Preview")
        preview_layout = QVBoxLayout(preview_grp)
        self.lbl_preview_canvas = QLabel()
        self.lbl_preview_canvas.setAlignment(Qt.AlignCenter)
        self.lbl_preview_canvas.setMinimumSize(320, 420)
        self.lbl_preview_canvas.setStyleSheet("background-color: #121316; border: 1px solid #27272A; border-radius: 8px;")
        preview_layout.addWidget(self.lbl_preview_canvas)
        splitter.addWidget(preview_grp)

        splitter.setSizes([180, 320, 420])
        layout.addWidget(splitter)

    def load_project(self, project: ProjectData) -> None:
        self.project = project
        self.char_list.clear()
        for c in project.characters:
            self.char_list.addItem(f"{c.name} ({c.id})")
        if project.characters:
            self.char_list.setCurrentRow(0)

    def _on_char_selected(self, row: int) -> None:
        if not self.project or row < 0 or row >= len(self.project.characters):
            return
        self.active_char = self.project.characters[row]
        self.edit_name.setText(self.active_char.name)
        color = self.active_char.color
        self.lbl_color_preview.setText(f"   {color}   ")
        self.lbl_color_preview.setStyleSheet(f"background-color: {color}; color: #000; border-radius: 4px; padding: 4px;")

        props = self.active_char.proportions
        self.slider_head.setValue(int(props.get("head_radius", 24)))
        self.slider_torso.setValue(int(props.get("torso_length", 65)))

        self._update_preview()

    def _on_name_changed(self, text: str) -> None:
        if self.active_char:
            self.active_char.name = text.strip() or "Hero"
            row = self.char_list.currentRow()
            if row >= 0:
                item = self.char_list.item(row)
                item.setText(f"{self.active_char.name} ({self.active_char.id})")

    def _pick_color(self) -> None:
        if not self.active_char:
            return
        col = QColorDialog.getColor(QColor(self.active_char.color), self, "Select Character Color")
        if col.isValid():
            hex_str = col.name().upper()
            self.active_char.color = hex_str
            self.lbl_color_preview.setText(f"   {hex_str}   ")
            self.lbl_color_preview.setStyleSheet(f"background-color: {hex_str}; color: #000; border-radius: 4px; padding: 4px;")
            self._update_preview()

    def _update_preview(self) -> None:
        if not self.active_char:
            return

        w, h = 320, 420
        img = Image.new("RGB", (w, h), (18, 19, 24))
        draw = ImageDraw.Draw(img)

        # Ground line
        draw.line([(20, h - 60), (w - 20, h - 60)], fill=(45, 48, 58), width=3)

        # Skeleton proportions
        props = SkeletonProportions(
            head_radius=float(self.slider_head.value()),
            torso_length=float(self.slider_torso.value()),
        )
        self.skeleton.props = props

        # Get pose
        pose_name = self.cb_pose.currentText()
        pose_map = {
            "Stand": POSE_STAND,
            "Wave": POSE_WAVE_1,
            "Walk": POSE_WALK_1,
            "Run": POSE_RUN_1,
            "Happy": POSE_HAPPY,
            "Sad": POSE_SAD,
            "Punch": POSE_FIGHT_PUNCH,
        }
        angles = pose_map.get(pose_name, POSE_STAND)

        # Compute joints in center of preview
        joints = self.skeleton.compute_joints(
            root_x=w * 0.5,
            root_y=h - 130,
            angles=angles,
            scale=1.1,
            facing_right=True,
        )

        # Draw stickman
        stroke_color = hex_to_rgb(self.active_char.color)
        line_w = 5

        def seg(p1, p2):
            draw.line([p1, p2], fill=stroke_color, width=line_w)
            r = int(line_w / 2)
            draw.ellipse([p1[0] - r, p1[1] - r, p1[0] + r, p1[1] + r], fill=stroke_color)
            draw.ellipse([p2[0] - r, p2[1] - r, p2[0] + r, p2[1] + r], fill=stroke_color)

        seg(joints["neck"], joints["pelvis"])
        seg(joints["pelvis"], joints["left_hip"])
        seg(joints["left_hip"], joints["left_knee"])
        seg(joints["left_knee"], joints["left_foot"])
        seg(joints["pelvis"], joints["right_hip"])
        seg(joints["right_hip"], joints["right_knee"])
        seg(joints["right_knee"], joints["right_foot"])
        seg(joints["neck"], joints["left_shoulder"])
        seg(joints["left_shoulder"], joints["left_elbow"])
        seg(joints["left_elbow"], joints["left_hand"])
        seg(joints["neck"], joints["right_shoulder"])
        seg(joints["right_shoulder"], joints["right_elbow"])
        seg(joints["right_elbow"], joints["right_hand"])

        hx, hy = joints["head_center"]
        hr = int(joints["head_radius"][0])
        draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(22, 24, 30), outline=stroke_color, width=line_w)

        # Convert PIL to QPixmap
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        qimg = QImage.fromData(buf.getvalue())
        self.lbl_preview_canvas.setPixmap(QPixmap.fromImage(qimg))

    def _add_character(self) -> None:
        if not self.project:
            return
        idx = len(self.project.characters) + 1
        new_char = CharacterModel(id=f"char_{idx}", name=f"Character {idx}", color="#F59E0B")
        self.project.characters.append(new_char)
        self.char_list.addItem(f"{new_char.name} ({new_char.id})")
        self.char_list.setCurrentRow(len(self.project.characters) - 1)

    def _save_characters(self) -> None:
        if self.project and self.active_char:
            self.active_char.proportions["head_radius"] = float(self.slider_head.value())
            self.active_char.proportions["torso_length"] = float(self.slider_torso.value())
            get_project_manager().save_project(self.project)
            QMessageBox.information(self, "Saved", "Characters saved successfully.")
