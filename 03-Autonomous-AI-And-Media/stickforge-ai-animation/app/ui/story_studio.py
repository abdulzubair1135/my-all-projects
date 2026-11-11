"""
Story Studio View for StickForge AI.
Handles AI script creation, structured story beats editing, visible DeepSeek browser controls,
and storyboard dispatch.
"""

from __future__ import annotations
from typing import Optional
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QPlainTextEdit,
    QLineEdit,
    QComboBox,
    QProgressBar,
    QMessageBox,
    QSplitter,
    QFrame,
)

from app.storage.project_manager import ProjectData, get_project_manager
from app.ai.ai_provider import get_ai_provider, GeneratedScript
from app.ai.deepseek_controller import get_deepseek_controller
from app.core.logging_manager import get_logger

logger = get_logger("story_studio_ui")


class StoryGenWorker(QThread):
    progress = Signal(float, str)
    finished_success = Signal(object)
    failed = Signal(str)

    def __init__(self, topic: str, genre: str, language: str, duration: float, provider_type: str):
        super().__init__()
        self.topic = topic
        self.genre = genre
        self.language = language
        self.duration = duration
        self.provider_type = provider_type

    def run(self):
        try:
            provider = get_ai_provider(self.provider_type)
            script = provider.generate_story(
                topic=self.topic,
                genre=self.genre,
                language=self.language,
                duration_target=self.duration,
                progress_callback=lambda p, m: self.progress.emit(p, m),
            )
            self.finished_success.emit(script)
        except Exception as e:
            logger.error(f"Story generation failed: {e}", exc_info=True)
            self.failed.emit(str(e))


