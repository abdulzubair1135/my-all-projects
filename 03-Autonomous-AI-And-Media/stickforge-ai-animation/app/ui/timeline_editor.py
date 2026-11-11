"""
Timeline & Video Preview Studio for StickForge AI.
Multi-track visual timeline representation and final video rendering export studio.
"""

from __future__ import annotations
import os
import subprocess
from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QProgressBar,
    QFrame,
    QSplitter,
    QMessageBox,
    QFileDialog,
)

from app.storage.project_manager import ProjectData, get_project_manager
from app.video.compositor import VideoCompositor
from app.video.ffmpeg_manager import probe_media
from app.ai.schema_validator import GeneratedStoryboard, SceneSpec, ActionSpec, CameraSpec, CharacterDef
from app.core.config import OUTPUT_DIR, CACHE_DIR
from app.core.logging_manager import get_logger

logger = get_logger("timeline_ui")


class RenderWorker(QThread):
    progress = Signal(float, str)
    finished_success = Signal(str)
    failed = Signal(str)

    def __init__(self, storyboard: GeneratedStoryboard, output_path: Path, width: int, height: int, fps: int):
        super().__init__()
        self.storyboard = storyboard
        self.output_path = output_path
        self.width = width
        self.height = height
        self.fps = fps

    def run(self):
        try:
            compositor = VideoCompositor(width=self.width, height=self.height, fps=self.fps)
            work_dir = CACHE_DIR / self.storyboard.project_id / "render"
            out = compositor.render_project_to_mp4(
                storyboard=self.storyboard,
                work_dir=work_dir,
                output_mp4_path=self.output_path,
                progress_callback=lambda p, m: self.progress.emit(p, m),
            )
            self.finished_success.emit(str(out))
        except Exception as e:
            logger.error(f"Render failed: {e}", exc_info=True)
            self.failed.emit(str(e))


