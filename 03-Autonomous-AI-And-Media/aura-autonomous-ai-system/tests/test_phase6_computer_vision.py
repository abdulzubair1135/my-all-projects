"""
Unit & Integration Tests for Phase 6 Computer Perception & Automation System.
"""

import unittest
from perception.screen import ScreenCapturer
from perception.ocr import OCREngine
from computer.mouse import MouseControl
from computer.keyboard import KeyboardControl
from core.controller import controller

class TestPhase6ComputerVision(unittest.TestCase):
    def setUp(self):
        self.screen = ScreenCapturer()
        self.ocr = OCREngine()
        self.mouse = MouseControl()
        self.keyboard = KeyboardControl()

    def test_screen_capturer(self):
        res = self.screen.capture_screen("test_capture.png")
        self.assertIn(res["status"], ["success", "fallback"])
        self.assertIn("hash", res)

    def test_ocr_engine(self):
        res = self.ocr.extract_text_from_image("non_existent_img.png")
        self.assertIn(res["status"], ["success", "fallback"])
        self.assertIn("text", res)

    def test_mouse_and_keyboard_autonomy_gate(self):
        # Level 1 autonomy -> Should be blocked
        controller.autonomy_level = 1
        res_m = self.mouse.click(100, 100)
        self.assertEqual(res_m["status"], "blocked")

        res_k = self.keyboard.type_text("hello")
        self.assertEqual(res_k["status"], "blocked")

        # Level 3 autonomy -> Should be permitted (simulated/success)
        controller.autonomy_level = 3
        res_m3 = self.mouse.click(100, 100)
        self.assertIn(res_m3["status"], ["success", "simulated"])

        # Reset autonomy level to default 1
        controller.autonomy_level = 1

if __name__ == "__main__":
    unittest.main()
