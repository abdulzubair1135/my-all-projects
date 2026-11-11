#!/usr/bin/env python3
"""
CLEVER AI Assistant - ARDUINO WORKING VERSION (FIXED)
"""

import sys
import os
import json
import time
import datetime
import webbrowser
import threading
import queue
import random
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import win32com.client
import pythoncom
import speech_recognition as sr
import serial

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_PATH = r"C:\AI_Assistant"
MEMORY_PATH = os.path.join(BASE_PATH, "memory", "memories.json")
os.makedirs(os.path.join(BASE_PATH, "memory"), exist_ok=True)

# ============================================================================
# ARDUINO CONTROLLER
# ============================================================================

class ArduinoController(QThread):
    connection_status = pyqtSignal(bool)
    
    def __init__(self, port='COM3', baud=9600):
        super().__init__()
        self.port = port
        self.baud = baud
        self.ser = None
        self.is_connected = False
        self.command_queue = queue.Queue()
        
    def connect(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=1)
            time.sleep(2)
            self.ser.write(b"PING\n")
            time.sleep(0.5)
            
            if self.ser.in_waiting:
                response = self.ser.readline().decode().strip()
                if "PONG" in response or "ARD:READY" in response:
                    self.is_connected = True
                    print(f"✅ Arduino connected on {self.port}")
                    self.connection_status.emit(True)
                    return True
            self.ser.close()
            return False
        except Exception as e:
            print(f"❌ Arduino connection error: {e}")
            return False
    
    def run(self):
        while self.is_connected:
            try:
                while not self.command_queue.empty():
                    cmd = self.command_queue.get_nowait()
                    self.ser.write(f"{cmd}\n".encode())
                    print(f"📤 Arduino << {cmd}")
                    time.sleep(0.1)
                
                if self.ser.in_waiting:
                    response = self.ser.readline().decode().strip()
                    if response:
                        print(f"📥 Arduino >> {response}")
                
                time.sleep(0.05)
            except Exception as e:
                print(f"⚠️ Arduino error: {e}")
                self.is_connected = False
                self.connection_status.emit(False)
    
    def send_state(self, state):
        self.command_queue.put(f"STATE:{state}")
    
    def send_message(self, message):
        if len(message) > 32:
            message = message[:32]
        self.command_queue.put(f"LCD:{message}")
    
    def send_command(self, cmd):
        self.command_queue.put(cmd)
    
    def beep(self):
        self.command_queue.put("BEEP")
    
    def disconnect(self):
        self.is_connected = False
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("🔌 Arduino disconnected")

# ============================================================================
# GOOGLE SEARCH
# ============================================================================

class GoogleSearch:
    @staticmethod
    def get_answer(query):
        try:
            query_encoded = urllib.parse.quote_plus(query)
            url = f"https://www.google.com/search?q={query_encoded}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            req = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(req, timeout=5)
            html = response.read().decode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            
            answer = soup.find('div', class_='Z0LcW')
            if answer:
                return answer.get_text()
            
            result = soup.find('div', class_='VwiC3b')
            if result:
                return result.get_text()[:200] + "..."
            
            return f"Here's what I found about {query}. I've opened Google for you."
        except Exception as e:
            return f"Search error: {e}"

# ============================================================================
# WINDOWS TTS
# ============================================================================

class WindowsTTS(QThread):
    speaking_started = pyqtSignal()
    speaking_finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.speech_queue = queue.Queue()
        self.is_running = True
        
    def run(self):
        pythoncom.CoInitialize()
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        while self.is_running:
            try:
                if not self.speech_queue.empty():
                    text = self.speech_queue.get_nowait()
                    self.speaking_started.emit()
                    speaker.Speak(text)
                    self.speaking_finished.emit()
                time.sleep(0.1)
            except:
                pass
        pythoncom.CoUninitialize()
    
    def speak(self, text):
        if text and text.strip():
            self.speech_queue.put(text.strip())
    
    def stop(self):
        self.is_running = False
        self.wait()

# ============================================================================
# SPEECH RECOGNITION
# ============================================================================

class SpeechRecognizer(QThread):
    text_detected = pyqtSignal(str)
    listening_started = pyqtSignal()
    listening_stopped = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.is_listening = False
        self.is_running = True
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
    
    def run(self):
        while self.is_running:
            if self.is_listening:
                try:
                    with self.microphone as source:
                        self.listening_started.emit()
                        audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=10)
                        text = self.recognizer.recognize_google(audio)
                        if text:
                            self.text_detected.emit(text)
                except:
                    pass
                self.listening_stopped.emit()
            time.sleep(0.1)
    
    def start_listening(self):
        self.is_listening = True
    
    def stop_listening(self):
        self.is_listening = False
    
    def stop(self):
        self.is_running = False
        self.wait()

# ============================================================================
# ANIMATED FACE
# ============================================================================

