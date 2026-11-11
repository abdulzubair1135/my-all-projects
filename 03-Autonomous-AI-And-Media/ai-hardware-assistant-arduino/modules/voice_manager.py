"""
CLEVER Voice Manager – Fresh Engine Every Time (Most Stable for Windows)
"""

import queue
import threading
import time
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import pyttsx3
import speech_recognition as sr
import logging

logger = logging.getLogger(__name__)


class TTSManager:
    def __init__(self):
  
  self.engine = None
        self.speech_queue = queue.Queue()
        self.running = True
        self.is_speaking = False
        threading.Thread(target=self._worker, daemon=True).start()
        logger.info("TTSManager ready - using fresh engine per speak")

    def _worker(self):
        while self.running:
            try:
                text = self.speech_queue.get(timeout=0.1)
                if text and text.strip():
                    self.is_speaking = True
                    try:
                        # Har baar NAYA engine banao (Windows ke liye best)
                        engine = pyttsx3.init()
                        engine.setProperty('rate', 165)
                        engine.setProperty('volume', 1.0)
                        engine.say(text.strip())
                        engine.runAndWait()
                        engine.stop()
                        del engine  # clean up
                    except Exception as e:
                        logger.error(f"TTS speak error: {e}")
                    finally:
                        self.is_speaking = False
                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:

                logger.error(f"TTS worker error: {e}")
                self.is_speaking = False
    def reset_tts(self):
        try:
            if self.engine:
                self.engine.stop()
        except:
            pass

        self.engine = None   # ✅ ANDAR hona chahiye
    def speak(self, text):
        if text and text.strip():
            self.speech_queue.put(text.strip())

    def stop(self):
        self.is_listening = False
        self.stop_event.set()
class GoogleRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.running = False
        self.callbacks = []

    def start_listening(self):
        self.running = True
        threading.Thread(target=self._listen, daemon=True).start()

    def _listen(self):
        with sr.Microphone() as source:
            while self.running:
                try:
                    audio = self.recognizer.listen(source, timeout=5)
                    text = self.recognizer.recognize_google(audio)
                    print(f"🌐 GOOGLE: {text}")

                    for cb in self.callbacks:
                        cb(text)

                except sr.WaitTimeoutError:
                    # 🟡 NORMAL case (no speech)
                    continue

                except sr.UnknownValueError:
                    continue

                except sr.RequestError:
                    print("❌ Network error → fallback")
                    self.running = False
                    for cb in self.callbacks:
                        cb("__google_fail__")

                except Exception as e:
                    print("⚠️ Minor Google error:", e)
                    continue

                    # 🔥 AUTO FALLBACK
                    for cb in self.callbacks:
                        cb("__google_fail__")

    def stop(self):
        self.running = False

    def on_text(self, callback):
        self.callbacks.append(callback)
class SpeechRecognizer:
    """VOSK‑based speech recognizer with auto‑restart."""
    def __init__(self, model_path=r"C:\AI_Assistant\models\vosk-model-en-us-0.22"):
        self.model_path = model_path
        self.model = None
        self.callbacks = []
        self.is_listening = False
        self.recording_thread = None
        self.stop_event = threading.Event()
        try:
            print(f"🧠 Loading VOSK model from {model_path}...")
            self.model = Model(model_path)
            print("✅ VOSK model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load VOSK model: {e}")
            raise
    
    def start_listening(self):
        if self.is_listening:
            return
        self.is_listening = True
        self.stop_event.clear()
        self.recording_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.recording_thread.start()

    def _listen_loop(self):
        print("🎤 Continuous Listening ON...")
        while self.is_listening and not self.stop_event.is_set():
            try:
                self._run_recognizer()
            except Exception as e:
                logger.error(f"Recognizer fatal error: {e}")
                if self.is_listening and not self.stop_event.is_set():
                    print("🔄 Restarting recognizer in 2 seconds...")
                    time.sleep(2)
                    continue
                else:
                    break

    def _run_recognizer(self):
        rec = KaldiRecognizer(self.model, 16000)
        samplerate = 16000
        blocksize = 8000
        device = None

        try:
            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    device = i
                    break

            if device is None:
                device = 0

            print(f"🎤 Using audio input device: {device} - {devices[device]['name']}")

        except Exception as e:
            logger.warning(f"Could not query devices: {e}")

        with sd.RawInputStream(
            samplerate=samplerate,
            blocksize=blocksize,
            device=device,
            dtype='int16',
            channels=1,
            latency='low'
        ) as stream:

            last_heartbeat = time.time()

            while self.is_listening and not self.stop_event.is_set():
                try:
                    # 🔊 heartbeat
                    now = time.time()
                    if now - last_heartbeat > 10:
                        print("🔊 Listening heartbeat...")
                        last_heartbeat = now

                    # 🎤 audio read
                    data, overflowed = stream.read(blocksize)

                    if overflowed:
                        logger.warning("Audio buffer overflow")
                        continue

                    if len(data) == 0:
                        continue

                    audio_bytes = bytes(data)

                    # 🔥 FINAL RESULT
                    if rec.AcceptWaveform(audio_bytes):
                        result = json.loads(rec.Result())
                        text = result.get("text", "").strip()

                        if text and len(text) > 3 and text not in ["the", "a", "uh"]:
                            print(f"🎤 FINAL: {text}")

                            for cb in self.callbacks:
                                try:
                                    cb(text)
                                except Exception as e:
                                    logger.error(f"Callback error: {e}")

                    # 🟡 PARTIAL RESULT (LIVE)
                    else:
                        partial = json.loads(rec.PartialResult())
                        ptext = partial.get("partial", "").strip()

                        if ptext:
                            print(f"🟡 PARTIAL: {ptext}")

                except Exception as e:
                    logger.error(f"Error in listening loop: {e}")
                    time.sleep(0.1)
                    continue

    def stop(self):
        self.is_listening = False
        self.stop_event.set()
        if self.recording_thread and self.recording_thread.is_alive():
            self.recording_thread.join(timeout=2)

    def on_text(self, callback):
        self.callbacks.append(callback)