class StoryStudioView(QWidget):
    """Interactive AI Story & Script Editor."""

    storyboard_ready = Signal()
    render_ready = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project: Optional[ProjectData] = None
        self.worker: Optional[StoryGenWorker] = None
        self.current_script: Optional[GeneratedScript] = None
        self.deepseek_ctrl = get_deepseek_controller()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        # 1. Header
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Story Studio")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #F8FAFC;")
        sub = QLabel("Write, prompt, and refine your animated story script.")
        sub.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(title)
        title_box.addWidget(sub)
        header.addLayout(title_box)
        header.addStretch()

        self.btn_save = QPushButton("Save Script")
        self.btn_save.setProperty("class", "btn-secondary")
        self.btn_save.clicked.connect(self._save_script)
        header.addWidget(self.btn_save)

        self.btn_to_storyboard = QPushButton("Convert to Storyboard ->")
        self.btn_to_storyboard.setProperty("class", "btn-secondary")
        self.btn_to_storyboard.clicked.connect(lambda: self._convert_to_storyboard(go_to_render=False))
        header.addWidget(self.btn_to_storyboard)

        self.btn_instant_render = QPushButton("🎬 Render Final Video (MP4)")
        self.btn_instant_render.setProperty("class", "btn-primary")
        self.btn_instant_render.clicked.connect(lambda: self._convert_to_storyboard(go_to_render=True))
        header.addWidget(self.btn_instant_render)

        layout.addLayout(header)

        # 2. AI Provider & Browser Controls Toolbar
        ai_toolbar = QFrame()
        ai_toolbar.setProperty("class", "card")
        ai_bar_layout = QHBoxLayout(ai_toolbar)
        ai_bar_layout.setContentsMargins(12, 8, 12, 8)
        ai_bar_layout.setSpacing(10)

        ai_bar_layout.addWidget(QLabel("AI Engine:"), 0)
        self.cb_ai_mode = QComboBox()
        self.cb_ai_mode.addItems([
            "Local Offline AI (Instant & Reliable)",
            "DeepSeek (Visible Browser)",
            "DeepSeek API",
        ])
        self.cb_ai_mode.currentIndexChanged.connect(self._on_ai_mode_changed)
        ai_bar_layout.addWidget(self.cb_ai_mode, 1)

        self.btn_open_browser = QPushButton("🌐 Open / Connect Browser")
        self.btn_open_browser.setProperty("class", "btn-secondary")
        self.btn_open_browser.clicked.connect(self._connect_browser)
        ai_bar_layout.addWidget(self.btn_open_browser)

        self.btn_check_session = QPushButton("🔍 Check Session")
        self.btn_check_session.setProperty("class", "btn-secondary")
        self.btn_check_session.clicked.connect(self._check_browser_session)
        ai_bar_layout.addWidget(self.btn_check_session)

        self.btn_focus_browser = QPushButton("👁️ Focus Browser")
        self.btn_focus_browser.setProperty("class", "btn-secondary")
        self.btn_focus_browser.clicked.connect(self.deepseek_ctrl.focus_browser)
        ai_bar_layout.addWidget(self.btn_focus_browser)

        self.lbl_session_status = QLabel("Session: Ready")
        self.lbl_session_status.setStyleSheet("color: #10B981; font-weight: 600; font-size: 12px;")
        ai_bar_layout.addWidget(self.lbl_session_status)

        layout.addWidget(ai_toolbar)

        # 3. Parameters Bar
        param_bar = QHBoxLayout()
        self.edit_topic = QLineEdit()
        self.edit_topic.setPlaceholderText("Enter story prompt or topic...")
        param_bar.addWidget(QLabel("Topic:"), 0)
        param_bar.addWidget(self.edit_topic, 2)

        self.cb_genre = QComboBox()
        self.cb_genre.addItems(["comedy", "suspense", "motivational", "action", "horror", "life_lessons"])
        param_bar.addWidget(QLabel("Genre:"), 0)
        param_bar.addWidget(self.cb_genre, 1)

        self.cb_lang = QComboBox()
        self.cb_lang.addItems(["hinglish", "english", "hindi"])
        param_bar.addWidget(QLabel("Lang:"), 0)
        param_bar.addWidget(self.cb_lang, 1)

        self.btn_generate = QPushButton("✨ Generate Script")
        self.btn_generate.setProperty("class", "btn-secondary")
        self.btn_generate.clicked.connect(lambda: self._generate_story(auto_render=False))
        param_bar.addWidget(self.btn_generate, 1)

        self.btn_quick_video = QPushButton("🚀 1-Click Generate & Make Video (MP4)")
        self.btn_quick_video.setProperty("class", "btn-primary")
        self.btn_quick_video.setStyleSheet("background-color: #2563EB; font-weight: 700; font-size: 13px; padding: 6px 14px;")
        self.btn_quick_video.clicked.connect(lambda: self._generate_story(auto_render=True))
        param_bar.addWidget(self.btn_quick_video, 2)

        layout.addLayout(param_bar)

        # 4. Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 5. Splitter: Left is script/narration, Right is Story Beats breakdown
        splitter = QSplitter(Qt.Horizontal)

        # Left editor
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setContentsMargins(0, 0, 8, 0)
        lbl_script = QLabel("Full Script & Narration Voiceover")
        lbl_script.setStyleSheet("font-weight: 600; color: #F1F5F9;")
        self.text_script = QPlainTextEdit()
        self.text_script.setPlaceholderText("Generated voiceover and dialogue lines will appear here...")
        left_layout.addWidget(lbl_script)
        left_layout.addWidget(self.text_script)
        splitter.addWidget(left_frame)

        # Right beats breakdown
        right_frame = QFrame()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(8, 0, 0, 0)
        lbl_beats = QLabel("Story Beats (Beginning, Conflict, Escalation, Climax, Ending)")
        lbl_beats.setStyleSheet("font-weight: 600; color: #F1F5F9;")
        self.text_beats = QPlainTextEdit()
        self.text_beats.setPlaceholderText("Story beats breakdown...")
        right_layout.addWidget(lbl_beats)
        right_layout.addWidget(self.text_beats)
        splitter.addWidget(right_frame)

        layout.addWidget(splitter)
        self._on_ai_mode_changed(0)

    def _on_ai_mode_changed(self, idx: int) -> None:
        is_browser = "DeepSeek (Visible" in self.cb_ai_mode.currentText()
        self.btn_open_browser.setVisible(is_browser)
        self.btn_check_session.setVisible(is_browser)
        self.btn_focus_browser.setVisible(is_browser)
        if not is_browser:
            self.lbl_session_status.setText("Engine: Local Instant AI Active")
            self.lbl_session_status.setStyleSheet("color: #38BDF8; font-weight: 600; font-size: 12px;")
        else:
            self.lbl_session_status.setText("Session: DeepSeek Browser")
            self.lbl_session_status.setStyleSheet("color: #F59E0B; font-weight: 600; font-size: 12px;")

    def _connect_browser(self) -> None:
        try:
            self.lbl_session_status.setText("Connecting Chromium...")
            res = self.deepseek_ctrl.connect_or_launch()
            st = res.get("state", "UNKNOWN")
            if st == "LOGGED_IN":
                self.lbl_session_status.setText("Session: Logged In & Ready")
                self.lbl_session_status.setStyleSheet("color: #10B981; font-weight: 600;")
                QMessageBox.information(self, "DeepSeek Connected", "DeepSeek browser is ready!")
            else:
                self.lbl_session_status.setText(f"Session: {st}")
                self.lbl_session_status.setStyleSheet("color: #F59E0B; font-weight: 600;")
                QMessageBox.information(
                    self,
                    "Browser Opened",
                    f"Chromium browser opened.\nCurrent state: {st}.\nPlease log in or complete verification in the browser window.",
                )
        except Exception as e:
            QMessageBox.critical(self, "Browser Error", f"Could not launch browser:\n{e}")

    def _check_browser_session(self) -> None:
        res = self.deepseek_ctrl.check_session()
        st = res.get("state", "UNKNOWN")
        if res.get("ready"):
            self.lbl_session_status.setText("Session: Logged In & Ready")
            self.lbl_session_status.setStyleSheet("color: #10B981; font-weight: 600;")
            QMessageBox.information(self, "Session Ready", "DeepSeek session is authenticated and ready.")
        else:
            self.lbl_session_status.setText(f"Session: {st}")
            self.lbl_session_status.setStyleSheet("color: #EF4444; font-weight: 600;")
            QMessageBox.warning(self, "Session Status", f"DeepSeek status: {st}\nDetails: {res.get('details')}")

    def load_project(self, project: ProjectData) -> None:
        self.project = project
        if project.topic and not self.edit_topic.text():
            self.edit_topic.setText(project.topic)
        self.cb_genre.setCurrentText(project.genre)
        self.cb_lang.setCurrentText(project.language)
        if project.script_text:
            self.text_script.setPlainText(project.script_text)

    def _generate_story(self, auto_render: bool = False) -> None:
        self._auto_render_mode = auto_render
        topic = self.edit_topic.text().strip() or "A Stickman Journey"
        genre = self.cb_genre.currentText()
        language = self.cb_lang.currentText()
        duration = self.project.duration_target if self.project else 30.0

        mode_text = self.cb_ai_mode.currentText()
        if "Local" in mode_text:
            provider_type = "mock"
        elif "API" in mode_text:
            provider_type = "deepseek_api"
        else:
            provider_type = "deepseek_browser"

        self.btn_generate.setEnabled(False)
        self.btn_quick_video.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)

        self.worker = StoryGenWorker(topic, genre, language, duration, provider_type)
        self.worker.progress.connect(self._on_worker_progress)
        self.worker.finished_success.connect(self._on_story_success)
        self.worker.failed.connect(self._on_story_failed)
        self.worker.start()

    def _on_worker_progress(self, pct: float, msg: str) -> None:
        self.progress_bar.setValue(int(pct))

    def _on_story_success(self, script: GeneratedScript) -> None:
        self.current_script = script
        self.btn_generate.setEnabled(True)
        self.btn_quick_video.setEnabled(True)
        self.progress_bar.setVisible(False)

        # Populate fields
        self.text_script.setPlainText(script.full_narration)
        beats_summary = []
        for b in script.beats:
            beats_summary.append(f"[{b.beat_name.upper()}] ({b.estimated_duration:.1f}s):\n{b.narration}\n")
        self.text_beats.setPlainText("\n".join(beats_summary))

        if self.project:
            self.project.script_text = script.full_narration
            self.project.name = script.title
            get_project_manager().save_project(self.project)

        if getattr(self, "_auto_render_mode", False):
            # Automatically convert to storyboard and proceed to video render!
            self._convert_to_storyboard(go_to_render=True)
        else:
            self.lbl_session_status.setText(f"✓ Story '{script.title}' ready! Click 'Render Final Video' when ready.")
            self.lbl_session_status.setStyleSheet("color: #10B981; font-weight: 600; font-size: 12px;")
            QMessageBox.information(
                self,
                "Story Generated",
                f"Story '{script.title}' generated successfully!\n\nClick '🎬 Render Final Video (MP4)' to create your video.",
            )

    def _on_story_failed(self, err_msg: str) -> None:
        self.btn_generate.setEnabled(True)
        self.btn_quick_video.setEnabled(True)
        self.progress_bar.setVisible(False)

        # If DeepSeek has an auth/block error, offer 1-click fallback to Local AI
        if "CloudFront" in err_msg or "DeepSeek" in err_msg or "login" in err_msg.lower():
            reply = QMessageBox.question(
                self,
                "DeepSeek Session Notice",
                f"{err_msg}\n\nWould you like to generate this story instantly using the Local Offline AI Engine instead?",
                QMessageBox.Yes | QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.cb_ai_mode.setCurrentIndex(0)  # Switch to Local Offline
                self._generate_story(auto_render=getattr(self, "_auto_render_mode", False))
                return

        QMessageBox.critical(self, "Generation Notice", f"Generation could not proceed:\n\n{err_msg}")

    def _save_script(self) -> None:
        if self.project:
            self.project.script_text = self.text_script.toPlainText()
            get_project_manager().save_project(self.project)
            QMessageBox.information(self, "Saved", "Script saved successfully.")

    def _convert_to_storyboard(self, go_to_render: bool = False) -> None:
        if not self.text_script.toPlainText().strip():
            QMessageBox.warning(self, "Empty Script", "Please generate or write a script first.")
            return

        provider = get_ai_provider("mock")
        if not self.current_script:
            self.current_script = provider.generate_story(
                topic=self.edit_topic.text() or "Stickman Story",
                genre=self.cb_genre.currentText(),
                language=self.cb_lang.currentText(),
                duration_target=self.project.duration_target if self.project else 30.0,
            )
            self.current_script.full_narration = self.text_script.toPlainText()

        proj_id = self.project.id if self.project else "proj_default"
        sb = provider.generate_storyboard(
            project_id=proj_id,
            script=self.current_script,
            aspect_ratio=self.project.aspect_ratio if self.project else "9:16",
        )

        if self.project:
            from app.storage.project_manager import SceneModel, SceneAction, CameraModel
            self.project.scenes = [
                SceneModel(
                    id=s.id,
                    sequence_order=s.sequence_order,
                    duration=s.duration,
                    background=s.background,
                    narration=s.narration,
                    camera=CameraModel(shot=s.camera.shot, movement=s.camera.movement),
                    actions=[SceneAction(character_id=a.character_id, action=a.action) for a in s.actions],
                )
                for s in sb.scenes
            ]
            get_project_manager().save_project(self.project)

        if go_to_render:
            self.render_ready.emit()
        else:
            self.storyboard_ready.emit()
            QMessageBox.information(
                self,
                "Storyboard Created",
                f"Converted script into {len(sb.scenes)} timed stickman scenes!",
            )
