#!/usr/bin/env python3
"""
CLEVER AI Assistant - Main Entry Point
"""

import sys
import os
import json
import socket

def is_online():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except:
        return False
import logging
from PyQt5.QtWidgets import QApplication

from modules.arduino_manager import ArduinoManager
from modules.voice_manager import VoiceManager
from modules.search_engine import SearchEngine
from modules.memory_system import MemorySystem
from modules.ai_assistant import AIAssistant
from modules.ui_manager import CleverWindow
from modules.ollama_engine import OllamaClient
from modules.groq_client import GroqClient
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_PATH = r"C:\AI_Assistant"
MEMORY_PATH = os.path.join(BASE_PATH, "memory", "memories.json")
CONFIG_PATH = os.path.join(BASE_PATH, "config.json")

os.makedirs(os.path.join(BASE_PATH, "memory"), exist_ok=True)

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {
            "arduino_port": "COM3",
            "google_mode": True,
            "ollama": {
                "enabled": False,
                "url": "http://localhost:11434",
                "model": "deepseek-r1:8b"
            }
        }

def main():
    print("\n" + "="*60)
    print("🚀 CLEVER AI - COMPLETE VERSION (with Ollama)")
    print("="*60)

    config = load_config()
    logger.info("Config loaded")

    print("\n📦 Initializing modules...")

    memory = MemorySystem(MEMORY_PATH)
    logger.info("Memory system ready")

    search = SearchEngine()
    logger.info("Search engine ready")

    arduino = ArduinoManager(port=config['arduino_port'])
    if arduino.connect():
        logger.info("Arduino connected")
    else:
        logger.warning("Arduino not connected")

    voice = VoiceManager()
    # 🔥 AUTO SELECT SPEECH ENGINE
    if is_online():
        print("🌐 Internet detected → Using Google Speech")
        voice.set_engine("google")
    else:
        print("📴 Offline → Using VOSK")
        voice.set_engine("vosk")
    logger.info("Voice manager ready")

    ollama_client = None
    if config.get('ollama', {}).get('enabled', False):
        ollama_client = OllamaClient(
            url=config['ollama']['url'],
            model=config['ollama']['model']
        )
        logger.info(f"Ollama client initialized with model {config['ollama']['model']}")
    api_key = config.get("groq_api_key")

    if not api_key:
       print("❌ Groq API key missing!")
    groq_client = GroqClient(api_key)
    print("🔍 Testing Groq API...")

    try:
        test_response = groq_client.generate("Say OK")
    
        if test_response:
            print("✅ Groq API Connected Successfully")
            print("🤖 Test Response:", test_response)
        else:
            print("❌ Groq API Failed (No response)")

    except Exception as e:
        print("❌ Groq API Error:", e)
    logger.info("Groq client initialized")
    # 🔥 IMPORTANT: gemini yaha pass nahi karna config ko
    ai = AIAssistant(memory, search, arduino, voice, ollama_client, groq_client)
    import threading

    threading.Thread(target=ai.idle_check, daemon=True).start()
    logger.info("AI Assistant ready")

    app = QApplication(sys.argv)
    window = CleverWindow(ai, arduino, voice, memory, config)

    window.show()

    # 🔥 AUTO START SYSTEM
    voice.start_listening()
    voice.speak("Clever AI is ready")

    try:
        sys.exit(app.exec_())
    except KeyboardInterrupt:
        print("App closed safely")

if __name__ == "__main__":
    main()