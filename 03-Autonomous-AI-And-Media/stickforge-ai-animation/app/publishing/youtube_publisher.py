"""
YouTube Data API v3 Publisher for StickForge AI.
Handles OAuth2 authorized video uploads, resumable chunked upload, and testing mocks.
"""

from __future__ import annotations
import os
import time
import uuid
from pathlib import Path
from typing import Optional, List

from app.core.logging_manager import get_logger
from app.publishing.base_publisher import BasePublisher, PublishingMetadata, PublishingResult
from app.video.ffmpeg_manager import probe_media

logger = get_logger("youtube_publisher")


class YouTubePublisher(BasePublisher):
    """YouTube Data API v3 implementation."""

    def __init__(self, client_secrets_file: Optional[Path] = None, simulate_mode: bool = False):
        self.client_secrets_file = client_secrets_file
        self.simulate_mode = simulate_mode or not bool(client_secrets_file and client_secrets_file.exists())

    def validate_media_and_metadata(self, media_path: Path, metadata: PublishingMetadata) -> List[str]:
        errors = []
        if not media_path.exists():
            errors.append(f"Media file does not exist: {media_path}")
            return errors

        if not metadata.title.strip():
            errors.append("Video title cannot be empty.")
        elif len(metadata.title) > 100:
            errors.append("Video title exceeds YouTube's 100 character limit.")

        try:
            info = probe_media(media_path)
            if not info["has_video"]:
                errors.append("Media file contains no video stream.")
            if info["duration"] <= 0.0:
                errors.append("Media duration must be greater than zero.")
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
                platform="youtube",
                status="FAILED",
                error_message="; ".join(errors),
            )

        if self.simulate_mode:
            logger.info("Publishing in verified simulation mode (no YouTube API client secrets configured).")
            if progress_callback:
                progress_callback(25.0)
                time.sleep(0.1)
                progress_callback(75.0)
                time.sleep(0.1)
                progress_callback(100.0)

            mock_id = f"yt_{uuid.uuid4().hex[:11]}"
            return PublishingResult(
                success=True,
                platform="youtube",
                video_id=mock_id,
                url=f"https://youtu.be/{mock_id}",
                status="COMPLETED",
                is_simulated=True,
            )

        # Real Google API upload
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            from google_auth_oauthlib.flow import InstalledAppFlow

            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.client_secrets_file),
                scopes=["https://www.googleapis.com/auth/youtube.upload"],
            )
            credentials = flow.run_local_server(port=0)
            youtube = build("youtube", "v3", credentials=credentials)

            body = {
                "snippet": {
                    "title": metadata.title,
                    "description": metadata.description,
                    "tags": metadata.tags,
                    "categoryId": "22",  # People & Blogs
                },
                "status": {
                    "privacyStatus": metadata.privacy_status,
                },
            }

            media = MediaFileUpload(str(media_path), chunksize=-1, resumable=True)
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            response = request.execute()

            vid = response.get("id")
            return PublishingResult(
                success=True,
                platform="youtube",
                video_id=vid,
                url=f"https://youtu.be/{vid}",
                status="COMPLETED",
            )
        except Exception as e:
            logger.error(f"YouTube upload failed: {e}", exc_info=True)
            return PublishingResult(
                success=False,
                platform="youtube",
                status="FAILED",
                error_message=str(e),
            )
