"""
AURA Vector Store Module.
Provides lightweight local vector index and similarity search over embedded memories.
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from memory.embedding_service import EmbeddingService, embedding_service
from core.logger import setup_logger

logger = setup_logger("VectorStore")

class VectorItem:
    def __init__(self, item_id: str, text: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None):
        self.item_id = item_id
        self.text = text
        self.vector = vector
        self.metadata = metadata or {}

class VectorStore:
    def __init__(self, embedder: Optional[EmbeddingService] = None):
        self.embedder = embedder or embedding_service
        self.index: Dict[str, VectorItem] = {}

    def add_item(self, item_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> VectorItem:
        vector = self.embedder.get_embedding(text)
        item = VectorItem(item_id=item_id, text=text, vector=vector, metadata=metadata)
        self.index[item_id] = item
        logger.debug(f"VectorStore added item [{item_id}] (len text={len(text)})")
        return item

    def search(self, query: str, top_k: int = 5, threshold: float = 0.1) -> List[Tuple[VectorItem, float]]:
        """
        Performs vector similarity search against query string.
        Returns list of (VectorItem, similarity_score) tuples sorted descending by similarity.
        """
        if not query or not self.index:
            return []

        query_vec = self.embedder.get_embedding(query)
        results: List[Tuple[VectorItem, float]] = []

        for item in self.index.values():
            sim = self.embedder.cosine_similarity(query_vec, item.vector)
            if sim >= threshold:
                results.append((item, sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def clear(self):
        self.index.clear()

vector_store = VectorStore()
