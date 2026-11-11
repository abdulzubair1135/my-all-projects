"""
AURA Source Ranker Module.
Evaluates and ranks research sources based on domain authority, relevance, and content length.
"""

from typing import List, Dict, Any
from core.logger import setup_logger

logger = setup_logger("SourceRanker")

class SourceRanker:
    HIGH_AUTHORITY_DOMAINS = [
        "docs.python.org", "developer.mozilla.org", "github.com",
        "arxiv.org", "wikipedia.org", "pypi.org", "pytorch.org",
        "fastapi.tiangolo.com", "microsoft.com", "w3.org"
    ]

    def rank_sources(self, sources: List[Dict[str, Any]], query: str = "") -> List[Dict[str, Any]]:
        """
        Calculates confidence score (0.0 to 1.0) for each source and sorts descending by confidence.
        """
        ranked = []
        for s in sources:
            url = s.get("url", "").lower()
            title = s.get("title", "")
            snippet = s.get("snippet", "")

            score = 0.5  # Base confidence score

            # Domain authority boost
            if any(dom in url for dom in self.HIGH_AUTHORITY_DOMAINS):
                score += 0.3
            elif ".edu" in url or ".org" in url or ".gov" in url:
                score += 0.2

            # Query relevance boost
            if query:
                q_words = set(query.lower().split())
                title_words = set(title.lower().split())
                snippet_words = set(snippet.lower().split())
                overlap = len(q_words.intersection(title_words.union(snippet_words)))
                if q_words:
                    score += 0.2 * (overlap / len(q_words))

            confidence = round(min(score, 1.0), 2)
            item = dict(s)
            item["confidence"] = confidence
            ranked.append(item)

        ranked.sort(key=lambda x: x["confidence"], reverse=True)
        logger.info(f"Ranked {len(ranked)} sources. Highest confidence: {ranked[0]['confidence'] if ranked else 'N/A'}")
        return ranked

source_ranker = SourceRanker()
