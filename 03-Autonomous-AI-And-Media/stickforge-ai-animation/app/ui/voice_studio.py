"""
Voice Studio View for StickForge AI.
Handles voiceover actor selection, audio preview, scene-by-scene narration generation, and audio duration tracking.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional, List
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QProgressBar,
    QMessageBox,
)

from app.storage.project_manager import ProjectData, get_project_manager
from app.audio.tts_provider import get_tts_provider, BaseTTSProvider
from app.core.config import CACHE_DIR
from app.core.logging_manager import get_logger

logger = get_logger("voice_studio_ui")


class VoiceGenWorker(QThread):
    progress = Signal(float, str)
    finished_success = Signal()
    failed = Signal(str)

    def __init__(self, project: ProjectData, provider_name: str, voice_id: str):
        super().__init__()
        self.project = project
        self.provider_name = provider_name
        self.voice_id = voice_id

    def run(self):
        try:
            tts = get_tts_provider(self.provider_name)
            audio_dir = CACHE_DIR / self.project.id / "audio"
            audio_dir.mkdir(parents=True, exist_ok=True)

            total = len(self.project.scenes)
            for idx, scene in enumerate(self.project.scenes):
                text = scene.narration.strip() or "..."
                out_path = audio_dir / f"scene_{idx:03d}.wav"
                dur = tts.synthesize(text, out_path, voice=self.voice_id)
                scene.duration = max(scene.duration, dur)
                pct = ((idx + 1) / total) * 100.0
                self.progress.emit(pct, f"Synthesized scene {idx + 1}/{total} ({dur:.1f}s)")

            get_project_manager().save_project(self.project)
            self.finished_success.emit()
        except Exception as e:
            logger.error(f"Voice generation failed: {e}", exc_info=True)
            self.failed.emit(str(e))


class VoiceStudioView(QWidget):
    """Voice selection and narration generator studio."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project: Optional[ProjectData] = None
        self.worker: Optional[VoiceGenWorker] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Voice & Narration Studio")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #F8FAFC;")
        sub = QLabel("Select speech actors, preview pronunciation, and generate synchronized scene voice tracks.")
        sub.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(title)
        title_box.addWidget(sub)
        hdr.addLayout(title_box)
        hdr.addStretch()

        self.btn_gen_all = QPushButton("Generate All Narration Audio")
        self.btn_gen_all.setProperty("class", "btn-primary")
        self.btn_gen_all.clicked.connect(self._generate_all_audio)
        hdr.addWidget(self.btn_gen_all)

        layout.addLayout(hdr)

        # Provider and Voice Bar
        bar = QHBoxLayout()
        bar.addWidget(QLabel("TTS Provider:"))
        self.cb_provider = QComboBox()
        self.cb_provider.addItems(["edge_tts", "pyttsx3"])
        self.cb_provider.currentTextChanged.connect(self._populate_voices)
        bar.addWidget(self.cb_provider)

        bar.addWidget(QLabel("Voice Actor:"))
        self.cb_voice = QComboBox()
        bar.addWidget(self.cb_voice, 2)

        self.btn_test = QPushButton("Test Voice")
        self.btn_test.setProperty("class", "btn-secondary")
        self.btn_test.clicked.connect(self._test_voice)
        bar.addWidget(self.btn_test)

        layout.addLayout(bar)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Scene Narrations Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Scene ID", "Narration Text", "Duration", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setStyleSheet("background-color: #18191E; border: 1px solid #2D3039;")
        layout.addWidget(self.table)

        self._populate_voices()

    def _populate_voices(self) -> None:
        self.cb_voice.clear()
        provider = get_tts_provider(self.cb_provider.currentText())
        voices = provider.get_available_voices()
        for v in voices:
            self.cb_voice.addItem(f"{v['name']}", v["id"])

    def load_project(self, project: ProjectData) -> None:
        self.project = project
        self._refresh_table()

    def _refresh_table(self) -> None:
        if not self.project:
            return
        self.table.setRowCount(len(self.project.scenes))
        for row, s in enumerate(self.project.scenes):
            self.table.setItem(row, 0, QTableWidgetItem(s.id))
            self.table.setItem(row, 1, QTableWidgetItem(s.narration or "—"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{s.duration:.1f}s"))
            self.table.setItem(row, 3, QTableWidgetItem("Ready"))

    def _test_voice(self) -> None:
        voice_id = self.cb_voice.currentData() or "en-US-ChristopherNeural"
        tts = get_tts_provider(self.cb_provider.currentText())
        test_out = CACHE_DIR / "voice_test.wav"
        sample_text = "Welcome to StickForge AI. Let's create an awesome animated stickman video!"
        try:
            dur = tts.synthesize(sample_text, test_out, voice=voice_id)
            QMessageBox.information(
                self,
                "Voice Test Successful",
                f"Generated speech sample ({dur:.1f}s) at:\n{test_out}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Voice Error", f"Speech synthesis failed:\n{e}")

    def _generate_all_audio(self) -> None:
        if not self.project or not self.project.scenes:
            QMessageBox.warning(self, "No Scenes", "Project has no scenes to synthesize.")
            return

        voice_id = self.cb_voice.currentData() or "en-US-ChristopherNeural"
        provider_name = self.cb_provider.currentText()

        self.btn_gen_all.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(5)

        self.worker = VoiceGenWorker(self.project, provider_name, voice_id)
        self.worker.progress.connect(self._on_progress)
        self.worker.finished_success.connect(self._on_success)
        self.worker.failed.connect(self._on_failed)
        self.worker.start()

    def _on_progress(self, pct: float, msg: str) -> None:
        self.progress_bar.setValue(int(pct))

    def _on_success(self) -> None:
        self.btn_gen_all.setEnabled(True)
        self.progress_bar.setVisible(False)
        self._refresh_table()
        QMessageBox.information(self, "Audio Generated", "All scene voice tracks synthesized and synchronized successfully!")

    def _on_failed(self, err: str) -> None:
        self.btn_gen_all.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Audio Error", f"Voice generation encountered an error:\n{err}")
