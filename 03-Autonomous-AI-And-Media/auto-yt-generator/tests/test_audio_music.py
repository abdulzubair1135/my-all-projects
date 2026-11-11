"""
Unit tests for Procedural Music Generator and SFX Engine.
"""

import unittest
import tempfile
from pathlib import Path
from app.audio.music import MusicGenerator
from app.audio.sfx import SFXGenerator


class TestAudioMusicAndSFX(unittest.TestCase):
    def setUp(self):
        self.music_gen = MusicGenerator(sample_rate=22050)
        self.sfx_gen = SFXGenerator(sample_rate=22050)

    def test_generate_cinematic_music(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = str(Path(tmp_dir) / "test_cinematic.wav")
            generated = self.music_gen.generate_music(
                duration_sec=6.0,
                output_path=out_file,
                style="dark_suspense",
                bpm=90,
            )
            self.assertTrue(Path(generated).exists())
            self.assertTrue(Path(generated).stat().st_size > 10000)

    def test_generate_phonk_music(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = str(Path(tmp_dir) / "test_phonk.wav")
            generated = self.music_gen.generate_music(
                duration_sec=5.0,
                output_path=out_file,
                style="phonk",
                bpm=145,
            )
            self.assertTrue(Path(generated).exists())
            self.assertTrue(Path(generated).stat().st_size > 10000)

    def test_generate_sfx(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            sfx_list = ["whoosh", "heartbeat", "clock_ticking", "flatline_beep", "glitch", "sub_drop"]
            for s_id in sfx_list:
                out_path = str(Path(tmp_dir) / f"sfx_{s_id}.wav")
                res = self.sfx_gen.generate_sfx(s_id, out_path, duration_sec=1.0)
                self.assertTrue(Path(res).exists())


if __name__ == "__main__":
    unittest.main()
