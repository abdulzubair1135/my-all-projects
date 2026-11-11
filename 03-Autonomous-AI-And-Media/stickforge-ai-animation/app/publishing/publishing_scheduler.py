"""
Publishing Scheduler and Smart Repurposing Engine for StickForge AI.
Generates platform-optimized captions, tags, and manages publishing queues.
"""

from __future__ import annotations
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from app.storage.database import get_db
from app.publishing.base_publisher import PublishingMetadata, PublishingResult
from app.publishing.youtube_publisher import YouTubePublisher
from app.publishing.instagram_publisher import InstagramPublisher


class SmartRepurposer:
    """Adapts story metadata for YouTube Shorts and Instagram Reels audiences."""

    @staticmethod
    def generate_youtube_shorts_metadata(
        title: str, premise: str, full_narration: str
    ) -> PublishingMetadata:
        clean_title = f"{title[:80]} #Shorts"
        desc = (
            f"{premise}\n\n"
            f"Watch how our stickman hero faces the unexpected!\n\n"
            f"#Shorts #Animation #Stickman #StoryTime #HindiStories #Anime"
        )
        tags = ["Shorts", "Stickman", "Animation", "Cartoons", "Hinglish Stories", "Comedy Shorts"]
        return PublishingMetadata(
            title=clean_title,
            description=desc,
            tags=tags,
            privacy_status="public",
        )

    @staticmethod
    def generate_instagram_reels_metadata(
        title: str, premise: str, full_narration: str
    ) -> PublishingMetadata:
        caption = (
            f"🎬 {title}\n\n"
            f"{premise}\n\n"
            f"Follow for more epic stickman stories! 🔥\n\n"
            f"#stickman #animation #reelsindia #viralreels #reelskarofeelkaro #storyteller #2danimation"
        )
        tags = ["#stickman", "#animation", "#reels", "#viral"]
        return PublishingMetadata(
            title=title[:90],
            description=caption,
            tags=tags,
            privacy_status="public",
        )


class PublishingScheduler:
    """Manages publishing queue and schedules."""

    def __init__(self):
        self.db = get_db()
        self.yt_publisher = YouTubePublisher()
        self.ig_publisher = InstagramPublisher()

    def schedule_job(
        self,
        project_id: str,
        platform: str,
        media_path: Path,
        metadata: PublishingMetadata,
        scheduled_time_iso: Optional[str] = None,
    ) -> str:
        job_id = f"pub_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        query = """
        INSERT INTO publishing_jobs (id, project_id, platform, media_path, title, description, tags, scheduled_time, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
        """
        self.db.execute(
            query,
            (
                job_id,
                project_id,
                platform,
                str(media_path),
                metadata.title,
                metadata.description,
                ",".join(metadata.tags),
                scheduled_time_iso or datetime.datetime.now().isoformat(),
            ),
        )
        self.db.commit()
        return job_id

    def list_queue(self, limit: int = 50) -> List[Dict[str, Any]]:
        cursor = self.db.execute("SELECT * FROM publishing_jobs ORDER BY created_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in cursor.fetchall()]

    def execute_job_now(self, job_id: str) -> PublishingResult:
        cursor = self.db.execute("SELECT * FROM publishing_jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"Job {job_id} not found.")

        job = dict(row)
        platform = job["platform"]
        media_path = Path(job["media_path"])
        metadata = PublishingMetadata(
            title=job["title"] or "StickForge Animation",
            description=job["description"] or "",
            tags=job["tags"].split(",") if job["tags"] else [],
        )

        if platform == "youtube":
            res = self.yt_publisher.publish_video(media_path, metadata)
        elif platform == "instagram":
            res = self.ig_publisher.publish_video(media_path, metadata)
        else:
            res = PublishingResult(success=False, platform=platform, status="FAILED", error_message="Unknown platform")

        # Update DB
        status_str = "COMPLETED" if res.success else "FAILED"
        self.db.execute(
            "UPDATE publishing_jobs SET status = ?, remote_id = ?, error_message = ? WHERE id = ?",
            (status_str, res.video_id, res.error_message, job_id),
        )
        self.db.commit()
        return res
