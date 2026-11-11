"""
Publishing Hub View for StickForge AI.
Connects YouTube Data API v3 and Instagram Reels publishing workflows with Smart Repurposing.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QPlainTextEdit,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QGroupBox,
    QFormLayout,
    QFileDialog,
    QMessageBox,
)

from app.storage.project_manager import ProjectData
from app.publishing.base_publisher import PublishingMetadata
from app.publishing.youtube_publisher import YouTubePublisher
from app.publishing.instagram_publisher import InstagramPublisher
from app.publishing.publishing_scheduler import SmartRepurposer, PublishingScheduler
from app.core.config import OUTPUT_DIR


class PublishingHubView(QWidget):
    """Social media publishing and queue management studio."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project: Optional[ProjectData] = None
        self.scheduler = PublishingScheduler()
        self.selected_video_path: Optional[Path] = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        hdr = QHBoxLayout()
        title_box = QVBoxLayout()
        title = QLabel("Social Media Publishing Hub")
        title.setStyleSheet("font-size: 20px; font-weight: 700; color: #F8FAFC;")
        sub = QLabel("Official YouTube Data API and Instagram Reels distribution with smart metadata repurposing.")
        sub.setStyleSheet("color: #94A3B8; font-size: 13px;")
        title_box.addWidget(title)
        title_box.addWidget(sub)
        hdr.addLayout(title_box)
        hdr.addStretch()
        layout.addLayout(hdr)

        # Main Metadata & Options Form
        grp = QGroupBox("Publishing Configuration & Smart Repurposing")
        form = QFormLayout(grp)

        # Video File Selection
        v_box = QHBoxLayout()
        self.lbl_video_path = QLabel("No video selected (select below or render from Timeline)")
        self.lbl_video_path.setStyleSheet("color: #94A3B8;")
        btn_browse = QPushButton("Browse MP4...")
        btn_browse.setProperty("class", "btn-secondary")
        btn_browse.clicked.connect(self._browse_video)
        v_box.addWidget(self.lbl_video_path, 1)
        v_box.addWidget(btn_browse)
        form.addRow("Video Media:", v_box)

        # Platform
        p_box = QHBoxLayout()
        self.cb_platform = QComboBox()
        self.cb_platform.addItems(["YouTube (Shorts / Standard)", "Instagram (Reels)"])
        p_box.addWidget(self.cb_platform, 1)

        btn_repurpose = QPushButton("✨ Smart Repurpose Metadata")
        btn_repurpose.setProperty("class", "btn-secondary")
        btn_repurpose.clicked.connect(self._auto_repurpose)
        p_box.addWidget(btn_repurpose)
        form.addRow("Target Platform:", p_box)

        self.edit_title = QLineEdit()
        form.addRow("Video Title:", self.edit_title)

        self.text_desc = QPlainTextEdit()
        self.text_desc.setMaximumHeight(90)
        form.addRow("Description / Caption:", self.text_desc)

        self.edit_tags = QLineEdit()
        self.edit_tags.setPlaceholderText("Comma separated tags, e.g. animation, shorts, stickman")
        form.addRow("Tags & Hashtags:", self.edit_tags)

        self.cb_privacy = QComboBox()
        self.cb_privacy.addItems(["public", "unlisted", "private"])
        form.addRow("Visibility:", self.cb_privacy)

        layout.addWidget(grp)

        # Action Buttons
        btn_bar = QHBoxLayout()
        btn_bar.addStretch()

        self.btn_publish = QPushButton("Publish Video Now")
        self.btn_publish.setProperty("class", "btn-primary")
        self.btn_publish.setMinimumHeight(38)
        self.btn_publish.clicked.connect(self._publish_now)
        btn_bar.addWidget(self.btn_publish)

        layout.addLayout(btn_bar)

        # Publishing Queue History
        q_hdr = QLabel("Publishing Queue & Upload History")
        q_hdr.setStyleSheet("font-weight: 600; color: #F1F5F9; margin-top: 10px;")
        layout.addWidget(q_hdr)

        self.table_queue = QTableWidget()
        self.table_queue.setColumnCount(6)
        self.table_queue.setHorizontalHeaderLabels([
            "Job ID", "Platform", "Title", "Status", "Remote ID / URL", "Created"
        ])
        self.table_queue.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_queue.setStyleSheet("background-color: #18191E; border: 1px solid #2D3039;")
        layout.addWidget(self.table_queue)

        self._refresh_queue()

    def load_project(self, project: ProjectData) -> None:
        self.project = project
        self.edit_title.setText(project.name)
        # Check if output video exists
        candidate = OUTPUT_DIR / f"{project.name.replace(' ', '_')}_{project.id}.mp4"
        if candidate.exists():
            self.selected_video_path = candidate
            self.lbl_video_path.setText(str(candidate.name))
        self._auto_repurpose()

    def _browse_video(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video to Publish", str(OUTPUT_DIR), "MP4 Videos (*.mp4)"
        )
        if file_path:
            self.selected_video_path = Path(file_path)
            self.lbl_video_path.setText(self.selected_video_path.name)

    def _auto_repurpose(self) -> None:
        title = self.project.name if self.project else (self.edit_title.text() or "Stickman Story")
        premise = self.project.topic if self.project else "An awesome stickman animated adventure."
        narr = self.project.script_text if self.project else ""

        if "Instagram" in self.cb_platform.currentText():
            meta = SmartRepurposer.generate_instagram_reels_metadata(title, premise, narr)
        else:
            meta = SmartRepurposer.generate_youtube_shorts_metadata(title, premise, narr)

        self.edit_title.setText(meta.title)
        self.text_desc.setPlainText(meta.description)
        self.edit_tags.setText(", ".join(meta.tags))

    def _publish_now(self) -> None:
        if not self.selected_video_path or not self.selected_video_path.exists():
            QMessageBox.warning(
                self, "No Video Selected", "Please select a valid rendered MP4 video file first."
            )
            return

        title = self.edit_title.text().strip()
        desc = self.text_desc.toPlainText().strip()
        tags = [t.strip() for t in self.edit_tags.text().split(",") if t.strip()]
        privacy = self.cb_privacy.currentText()
        is_yt = "YouTube" in self.cb_platform.currentText()
        platform = "youtube" if is_yt else "instagram"

        metadata = PublishingMetadata(
            title=title,
            description=desc,
            tags=tags,
            privacy_status=privacy,
        )

        job_id = self.scheduler.schedule_job(
            project_id=self.project.id if self.project else "p_default",
            platform=platform,
            media_path=self.selected_video_path,
            metadata=metadata,
        )

        # Execute
        res = self.scheduler.execute_job_now(job_id)
        self._refresh_queue()

        if res.success:
            sim_notice = "\n(Simulated Upload: Validated metadata & stream format successfully)" if res.is_simulated else ""
            QMessageBox.information(
                self,
                "Publishing Successful",
                f"Video published successfully to {platform.capitalize()}!{sim_notice}\n\nVideo ID: {res.video_id}\nURL: {res.url}",
            )
        else:
            QMessageBox.critical(
                self,
                "Publishing Failed",
                f"Failed to publish to {platform}:\n{res.error_message}",
            )

    def _refresh_queue(self) -> None:
        queue = self.scheduler.list_queue(limit=20)
        self.table_queue.setRowCount(len(queue))
        for row, job in enumerate(queue):
            self.table_queue.setItem(row, 0, QTableWidgetItem(job.get("id", "")))
            self.table_queue.setItem(row, 1, QTableWidgetItem(job.get("platform", "").capitalize()))
            self.table_queue.setItem(row, 2, QTableWidgetItem(job.get("title", "")))
            self.table_queue.setItem(row, 3, QTableWidgetItem(job.get("status", "")))
            self.table_queue.setItem(row, 4, QTableWidgetItem(job.get("remote_id", "") or "—"))
            self.table_queue.setItem(row, 5, QTableWidgetItem(str(job.get("created_at", ""))))
