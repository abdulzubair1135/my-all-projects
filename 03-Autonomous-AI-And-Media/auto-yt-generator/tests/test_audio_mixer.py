"""
Unit tests for Audio Mixer and Voice Ducking Engine.
"""

import unittest
import tempfile
from pathlib import Path
from app.audio.mixer import AudioMixer
from app.audio.music import MusicGenerator
from app.audio.providers.mock_tts_provider import MockTTSProvider
from app.models.scene import SceneModel


class TestAudioMixer(unittest.TestCase):
    def setUp(self):
        self.mixer = AudioMixer(sample_rate=22050)
        self.music_gen = MusicGenerator(sample_rate=22050)
        self.mock_tts = MockTTSProvider()

    def test_audio_mixer_with_ducking(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # 1. Generate Voiceover
            v_path = str(Path(tmp_dir) / "voice1.wav")
            self.mock_tts.generate_speech("Test voiceover line for mixer.", v_path)

            # 2. Generate Music
            m_path = str(Path(tmp_dir) / "music.wav")
            self.music_gen.generate_music(duration_sec=6.0, output_path=m_path)

            # 3. Create Scene List
            scenes = [
                SceneModel(
                    scene_index=1,
                    duration_sec=6.0,
                    narration_text="Test voiceover line for mixer.",
                    background_id="bedroom_dark",
                    audio_file=v_path,
                )
            ]

            # 4. Master Mix
            out_master = str(Path(tmp_dir) / "master.wav")
            mixed_path = self.mixer.mix_project_audio(
                scenes=scenes,
                music_path=m_path,
                output_path=out_master,
                ducking_ratio=0.25,
            )

            self.assertTrue(Path(mixed_path).exists())
            self.assertTrue(Path(mixed_path).stat().st_size > 15000)


if __name__ == "__main__":
    unittest.main()
