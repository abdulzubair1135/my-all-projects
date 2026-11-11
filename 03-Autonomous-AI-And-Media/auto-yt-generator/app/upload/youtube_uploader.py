"""
AUTO YT GENERATOR — YouTube Direct Auto-Uploader (API v3).

Features:
- Uploads final MP4 video to YouTube channel
- Sets Title, Description, Tags, Category, and Privacy (public/unlisted/private)
- Uploads custom high-CTR thumbnail
- Graceful dry-run mode when client_secrets.json is not configured
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from app.models.project import ProjectModel
from app.models.script import ScriptModel
from app.logger import logger


class YouTubeUploader:
    """Handles authentication and automated video upload to YouTube."""

    def __init__(self, client_secrets_file: Optional[str] = "client_secrets.json"):
        self.client_secrets_file = client_secrets_file

    def upload_project_video(
        self,
        project: ProjectModel,
        privacy_status: str = "unlisted",
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Uploads rendered video and thumbnail for a project."""
        project_dir = Path(project.project_dir or f"projects/{project.id}")
        video_path = project_dir / "final" / "video.mp4"
        thumb_path = project_dir / "final" / "thumbnail.png"
        desc_path = project_dir / "final" / "description.txt"
        tags_path = project_dir / "final" / "tags.txt"

        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Load Metadata
        description = ""
        if desc_path.exists():
            with open(desc_path, "r", encoding="utf-8") as f:
                description = f.read()

        tags = []
        if tags_path.exists():
            with open(tags_path, "r", encoding="utf-8") as f:
                tags = [t.strip() for t in f.read().split(",") if t.strip()]

        title = project.title or project.config.topic

        secrets_exist = self.client_secrets_file and Path(self.client_secrets_file).exists()

        if dry_run or not secrets_exist:
            logger.info("YouTube Uploader running in SIMULATION mode (no client_secrets.json).")
            simulated_response = {
                "status": "SIMULATED_UPLOAD_SUCCESS",
                "video_id": f"sim_{project.id[:8]}",
                "title": title,
                "privacy": privacy_status,
                "video_url": f"https://youtu.be/sim_{project.id[:8]}",
                "thumbnail_uploaded": thumb_path.exists(),
                "note": "Add client_secrets.json to root folder to enable direct live channel upload.",
            }
            logger.info(f"YouTube Upload Simulated: {simulated_response['video_url']}")
            return simulated_response

        # Live Google API Client flow
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            from google_auth_oauthlib.flow import InstalledAppFlow

            SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
            flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, SCOPES)
            credentials = flow.run_local_server(port=0)
            youtube = build("youtube", "v3", credentials=credentials)

            body = {
                "snippet": {
                    "title": title[:100],
                    "description": description,
                    "tags": tags,
                    "categoryId": "28",  # Science & Technology
                },
                "status": {
                    "privacyStatus": privacy_status,
                },
            }

            media = MediaFileUpload(str(video_path), chunksize=-1, resumable=True)
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
            response = request.execute()
            video_id = response.get("id")

            # Upload thumbnail if available
            if thumb_path.exists() and video_id:
                youtube.thumbnails().set(videoId=video_id, media_body=MediaFileUpload(str(thumb_path))).execute()

            logger.info(f"Successfully uploaded to YouTube: https://youtu.be/{video_id}")
            return {
                "status": "UPLOAD_SUCCESS",
                "video_id": video_id,
                "video_url": f"https://youtu.be/{video_id}",
            }
        except Exception as e:
            logger.error(f"Live YouTube upload failed: {e}")
            raise


# Default uploader instance
youtube_uploader = YouTubeUploader()
