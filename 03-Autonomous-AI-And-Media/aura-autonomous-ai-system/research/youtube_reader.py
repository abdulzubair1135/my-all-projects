"""
AURA YouTube Learning Module.
Extracts transcripts, captions, and structured timestamped sections from YouTube videos without video downloads.
"""

import urllib.request
import urllib.parse
import re
import json
from typing import Dict, Any, List, Optional
from core.logger import setup_logger

logger = setup_logger("YouTubeReader")

class YouTubeReader:
    def extract_video_id(self, url_or_id: str) -> Optional[str]:
        if len(url_or_id) == 11 and not ("/" in url_or_id or "." in url_or_id):
            return url_or_id
        
        # Matches youtube.com/watch?v=ID or youtu.be/ID
        match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url_or_id)
        return match.group(1) if match else None

    def fetch_transcript(self, url_or_id: str) -> Dict[str, Any]:
        video_id = self.extract_video_id(url_or_id)
        if not video_id:
            logger.error(f"Invalid YouTube URL or Video ID: {url_or_id}")
            return {"status": "error", "error": "Invalid YouTube URL or Video ID", "transcript": []}

        logger.info(f"Fetching transcript for YouTube Video ID: '{video_id}'")

        # Try youtube_transcript_api if available
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([item["text"] for item in transcript_list])
            return {
                "video_id": video_id,
                "status": "success",
                "full_text": full_text,
                "transcript": transcript_list
            }
        except Exception as e:
            logger.warning(f"youtube_transcript_api not available or error: {e}. Trying fallback HTML caption extraction.")

        # Fallback HTML timedtext caption fetch
        return self._fallback_caption_fetch(video_id)

    def _fallback_caption_fetch(self, video_id: str) -> Dict[str, Any]:
        url = f"https://www.youtube.com/watch?v={video_id}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                html = resp.read().decode("utf-8", errors="ignore")
                # Search for playerCaptionsTracklistRenderer
                match = re.search(r'"captionTracks":\s*(\[.*?\])', html)
                if match:
                    tracks = json.loads(match.group(1))
                    if tracks:
                        caption_url = tracks[0].get("baseUrl")
                        if caption_url:
                            with urllib.request.urlopen(caption_url, timeout=10) as cap_resp:
                                xml_text = cap_resp.read().decode("utf-8", errors="ignore")
                                text_lines = re.findall(r'<text[^>]*>(.*?)</text>', xml_text)
                                clean_lines = [re.sub(r'<[^>]+>', '', line).strip() for line in text_lines if line]
                                full_text = " ".join(clean_lines)
                                return {
                                    "video_id": video_id,
                                    "status": "success",
                                    "full_text": full_text,
                                    "transcript": [{"text": line, "start": i*5} for i, line in enumerate(clean_lines)]
                                }
        except Exception as e:
            logger.error(f"Fallback YouTube caption fetch error for '{video_id}': {e}")

        return {
            "video_id": video_id,
            "status": "error",
            "error": f"Captions unavailable for video {video_id}",
            "full_text": "",
            "transcript": []
        }

youtube_reader = YouTubeReader()
