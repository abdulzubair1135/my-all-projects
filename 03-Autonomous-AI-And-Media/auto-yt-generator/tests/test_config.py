"""
Unit tests for configuration loading and validation.
"""

import unittest
from app.config import load_config, Config


class TestConfig(unittest.TestCase):
    def test_config_defaults(self):
        config = load_config()
        self.assertIsInstance(config, Config)
        self.assertEqual(config.app.name, "AUTO YT GENERATOR")
        self.assertEqual(config.video.default_fps, 30)
        self.assertEqual(config.audio.sample_rate, 44100)
        self.assertIn("dark_cartoon", config.styles.available)


if __name__ == "__main__":
    unittest.main()
