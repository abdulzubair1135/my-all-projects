"""
Unit tests for AURA Model Adapter and Backends module.
"""

import unittest
from brain.ollama_backend import MockBackend
from brain.model_adapter import ModelAdapter
from core.model_router import ModelRouter

class TestModelAdapter(unittest.TestCase):
    def setUp(self):
        self.mock_backend = MockBackend()
        self.adapter = ModelAdapter(backend=self.mock_backend)
        self.router = ModelRouter()

    def test_mock_backend_generate(self):
        res = self.adapter.generate("Plan tasks for topic", model="qwen3:4b")
        self.assertIn("tasks", res)

    def test_mock_backend_chat(self):
        messages = [{"role": "user", "content": "evaluate output"}]
        res = self.adapter.chat(messages, model="qwen3:1.7b")
        self.assertIn("success", res)

    def test_model_router_selection(self):
        fast = self.router.select_model("trivial")
        self.assertEqual(fast, self.router.fast_model)
        normal = self.router.select_model("normal")
        self.assertEqual(normal, self.router.normal_model)

if __name__ == "__main__":
    unittest.main()
