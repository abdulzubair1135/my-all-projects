"""
Settings view for StickForge AI.
Configures AI providers, browser automation, TTS preferences, rendering profiles, and cache management.
"""

from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QLineEdit,
    QGroupBox,
    QFormLayout,
    QMessageBox,
    QScrollArea,
)

from app.core.config import get_config, save_config
from app.core.resource_manager import get_resource_manager


class SettingsView(QWidget):
    """Studio settings panel."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.config = get_config()
        self.resource_mgr = get_resource_manager()
        self._setup_ui()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(20)

        # Header
        title = QLabel("Settings & Preferences")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #F8FAFC;")
        layout.addWidget(title)

        # 1. AI Settings Group
        grp_ai = QGroupBox("AI Provider & DeepSeek Configuration")
        ai_form = QFormLayout(grp_ai)
        self.cb_ai_provider = QComboBox()
        self.cb_ai_provider.addItems(["deepseek_browser", "deepseek_api", "mock"])
        self.cb_ai_provider.setCurrentText(self.config.ai.provider)
        ai_form.addRow("Active Provider:", self.cb_ai_provider)

        self.edit_api_key = QLineEdit()
        self.edit_api_key.setEchoMode(QLineEdit.Password)
        self.edit_api_key.setPlaceholderText("Optional DeepSeek API Key (leave blank for browser mode)")
        self.edit_api_key.setText(self.config.ai.deepseek_api_key)
        ai_form.addRow("API Key:", self.edit_api_key)
        layout.addWidget(grp_ai)

        # 2. Browser Automation Settings Group
        grp_browser = QGroupBox("Chromium Browser Automation")
        b_form = QFormLayout(grp_browser)
        self.chk_headless = QCheckBox("Run Headless (Not recommended: browser must be visible for DeepSeek)")
        self.chk_headless.setChecked(self.config.browser.headless)
        b_form.addRow(self.chk_headless)

        self.spin_slow_mo = QSpinBox()
        self.spin_slow_mo.setRange(0, 1000)
        self.spin_slow_mo.setValue(self.config.browser.slow_mo_ms)
        self.spin_slow_mo.setSuffix(" ms")
        b_form.addRow("Action Delay (Slow-mo):", self.spin_slow_mo)
        layout.addWidget(grp_browser)

        # 3. Audio & Voice Settings Group
        grp_tts = QGroupBox("Text-to-Speech (TTS)")
        tts_form = QFormLayout(grp_tts)
        self.cb_tts_provider = QComboBox()
        self.cb_tts_provider.addItems(["edge_tts", "pyttsx3"])
        self.cb_tts_provider.setCurrentText(self.config.tts.default_provider)
        tts_form.addRow("Default Provider:", self.cb_tts_provider)

        self.edit_voice_en = QLineEdit(self.config.tts.default_voice_en)
        tts_form.addRow("Default English Voice:", self.edit_voice_en)

        self.edit_voice_hi = QLineEdit(self.config.tts.default_voice_hi)
        tts_form.addRow("Default Hindi Voice:", self.edit_voice_hi)
        layout.addWidget(grp_tts)

        # 4. Video & Rendering Group
        grp_video = QGroupBox("Video Encoding Defaults")
        v_form = QFormLayout(grp_video)
        self.spin_fps = QSpinBox()
        self.spin_fps.setRange(15, 60)
        self.spin_fps.setValue(self.config.video.default_fps)
        v_form.addRow("Default FPS:", self.spin_fps)

        self.spin_crf = QSpinBox()
        self.spin_crf.setRange(15, 35)
        self.spin_crf.setValue(self.config.video.crf)
        v_form.addRow("Video Quality (CRF):", self.spin_crf)
        layout.addWidget(grp_video)

        # 5. Cache & Storage Management
        grp_storage = QGroupBox("Cache & Storage")
        s_layout = QVBoxLayout(grp_storage)
        cache_size = self.resource_mgr.get_cache_size_mb()
        self.lbl_cache = QLabel(f"Current Cache Size: {cache_size} MB")
        s_layout.addWidget(self.lbl_cache)

        btn_clear_cache = QPushButton("Purge Render & Audio Cache")
        btn_clear_cache.setProperty("class", "btn-secondary")
        btn_clear_cache.clicked.connect(self._clear_cache)
        s_layout.addWidget(btn_clear_cache)
        layout.addWidget(grp_storage)

        # Save Button
        btn_save = QPushButton("Save Settings")
        btn_save.setProperty("class", "btn-primary")
        btn_save.setMinimumHeight(38)
        btn_save.clicked.connect(self._save_settings)
        layout.addWidget(btn_save)

        layout.addStretch()
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _clear_cache(self) -> None:
        self.resource_mgr.clear_cache()
        self.lbl_cache.setText(f"Current Cache Size: {self.resource_mgr.get_cache_size_mb()} MB")
        QMessageBox.information(self, "Cache Cleared", "Temporary render cache has been cleared.")

    def _save_settings(self) -> None:
        self.config.ai.provider = self.cb_ai_provider.currentText()
        self.config.ai.deepseek_api_key = self.edit_api_key.text().strip()
        self.config.browser.headless = self.chk_headless.isChecked()
        self.config.browser.slow_mo_ms = self.spin_slow_mo.value()
        self.config.tts.default_provider = self.cb_tts_provider.currentText()
        self.config.tts.default_voice_en = self.edit_voice_en.text().strip()
        self.config.tts.default_voice_hi = self.edit_voice_hi.text().strip()
        self.config.video.default_fps = self.spin_fps.value()
        self.config.video.crf = self.spin_crf.value()

        save_config(self.config)
        QMessageBox.information(self, "Settings Saved", "Preferences updated successfully.")
