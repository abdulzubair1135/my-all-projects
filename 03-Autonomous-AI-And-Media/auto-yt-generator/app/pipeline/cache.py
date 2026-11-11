"""
AUTO YT GENERATOR — Hash-Based Caching Layer.

Provides fast SHA256/xxhash key generation and disk/sqlite cache storage
to avoid regenerating identical AI scripts, voice clips, or assets.
"""

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Optional
from pathlib import Path
from app.constants import DB_FILE
from app.logger import logger


class CacheManager:
    """Manages cache lookups and storage using input hashing."""

    def __init__(self, db_path: str = DB_FILE, ttl_seconds: int = 86400):
        self.db_path = db_path
        self.ttl_seconds = ttl_seconds
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Ensure cache table exists in database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    cache_key TEXT PRIMARY KEY,
                    stage TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP
                )
            """)
            conn.commit()

    @staticmethod
    def generate_key(stage: str, payload: Any) -> str:
        """Computes a deterministic hash key from the stage name and payload dictionary/string."""
        if isinstance(payload, dict):
            serialized = json.dumps(payload, sort_keys=True, default=str)
        else:
            serialized = str(payload)

        raw = f"{stage}:{serialized}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, cache_key: str) -> Optional[Any]:
        """Retrieves cached JSON object if present and not expired."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT data_json, expires_at FROM cache WHERE cache_key = ?",
                (cache_key,),
            )
            row = cursor.fetchone()
            if not row:
                return None

            expires_at_str = row["expires_at"]
            if expires_at_str:
                expires_at = datetime.fromisoformat(expires_at_str)
                if datetime.utcnow() > expires_at:
                    self.delete(cache_key)
                    return None

            logger.debug(f"Cache HIT for key: {cache_key[:12]}...")
            return json.loads(row["data_json"])

    def set(self, cache_key: str, stage: str, data: Any) -> None:
        """Stores a serialized JSON payload in the cache."""
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=self.ttl_seconds)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO cache (cache_key, stage, data_json, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    cache_key,
                    stage,
                    json.dumps(data, default=str),
                    now.isoformat(),
                    expires_at.isoformat(),
                ),
            )
            conn.commit()
            logger.debug(f"Cache SET for key: {cache_key[:12]}... (Stage: {stage})")

    def delete(self, cache_key: str) -> None:
        """Removes an item from cache."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cache WHERE cache_key = ?", (cache_key,))
            conn.commit()


# Default cache instance
cache = CacheManager()
