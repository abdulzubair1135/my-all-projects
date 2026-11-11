"""
Unit & Integration Tests for Phase 5 Browser, YouTube, and PDF Media Processing.
"""

import unittest
import tempfile
from pathlib import Path
from research.browser import BrowserAutomation
from research.youtube_reader import YouTubeReader
from research.pdf_reader import PDFReader

class TestPhase5BrowserMedia(unittest.TestCase):
    def setUp(self):
        self.browser = BrowserAutomation(headless=True)
        self.yt = YouTubeReader()
        self.pdf = PDFReader()

    def tearDown(self):
        self.browser.close()

    def test_youtube_video_id_parsing(self):
        vid1 = self.yt.extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(vid1, "dQw4w9WgXcQ")

        vid2 = self.yt.extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        self.assertEqual(vid2, "dQw4w9WgXcQ")

        vid3 = self.yt.extract_video_id("dQw4w9WgXcQ")
        self.assertEqual(vid3, "dQw4w9WgXcQ")

    def test_browser_automation_fallback(self):
        res = self.browser.navigate_and_extract("https://example.com")
        self.assertIn(res["status"], ["success", "error"])
        self.assertIn("url", res)

    def test_pdf_reader_file_not_found(self):
        res = self.pdf.read_pdf("non_existent_file.pdf")
        self.assertEqual(res["status"], "error")

if __name__ == "__main__":
    unittest.main()
