import json
import re
from typing import Optional, Dict, Any, List

class ProtocolParser:
    """
    Robust extractor and parser for AI JSON responses.
    Handles DeepSeek R1 <think> tags, markdown code blocks, backticks, trailing commas,
    unescaped control characters, unclosed strings, and partial JSON healing.
    """

    @staticmethod
    def strip_think_tags(text: str) -> str:
        """Strips DeepSeek R1 <think>...</think> and <thinking>...</thinking> reasoning traces."""
        if not text:
            return ""
        cleaned = re.sub(r"<think(?:ing)?>[\s\S]*?</think(?:ing)?>", "", text, flags=re.IGNORECASE)
        return cleaned.strip()

    @staticmethod
    def extract_think_tags(text: str) -> Optional[str]:
        """Extracts DeepSeek R1 <think>...</think> or <thinking>...</thinking> reasoning trace."""
        if not text:
            return None
        match = re.search(r"<think(?:ing)?>([\s\S]*?)</think(?:ing)?>", text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None

    @classmethod
    def extract_json_block(cls, text: str) -> Optional[str]:
        if not text or not isinstance(text, str):
            return None

        clean_text = cls.strip_think_tags(text)

        # 1. Look for all ```json ... ``` code fences
        code_fence_matches = re.findall(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_text, re.IGNORECASE)
        for candidate in code_fence_matches:
            candidate = candidate.strip()
            if candidate.startswith("{") and candidate.endswith("}"):
                return candidate

        # 2. Look for outermost JSON object { ... }
        start_idx = clean_text.find("{")
        end_idx = clean_text.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            candidate = clean_text[start_idx : end_idx + 1].strip()
            return candidate

        if start_idx != -1:
            return clean_text[start_idx:].strip()

        return None

    @classmethod
    def heal_json_string(cls, json_str: str) -> str:
        """
        Attempts multi-pass healing on common LLM JSON formatting errors.
        """
        healed = json_str

        # Pass 1: Remove trailing commas before closing braces/brackets
        healed = re.sub(r",\s*([\]}])", r"\1", healed)

        # Pass 2: Clean non-printable control chars
        healed = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", healed)

        return healed

    @classmethod
    def parse_raw_response(cls, text: str, prompt: str = "") -> Dict[str, Any]:
        """
        Parse AI response into a structured dict.
        NEVER raises — uses CognitiveAIEngine as last-resort fallback.
        """
        json_str = cls.extract_json_block(text)

        if json_str:
            # Attempt 1: Direct parse
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

            # Attempt 2: Healed parse
            healed = cls.heal_json_string(json_str)
            try:
                return json.loads(healed)
            except json.JSONDecodeError:
                pass

            # Attempt 3: Auto-close unclosed strings and brackets
            try:
                fixed = healed
                if fixed.count('"') % 2 != 0:
                    fixed += '"'
                open_braces = fixed.count("{") - fixed.count("}")
                open_brackets = fixed.count("[") - fixed.count("]")
                auto_closed = fixed + ("]" * max(0, open_brackets)) + ("}" * max(0, open_braces))
                auto_closed = cls.heal_json_string(auto_closed)
                return json.loads(auto_closed)
            except Exception:
                pass

            # Attempt 4: Fallback action extractor using regex for individual actions
            actions = []
            file_matches = re.findall(
                r'\{\s*"type"\s*:\s*"(?:write_file|edit_file)"\s*,\s*"path"\s*:\s*"([^"]+)"\s*,\s*"content"\s*:\s*"([\s\S]*?)"\s*\}',
                json_str
            )
            for path, content in file_matches:
                try:
                    clean_content = json.loads(f'"{content}"')
                except Exception:
                    clean_content = content.replace('\\n', '\n').replace('\\"', '"')
                actions.append({
                    "type": "write_file",
                    "path": path,
                    "content": clean_content
                })

            if actions:
                return {
                    "summary": "Extracted actions via resilient recovery parser",
                    "actions": actions
                }

        # ── Last Resort: CognitiveAIEngine Fallback ─────────────────────────────
        # Determine if this looks like a plan request or code action request
        try:
            from core.cognitive_engine import CognitiveAIEngine as _CE
        except ImportError:
            try:
                from ..core.cognitive_engine import CognitiveAIEngine as _CE
            except ImportError:
                _CE = None

        context = ((text or "") + " " + (prompt or "")).lower()
        is_plan = any(k in context for k in [
            "project_name", "tasks", "dag", "architect", "plan", "task graph",
            "deconstruct", "architectural mission", "feature extension", "depends_on"
        ])

        if _CE:
            hint = (prompt or (text or "")[:300])
            if is_plan:
                return _CE.generate_plan(hint)
            else:
                return _CE.generate_code_actions(hint)

        # Absolute last resort — minimal valid plan
        return {
            "project_name": "project_update",
            "summary": "Implement the requested software changes",
            "tasks": [
                {
                    "id": "task-1",
                    "title": "Implement requested changes",
                    "description": (prompt or (text or "")[:300] or "Apply requested software updates"),
                    "depends_on": []
                }
            ]
        }
