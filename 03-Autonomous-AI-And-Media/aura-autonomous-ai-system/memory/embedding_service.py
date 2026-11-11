"""
AURA Embedding Service.
Generates normalized vector embeddings for local semantic search.
Lightweight, local-first, zero-cloud dependency.
"""

import math
import hashlib
import json
from typing import List, Optional
from core.logger import setup_logger

logger = setup_logger("EmbeddingService")

class EmbeddingService:
    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def get_embedding(self, text: str) -> List[float]:
        """
        Generates a 128-dimensional normalized embedding vector for input text.
        Uses deterministic character n-gram hashing for local-first fast embedding generation.
        """
        if not text:
            return [0.0] * self.dimension

        vec = [0.0] * self.dimension
        cleaned_text = text.lower().strip()
        words = cleaned_text.split()

        # Token & character n-gram feature mapping
        for word in words:
            # Word hashing
            h_val = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
            idx = h_val % self.dimension
            vec[idx] += 1.0

            # Sub-word char 3-gram hashing
            for i in range(len(word) - 2):
                gram = word[i:i+3]
                g_val = int(hashlib.sha256(gram.encode("utf-8")).hexdigest(), 16)
                g_idx = g_val % self.dimension
                vec[g_idx] += 0.5

        # Normalize vector to unit length (L2 norm)
        magnitude = math.sqrt(sum(v * v for v in vec))
        if magnitude > 0:
            vec = [v / magnitude for v in vec]

        return vec

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calculates cosine similarity between two unit-normalized vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        return sum(a * b for a, b in zip(vec_a, vec_b))

embedding_service = EmbeddingService()
