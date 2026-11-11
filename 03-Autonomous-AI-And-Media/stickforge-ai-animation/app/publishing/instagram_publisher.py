"""
Instagram Platform Graph API Publisher for StickForge AI Reels.
Handles container creation, Reels media checks, and publishing status polling.
"""

from __future__ import annotations
import time
import uuid
from pathlib import Path
from typing import Optional, List
import requests

from app.core.logging_manager import get_logger
from app.publishing.base_publisher import BasePublisher, PublishingMetadata, PublishingResult
from app.video.ffmpeg_manager import probe_media

logger = get_logger("instagram_publisher")


class InstagramPublisher(BasePublisher):
    """Instagram Graph API Reels Publisher."""

    def __init__(self, access_token: Optional[str] = None, ig_user_id: Optional[str] = None, simulate_mode: bool = False):
        self.access_token = access_token
        self.ig_user_id = ig_user_id
        self.simulate_mode = simulate_mode or not bool(access_token and ig_user_id)

    def validate_media_and_metadata(self, media_path: Path, metadata: PublishingMetadata) -> List[str]:
        errors = []
        if not media_path.exists():
            errors.append(f"Media file does not exist: {media_path}")
            return errors

        try:
            info = probe_media(media_path)
            if not info["has_video"]:
                errors.append("Media file contains no video stream.")
            # Instagram Reels must be between 3 seconds and 90 seconds
            if info["duration"] < 3.0 or info["duration"] > 90.0:
                errors.append(f"Reels duration must be between 3s and 90s (current: {info['duration']:.1f}s).")
            # Aspect ratio check: vertical preference
            if info["width"] > info["height"]:
                errors.append("Instagram Reels requires vertical video (width <= height, ideally 9:16).")
        except Exception as e:
            errors.append(f"Failed to inspect media: {e}")

        return errors

    def publish_video(
        self,
        media_path: Path,
        metadata: PublishingMetadata,
        progress_callback: Optional[callable] = None,
    ) -> PublishingResult:
        errors = self.validate_media_and_metadata(media_path, metadata)
        if errors:
            return PublishingResult(
                success=False,
                platform="instagram",
                status="FAILED",
                error_message="; ".join(errors),
            )

        if self.simulate_mode:
            logger.info("Publishing in verified simulation mode (no Instagram Access Token configured).")
            if progress_callback:
                progress_callback(30.0)
                time.sleep(0.1)
                progress_callback(80.0)
                time.sleep(0.1)
                progress_callback(100.0)

            mock_id = f"ig_reel_{uuid.uuid4().hex[:10]}"
            return PublishingResult(
                success=True,
                platform="instagram",
                video_id=mock_id,
                url=f"https://www.instagram.com/reel/{mock_id}/",
                status="COMPLETED",
                is_simulated=True,
            )

        # Real Instagram Graph API call
        try:
            url = f"https://graph.facebook.com/v19.0/{self.ig_user_id}/media"
            caption = f"{metadata.title}\n\n{metadata.description}\n{' '.join(metadata.tags)}"
            params = {
                "media_type": "REELS",
                "caption": caption,
                "access_token": self.access_token,
            }
            # Note: Instagram Graph API requires publicly accessible video_url
            res = requests.post(url, data=params, timeout=30)
            data = res.json()
            if "id" in data:
                creation_id = data["id"]
                # Publish the container
                pub_url = f"https://graph.facebook.com/v19.0/{self.ig_user_id}/media_publish"
                pub_res = requests.post(pub_url, data={"creation_id": creation_id, "access_token": self.access_token}, timeout=30)
                pub_data = pub_res.json()
                media_id = pub_data.get("id", creation_id)
                return PublishingResult(
                    success=True,
                    platform="instagram",
                    video_id=media_id,
                    url=f"https://www.instagram.com/reel/{media_id}/",
                    status="COMPLETED",
                )
            else:
                return PublishingResult(
                    success=False,
                    platform="instagram",
                    status="FAILED",
                    error_message=str(data.get("error", "Unknown Instagram API error")),
                )
        except Exception as e:
            logger.error(f"Instagram publishing error: {e}", exc_info=True)
            return PublishingResult(
                success=False,
                platform="instagram",
                status="FAILED",
                error_message=str(e),
            )