class TimelineEditorView(QWidget):
    """Multi-track timeline and MP4 export console."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project: Optional[ProjectData] = None
        self.worker: Optional[RenderWorker] = None
        self.last_rendered_mp4: Optional[Path] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Timeline & Video Export")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #F8FAFC;")
        sub = QLabel("Multi-track scene arrangement and high-resolution MP4 rendering.")
        sub.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(title)
        title_box.addWidget(sub)
        hdr.addLayout(title_box)
        hdr.addStretch()

        self.btn_render = QPushButton("🎬 Render Final Video (MP4)")
        self.btn_render.setProperty("class", "btn-primary")
        self.btn_render.setMinimumHeight(38)
        self.btn_render.clicked.connect(self._start_render)
        hdr.addWidget(self.btn_render)

        self.btn_open_video = QPushButton("Open Video")
        self.btn_open_video.setProperty("class", "btn-secondary")
        self.btn_open_video.setEnabled(False)
        self.btn_open_video.clicked.connect(self._open_rendered_video)
        hdr.addWidget(self.btn_open_video)

        layout.addLayout(hdr)

        # Export Profile Options
        opt_bar = QHBoxLayout()
        opt_bar.addWidget(QLabel("Export Profile:"))
        self.cb_profile = QComboBox()
        self.cb_profile.addItems([
            "YouTube Shorts / Reels (1080x1920, 30 FPS, Vertical 9:16)",
            "YouTube Landscape (1920x1080, 30 FPS, 16:9)",
            "Fast Preview (540x960, 24 FPS)",
        ])
        opt_bar.addWidget(self.cb_profile, 2)
        opt_bar.addStretch()
        layout.addLayout(opt_bar)

        # Progress bar
        self.lbl_render_status = QLabel("Ready to render.")
        self.lbl_render_status.setStyleSheet("color: #94A3B8; font-size: 12px;")
        layout.addWidget(self.lbl_render_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Visual Multi-track Timeline Representation
        timeline_frame = QFrame()
        timeline_frame.setProperty("class", "card")
        tl_layout = QVBoxLayout(timeline_frame)
        tl_layout.setSpacing(8)

        lbl_tl = QLabel("Active Multi-Track Timeline")
        lbl_tl.setStyleSheet("font-weight: 700; color: #38BDF8;")
        tl_layout.addWidget(lbl_tl)

        # Track 1: Video Scenes
        self.track_scenes = self._create_track_row("Scenes Track", "#0284C7")
        tl_layout.addLayout(self.track_scenes)

        # Track 2: Stickman Animation
        self.track_anim = self._create_track_row("Stickman Animation", "#10B981")
        tl_layout.addLayout(self.track_anim)

        # Track 3: Voiceover Narration
        self.track_voice = self._create_track_row("Narration Speech", "#F59E0B")
        tl_layout.addLayout(self.track_voice)

        # Track 4: Subtitles
        self.track_subs = self._create_track_row("Subtitles & Captions", "#8B5CF6")
        tl_layout.addLayout(self.track_subs)

        layout.addWidget(timeline_frame)

    def _create_track_row(self, label_text: str, color_hex: str) -> QHBoxLayout:
        row = QHBoxLayout()
        lbl = QLabel(label_text)
        lbl.setFixedWidth(140)
        lbl.setStyleSheet("font-weight: 600; color: #E2E8F0;")
        row.addWidget(lbl)

        block = QFrame()
        block.setFixedHeight(30)
        block.setStyleSheet(f"background-color: {color_hex}; border-radius: 4px;")
        row.addWidget(block, 1)
        return row

    def load_project(self, project: ProjectData) -> None:
        self.project = project
        self.lbl_render_status.setText(f"Project loaded: {project.name}. Total Scenes: {len(project.scenes)}")

    def _start_render(self) -> None:
        if not self.project or not self.project.scenes:
            QMessageBox.warning(self, "No Scenes", "Project has no scenes to render.")
            return

        profile_text = self.cb_profile.currentText()
        if "540x960" in profile_text:
            w, h, fps = 540, 960, 24
        elif "1920x1080" in profile_text:
            w, h, fps = 1920, 1080, 30
        else:
            w, h, fps = 1080, 1920, 30

        output_file = OUTPUT_DIR / f"{self.project.name.replace(' ', '_')}_{self.project.id}.mp4"

        # Build GeneratedStoryboard
        sb = GeneratedStoryboard(
            schema_version=1,
            project_id=self.project.id,
            title=self.project.name,
            language=getattr(self.project, "language", "hinglish"),
            aspect_ratio="9:16" if h > w else "16:9",
            characters=[
                CharacterDef(
                    id=c.id,
                    name=c.name,
                    color=c.color,
                    voice_id=getattr(c, "voice_id", "en-US-ChristopherNeural"),
                )
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

        self.btn_render.setEnabled(False)
        self.btn_open_video.setEnabled(False)
        self.progress_bar.setValue(2)

        self.worker = RenderWorker(sb, output_file, w, h, fps)
        self.worker.progress.connect(self._on_render_progress)
        self.worker.finished_success.connect(self._on_render_success)
        self.worker.failed.connect(self._on_render_failed)
        self.worker.start()

    def _on_render_progress(self, pct: float, msg: str) -> None:
        self.progress_bar.setValue(int(pct))
        self.lbl_render_status.setText(msg)

    def _on_render_success(self, file_path_str: str) -> None:
        self.btn_render.setEnabled(True)
        self.btn_open_video.setEnabled(True)
        self.last_rendered_mp4 = Path(file_path_str)
        self.lbl_render_status.setText(f"✓ Video rendered successfully: {self.last_rendered_mp4.name}")

        QMessageBox.information(
            self,
            "Render Complete",
            f"Video rendered successfully!\n\nFile saved to:\n{file_path_str}",
        )

    def _on_render_failed(self, err: str) -> None:
        self.btn_render.setEnabled(True)
        self.btn_open_video.setEnabled(False)
        self.lbl_render_status.setText(f"✕ Render failed: {err}")
        QMessageBox.critical(self, "Render Failed", f"Video rendering encountered an error:\n{err}")

    def _open_rendered_video(self) -> None:
        if self.last_rendered_mp4 and self.last_rendered_mp4.exists():
            os.startfile(str(self.last_rendered_mp4))
