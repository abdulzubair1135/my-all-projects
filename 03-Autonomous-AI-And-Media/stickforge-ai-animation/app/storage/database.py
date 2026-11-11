"""
SQLite Database connection and migration manager for StickForge AI.
Handles database initialization, schema versioning, and transaction execution.
"""

from __future__ import annotations
import sqlite3
import threading
from pathlib import Path
from typing import Any, Callable, List, Optional
from app.core.config import DATABASE_PATH
from app.core.logging_manager import get_logger

logger = get_logger("database")

CURRENT_SCHEMA_VERSION = 1


class Database:
    """Thread-safe SQLite connection and transaction manager."""

    def __init__(self, db_path: Path = DATABASE_PATH):
        self.db_path = db_path
        self._local = threading.local()
        self._init_lock = threading.Lock()

    def get_connection(self) -> sqlite3.Connection:
        """Get or initialize thread-local SQLite connection with WAL mode."""
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,
                check_same_thread=False,
            )
            conn.row_factory = sqlite3.Row
            # Enable WAL mode and foreign keys for durability and concurrency
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            self._local.conn = conn
        return self._local.conn

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query within the current thread connection."""
        conn = self.get_connection()
        return conn.execute(query, params)

    def executemany(self, query: str, seq_of_params: list) -> sqlite3.Cursor:
        conn = self.get_connection()
        return conn.executemany(query, seq_of_params)

    def commit(self) -> None:
        conn = self.get_connection()
        conn.commit()

    def rollback(self) -> None:
        conn = self.get_connection()
        conn.rollback()

    def initialize(self) -> None:
        """Create initial schema and run pending migrations."""
        with self._init_lock:
            conn = self.get_connection()
            with conn:
                # 1. Migration tracking table
                conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                );
                """)

                # Check applied version
                cur = conn.execute("SELECT MAX(version) FROM schema_migrations")
                row = cur.fetchone()
                applied_version = row[0] if (row and row[0] is not None) else 0

                if applied_version < 1:
                    logger.info("Applying database migration v1...")
                    self._apply_migration_v1(conn)
                    conn.execute(
                        "INSERT INTO schema_migrations (version, description) VALUES (1, 'Initial StickForge AI Schema')"
                    )

            logger.info("Database initialized successfully.")

    def _apply_migration_v1(self, conn: sqlite3.Connection) -> None:
        """Initial database tables creation."""
        conn.executescript("""
        -- Projects table
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            topic TEXT,
            genre TEXT,
            language TEXT DEFAULT 'hinglish',
            duration_target REAL DEFAULT 30.0,
            aspect_ratio TEXT DEFAULT '9:16',
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT
        );

        -- Characters
        CREATE TABLE IF NOT EXISTS characters (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            name TEXT NOT NULL,
            style TEXT DEFAULT 'classic_stickman',
            color TEXT DEFAULT '#FFFFFF',
            line_thickness INTEGER DEFAULT 4,
            voice_id TEXT,
            proportions_json TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        -- Scenes
        CREATE TABLE IF NOT EXISTS scenes (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            sequence_order INTEGER NOT NULL,
            duration REAL DEFAULT 5.0,
            background TEXT DEFAULT 'white',
            narration TEXT,
            dialogue TEXT,
            camera_settings_json TEXT,
            actions_json TEXT,
            sound_effects_json TEXT,
            transition TEXT DEFAULT 'none',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        -- Assets
        CREATE TABLE IF NOT EXISTS assets (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            asset_type TEXT NOT NULL, -- background, music, sfx, font, thumbnail
            file_path TEXT NOT NULL,
            source TEXT,
            license_info TEXT,
            attribution TEXT,
            is_commercial_allowed INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- AI Jobs
        CREATE TABLE IF NOT EXISTS ai_jobs (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            task_type TEXT NOT NULL, -- story, storyboard, narration, character
            provider TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            prompt TEXT,
            result_json TEXT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- AI Response Segments (For DeepSeek multi-step Continue automation)
        CREATE TABLE IF NOT EXISTS ai_response_segments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT NOT NULL,
            segment_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES ai_jobs(id) ON DELETE CASCADE
        );

        -- Render Jobs
        CREATE TABLE IF NOT EXISTS render_jobs (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            progress REAL DEFAULT 0.0,
            output_profile TEXT NOT NULL, -- shorts, reels, landscape
            output_file_path TEXT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
        );

        -- Publishing Accounts (Non-secret metadata)
        CREATE TABLE IF NOT EXISTS publishing_accounts (
            id TEXT PRIMARY KEY,
            platform TEXT NOT NULL, -- youtube, instagram
            account_name TEXT NOT NULL,
            is_authorized INTEGER DEFAULT 0,
            token_expiry TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Publishing Jobs
        CREATE TABLE IF NOT EXISTS publishing_jobs (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            platform TEXT NOT NULL,
            media_path TEXT NOT NULL,
            title TEXT,
            description TEXT,
            tags TEXT,
            scheduled_time TIMESTAMP,
            status TEXT DEFAULT 'PENDING',
            remote_id TEXT,
            error_message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );

        -- Task Checkpoints
        CREATE TABLE IF NOT EXISTS task_checkpoints (
            job_id TEXT PRIMARY KEY,
            task_type TEXT NOT NULL,
            step_name TEXT NOT NULL,
            state_data_json TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Browser Status History
        CREATE TABLE IF NOT EXISTS browser_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)


# Global Database instance
_db_instance: Optional[Database] = None


def get_db() -> Database:
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
        _db_instance.initialize()
    return _db_instance
