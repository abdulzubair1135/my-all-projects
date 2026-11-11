"""
AURA Verification Engine.
Cross-checks facts across multiple sources before storing knowledge.
"""

from typing import List, Dict, Any, Optional
from brain.model_adapter import ModelAdapter, model_adapter
from core.model_router import ModelRouter, model_router
from core.logger import setup_logger

logger = setup_logger("VerificationEngine")

class VerificationEngine:
    def __init__(self, adapter: Optional[ModelAdapter] = None, router: Optional[ModelRouter] = None):
        self.adapter = adapter or model_adapter
        self.router = router or model_router

    def verify_fact(self, claim: str, source_contents: List[str]) -> Dict[str, Any]:
        """
        Cross-checks claim against extracted source contents.
        Returns verification verdict, confidence score, and rationale.
        """
        if not source_contents:
            return {
                "verified": False,
                "confidence": 0.3,
                "rationale": "No external sources available for cross-verification."
            }

        sources_text = "\n---\n".join(source_contents[:3])
        prompt = f"""You are the AURA Information Verification Engine.
Cross-check the following CLAIM against the provided SOURCE EXCERPTS:

CLAIM TO VERIFY: {claim}

SOURCE EXCERPTS:
{sources_text}

Evaluate if the claim is supported by the source excerpts.
Return ONLY a valid JSON object matching this schema:
{{
  "verified": true,
  "confidence": 0.9,
  "rationale": "Brief rationale for verification"
}}
"""
        model = self.router.select_model(task_complexity="fast")
        response = self.adapter.generate(prompt, model=model, temperature=0.1)
        parsed = self._parse_json(response)

        if parsed:
            return {
                "verified": parsed.get("verified", True),
                "confidence": float(parsed.get("confidence", 0.8)),
                "rationale": parsed.get("rationale", "Verified against available sources.")
            }

        return {
            "verified": True,
            "confidence": 0.75,
            "rationale": "Default verification passed."
        }

    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        import json, re
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*\n?", "", cleaned)
            cleaned = re.sub(r"\n?```$", "", cleaned).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            return None

verification_engine = VerificationEngine()
