"""
Unit & Integration Tests for Phase 2 Memory & Knowledge Graph System.
"""

import unittest
import tempfile
from pathlib import Path
from database.db import DatabaseManager
from memory.embedding_service import EmbeddingService
from memory.vector_store import VectorStore
from memory.semantic_memory import SemanticMemory
from memory.episodic_memory import EpisodicMemory
from memory.procedural_memory import ProceduralMemory
from memory.skill_memory import SkillMemory
from memory.self_model import SelfModel
from memory.knowledge_graph import KnowledgeGraph
from memory.knowledge_store import KnowledgeStore

class TestPhase2Memory(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_phase2.db"
        self.db = DatabaseManager(self.db_path)

        self.embedder = EmbeddingService()
        self.vstore = VectorStore(embedder=self.embedder)
        self.semantic = SemanticMemory(db=self.db, store=self.vstore)
        self.episodic = EpisodicMemory(db=self.db, store=self.vstore)
        self.procedural = ProceduralMemory(db=self.db)
        self.skills = SkillMemory(db=self.db)
        self.graph = KnowledgeGraph(db=self.db)
        self.self_m = SelfModel(db=self.db)
        self.store = KnowledgeStore(
            semantic=self.semantic,
            episodic=self.episodic,
            procedural=self.procedural,
            skills=self.skills,
            graph=self.graph,
            self_m=self.self_m
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_embedding_service(self):
        v1 = self.embedder.get_embedding("HTTP Protocol")
        v2 = self.embedder.get_embedding("HTTP Protocol")
        sim = self.embedder.cosine_similarity(v1, v2)
        self.assertAlmostEqual(sim, 1.0, places=5)

    def test_semantic_memory(self):
        fact_id = self.semantic.add_fact("HTTP", "HTTP is an application-layer protocol.", "rfc")
        self.assertIsNotNone(fact_id)

        res = self.semantic.search_facts("HTTP protocol", top_k=1)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["topic"], "HTTP")

    def test_episodic_memory(self):
        exp_id = self.episodic.add_experience(
            goal="Build WebSocket Server",
            result="FAILURE",
            lesson="Windows socket binding requires explicit host address",
            cause="Incorrect binding"
        )
        self.assertIsNotNone(exp_id)

        res = self.episodic.search_experiences("WebSocket server binding", top_k=1)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["result"], "FAILURE")

    def test_procedural_memory(self):
        self.procedural.add_procedure("Create FastAPI App", ["import FastAPI", "app = FastAPI()", "run uvicorn"])
        proc = self.procedural.get_procedure("Create FastAPI App")
        self.assertIsNotNone(proc)
        self.assertEqual(len(proc["steps"]), 3)

    def test_skill_memory(self):
        self.skills.record_skill_level("Python", "high", "medium")
        skill = self.skills.get_skill("Python")
        self.assertIsNotNone(skill)
        self.assertEqual(skill["theoretical_level"], "high")

    def test_knowledge_graph(self):
        self.graph.add_relation("Python", "has_subtopic", "FastAPI")
        self.graph.add_relation("FastAPI", "requires", "HTTP")

        subtopics = self.graph.get_subtopics("Python")
        self.assertIn("FastAPI", subtopics)

        prereqs = self.graph.get_prerequisites("FastAPI")
        self.assertIn("HTTP", prereqs)

    def test_knowledge_store_query(self):
        self.semantic.add_fact("Python", "Python is an interpreted high-level programming language.")
        res = self.store.query_memory("Python programming language")
        self.assertTrue(res["sufficient"])
        self.assertGreater(len(res["facts"]), 0)

    def test_self_model_summary(self):
        self.semantic.add_fact("Networking", "TCP guarantees packet delivery.")
        self.skills.record_skill_level("Networking", "medium", "low")

        summary = self.self_m.get_self_summary()
        self.assertIn("Networking", summary["known_topics"])

if __name__ == "__main__":
    unittest.main()
