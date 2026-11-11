"""
Unit tests for Voiceover Generation, TTS Providers, and Lip Sync.
"""

import unittest
import tempfile
from pathlib import Path
from app.audio.providers.mock_tts_provider import MockTTSProvider
from app.audio.voice import VoiceEngine
from app.audio.lipsync import LipSyncEngine


class TestAudioVoiceEngine(unittest.TestCase):
    def setUp(self):
        self.mock_tts = MockTTSProvider()
        self.voice_engine = VoiceEngine(provider=self.mock_tts)
        self.lipsync_engine = LipSyncEngine()

    def test_mock_tts_generation(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = str(Path(tmp_dir) / "test_speech.wav")
            generated = self.mock_tts.generate_speech(
                text="Hello world, this is a test of automated narration.",
                output_path=out_file,
                language="en",
                speed=1.0,
            )
            self.assertTrue(Path(generated).exists())
            self.assertTrue(Path(generated).stat().st_size > 1000)

    def test_voice_engine_duration(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = str(Path(tmp_dir) / "test_dur.wav")
            audio_path, duration = self.voice_engine.generate_narration(
                text="The human brain consumes twenty percent of total energy.",
                output_path=out_file,
                language="en",
            )
            self.assertTrue(Path(audio_path).exists())
            self.assertTrue(duration > 1.0)

    def test_lipsync_mouth_mapping(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_file = str(Path(tmp_dir) / "test_lip.wav")
            audio_path, _ = self.voice_engine.generate_narration(
                text="Talking test line.",
                output_path=out_file,
            )

            mouth_0 = self.lipsync_engine.get_mouth_state_at_time(audio_path, time_sec=0.1, is_talking=True)
            mouth_1 = self.lipsync_engine.get_mouth_state_at_time(audio_path, time_sec=0.4, is_talking=True)

            self.assertIn(mouth_0, ["open", "a", "e", "o", "idle"])
            self.assertIn(mouth_1, ["open", "a", "e", "o", "idle"])


if __name__ == "__main__":
    unittest.main()
