"""
AURA Webpage Reader Module.
Fetches webpage content and extracts clean structured text and readable text body.
"""

import urllib.request
import urllib.parse
import re
from typing import Dict, Any, Optional
from core.logger import setup_logger

logger = setup_logger("WebpageReader")

class WebpageReader:
    def __init__(self, user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"):
        self.headers = {"User-Agent": user_agent}

    def read_url(self, url: str, max_chars: int = 5000) -> Dict[str, Any]:
        # Quote spaces or unquoted characters in URL
        encoded_url = urllib.parse.quote(url, safe=":/=?&%#")
        logger.info(f"Reading webpage content from URL: '{encoded_url}'")
        try:
            req = urllib.request.Request(encoded_url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                text = self._extract_text(html)
                truncated = text[:max_chars]
                return {
                    "url": encoded_url,
                    "status": "success",
                    "content": truncated,
                    "char_count": len(text)
                }
        except Exception as e:
            logger.error(f"Failed to read webpage '{encoded_url}': {e}")
            return {
                "url": encoded_url,
                "status": "error",
                "content": f"Failed to retrieve content: {e}",
                "char_count": 0
            }

    def _extract_text(self, html: str) -> str:
        # Remove script and style tags
        cleaned = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', html, flags=re.DOTALL | re.IGNORECASE)
        # Strip HTML tags
        text = re.sub(r'<[^>]+>', ' ', cleaned)
        # Collapse whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

webpage_reader = WebpageReader()
