"""
Unit & Integration Tests for Phase 3 Research Engine System.
"""

import unittest
import tempfile
from pathlib import Path
from database.db import DatabaseManager
from brain.ollama_backend import MockBackend
from brain.model_adapter import ModelAdapter
from memory.embedding_service import EmbeddingService
from memory.vector_store import VectorStore
from memory.semantic_memory import SemanticMemory
from memory.episodic_memory import EpisodicMemory
from memory.knowledge_store import KnowledgeStore
from research.search import SearchEngine
from research.webpage_reader import WebpageReader
from research.source_ranker import SourceRanker
from research.verification import VerificationEngine
from research.research_engine import ResearchEngine

class TestPhase3Research(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_phase3.db"
        self.db = DatabaseManager(self.db_path)

        self.mock_backend = MockBackend()
        self.adapter = ModelAdapter(backend=self.mock_backend)

        self.embedder = EmbeddingService()
        self.vstore = VectorStore(embedder=self.embedder)
        self.semantic = SemanticMemory(db=self.db, store=self.vstore)
        self.episodic = EpisodicMemory(db=self.db, store=self.vstore)
        self.k_store = KnowledgeStore(semantic=self.semantic, episodic=self.episodic)

        self.search = SearchEngine()
        self.reader = WebpageReader()
        self.ranker = SourceRanker()
        self.verifier = VerificationEngine(adapter=self.adapter)
        self.research = ResearchEngine(
            k_store=self.k_store,
            search_inst=self.search,
            reader_inst=self.reader,
            ranker_inst=self.ranker,
            verifier_inst=self.verifier,
            db=self.db
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_search_engine(self):
        results = self.search.search("Python socket tutorial", max_results=3)
        self.assertGreater(len(results), 0)
        self.assertIn("title", results[0])
        self.assertIn("url", results[0])

    def test_webpage_reader_extraction(self):
        sample_html = "<html><body><h1>Python Sockets</h1><script>var x=1;</script><p>Sockets allow network communication.</p></body></html>"
        text = self.reader._extract_text(sample_html)
        self.assertIn("Python Sockets", text)
        self.assertIn("Sockets allow network communication.", text)
        self.assertNotIn("var x=1", text)

    def test_source_ranker(self):
        sources = [
            {"title": "Random Blog", "url": "https://randomblog.com/post", "snippet": "Sockets"},
            {"title": "Python Official Docs", "url": "https://docs.python.org/3/library/socket.html", "snippet": "Socket interface"}
        ]
        ranked = self.ranker.rank_sources(sources, query="Python socket library")
        self.assertEqual(ranked[0]["url"], "https://docs.python.org/3/library/socket.html")
        self.assertGreater(ranked[0]["confidence"], ranked[1]["confidence"])

    def test_verification_engine(self):
        res = self.verifier.verify_fact(
            claim="TCP protocol guarantees in-order delivery of data packets.",
            source_contents=["TCP is a connection-oriented protocol that ensures ordered, reliable delivery."]
        )
        self.assertTrue(res["verified"])
        self.assertGreaterEqual(res["confidence"], 0.7)

    def test_full_research_workflow(self):
        # 1. Research topic not in memory -> forces web research
        result = self.research.research_topic("Python Socket Programming", force_web=True)
        self.assertEqual(result["source"], "web_research")
        self.assertIn("fact_id", result)

        # 2. Re-research same topic without force_web -> uses memory search
        mem_result = self.research.research_topic("Python Socket Programming", force_web=False)
        self.assertEqual(mem_result["source"], "memory")
        self.assertTrue(len(mem_result["facts"]) > 0)

if __name__ == "__main__":
    unittest.main()