class AnimatedFace(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 200)
        self.setAlignment(Qt.AlignCenter)
        self.state = "idle"
        self.setText("⚡ CLEVER")
        self.setStyleSheet("color: #00ffff; font-size: 24px; font-weight: bold;")
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_face)
        self.timer.start(500)
        self.dots = 0
    
    def update_face(self):
        self.dots = (self.dots + 1) % 4
        dots = "." * self.dots
        states = {
            "listening": f"🎤 Listening{dots}",
            "thinking": f"🤔 Thinking{dots}",
            "speaking": f"🗣️ Speaking{dots}",
            "idle": "⚡ CLEVER"
        }
        self.setText(states.get(self.state, "⚡ CLEVER"))
    
    def set_state(self, state):
        self.state = state

# ============================================================================
# MEMORY SYSTEM
# ============================================================================

class Memory:
    def __init__(self):
        self.file = MEMORY_PATH
        self.data = self.load()
    
    def load(self):
        if os.path.exists(self.file):
            try:
                with open(self.file, 'r') as f:
                    return json.load(f)
            except:
                return {"notes": []}
        return {"notes": []}
    
    def save(self):
        with open(self.file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def add_note(self, note):
        self.data["notes"].append({
            "content": note,
            "time": time.time()
        })
        self.save()
    
    def get_notes(self):
        return self.data["notes"][-10:]

# ============================================================================
# MAIN WINDOW
# ============================================================================

class CleverWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.memory = Memory()
        self.google = GoogleSearch()
        self.google_mode = True
        
        self.arduino = ArduinoController(port='COM3')
        if self.arduino.connect():
            self.arduino.start()
            self.arduino.connection_status.connect(self.on_arduino_status)
            self.arduino.send_message("CLEVER Ready")
            self.arduino.beep()
        
        self.tts = WindowsTTS()
        self.tts.speaking_started.connect(lambda: self.face.set_state("speaking"))
        self.tts.speaking_finished.connect(lambda: self.face.set_state("idle"))
        self.tts.start()
        
        self.recognizer = SpeechRecognizer()
        self.recognizer.text_detected.connect(self.on_speech)
        self.recognizer.listening_started.connect(lambda: self.face.set_state("listening"))
        self.recognizer.listening_stopped.connect(lambda: self.face.set_state("idle"))
        self.recognizer.start()
        
        self.init_ui()
        self.is_listening = False
        
        welcome = "Hello! I'm CLEVER. Arduino connected!"
        self.add_message("CLEVER", welcome)
        self.speak(welcome)
        
        print("\n✅ CLEVER AI Ready with Arduino!")
    
    def init_ui(self):
        self.setWindowTitle("CLEVER AI")
        self.setGeometry(100, 100, 900, 600)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #0a0a14; }
            QTextEdit, QListWidget {
                background-color: #1a1a2a;
                color: #00ffff;
                border: 2px solid #00ffff;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton {
                background-color: #1a1a2a;
                color: #00ffff;
                border: 2px solid #00ffff;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ffff;
                color: #0a0a14;
            }
        """)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Left - Chat
        left = QWidget()
        left_layout = QVBoxLayout(left)
        
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        left_layout.addWidget(self.chat)
        
        input_layout = QHBoxLayout()
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(60)
        self.input_field.setPlaceholderText("Type here...")
        self.send_btn = QPushButton("ASK")
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        left_layout.addLayout(input_layout)
        
        btn_layout = QHBoxLayout()
        self.listen_btn = QPushButton("🎤 LISTEN")
        self.listen_btn.setCheckable(True)
        self.listen_btn.clicked.connect(self.toggle_listen)
        self.mode_btn = QPushButton("🌐 GOOGLE: ON")
        self.mode_btn.clicked.connect(self.toggle_google)
        btn_layout.addWidget(self.listen_btn)
        btn_layout.addWidget(self.mode_btn)
        left_layout.addLayout(btn_layout)
        
        # Center - Face
        center = QWidget()
        center_layout = QVBoxLayout(center)
        
        self.face = AnimatedFace()
        center_layout.addWidget(self.face)
        
        status_frame = QFrame()
        status_frame.setStyleSheet("border: 1px solid #3355aa; border-radius: 5px; padding: 10px;")
        status_layout = QVBoxLayout(status_frame)
        self.arduino_status = QLabel("✅ Arduino: Connected")
        status_layout.addWidget(self.arduino_status)
        center_layout.addWidget(status_frame)
        
        # Right - Notes
        right = QWidget()
        right_layout = QVBoxLayout(right)
        
        right_layout.addWidget(QLabel("📝 NOTES"))
        self.notes_list = QListWidget()
        right_layout.addWidget(self.notes_list)
        
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Remember...")
        right_layout.addWidget(self.note_input)
        
        note_btn = QPushButton("SAVE")
        note_btn.clicked.connect(self.save_note)
        right_layout.addWidget(note_btn)
        
        layout.addWidget(left, 3)
        layout.addWidget(center, 2)
        layout.addWidget(right, 2)
        
        self.refresh_notes()
    
    def on_arduino_status(self, connected):
        if connected:
            self.arduino_status.setText("✅ Arduino: Connected")
        else:
            self.arduino_status.setText("🔴 Arduino: Disconnected")
    
    def on_speech(self, text):
        self.add_message("YOU", text)
        self.process_command(text)
        if self.is_listening:
            self.toggle_listen()
    
    def toggle_listen(self):
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.recognizer.start_listening()
            self.listen_btn.setText("⏹️ STOP")
            if self.arduino:
                self.arduino.send_state("LISTENING")
        else:
            self.recognizer.stop_listening()
            self.listen_btn.setText("🎤 LISTEN")
            if self.arduino:
                self.arduino.send_state("READY")
    
    def toggle_google(self):
        self.google_mode = not self.google_mode
        self.mode_btn.setText(f"🌐 GOOGLE: {'ON' if self.google_mode else 'OFF'}")
        self.add_message("CLEVER", f"Google Search {('ON' if self.google_mode else 'OFF')}")
    
    def add_message(self, sender, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        color = "#00ffff" if sender == "CLEVER" else "#ffffff"
        self.chat.append(f'<font color="#88aaff">[{timestamp}]</font> <font color="{color}"><b>{sender}:</b> {message}</font>')
        
        if sender == "CLEVER" and self.arduino and self.arduino.is_connected:
            self.arduino.send_message(message[:32])
    
    def speak(self, text):
        if text:
            self.tts.speak(text)
    
    def send_message(self):
        text = self.input_field.toPlainText().strip()
        if text:
            self.input_field.clear()
            self.add_message("YOU", text)
            self.process_command(text)
    
    def save_note(self):
        text = self.note_input.text().strip()
        if text:
            self.memory.add_note(text)
            self.note_input.clear()
            self.refresh_notes()
            self.speak("Note saved")
    
    def refresh_notes(self):
        self.notes_list.clear()
        for note in self.memory.get_notes():
            self.notes_list.addItem(f"📝 {note['content'][:30]}")
    
    # ========== MAIN PROCESS COMMAND - FIXED ==========
    def process_command(self, command):
        """Process user commands - SINGLE VERSION"""
        cmd = command.lower().strip()
        
        # Arduino ko batayo
        if self.arduino and self.arduino.is_connected:
            self.arduino.send_state("THINKING")
            self.arduino.send_message(f"CMD:{command[:20]}")
        
        # TIME
        if "time" in cmd:
            if self.arduino:
                self.arduino.send_state("TIME")
            current = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The time is {current}")
            self.add_message("CLEVER", f"The time is {current}")
        
        # DATE
        elif "date" in cmd:
            if self.arduino:
                self.arduino.send_state("TIME")
            current = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"Today is {current}")
            self.add_message("CLEVER", f"Today is {current}")
        
        # REMEMBER
        elif "remember" in cmd:
            if self.arduino:
                self.arduino.send_state("NOTE")
            note = cmd.replace("remember", "").replace("that", "").strip()
            if note:
                self.memory.add_note(note)
                self.refresh_notes()
                self.speak(f"I'll remember: {note}")
                self.add_message("CLEVER", f"Remembered: {note}")
        
        # NOTES
        elif "notes" in cmd or "what do you remember" in cmd:
            notes = self.memory.get_notes()
            if notes:
                self.add_message("CLEVER", "Your notes:")
                for note in notes[-5:]:
                    self.add_message("NOTE", f"• {note['content']}")
                self.speak("Here are your recent notes")
            else:
                self.speak("You have no notes yet")
        
        # GOOGLE ON
        elif "google on" in cmd:
            self.google_mode = True
            self.mode_btn.setText("🌐 GOOGLE: ON")
            self.speak("Google search is on")
            self.add_message("CLEVER", "Google Search ON")
        
        # GOOGLE OFF
        elif "google off" in cmd:
            self.google_mode = False
            self.mode_btn.setText("🌐 GOOGLE: OFF")
            self.speak("Google search is off")
            self.add_message("CLEVER", "Google Search OFF")
        
        # SEARCH (Google mode on)
        elif self.google_mode and len(cmd) > 3 and not any(x in cmd for x in ["time", "date", "remember", "notes", "google", "bye", "exit", "quit", "help"]):
            if self.arduino:
                self.arduino.send_state("SEARCHING")
            self.add_message("CLEVER", f"🔍 Searching: {cmd}")
            answer = self.google.get_answer(cmd)
            self.add_message("CLEVER", answer)
            self.speak(answer[:150])
            webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote_plus(cmd)}")
        
        # EXIT
        elif "bye" in cmd or "exit" in cmd or "quit" in cmd:
            self.speak("Goodbye! Have a great day!")
            self.add_message("CLEVER", "Goodbye!")
            QTimer.singleShot(2000, self.close)
        
        # HELP
        elif "help" in cmd:
            help_text = "I can tell time, date, remember notes, search Google, and more!"
            self.speak(help_text)
            self.add_message("CLEVER", help_text)
        
        # DEFAULT
        else:
            self.speak("Try asking about time, date, or say 'google on' to search")
        
        # Back to ready
        if self.arduino and self.arduino.is_connected:
            self.arduino.send_state("READY")
    
    def closeEvent(self, event):
        self.recognizer.stop()
        self.tts.stop()
        if self.arduino:
            self.arduino.disconnect()
        event.accept()

# ============================================================================
# MAIN
# ============================================================================

def main():
    app = QApplication(sys.argv)
    window = CleverWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()