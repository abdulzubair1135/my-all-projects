"""
Unit tests for AURA Configuration module.
"""

import unittest
from config import SystemConfig, HardwareConfig, ModelConfig, StorageConfig

class TestConfig(unittest.TestCase):
    def test_default_config_values(self):
        cfg = SystemConfig()
        self.assertEqual(cfg.hardware.vram_mb, 4096)
        self.assertEqual(cfg.hardware.ram_gb, 16)
        self.assertEqual(cfg.models.fast_model, "qwen3:1.7b")
        self.assertEqual(cfg.models.normal_model, "qwen3:4b")
        self.assertTrue(cfg.storage.db_path.name.endswith(".db"))

if __name__ == "__main__":
    unittest.main()
