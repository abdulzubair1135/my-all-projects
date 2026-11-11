"""
AUTO YT GENERATOR — Semantic Narration & Sentiment Director.

Analyzes narration text at sentence and keyword levels to extract:
- Emotion (curiosity, fear, shock, urgency, humor, awe)
- Narrative Intent (hook, explain, escalate, surprise, question, conclude)
- Importance Weight (0.0 to 1.0)
- Highlight Keywords (for bouncing captions and motion graphics)
- Infographic / B-Roll Cutaway suitability
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from app.models.scene import SemanticCue, InfographicConfig


class SemanticDirector:
    """Extracts emotional, narrative, and visual triggers from spoken narration text."""

    EMOTION_KEYWORDS = {
        "fear": ["danger", "die", "death", "kill", "shut down", "collapse", "destroyed", "disaster", "fatal", "damage", "terrifying"],
        "shock": ["instant", "suddenly", "explodes", "massive", "unbelievable", "shocking", "never", "impossible", "insane"],
        "curiosity": ["why", "how", "what if", "secret", "mystery", "curiously", "turns out", "discover", "wonder"],
        "urgency": ["immediately", "seconds", "rapidly", "fast", "countdown", "running out", "critical", "emergency"],
        "awe": ["billion", "enormous", "galaxy", "universe", "infinite", "power", "energy", "trillion", "magnificent"],
    }

    def analyze_narration_beat(self, text: str, section_name: str = "") -> SemanticCue:
        """Analyzes a narration beat and returns rich semantic metadata."""
        cleaned = text.lower().strip()

        # 1. Detect Emotion
        detected_emotion = "neutral"
        highest_score = 0

        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in cleaned)
            if matches > highest_score:
                highest_score = matches
                detected_emotion = emotion

        # Default section emotional tone if no specific keywords matched
        if detected_emotion == "neutral":
            if "hook" in section_name:
                detected_emotion = "curiosity"
            elif "escalation" in section_name:
                detected_emotion = "urgency"
            elif "surprising" in section_name:
                detected_emotion = "shock"
            elif "question" in section_name:
                detected_emotion = "curiosity"

        # 2. Detect Intent
        intent = "explain"
        if "hook" in section_name or "?" in text:
            intent = "hook" if "hook" in section_name else "question"
        elif "escalat" in section_name:
            intent = "escalate"
        elif "surpris" in section_name:
            intent = "shock"
        elif "conclu" in section_name:
            intent = "conclude"

        # 3. Calculate Importance
        importance = 0.5
        if detected_emotion in ["shock", "fear"]:
            importance = 0.9
        elif detected_emotion in ["urgency", "curiosity"]:
            importance = 0.75
        elif intent == "hook":
            importance = 0.95

        # 4. Extract Highlight Keywords (Capitalized, numbers, or emotional keywords)
        words = re.findall(r"\b[A-Za-z0-9%$]+\b", text)
        highlights = []
        for w in words:
            w_lower = w.lower()
            if any(w_lower in kw_list for kw_list in self.EMOTION_KEYWORDS.values()) or any(c.isdigit() for c in w):
                if len(w) > 2 and w not in highlights:
                    highlights.append(w)

        if not highlights and words:
            # Pick longest meaningful word
            candidates = [w for w in words if len(w) > 4 and w.lower() not in ["this", "that", "which", "there", "their", "about", "could", "would"]]
            if candidates:
                highlights.append(max(candidates, key=len))

        return SemanticCue(
            emotion=detected_emotion,
            intent=intent,
            importance=importance,
            highlight_keywords=highlights[:4],
        )

    def detect_infographic_opportunity(self, text: str) -> Tuple[bool, Optional[InfographicConfig]]:
        """Checks if a narration beat contains statistics, comparisons, or data suitable for an infographic cutaway."""
        cleaned = text.lower()

        # Check for numbers / percentages / time / billions
        number_match = re.search(r"(\d+(?:\.\d+)?)\s*(percent|%|seconds?|minutes?|hours?|billion|million|trillion|watts?|calories?)?", cleaned)

        if "percent" in cleaned or "%" in cleaned or "billion" in cleaned or "energy" in cleaned or "statistics" in cleaned:
            stat_val = None
            suffix = ""
            if number_match:
                try:
                    stat_val = float(number_match.group(1))
                    suffix = number_match.group(2) or ""
                except Exception:
                    pass

            title = "KEY METRIC"
            if "brain" in cleaned:
                title = "BRAIN ENERGY DRAIN"
            elif "billion" in cleaned or "company" in cleaned:
                title = "MARKET VALUATION"
            elif "second" in cleaned:
                title = "CRITICAL TIMEFRAME"

            cfg = InfographicConfig(
                type="stats_counter" if stat_val else "alert_card",
                title=title,
                stat_number=stat_val or 100,
                stat_suffix=f" {suffix.upper()}".strip() if suffix else "",
                description=text[:80] + ("..." if len(text) > 80 else ""),
                highlight_color="#ec4899" if "danger" in cleaned else "#38bdf8",
            )
            return True, cfg

        return False, None


# Default semantic director instance
semantic_director = SemanticDirector()
