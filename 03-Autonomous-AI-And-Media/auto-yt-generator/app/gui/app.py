"""
AUTO YT GENERATOR — Desktop GUI Studio (PyQt5) with Video Player & Gallery.

Modern dark-themed desktop studio interface for:
- 1-Click Automated YouTube Video Generation
- 🎬 My Videos Gallery & Player (Play Video, Open Folder, View Thumbnail & Chapters)
- Storyboard, Script & Asset Inspection
- Phonk & Procedural Music Lab
- Project Manager & Settings
"""

import sys
import os
import threading
from pathlib import Path

# Ensure root is on path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QFrame,
    QFileDialog,
    QScrollArea,
    QGridLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QIcon

from app.constants import APP_NAME, APP_VERSION, VideoStyle, Language, DEFAULT_DURATION
from app.config import settings
from app.database import db
from app.models.project import ProjectModel, ProjectConfig
from app.pipeline.pipeline import PipelineOrchestrator
from app.pipeline.stages import (
    ResearchStage,
    ScriptStage,
    ScenePlanningStage,
    AssetGenerationStage,
    VoiceGenerationStage,
    AudioMixStage,
    VideoRenderStage,
    OutputStage,
)
from app.audio.music import music_generator
import uuid


class WorkerSignals(QObject):
    log = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION} — AI YouTube Studio")
        self.resize(1150, 750)
        self.last_rendered_project_id = None
        self._apply_dark_theme()
        self._init_ui()

    def _apply_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(15, 18, 25))
        palette.setColor(QPalette.WindowText, QColor(240, 240, 245))
        palette.setColor(QPalette.Base, QColor(22, 26, 36))
        palette.setColor(QPalette.AlternateBase, QColor(28, 32, 45))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, QColor(240, 240, 245))
        palette.setColor(QPalette.Button, QColor(32, 36, 50))
        palette.setColor(QPalette.ButtonText, QColor(240, 240, 245))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(56, 189, 248))
        palette.setColor(QPalette.Highlight, QColor(140, 60, 240))
        palette.setColor(QPalette.HighlightedText, Qt.white)
        self.setPalette(palette)

    def _init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header
        header_layout = QHBoxLayout()
        header = QLabel(f"🎬 {APP_NAME} — Automated YouTube Studio")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("color: #a855f7; margin-bottom: 4px;")
        header_layout.addWidget(header)
        header_layout.addStretch()

        btn_open_all = QPushButton("📂 Open All Projects Folder")
        btn_open_all.setStyleSheet("background: #334155; color: white; padding: 6px 12px; border-radius: 6px; font-weight: bold;")
        btn_open_all.clicked.connect(self._open_projects_directory)
        header_layout.addWidget(btn_open_all)

        main_layout.addLayout(header_layout)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: #1e222d;
                color: #94a3b8;
                padding: 10px 22px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 4px;
                font-weight: bold;
                font-size: 11pt;
            }
            QTabBar::tab:selected {
                background: #8b5cf6;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #334155;
                background: #111520;
                border-radius: 8px;
            }
        """)

        self.tab_create = self._create_generator_tab()
        self.tab_gallery = self._create_gallery_tab()
        self.tab_projects = self._create_projects_tab()
        self.tab_music = self._create_music_lab_tab()

        self.tabs.addTab(self.tab_create, "⚡ 1-Click Video Generator")
        self.tabs.addTab(self.tab_gallery, "🎬 My Created Videos (Gallery)")
        self.tabs.addTab(self.tab_projects, "📁 Project Manager")
        self.tabs.addTab(self.tab_music, "🎹 Phonk & Music Lab")

        self.tabs.currentChanged.connect(self._on_tab_changed)

        main_layout.addWidget(self.tabs)

    def _create_generator_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # Topic Input
        lbl_topic = QLabel("Video Topic or Question:")
        lbl_topic.setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.txt_topic = QLineEdit()
        self.txt_topic.setPlaceholderText("e.g. What happened if I make a billion dollar company?")
        self.txt_topic.setStyleSheet("background: #1e293b; color: white; padding: 10px; border-radius: 6px; border: 1px solid #475569; font-size: 11pt;")
        layout.addWidget(lbl_topic)
        layout.addWidget(self.txt_topic)

        # Options Row
        opts_layout = QHBoxLayout()

        # Style
        v_style = QVBoxLayout()
        v_style.addWidget(QLabel("Art Style:"))
        self.cmb_style = QComboBox()
        for s in VideoStyle:
            self.cmb_style.addItem(s.value.title().replace("_", " "), s.value)
        self.cmb_style.setStyleSheet("background: #1e293b; color: white; padding: 6px; border-radius: 4px;")
        v_style.addWidget(self.cmb_style)
        opts_layout.addLayout(v_style)

        # Language
        v_lang = QVBoxLayout()
        v_lang.addWidget(QLabel("Language:"))
        self.cmb_lang = QComboBox()
        self.cmb_lang.addItem("English (en)", "en")
        self.cmb_lang.addItem("Hindi (hi)", "hi")
        self.cmb_lang.addItem("Urdu (ur)", "ur")
        self.cmb_lang.setStyleSheet("background: #1e293b; color: white; padding: 6px; border-radius: 4px;")
        v_lang.addWidget(self.cmb_lang)
        opts_layout.addLayout(v_lang)

        # Format (16:9 or 9:16 Shorts)
        v_fmt = QVBoxLayout()
        v_fmt.addWidget(QLabel("Format:"))
        self.cmb_format = QComboBox()
        self.cmb_format.addItem("YouTube Standard (16:9)", "16:9")
        self.cmb_format.addItem("Shorts / Reels (9:16)", "9:16")
        self.cmb_format.setStyleSheet("background: #1e293b; color: white; padding: 6px; border-radius: 4px;")
        v_fmt.addWidget(self.cmb_format)
        opts_layout.addLayout(v_fmt)

        # Duration
        v_dur = QVBoxLayout()
        v_dur.addWidget(QLabel("Duration (seconds):"))
        self.spn_duration = QSpinBox()
        self.spn_duration.setRange(30, 900)
        self.spn_duration.setValue(DEFAULT_DURATION)
        self.spn_duration.setStyleSheet("background: #1e293b; color: white; padding: 6px; border-radius: 4px;")
        v_dur.addWidget(self.spn_duration)
        opts_layout.addLayout(v_dur)

        layout.addLayout(opts_layout)

        # Generate Button
        self.btn_generate = QPushButton("🚀 Generate Complete 1080p Video (1-Click)")
        self.btn_generate.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.btn_generate.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b5cf6, stop:1 #ec4899);
                color: white;
                padding: 12px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #7c3aed, stop:1 #db2777);
            }
        """)
        self.btn_generate.clicked.connect(self._on_start_generation)
        layout.addWidget(self.btn_generate)

        # Quick Action Buttons after Generation (Initially Hidden)
        self.actions_row = QHBoxLayout()
        self.btn_play_latest = QPushButton("▶️ Play Rendered Video")
        self.btn_play_latest.setStyleSheet("background: #10b981; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        self.btn_play_latest.clicked.connect(self._play_latest_video)
        self.btn_play_latest.hide()

        self.btn_open_folder_latest = QPushButton("📂 Open Video Folder")
        self.btn_open_folder_latest.setStyleSheet("background: #3b82f6; color: white; font-weight: bold; padding: 8px 16px; border-radius: 6px;")
        self.btn_open_folder_latest.clicked.connect(self._open_latest_folder)
        self.btn_open_folder_latest.hide()

        self.actions_row.addWidget(self.btn_play_latest)
        self.actions_row.addWidget(self.btn_open_folder_latest)
        self.actions_row.addStretch()
        layout.addLayout(self.actions_row)

        # Progress Bar & Console
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #475569;
                border-radius: 4px;
                text-align: center;
                background: #0f172a;
                color: white;
            }
            QProgressBar::chunk {
                background: #8b5cf6;
            }
        """)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.txt_console = QTextEdit()
        self.txt_console.setReadOnly(True)
        self.txt_console.setStyleSheet("background: #0b0f19; color: #38bdf8; font-family: Consolas; font-size: 10pt; border-radius: 6px;")
        layout.addWidget(self.txt_console)

        return widget

    def _create_gallery_tab(self) -> QWidget:
        """Gallery view showing all created videos with thumbnails and 1-click play/open buttons."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        top_bar = QHBoxLayout()
        lbl = QLabel("🎬 Your Rendered Video Library")
        lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl.setStyleSheet("color: #38bdf8;")
        top_bar.addWidget(lbl)
        top_bar.addStretch()

        btn_refresh = QPushButton("🔄 Refresh Videos")
        btn_refresh.setStyleSheet("background: #3b82f6; color: white; font-weight: bold; padding: 6px 14px; border-radius: 6px;")
        btn_refresh.clicked.connect(self._populate_gallery)
        top_bar.addWidget(btn_refresh)
        layout.addLayout(top_bar)

        # Scroll area for video cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: #0d111a; border: none;")

        self.gallery_container = QWidget()
        self.gallery_layout = QVBoxLayout(self.gallery_container)
        self.gallery_layout.setSpacing(12)
        self.scroll_area.setWidget(self.gallery_container)

        layout.addWidget(self.scroll_area)
        self._populate_gallery()
        return widget

    def _populate_gallery(self):
        # Clear existing cards
        while self.gallery_layout.count():
            child = self.gallery_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        projects = db.list_projects()
        completed_count = 0

        for p in reversed(projects):
            p_dir = Path(settings.paths.projects_dir) / p.id
            vid_path = p_dir / "final" / "video.mp4"
            thumb_path = p_dir / "final" / "thumbnail.png"
            if not thumb_path.exists():
                thumb_path = p_dir / "thumbnail" / "thumbnail.png"

            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background: #1a1e2b;
                    border: 1px solid #334155;
                    border-radius: 10px;
                    padding: 10px;
                }
                QFrame:hover {
                    border: 1px solid #8b5cf6;
                    background: #202536;
                }
            """)
            card_layout = QHBoxLayout(card)

            # 1. Thumbnail Image
            thumb_lbl = QLabel()
            thumb_lbl.setFixedSize(200, 112)
            thumb_lbl.setStyleSheet("background: #0f172a; border-radius: 6px;")
            thumb_lbl.setAlignment(Qt.AlignCenter)

            if thumb_path.exists():
                pix = QPixmap(str(thumb_path))
                thumb_lbl.setPixmap(pix.scaled(200, 112, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                thumb_lbl.setText("🎬 Video")
                thumb_lbl.setStyleSheet("background: #0f172a; color: #64748b; font-weight: bold; border-radius: 6px;")

            card_layout.addWidget(thumb_lbl)

            # 2. Video Details
            info_layout = QVBoxLayout()
            title_lbl = QLabel(p.topic)
            title_lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
            title_lbl.setStyleSheet("color: #f8fafc;")
            title_lbl.setWordWrap(True)
            info_layout.addWidget(title_lbl)

            status_color = "#10b981" if vid_path.exists() else "#eab308"
            status_text = "READY TO WATCH" if vid_path.exists() else f"Stage: {p.current_stage}"
            meta_lbl = QLabel(f"⏱ {p.duration_seconds}s  |  🎨 {p.style}  |  🌐 {p.language.upper()}  |  ● {status_text}")
            meta_lbl.setStyleSheet(f"color: {status_color}; font-size: 9pt; font-weight: bold;")
            info_layout.addWidget(meta_lbl)

            dir_lbl = QLabel(f"📁 {p_dir}")
            dir_lbl.setStyleSheet("color: #64748b; font-size: 8pt;")
            info_layout.addWidget(dir_lbl)

            card_layout.addLayout(info_layout, stretch=1)

            # 3. Action Buttons
            btn_layout = QVBoxLayout()
            btn_layout.setSpacing(6)

            if vid_path.exists():
                btn_play = QPushButton("▶️ Play Video")
                btn_play.setStyleSheet("background: #10b981; color: white; font-weight: bold; padding: 8px 14px; border-radius: 6px;")
                btn_play.clicked.connect(lambda _, vp=str(vid_path): self._open_file_in_os(vp))
                btn_layout.addWidget(btn_play)
                completed_count += 1

            btn_folder = QPushButton("📂 Open Folder")
            btn_folder.setStyleSheet("background: #3b82f6; color: white; font-weight: bold; padding: 6px 14px; border-radius: 6px;")
            btn_folder.clicked.connect(lambda _, pd=str(p_dir): self._open_folder_in_os(pd))
            btn_layout.addWidget(btn_folder)

            card_layout.addLayout(btn_layout)
            self.gallery_layout.addWidget(card)

        if len(projects) == 0:
            no_vid = QLabel("No videos generated yet. Create your first video in '1-Click Video Generator' tab!")
            no_vid.setStyleSheet("color: #64748b; font-size: 11pt; padding: 30px;")
            no_vid.setAlignment(Qt.AlignCenter)
            self.gallery_layout.addWidget(no_vid)

        self.gallery_layout.addStretch()

    def _create_projects_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.table_projects = QTableWidget()
        self.table_projects.setColumnCount(6)
        self.table_projects.setHorizontalHeaderLabels(["ID", "Topic", "Style", "Language", "Stage", "Progress"])
        self.table_projects.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_projects.setStyleSheet("background: #1e293b; color: white; gridline-color: #334155;")
        layout.addWidget(self.table_projects)

        btn_row = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Refresh Projects")
        btn_refresh.setStyleSheet("background: #3b82f6; color: white; padding: 8px; border-radius: 6px; font-weight: bold;")
        btn_refresh.clicked.connect(self._refresh_projects_table)
        btn_row.addWidget(btn_refresh)

        btn_del = QPushButton("🗑️ Delete Selected Project")
        btn_del.setStyleSheet("background: #ef4444; color: white; padding: 8px; border-radius: 6px; font-weight: bold;")
        btn_del.clicked.connect(self._delete_selected_project)
        btn_row.addWidget(btn_del)

        layout.addLayout(btn_row)
        self._refresh_projects_table()
        return widget

    def _create_music_lab_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        lbl = QLabel("🎹 Procedural Beat & Score Synthesizer")
        lbl.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl.setStyleSheet("color: #f43f5e;")
        layout.addWidget(lbl)

        row = QHBoxLayout()
        v_dur = QVBoxLayout()
        v_dur.addWidget(QLabel("Track Duration (sec):"))
        spn_m_dur = QSpinBox()
        spn_m_dur.setRange(5, 300)
        spn_m_dur.setValue(30)
        spn_m_dur.setStyleSheet("background: #1e293b; color: white; padding: 6px;")
        v_dur.addWidget(spn_m_dur)
        row.addLayout(v_dur)

        v_bpm = QVBoxLayout()
        v_bpm.addWidget(QLabel("BPM:"))
        spn_bpm = QSpinBox()
        spn_bpm.setRange(60, 180)
        spn_bpm.setValue(145)
        spn_bpm.setStyleSheet("background: #1e293b; color: white; padding: 6px;")
        v_bpm.addWidget(spn_bpm)
        row.addLayout(v_bpm)

        layout.addLayout(row)

        btn_phonk = QPushButton("🔥 Synthesize Phonk Beat (WAV)")
        btn_phonk.setStyleSheet("background: #f43f5e; color: white; font-weight: bold; padding: 10px; border-radius: 6px;")
        btn_phonk.clicked.connect(lambda: self._generate_standalone_beat("phonk", spn_m_dur.value(), spn_bpm.value()))
        layout.addWidget(btn_phonk)

        btn_cinematic = QPushButton("🌌 Synthesize Dark Suspense Score (WAV)")
        btn_cinematic.setStyleSheet("background: #6366f1; color: white; font-weight: bold; padding: 10px; border-radius: 6px;")
        btn_cinematic.clicked.connect(lambda: self._generate_standalone_beat("dark_suspense", spn_m_dur.value(), 90))
        layout.addWidget(btn_cinematic)

        self.lbl_music_status = QLabel("Ready.")
        self.lbl_music_status.setStyleSheet("color: #94a3b8; font-style: italic;")
        layout.addWidget(self.lbl_music_status)

        layout.addStretch()
        return widget

    def _on_start_generation(self):
        topic = self.txt_topic.text().strip()
        if not topic:
            QMessageBox.warning(self, "Missing Topic", "Please enter a video topic first.")
            return

        style = self.cmb_style.currentData()
        lang = self.cmb_lang.currentData()
        dur = self.spn_duration.value()
        fmt = self.cmb_format.currentData()
        res = "1080x1920" if fmt == "9:16" else "1920x1080"

        self.btn_generate.setEnabled(False)
        self.btn_play_latest.hide()
        self.btn_open_folder_latest.hide()
        self.txt_console.clear()
        self.txt_console.append(f"[START] Creating project for: '{topic}'...")

        # Worker thread
        signals = WorkerSignals()
        signals.log.connect(self.txt_console.append)
        signals.finished.connect(self._on_generation_finished)
        signals.error.connect(self._on_generation_error)

        def _worker():
            try:
                project_id = str(uuid.uuid4())
                project_dir = Path(settings.paths.projects_dir) / project_id
                project_dir.mkdir(parents=True, exist_ok=True)
                for sub in ["assets", "audio", "renders", "final", "thumbnail", "metadata"]:
                    (project_dir / sub).mkdir(exist_ok=True)

                config = ProjectConfig(
                    topic=topic,
                    language=lang,
                    duration_seconds=dur,
                    style=style,
                    resolution=res,
                    fps=15,
                )
                project = ProjectModel(
                    id=project_id,
                    title=topic[:60],
                    config=config,
                    project_dir=str(project_dir),
                )
                db.create_project(project)
                signals.log.emit(f"[+] Project registered in DB: {project_id}")

                orchestrator = PipelineOrchestrator([
                    ResearchStage(),
                    ScriptStage(),
                    ScenePlanningStage(),
                    AssetGenerationStage(),
                    VoiceGenerationStage(),
                    AudioMixStage(),
                    VideoRenderStage(),
                    OutputStage(),
                ])

                signals.log.emit("[+] Running 8-Stage Automated Production Pipeline...")
                job = orchestrator.run_pipeline(project)

                if job.status.value == "COMPLETED":
                    signals.finished.emit(project_id)
                else:
                    signals.error.emit("Pipeline failed. Check system logs.")
            except Exception as e:
                signals.error.emit(str(e))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_generation_finished(self, project_id: str):
        self.btn_generate.setEnabled(True)
        self.progress_bar.setValue(100)
        self.last_rendered_project_id = project_id

        vid_path = Path(settings.paths.projects_dir) / project_id / "final" / "video.mp4"
        self.txt_console.append(f"\n🎉 [SUCCESS] 1080p Video Rendered: {vid_path}")

        # Show Action buttons
        self.btn_play_latest.show()
        self.btn_open_folder_latest.show()

        self._refresh_projects_table()
        self._populate_gallery()
        QMessageBox.information(self, "Video Complete!", f"Video generation completed successfully!\n\nClick 'Play Rendered Video' or check the 'My Created Videos' tab to watch.")

    def _on_generation_error(self, err_msg: str):
        self.btn_generate.setEnabled(True)
        self.txt_console.append(f"\n❌ [ERROR] {err_msg}")
        QMessageBox.critical(self, "Error", f"Generation failed:\n{err_msg}")

    def _play_latest_video(self):
        if self.last_rendered_project_id:
            vid_path = Path(settings.paths.projects_dir) / self.last_rendered_project_id / "final" / "video.mp4"
            if vid_path.exists():
                self._open_file_in_os(str(vid_path))

    def _open_latest_folder(self):
        if self.last_rendered_project_id:
            p_dir = Path(settings.paths.projects_dir) / self.last_rendered_project_id / "final"
            self._open_folder_in_os(str(p_dir))

    def _open_file_in_os(self, path: str):
        """Plays video in Windows default media player."""
        try:
            os.startfile(path)
        except Exception as e:
            QMessageBox.warning(self, "Could Not Open", f"Unable to open video: {e}")

    def _open_folder_in_os(self, folder_path: str):
        """Opens folder in Windows Explorer."""
        try:
            os.startfile(folder_path)
        except Exception as e:
            QMessageBox.warning(self, "Could Not Open", f"Unable to open directory: {e}")

    def _open_projects_directory(self):
        p_dir = Path(settings.paths.projects_dir).resolve()
        p_dir.mkdir(parents=True, exist_ok=True)
        self._open_folder_in_os(str(p_dir))

    def _on_tab_changed(self, index: int):
        if index == 1:  # Gallery Tab
            self._populate_gallery()
        elif index == 2:  # Projects Tab
            self._refresh_projects_table()

    def _refresh_projects_table(self):
        projects = db.list_projects()
        self.table_projects.setRowCount(len(projects))
        for row, p in enumerate(projects):
            self.table_projects.setItem(row, 0, QTableWidgetItem(p.id[:8] + "..."))
            self.table_projects.setItem(row, 1, QTableWidgetItem(p.topic[:35]))
            self.table_projects.setItem(row, 2, QTableWidgetItem(p.style))
            self.table_projects.setItem(row, 3, QTableWidgetItem(p.language))
            self.table_projects.setItem(row, 4, QTableWidgetItem(p.current_stage))
            self.table_projects.setItem(row, 5, QTableWidgetItem(f"{p.progress_percent:.0f}%"))

    def _delete_selected_project(self):
        row = self.table_projects.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Select Row", "Please select a project from the table to delete.")
            return

        projects = db.list_projects()
        if row < len(projects):
            target = projects[row]
            confirm = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete project '{target.topic}'?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                db.delete_project(target.id)
                self._refresh_projects_table()
                self._populate_gallery()

    def _generate_standalone_beat(self, style: str, duration: int, bpm: int):
        out_file, _ = QFileDialog.getSaveFileName(self, "Save Beat As", f"{style}_beat.wav", "WAV Audio (*.wav)")
        if out_file:
            self.lbl_music_status.setText(f"Synthesizing {style} track...")
            music_generator.generate_music(duration_sec=duration, output_path=out_file, style=style, bpm=bpm)
            self.lbl_music_status.setText(f"Rendered: {out_file}")
            QMessageBox.information(self, "Beat Generated", f"Audio track saved to:\n{out_file}")


def launch_gui():
    """Entrypoint to launch the Desktop GUI application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    launch_gui()