class VoiceManager:
    def __init__(self):
        self.tts = TTSManager()
        try:
            self.vosk = SpeechRecognizer()
            self.google = GoogleRecognizer()

            self.current_engine = "vosk"
            self.recognizer = self.vosk
        except Exception as e:
            logger.error(f"Failed to initialize speech recognizer: {e}")
            self.recognizer = None

        self.callbacks = []
        self.on_listening_start_callbacks = []
        self.on_listening_stop_callbacks = []
        self.on_speaking_start_callbacks = []
        self.on_speaking_stop_callbacks = []

        if self.recognizer:
            self.recognizer.on_text(self._on_text)
    def set_engine(self, engine):
        try:
            self.recognizer.stop()
        except:
            pass

        if engine == "google":
            self.recognizer = self.google
            self.current_engine = "google"
            print("🎤 Switched to GOOGLE STT")
        else:
            self.recognizer = self.vosk
            self.current_engine = "vosk"
            print("🎤 Switched to VOSK")

        # 🔥 FIX: clear old callbacks
        self.recognizer.callbacks = []
        self.recognizer.on_text(self._on_text)

        self.start_listening()
    def _on_text(self, text):
        if text == "__google_fail__":
            if self.current_engine != "vosk":   # 🔥 IMPORTANT CHECK
                print("⚡ Auto switching to VOSK")
                self.set_engine("vosk")
            return

        for cb in self.callbacks:
            try:
                cb(text)
            except Exception as e:
                logger.error(f"Speech callback error: {e}")

    def start_listening(self):
        if not self.recognizer:
            return
        for cb in self.on_listening_start_callbacks:
            try:
                cb()
            except:
                pass
        self.recognizer.start_listening()

    def stop_listening(self):
        if not self.recognizer:
            return
        self.recognizer.stop()
        for cb in self.on_listening_stop_callbacks:
            try:
                cb()
            except:
                pass

    def speak(self, text):
        def speak_thread():
            for cb in self.on_speaking_start_callbacks:
                try:
                    cb()
                except:
                    pass

            self.tts.speak(text)

            while self.tts.is_speaking:
                time.sleep(0.05)

            for cb in self.on_speaking_stop_callbacks:
                try:
                    cb()
                except:
                    pass

        threading.Thread(target=speak_thread, daemon=True).start()

    def on_speech(self, callback):
        self.callbacks.append(callback)

    def on_listening_start(self, callback):
        self.on_listening_start_callbacks.append(callback)

    def on_listening_stop(self, callback):
        self.on_listening_stop_callbacks.append(callback)

    def on_speaking_start(self, callback):
        self.on_speaking_start_callbacks.append(callback)

    def on_speaking_stop(self, callback):
        self.on_speaking_stop_callbacks.append(callback)

    def stop(self):
        self.running = False
        self.is_speaking = False