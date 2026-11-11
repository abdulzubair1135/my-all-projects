"""
Unit tests for AI Research Engine.
"""

import unittest
from app.ai.research import ResearchEngine, ResearchResult
from app.ai.providers.local import LocalAIProvider


class TestAIResearch(unittest.TestCase):
    def setUp(self):
        self.provider = LocalAIProvider()
        self.engine = ResearchEngine(provider=self.provider)

    def test_research_topic_structure(self):
        result = self.engine.research_topic("What happens if you stop sleeping?")
        self.assertIsInstance(result, ResearchResult)
        self.assertTrue(len(result.verified_facts) > 0)
        self.assertTrue(len(result.assumptions) > 0)
        self.assertTrue(len(result.hypothetical_scenarios) > 0)
        self.assertTrue(len(result.estimates) > 0)
        self.assertTrue(len(result.key_concepts) > 0)


if __name__ == "__main__":
    unittest.main()
