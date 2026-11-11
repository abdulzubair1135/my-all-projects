# modules/ui_manager.py
"""
UI Manager - Main Window with Professional Design and Ollama Integration
Thread‑safe: all UI updates happen in main thread via signals.
"""

import sys
import os
import json
import requests
import queue
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import math
import threading

try:
    from PyQt5.QtWidgets import QSystemTrayIcon, QMenu
except ImportError:
    QSystemTrayIcon = None


class AnimatedFace(QWidget):
    """Custom animated face widget with multiple expressions and smooth transitions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 250)
        self.setMaximumSize(400, 300)
        
        self.state = "idle"
        self.blink_state = 0
        self.pupil_offset = 0
        self.glow_intensity = 0
        self.breathing = 0
        self.thinking_dots = 0
        self.sound_wave = 0
        
        

        self.primary_color = QColor(0, 255, 255)
        self.secondary_color = QColor(100, 200, 255)
        self.bg_color = QColor(10, 10, 20)

        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self._do_blink)
        self.blink_timer.start(3000)

        self.breathing_timer = QTimer()
        self.breathing_timer.timeout.connect(self._update_breathing)
        self.breathing_timer.start(50)

        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update)
        self.animation_timer.start(33)

        self.dot_timer = QTimer()
        self.dot_timer.timeout.connect(self._update_dots)

    def _do_blink(self):
        self.blink_state = 10
        QTimer.singleShot(150, self._reset_blink)

    def _reset_blink(self):
        self.blink_state = 0

    def _update_breathing(self):
        self.breathing = (self.breathing + 0.1) % (2 * math.pi)
        if self.state in ["listening", "thinking", "searching"]:
            self.glow_intensity = 0.5 + 0.5 * math.sin(self.breathing)
        self.update()

    def _update_dots(self):
        self.thinking_dots = (self.thinking_dots + 1) % 4
        self.update()

    def set_state(self, state):
        self.state = state
        if state == "thinking" or state == "searching":
            self.thinking_dots = 0
            self.dot_timer.start(500)
        else:
            self.dot_timer.stop()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QRadialGradient(self.width()/2, self.height()/2, self.width()/2)
        gradient.setColorAt(0, QColor(15, 15, 30))
        gradient.setColorAt(1, QColor(5, 5, 15))
        painter.fillRect(self.rect(), gradient)

        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2 - 20

        painter.setPen(QPen(self.primary_color, 3))
        painter.setBrush(QBrush(QColor(20, 20, 40, 200)))
        painter.drawRoundedRect(cx - 80, cy - 70, 160, 140, 20, 20)

        if self.state in ["listening", "thinking", "searching"]:
            glow_pen = QPen(QColor(0, 255, 255, int(50 + 50 * self.glow_intensity)), 2)
            painter.setPen(glow_pen)
            painter.drawRoundedRect(cx - 85, cy - 75, 170, 150, 20, 20)

        eye_y = cy - 25
        left_eye_x = cx - 30
        right_eye_x = cx + 30

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(left_eye_x - 10, eye_y - 10, 20, 20)
        painter.drawEllipse(right_eye_x - 10, eye_y - 10, 20, 20)

        if self.state == "listening":
            self.pupil_offset = int(3 * math.sin(self.breathing * 2))
        elif self.state == "thinking":
            self.pupil_offset = int(2 * math.sin(self.breathing))
        else:
            self.pupil_offset = 0

        painter.setBrush(QBrush(self.primary_color))
        painter.drawEllipse(left_eye_x - 5 + self.pupil_offset, eye_y - 5, 10, 10)
        painter.drawEllipse(right_eye_x - 5 + self.pupil_offset, eye_y - 5, 10, 10)

        if self.blink_state > 0:
            painter.setPen(QPen(self.primary_color, 2))
            painter.setBrush(QBrush(self.bg_color))
            painter.drawRect(left_eye_x - 12, eye_y - 12, 24, 8)
            painter.drawRect(right_eye_x - 12, eye_y - 12, 24, 8)

        mouth_y = cy + 15

        if self.state == "speaking":
            self.sound_wave = (self.sound_wave + 1) % 20
            amplitude = 5 + 5 * math.sin(self.sound_wave * 0.3)
            path = QPainterPath()
            path.moveTo(cx - 30, mouth_y)
            path.cubicTo(cx - 15, mouth_y - amplitude,
                         cx + 15, mouth_y - amplitude,
                         cx + 30, mouth_y)
            painter.setPen(QPen(self.primary_color, 3))
            painter.drawPath(path)

            for i in range(3):
                alpha = 100 - i * 30
                painter.setPen(QPen(QColor(0, 255, 255, alpha), 2))
                painter.drawEllipse(cx - 5, mouth_y + 5 + i*8, 10 + i*5, 5 + i*3)

        elif self.state == "listening":
            painter.setPen(QPen(self.primary_color, 3))
            painter.drawArc(cx - 20, mouth_y - 5, 40, 15, 30 * 16, 120 * 16)

        elif self.state == "thinking":
            painter.setPen(QPen(self.primary_color, 3))
            painter.drawLine(cx - 20, mouth_y, cx + 20, mouth_y)

            painter.setPen(QPen(self.primary_color, 4))
            for i in range(3):
                if i < self.thinking_dots:
                    painter.setBrush(QBrush(self.primary_color))
                else:
                    painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(cx - 10 + i*10, mouth_y + 5, 5, 5)

        elif self.state == "happy":
            painter.setPen(QPen(self.primary_color, 3))
            painter.drawArc(cx - 25, mouth_y - 10, 50, 25, 0, 180 * 16)

        elif self.state == "sad":
            painter.setPen(QPen(self.primary_color, 3))
            painter.drawArc(cx - 25, mouth_y, 50, 25, 180 * 16, 180 * 16)

        elif self.state == "searching":
            painter.setPen(QPen(self.primary_color, 3))
            painter.drawArc(cx - 20, mouth_y - 5, 40, 15, 0, 360 * 16)

        else:
            painter.setPen(QPen(self.primary_color, 3))
            painter.drawLine(cx - 20, mouth_y, cx + 20, mouth_y)

        painter.setPen(QPen(QColor(150, 150, 200), 1))
        painter.setFont(QFont("Segoe UI", 10, QFont.Bold))

        status_text = {
            "listening": "🎤 LISTENING",
            "thinking": "🤔 THINKING",
            "speaking": "🗣️ SPEAKING",
            "happy": "😊 HAPPY",
            "sad": "😔 SAD",
            "searching": "🔍 SEARCHING",
            "idle": "⚡ CLEVER"
        }.get(self.state, "⚡ CLEVER")

        painter.drawText(self.rect().adjusted(0, 30, 0, 0),
                         Qt.AlignBottom | Qt.AlignHCenter, status_text)


class SettingsDialog(QDialog):
    """Settings dialog for configuring Arduino port, Ollama, and testing connection."""
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(450, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        arduino_group = QGroupBox("Arduino")
        arduino_layout = QFormLayout()
        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        ports = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10"]
        self.port_combo.addItems(ports)
        self.port_combo.setCurrentText(self.config.get("arduino_port", "COM3"))
        arduino_layout.addRow("Port:", self.port_combo)

        lcd_note = QLabel("Note: LCD address in Arduino code should be 0x27 or 0x3F.")
        lcd_note.setWordWrap(True)
        lcd_note.setStyleSheet("color: #88aaff; font-size: 10px;")
        arduino_layout.addRow(lcd_note)

        arduino_group.setLayout(arduino_layout)
        layout.addWidget(arduino_group)

        ollama_group = QGroupBox("Ollama")
        ollama_layout = QFormLayout()
        self.ollama_enabled = QCheckBox("Enable Ollama")
        self.ollama_enabled.setChecked(self.config.get("ollama", {}).get("enabled", False))
        self.ollama_url = QLineEdit(self.config.get("ollama", {}).get("url", "http://localhost:11434"))
        self.custom_model = QLineEdit(self.config.get("ollama", {}).get("model", "deepseek-r1:8b"))
        ollama_layout.addRow(self.ollama_enabled)
        ollama_layout.addRow("URL:", self.ollama_url)
        ollama_layout.addRow("Model (or custom):", self.custom_model)

        self.test_ollama_btn = QPushButton("Test Connection")
        self.test_ollama_btn.clicked.connect(self.test_ollama)
        self.test_ollama_result = QLabel("")
        self.test_ollama_result.setWordWrap(True)
        ollama_layout.addRow(self.test_ollama_btn, self.test_ollama_result)

        ollama_group.setLayout(ollama_layout)
        layout.addWidget(ollama_group)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def test_ollama(self):
        url = self.ollama_url.text().rstrip('/')
        model = self.custom_model.text()
        self.test_ollama_result.setText("Testing...")
        QApplication.processEvents()
        try:
            response = requests.get(url + "/api/tags", timeout=3)
            if response.status_code == 200:
                data = response.json()
                models = [m['name'] for m in data.get('models', [])]
                if model in models:
                    self.test_ollama_result.setText(f"✅ OK! Model '{model}' found.")
                else:
                    self.test_ollama_result.setText(f"⚠️ Server OK, but model '{model}' not found.\nAvailable: {', '.join(models)}")
            else:
                self.test_ollama_result.setText(f"❌ Server error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.test_ollama_result.setText("❌ Cannot connect to Ollama. Is it running?")
        except Exception as e:
            self.test_ollama_result.setText(f"❌ Error: {e}")

    def get_config(self):
        new_config = self.config.copy()
        new_config["arduino_port"] = self.port_combo.currentText()
        if "ollama" not in new_config:
            new_config["ollama"] = {}
        new_config["ollama"]["enabled"] = self.ollama_enabled.isChecked()
        new_config["ollama"]["url"] = self.ollama_url.text()
        new_config["ollama"]["model"] = self.custom_model.text()
        return new_config


class CleverWindow(QMainWindow):
    """Main application window with professional design – thread‑safe."""

    # Signals for thread‑safe UI updates
    message_signal = pyqtSignal(str, str)   # (sender, message)
    face_state_signal = pyqtSignal(str)     # state name
    voice_text_signal = pyqtSignal(str)     # recognized text

    def __init__(self, ai, arduino, voice, memory, config):
        super().__init__()
        self.waiting = False
        self.waiting_mode = False
        self.ai = ai
        self.arduino = arduino
        self.voice = voice
        self.memory = memory
        self.config = config
        self.is_listening = False
        self.is_minimized_to_tray = False
        self.is_speaking = False
        # Create UI first – this creates self.face and other widgets
        self.init_ui()

        # Connect signals (face now exists)
        self.message_signal.connect(self._add_message)
        self.face_state_signal.connect(self.face.set_state)
        self.voice_text_signal.connect(self.on_voice_text)

        # Setup voice callbacks (these will emit signals)
        self.setup_callbacks()

        # Other initialisations
        self.refresh_notes()
        self.setup_system_tray()
        self.update_arduino_status()

        # Now add the welcome message (after signals are connected)
        self.add_message("CLEVER", "Hello! I'm CLEVER. How can I help you today?")

    def init_ui(self):
        self.setWindowTitle("CLEVER AI Assistant")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Left panel
        left_panel = QWidget()
        left_panel.setFixedWidth(250)
        left_panel.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                              stop:0 #0a0a14, stop:1 #0f0f1a);
            border-right: 1px solid #2a2a3a;
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(20)
        left_layout.setContentsMargins(10, 20, 10, 20)

        title_label = QLabel("⚡ CLEVER AI")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #00ffff;")
        title_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title_label)

        # Quick Actions
        quick_group = QGroupBox("Quick Actions")
        quick_group.setStyleSheet("QGroupBox { color: #88aaff; border: 1px solid #2a2a3a; border-radius: 8px; margin-top: 10px; }")
        quick_layout = QVBoxLayout()

        self.time_btn = QPushButton("🕐 Time")
        self.time_btn.clicked.connect(lambda: self.process_text("time"))
        self.date_btn = QPushButton("📅 Date")
        self.date_btn.clicked.connect(lambda: self.process_text("date"))
        self.joke_btn = QPushButton("😂 Joke")
        self.joke_btn.clicked.connect(lambda: self.process_text("joke"))
        self.remember_btn = QPushButton("📝 Remember")
        self.remember_btn.clicked.connect(self.quick_remember)

        quick_layout.addWidget(self.time_btn)
        quick_layout.addWidget(self.date_btn)
        quick_layout.addWidget(self.joke_btn)
        quick_layout.addWidget(self.remember_btn)
        quick_group.setLayout(quick_layout)
        left_layout.addWidget(quick_group)

        # Mode
        mode_group = QGroupBox("Mode")
        mode_group.setStyleSheet("QGroupBox { color: #88aaff; border: 1px solid #2a2a3a; border-radius: 8px; margin-top: 10px; }")
        mode_layout = QVBoxLayout()

        self.google_mode_btn = QPushButton("🌐 Google Search")
        self.google_mode_btn.setCheckable(True)
        self.google_mode_btn.setChecked(self.ai.google_mode)
        self.google_mode_btn.clicked.connect(self.toggle_google)

        self.ollama_mode_btn = QPushButton("🤖 Ollama AI")
        self.ollama_mode_btn.setCheckable(True)
        self.ollama_mode_btn.setChecked(self.ai.use_ollama)
        self.ollama_mode_btn.clicked.connect(self.toggle_ollama)

        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.ollama_model_combo = QComboBox()
        self.ollama_model_combo.setEditable(True)
        self.ollama_model_combo.addItems(["llama2", "mistral", "phi", "neural-chat", "deepseek-r1:8b","gemma3:1b"])
        self.ollama_model_combo.setCurrentText(self.ai.ollama_model if self.ai.ollama else "deepseek-r1:8b")
        self.ollama_model_combo.currentTextChanged.connect(self.change_ollama_model)
        model_layout.addWidget(self.ollama_model_combo)

        mode_layout.addWidget(self.google_mode_btn)
        mode_layout.addWidget(self.ollama_mode_btn)
        mode_layout.addLayout(model_layout)
        mode_group.setLayout(mode_layout)
        left_layout.addWidget(mode_group)

        # Status
        status_group = QGroupBox("Status")
        status_group.setStyleSheet("QGroupBox { color: #88aaff; border: 1px solid #2a2a3a; border-radius: 8px; margin-top: 10px; }")
        status_layout = QVBoxLayout()

        self.arduino_status = QLabel("🔌 Arduino: Connecting...")
        self.arduino_status.setStyleSheet("color: #ffff00;")
        status_layout.addWidget(self.arduino_status)

        self.mode_indicator = QLabel("🌐 Mode: " + ("Google" if self.ai.google_mode else ("Ollama" if self.ai.use_ollama else "Basic")))
        self.mode_indicator.setStyleSheet("color: #00ffff;")
        status_layout.addWidget(self.mode_indicator)

        self.reconnect_arduino_btn = QPushButton("Reconnect Arduino")
        self.reconnect_arduino_btn.clicked.connect(self.reconnect_arduino)
        status_layout.addWidget(self.reconnect_arduino_btn)

        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.clicked.connect(self.open_settings)
        status_layout.addWidget(self.settings_btn)

        status_group.setLayout(status_layout)
        left_layout.addWidget(status_group)

        left_layout.addStretch()
        main_layout.addWidget(left_panel)

        # Center panel
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(20, 20, 20, 20)

        face_container = QWidget()
        face_container.setStyleSheet("background-color: rgba(20,20,40,0.5); border-radius: 20px;")
        face_layout = QVBoxLayout(face_container)
        self.face = AnimatedFace()
        self.face.setStyleSheet("border: none;")
        face_layout.addWidget(self.face, alignment=Qt.AlignCenter)
        center_layout.addWidget(face_container)

        chat_label = QLabel("💬 Conversation")
        chat_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ffff; margin-top: 15px;")
        center_layout.addWidget(chat_label)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet("""
            background-color: rgba(15,15,25,0.9);
            border: 1px solid #2a2a3a;
            border-radius: 10px;
            padding: 10px;
            font-family: 'Segoe UI', 'Consolas', monospace;
            font-size: 12px;
        """)
        center_layout.addWidget(self.chat)

        input_layout = QHBoxLayout()
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(80)
        self.input_field.setPlaceholderText("Type your message here... (Press Enter to send)")
        self.input_field.setStyleSheet("""
            background-color: rgba(15,15,25,0.9);
            border: 1px solid #2a2a3a;
            border-radius: 10px;
            padding: 8px;
        """)
        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedWidth(80)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        center_layout.addLayout(input_layout)

        voice_layout = QHBoxLayout()
        self.listen_btn = QPushButton("🎤 Start Listening")
        self.switch_stt_btn = QPushButton("🔄 Switch STT (VOSK/Google)")
        self.switch_stt_btn.clicked.connect(self.toggle_stt)
        voice_layout.addWidget(self.switch_stt_btn)
        self.listen_btn.setCheckable(True)
        self.listen_btn.clicked.connect(self.toggle_listen)
        voice_layout.addWidget(self.listen_btn)

        self.stop_voice_btn = QPushButton("🔇 Stop Speaking")
        self.stop_voice_btn.clicked.connect(self.stop_speaking)
        voice_layout.addWidget(self.stop_voice_btn)

        center_layout.addLayout(voice_layout)

        main_layout.addWidget(center_panel, stretch=1)

        # Right panel
        right_panel = QWidget()
        right_panel.setFixedWidth(280)
        right_panel.setStyleSheet("background-color: #0f0f1a; border-left: 1px solid #2a2a3a;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 20, 10, 20)

        notes_label = QLabel("📝 Notes")
        notes_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #88aaff;")
        right_layout.addWidget(notes_label)

        self.notes_list = QListWidget()
        self.notes_list.setStyleSheet("background-color: rgba(20,20,40,0.6); border-radius: 8px;")
        right_layout.addWidget(self.notes_list)

        note_input_layout = QHBoxLayout()
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Add a note...")
        self.note_input.returnPressed.connect(self.save_note)
        self.note_btn = QPushButton("Save")
        self.note_btn.clicked.connect(self.save_note)
        note_input_layout.addWidget(self.note_input)
        note_input_layout.addWidget(self.note_btn)
        right_layout.addLayout(note_input_layout)

        history_label = QLabel("📜 Recent Commands")
        history_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #88aaff; margin-top: 20px;")
        right_layout.addWidget(history_label)

        self.history_list = QListWidget()
        self.history_list.setStyleSheet("background-color: rgba(20,20,40,0.6); border-radius: 8px;")
        right_layout.addWidget(self.history_list)

        right_layout.addStretch()
        main_layout.addWidget(right_panel)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a14;
            }
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                  stop:0 #1a1a2a, stop:1 #0f0f1a);
                color: #00ffff;
                border: 1px solid #00ffff;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ffff;
                color: #0a0a14;
            }
            QPushButton:checked {
                background-color: #00aa88;
                border-color: #00ffaa;
                color: white;
            }
            QLineEdit, QTextEdit, QListWidget {
                background-color: #1a1a2a;
                color: #ccddff;
                border: 1px solid #2a2a3a;
                border-radius: 6px;
                padding: 4px;
            }
            QGroupBox {
                color: #88aaff;
                border: 1px solid #2a2a3a;
                border-radius: 8px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #ccddff;
            }
        """)

    def setup_callbacks(self):
        self.voice.on_speech(lambda text: self.voice_text_signal.emit(text))
        self.voice.on_listening_start(lambda: self.face_state_signal.emit("listening"))
        self.voice.on_listening_stop(lambda: self.face_state_signal.emit("idle"))
        self.voice.on_speaking_start(lambda: self.face_state_signal.emit("speaking"))
        self.voice.on_speaking_stop(lambda: self.face_state_signal.emit("idle"))
        
    def toggle_stt(self):
        if self.voice.current_engine == "vosk":
            self.voice.set_engine("google")
            self.add_message("CLEVER", "Switched to Google Speech")
        else:
            self.voice.set_engine("vosk")
            self.add_message("CLEVER", "Switched to VOSK")
    def on_voice_text(self, text):
        text = text.lower()
        # 🔥 SPEAKING LOCK
        if self.is_speaking:
            if "stop" in text:
                self.voice.stop()
                self.is_speaking = False
            return
        self.add_message("YOU", f"[voice] {text}")

        # STOP
        if "stop" in text:
            

            # 🔥 YE LINE ADD KAR (IMPORTANT)
            self.voice.stop()

            if self.arduino:
                self.arduino.send_message(" | ")

            self.add_message("CLEVER", "Stopped")
            return

        # WAKE
        if "hey clever" in text or "hey glover" in text or "the glover" in text or " glover" in text or "the clever" in text or "clever" in text or "hello" in text:
            self.voice.stop_listening()
            self.voice.speak("Yes I am listening")

            
            QTimer.singleShot(2500, self.voice.start_listening)

            self.waiting = True
            return

        # 🔥 MODE REQUEST (only when user asks)
        if ("mode" in text or "function" in text) and getattr(self, "waiting", False):
            self.voice.stop_listening()
            self.voice.speak("Which mode? simple, offline, online or google")

            
            QTimer.singleShot(2500, self.voice.start_listening)

            self.waiting_mode = True
            return

        # 🔥 MODE SELECT (LOCK MODE)
        if getattr(self, "waiting_mode", False):

            self.waiting_mode = False

            if "simple" in text:
                response = self.ai.set_mode("simple")

            elif "ollama" in text or "offline" in text:
                response = self.ai.set_mode("ollama")

            elif "api" in text or "online" in text:
                response = self.ai.set_mode("api")

            elif "google" in text:
                response = self.ai.set_mode("google")

            else:
                response = "Mode not recognized"

            self.voice.stop_listening()
            self.is_speaking = True
            self.voice.speak(response)

            QTimer.singleShot(3000, lambda: setattr(self, "is_speaking", False))
            self.add_message("CLEVER", response)
            QTimer.singleShot(2500, self.voice.start_listening)
            return

        # 🔥 NORMAL COMMAND (NO MODE CHANGE HERE)
        if self.waiting:
            self.waiting = False

            self.voice.stop_listening()

            response = self.ai.handle(text)

            self.add_message("CLEVER", response)

            # 🔥 mic auto ON again
            
            QTimer.singleShot(2500, self.voice.start_listening)
    def add_message(self, sender, message):
        self.message_signal.emit(sender, message)

    def _add_message(self, sender, message):
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        color = "#00ffff" if sender == "CLEVER" else "#ffffff"
        formatted = f'<font color="#88aaff">[{timestamp}]</font> '
        formatted += f'<font color="{color}" style="font-weight: bold;">{sender}:</font> '
        formatted += f'<font color="#dddddd">{message}</font>'
        self.chat.append(formatted)
        self.chat.verticalScrollBar().setValue(self.chat.verticalScrollBar().maximum())
        if sender == "YOU":
            self.history_list.insertItem(0, f"{timestamp} - {message[:40]}...")
            if self.history_list.count() > 20:
                self.history_list.takeItem(20)

    def setup_system_tray(self):
        if QSystemTrayIcon is not None:
            self.tray_icon = QSystemTrayIcon(self)
            tray_menu = QMenu()
            show_action = tray_menu.addAction("Show")
            show_action.triggered.connect(self.show_normal)
            quit_action = tray_menu.addAction("Quit")
            quit_action.triggered.connect(self.quit_app)
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
        else:
            self.tray_icon = None

    def show_normal(self):
        self.showNormal()
        self.activateWindow()

    def quit_app(self):
        self.voice.stop()
        if self.arduino:
            self.arduino.disconnect()
        QApplication.quit()

    def closeEvent(self, event):
        if self.tray_icon and self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage("CLEVER AI", "Application minimized to tray.", QSystemTrayIcon.Information, 2000)
            event.ignore()
        else:
            reply = QMessageBox.question(
                self, "Exit",
                "Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.voice.stop()
                if self.arduino:
                    self.arduino.disconnect()
                event.accept()
            else:
                event.ignore()

    def update_arduino_status(self):
        if self.arduino and self.arduino.is_connected:
            self.arduino_status.setText("🔌 Arduino: Connected")
            self.arduino_status.setStyleSheet("color: #00ff00;")
        else:
            self.arduino_status.setText("🔌 Arduino: Disconnected")
            self.arduino_status.setStyleSheet("color: #ff6666;")

    def reconnect_arduino(self):
        self.arduino.disconnect()
        if self.arduino.connect():
            self.update_arduino_status()
            self.add_message("CLEVER", "Arduino reconnected successfully.")
        else:
            self.add_message("CLEVER", "Failed to reconnect Arduino. Check port.")

    def open_settings(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec_() == QDialog.Accepted:
            new_config = dialog.get_config()
            self.config.update(new_config)
            try:
                with open(r"C:\AI_Assistant\config.json", "w") as f:
                    json.dump(self.config, f, indent=2)
            except Exception as e:
                print(f"Error saving config: {e}")
            self.ai.google_mode = self.config.get("google_mode", True)
            self.ai.use_ollama = self.config.get("ollama", {}).get("enabled", False)
            self.ai.ollama_model = self.config.get("ollama", {}).get("model", "deepseek-r1:8b")
            self.google_mode_btn.setChecked(self.ai.google_mode)
            self.ollama_mode_btn.setChecked(self.ai.use_ollama)
            self.ollama_model_combo.setCurrentText(self.ai.ollama_model)
            self.mode_indicator.setText("🌐 Mode: " + ("Google" if self.ai.google_mode else ("Ollama" if self.ai.use_ollama else "Basic")))
            if self.ai.use_ollama and not self.ai.ollama:
                from modules.ollama_engine import OllamaClient
                self.ai.ollama = OllamaClient(
                    url=self.config["ollama"]["url"],
                    model=self.config["ollama"]["model"]
                )
            elif not self.ai.use_ollama and self.ai.ollama:
                self.ai.ollama = None
            if self.arduino:
                self.arduino.disconnect()
                self.arduino.port = self.config["arduino_port"]
                if self.arduino.connect():
                    self.update_arduino_status()
                else:
                    self.add_message("CLEVER", "Arduino connection failed with new port.")

    def toggle_google(self):
        if self.google_mode_btn.isChecked():
            self.ai.google_mode = True
            self.ai.use_ollama = False
            self.ollama_mode_btn.setChecked(False)
            self.mode_indicator.setText("🌐 Mode: Google")
            self.add_message("CLEVER", "Google search mode enabled.")
        else:
            self.ai.google_mode = False
            if not self.ai.use_ollama:
                self.mode_indicator.setText("🌐 Mode: Basic")
            self.add_message("CLEVER", "Google search mode disabled.")

    def toggle_ollama(self):
        if self.ollama_mode_btn.isChecked():
            if self.ai.ollama is None:
                from modules.ollama_engine import OllamaClient
                self.ai.ollama = OllamaClient(
                    url=self.config.get("ollama", {}).get("url", "http://localhost:11434"),
                    model=self.ollama_model_combo.currentText()
                )
                self.ai.ollama_model = self.ollama_model_combo.currentText()
            self.ai.use_ollama = True
            self.ai.google_mode = False
            self.google_mode_btn.setChecked(False)
            self.mode_indicator.setText("🌐 Mode: Ollama")
            self.add_message("CLEVER", f"Ollama mode enabled using {self.ai.ollama_model}.")
        else:
            self.ai.use_ollama = False
            if not self.ai.google_mode:
                self.mode_indicator.setText("🌐 Mode: Basic")
            self.add_message("CLEVER", "Ollama mode disabled.")

    def change_ollama_model(self, model):
        if self.ai.ollama:
            self.ai.ollama.set_model(model)
            self.ai.ollama_model = model
            self.add_message("CLEVER", f"Ollama model changed to {model}.")

    def toggle_listen(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.listen_btn.setText("⏹ Stop Listening")
            self.face_state_signal.emit("listening")
            if self.arduino and self.arduino.is_connected:
                self.arduino.send_state("LISTENING")
            self.voice.start_listening()
            self.add_message("CLEVER", "🎤 Listening started...")
        else:
            self.voice.stop_listening()
            self.listen_btn.setText("🎤 Start Listening")
            self.face_state_signal.emit("idle")
            if self.arduino and self.arduino.is_connected:
                self.arduino.send_state("READY")
            self.add_message("CLEVER", "🛑 Listening stopped.")

    def stop_speaking(self):
       
        self.voice.stop()

        if self.arduino:
            self.arduino.send_message(" | ")

        self.add_message("CLEVER", "Speech stopped.")

    def quick_remember(self):
        text, ok = QInputDialog.getText(self, "Remember", "What should I remember?")
        if ok and text:
            self.memory.add_note(text)
            self.refresh_notes()
            self.voice.speak(f"I'll remember: {text}")
            self.add_message("CLEVER", f"I'll remember: {text}")
            if self.arduino:
                self.arduino.send_state("NOTE")
                self.face.set_state("happy")
                QTimer.singleShot(1000, lambda: self.face.set_state("idle"))

    def send_message(self):
        text = self.input_field.toPlainText().strip()
        if text:
            self.input_field.clear()
            self.add_message("YOU", text)
            self.process_text(text)

    def process_text(self, text):
        """Process user input – speak call is in AI assistant, not here."""
        self.face.set_state("thinking" if not self.ai.use_ollama else "searching")
        QApplication.processEvents()
        response = self.ai.handle(text)
        self.add_message("CLEVER", response)
        self.face.set_state("idle")

    def save_note(self):
        text = self.note_input.text().strip()
        if text:
            self.memory.add_note(text)
            self.note_input.clear()
            self.refresh_notes()
            self.voice.speak("Note saved")
            self.add_message("CLEVER", f"Note saved: {text}")
            if self.arduino:
                self.arduino.send_state("NOTE")
                self.face.set_state("happy")
                QTimer.singleShot(1000, lambda: self.face.set_state("idle"))

    def refresh_notes(self):
        self.notes_list.clear()
        for note in self.memory.get_notes(10):
            item = QListWidgetItem(f"📝 {note['content'][:40]}")
            item.setForeground(QColor(0, 255, 255))
            self.notes_list.addItem(item)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.NoModifier:
            if self.input_field.hasFocus():
                self.send_message()
                event.accept()
                return
        super().keyPressEvent(event)
    

        event.accept()
    def keyPressEvent(self, event):
        from PyQt5.QtCore import Qt

        if event.key() == Qt.Key_Escape:
            self.close()
