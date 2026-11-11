"""
AURA Main Research Engine.
Orchestrates autonomous research: Memory Check -> Web Search -> Rank -> Extract -> Verify -> Store.
"""

import uuid
import datetime
from typing import Dict, Any, List, Optional
from memory.knowledge_store import KnowledgeStore, knowledge_store
from research.search import SearchEngine, search_engine
from research.webpage_reader import WebpageReader, webpage_reader
from research.source_ranker import SourceRanker, source_ranker
from research.verification import VerificationEngine, verification_engine
from database.db import DatabaseManager, db_manager
from core.logger import setup_logger

logger = setup_logger("ResearchEngine")

class ResearchEngine:
    def __init__(
        self,
        k_store: Optional[KnowledgeStore] = None,
        search_inst: Optional[SearchEngine] = None,
        reader_inst: Optional[WebpageReader] = None,
        ranker_inst: Optional[SourceRanker] = None,
        verifier_inst: Optional[VerificationEngine] = None,
        db: Optional[DatabaseManager] = None
    ):
        self.knowledge_store = k_store or knowledge_store
        self.search = search_inst or search_engine
        self.reader = reader_inst or webpage_reader
        self.ranker = ranker_inst or source_ranker
        self.verifier = verifier_inst or verification_engine
        self.db = db or db_manager

    def research_topic(self, topic: str, force_web: bool = False) -> Dict[str, Any]:
        """
        Researches a topic using the full workflow:
        1. Query existing KnowledgeStore memory.
        2. If memory insufficient (or force_web=True), search web.
        3. Rank sources by confidence & domain authority.
        4. Read top pages & extract text.
        5. Verify facts and store into SemanticMemory & SQLite sources table.
        """
        logger.info(f"Starting research process for topic: '{topic}'")

        # 1. Memory Check First
        if not force_web:
            mem_result = self.knowledge_store.query_memory(topic, threshold=0.3)
            if mem_result["sufficient"]:
                logger.info(f"Existing memory is sufficient for topic '{topic}'. Skipping web search.")
                return {
                    "topic": topic,
                    "source": "memory",
                    "confidence": mem_result["max_similarity"],
                    "facts": mem_result["facts"],
                    "experiences": mem_result["experiences"]
                }

        # 2. Web Search
        search_results = self.search.search(topic, max_results=5)

        # 3. Rank Sources
        ranked_sources = self.ranker.rank_sources(search_results, query=topic)

        # 4. Extract content from top source
        extracted_content = []
        for src in ranked_sources[:2]:
            url = src["url"]
            read_res = self.reader.read_url(url, max_chars=3000)
            if read_res["status"] == "success":
                extracted_content.append(read_res["content"])

            # Store in SQLite sources table
            src_id = f"src_{uuid.uuid4().hex[:8]}"
            now = datetime.datetime.now().isoformat()
            self.db.execute_update(
                """INSERT INTO sources (id, url_or_title, type, summary, confidence, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (src_id, url, "webpage", src.get("snippet", ""), src.get("confidence", 0.8), now)
            )

        # 5. Verification & Summary
        ver_result = self.verifier.verify_fact(topic, extracted_content)

        # 6. Store in Semantic Memory
        content_summary = "\n".join(extracted_content[:1])[:500] if extracted_content else f"Researched topic '{topic}'"
        fact_id = self.knowledge_store.semantic.add_fact(
            topic=topic,
            content=content_summary,
            source=ranked_sources[0]["url"] if ranked_sources else "web_search",
            confidence=ver_result["confidence"]
        )

        logger.info(f"Research completed for '{topic}'. Fact stored [{fact_id}] confidence={ver_result['confidence']}")
        return {
            "topic": topic,
            "source": "web_research",
            "fact_id": fact_id,
            "confidence": ver_result["confidence"],
            "rationale": ver_result["rationale"],
            "sources": ranked_sources,
            "content": content_summary
        }

research_engine = ResearchEngine()
