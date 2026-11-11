import datetime
import webbrowser
import urllib.parse
import random
import threading
import time

class AIAssistant:
    def __init__(self, memory, search, arduino, voice, ollama=None, gemini=None):
        self.memory = memory
        self.search = search
        self.arduino = arduino
        self.voice = voice
        self.ollama = ollama
        self.ollama_model = "gemma3:1b"
        self.api_client = gemini  # (ab ye Groq hai)
        self.google_mode = False
        
        self.use_ollama = False

        # 🔥 ONLY ONE MODE SYSTEM
        self.mode = "simple"

# ✅ ADD HERE
        self.last_interaction = time.time()


    def set_mode(self, mode):
        self.mode = mode

        # 🔥 RESET ALL FIRST
        self.google_mode = False
        self.use_ollama = False

        if mode == "simple":
            return "Simple mode activated"

        elif mode == "ollama":
            self.use_ollama = True
            self.ollama_model = "gemma3:1b"
            return "Offline AI activated"

        elif mode == "api":
            return "Online API activated"

        elif mode == "google":
            self.google_mode = True
            return "Google mode activated"

        return "Unknown mode"
    # 🔥 LCD SCROLL
    def send_lcd(self, text):
        if not self.arduino or not self.arduino.is_connected:
            print("❌ Arduino not connected")
            return

        text = text.replace("\n", " ")

        for i in range(0, len(text), 32):
            chunk = text[i:i+32]
            self.arduino.send_message(chunk)
            time.sleep(1.5)

        print("📺 LCD:", text)

        self.arduino.send_message(text)
    def idle_check(self):
        while True:
            if time.time() - self.last_interaction > 20:

                if self.arduino:
                    self.arduino.command_queue.put("SERVO")
                    self.arduino.send_message("Hey I am Clever")

                self.speak("Hey I am Clever, do you want to know about me")

                time.sleep(240)  # 4 min next

            time.sleep(2)
    # 🔥 SPEAK CONTROL
    def speak(self, text):
        if not self.voice:
            return

        self.voice.stop_listening()
        self.voice.speak(text)

        def resume():
            time.sleep(2)
            self.voice.start_listening()

        threading.Thread(target=resume).start()
    
    # 🔥 MAIN PROCESS
    def process(self, text):
        cmd = text.lower().strip()

        print("MODE =", self.mode)
        if "shake" in cmd or "handshake" in cmd or "hands" in cmd or "hand" in cmd :
            self.arduino.command_queue.put("SERVO")
            self.arduino.send_message("Nice to meet you")
            return "Nice to meet you"
        if "light" in cmd and ("on" in cmd or "start" in cmd):
            self.arduino.command_queue.put("LED_ON")
            return "Light turned on"

        if "light" in cmd and ("off" in cmd or "stop" in cmd or "of" in cmd):
            self.arduino.command_queue.put("LED_OFF")
            return "Light turned off"
        # SIMPLE MODE
        if self.mode == "simple":
            if "time" in cmd:
                return datetime.datetime.now().strftime("Time is %I:%M %p")

            if "joke" in cmd:
                return "Why do programmers love dark mode? Because light attracts bugs."

            return "Simple mode active"

        # 🔥 OLLAMA
        elif self.mode == "ollama":
            if self.ollama:
                short_prompt = f"Answer in 1-2 short sentences only: {cmd}"
                return self.ollama.generate(short_prompt)
            else:
                return "Ollama not connected"

        # 🔥 GEMINI
        elif self.mode == "api":
            if self.api_client:
                short_prompt = f"Answer in 1-2 short sentences only: {cmd}"
                return self.api_client.generate(short_prompt)
            else:
                return "API not connected"

        # GOOGLE
        elif self.mode == "google":
            return f"Searching Google for {cmd}"

        return "Mode not set"
    def handle(self, text):
        cmd = text.lower().strip()

        # 🔥 UPDATE INTERACTION TIME
        self.last_interaction = time.time()

        # 🧠 PROCESS
        response = self.process(cmd)

        # 🔥 STATE
        if self.arduino:
            self.arduino.send_state("SPEAKING")

        # 📺 LCD
        if self.arduino:
            self.send_lcd(response)
            self.send_lcd("TEST LCD WORKING")
        # 🔊 SPEAK
        self.speak(response)

        # 🌐 GOOGLE
        if self.mode == "google":
            import webbrowser, urllib.parse
            webbrowser.open(
                f"https://www.google.com/search?q={urllib.parse.quote_plus(cmd)}"
            )

        # 🔥 WAIT
        time.sleep(7)

        # 🔥 CLEAR
        if self.arduino:
            self.arduino.command_queue.put("CLEAR")
            self.arduino.send_state("READY")

        return response