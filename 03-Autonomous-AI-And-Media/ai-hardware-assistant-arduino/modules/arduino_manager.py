"""
Arduino Communication Manager – Robust version with retry and logging.
"""

import serial
import threading
import queue
import time
import logging

logger = logging.getLogger(__name__)

class ArduinoManager:
    def __init__(self, port='COM3', baud=9600):
        self.port = port
        self.baud = baud
        self.ser = None
        self.is_connected = False
        self.command_queue = queue.Queue()
        self.running = False
        self.thread = None

    def connect(self, retries=3):
        """Connect to Arduino with retries."""
        for attempt in range(retries):
            try:
                logger.info(f"Attempting to connect to {self.port} (attempt {attempt+1}/{retries})...")
                self.ser = serial.Serial(self.port, self.baud, timeout=2)
                time.sleep(2)  # Wait for Arduino reset

                # Clear buffers
                self.ser.reset_input_buffer()
                self.ser.reset_output_buffer()

                # Send PING and wait for response
                self.ser.write(b"PING\n")
                self.ser.flush()
                time.sleep(1)

                # Read response
                start_time = time.time()
                while time.time() - start_time < 3:
                    if self.ser.in_waiting:
                        response = self.ser.readline().decode().strip()
                        logger.debug(f"Received: {response}")
                        if "PONG" in response or "ARD:READY" in response or "ALIVE" in response:
                            self.is_connected = True
                            logger.info(f"✅ Arduino connected on {self.port}")
                            self.running = True
                            self.thread = threading.Thread(target=self._listener, daemon=True)
                            self.thread.start()
                            return True
                    time.sleep(0.1)

                logger.warning("No valid response from Arduino")
                self.ser.close()

            except Exception as e:
                logger.error(f"Connection error: {e}")
                if self.ser and self.ser.is_open:
                    self.ser.close()
                time.sleep(1)

        return False

    def _listener(self):
        """Background thread to send queued commands and read responses."""
        while self.running and self.is_connected:
            try:
                # Send queued commands
                while not self.command_queue.empty():
                    cmd = self.command_queue.get_nowait()
                    self.ser.write(f"{cmd}\n".encode())
                    self.ser.flush()
                    logger.debug(f"📤 Sent: {cmd}")

                # Read incoming data
                if self.ser and self.ser.in_waiting:
                    response = self.ser.readline().decode().strip()
                    if response:
                        logger.debug(f"📥 Received: {response}")

                time.sleep(0.05)
            except Exception as e:
                logger.error(f"Listener error: {e}")
                self.is_connected = False
                break

    def send_state(self, state):
        """Send AI state to Arduino."""
        if self.is_connected:
            self.command_queue.put(f"STATE:{state}")

    def send_message(self, message):
        """Send message to LCD."""
        if self.is_connected and message:
            if len(message) > 32:
                message = message[:32]
            self.command_queue.put(f"LCD:{message}")

    def beep(self):
        """Make Arduino beep."""
        if self.is_connected:
            self.command_queue.put("BEEP")

    def disconnect(self):
        """Disconnect Arduino."""
        self.running = False
        self.is_connected = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1)
        if self.ser and self.ser.is_open:
            self.ser.close()
            logger.info("Arduino disconnected")