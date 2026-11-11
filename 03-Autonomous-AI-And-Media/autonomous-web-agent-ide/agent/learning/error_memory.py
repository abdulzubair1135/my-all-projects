"""
error_memory.py
Self-learning error fingerprint memory for Autonomous Web-Agent IDE.

Stores successful fix patterns in SQLite so the agent can instantly
resolve previously-seen errors without consulting AI.
"""

import hashlib
import json
import re
import sqlite3
import time
from pathlib import Path
from typing import Optional, Dict, Any


class ErrorMemory:
    """
    Persistent error fingerprint memory.
    
    Flow:
        Error occurs → fingerprint() → lookup() → 
        if known: apply cached patch immediately
        else: consult AI → record_success() after fix
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_tables()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_tables(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS error_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fingerprint TEXT UNIQUE NOT NULL,
                    error_type TEXT,
                    normalized_message TEXT,
                    affected_command TEXT,
                    root_cause TEXT,
                    successful_patch TEXT,
                    patch_type TEXT,
                    patch_description TEXT,
                    success_count INTEGER DEFAULT 1,
                    fail_count INTEGER DEFAULT 0,
                    provider TEXT,
                    project_type TEXT,
                    created_at REAL,
                    last_seen REAL,
                    last_success REAL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_fingerprint ON error_memory(fingerprint)")
            conn.commit()

    # ─── Fingerprinting ───────────────────────────────────────────────────────

    def fingerprint(
        self,
        stderr: str,
        command: str = "",
        exit_code: int = 1,
        project_type: str = "",
    ) -> str:
        """
        Generate a stable fingerprint for an error.
        
        Strips volatile parts (line numbers, timestamps, temp paths)
        so the same logical error always produces the same fingerprint.
        """
        normalized = self._normalize_error(stderr)
        raw = f"{normalized}|{command.split()[0] if command else ''}|{exit_code}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def _normalize_error(self, text: str) -> str:
        """Remove volatile tokens from error text."""
        if not text:
            return ""
        # Remove line numbers like "line 42", ":42:", "(line 42)"
        text = re.sub(r'(line\s+\d+|:\d+:|^\s*\d+\s*\|)', '', text, flags=re.MULTILINE | re.IGNORECASE)
        # Remove temp/cache paths
        text = re.sub(r'/tmp/[^\s]+', '/tmp/...', text)
        text = re.sub(r'C:\\Users\\[^\\]+\\AppData\\[^\s]+', 'APPDATA/...', text)
        text = re.sub(r'C:\\Users\\[^\\]+\\Temp\\[^\s]+', 'TEMP/...', text)
        # Remove timestamps
        text = re.sub(r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}', 'TIMESTAMP', text)
        # Remove memory addresses
        text = re.sub(r'0x[0-9a-fA-F]+', '0xADDR', text)
        # Remove UUIDs
        text = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 'UUID', text, flags=re.IGNORECASE)
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Take first 500 chars — enough for identity, not too volatile
        return text[:500]

    # ─── Lookup ───────────────────────────────────────────────────────────────

    def lookup(self, fingerprint: str) -> Optional[Dict[str, Any]]:
        """
        Look up a known fix for an error fingerprint.
        Returns fix dict if found and previously successful, else None.
        """
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT * FROM error_memory
                WHERE fingerprint = ?
                  AND success_count > 0
                  AND successful_patch IS NOT NULL
                ORDER BY success_count DESC
                LIMIT 1
                """,
                (fingerprint,),
            ).fetchone()

        if not row:
            return None

        return {
            "fingerprint": row["fingerprint"],
            "error_type": row["error_type"],
            "root_cause": row["root_cause"],
            "successful_patch": json.loads(row["successful_patch"]) if row["successful_patch"] else None,
            "patch_type": row["patch_type"],
            "patch_description": row["patch_description"],
            "success_count": row["success_count"],
            "fail_count": row["fail_count"],
            "provider": row["provider"],
        }

    # ─── Recording ────────────────────────────────────────────────────────────

    def record_success(
        self,
        fingerprint: str,
        stderr: str,
        command: str,
        root_cause: str,
        patch: Any,  # list of action dicts or string patch
        patch_type: str,  # "actions" | "command" | "code_patch"
        patch_description: str,
        provider: str = "",
        project_type: str = "",
        error_type: str = "",
    ):
        """Record a successfully applied fix."""
        now = time.time()
        patch_json = json.dumps(patch) if not isinstance(patch, str) else json.dumps({"raw": patch})
        normalized = self._normalize_error(stderr)

        with self._conn() as conn:
            existing = conn.execute(
                "SELECT id, success_count FROM error_memory WHERE fingerprint = ?",
                (fingerprint,),
            ).fetchone()

            if existing:
                conn.execute(
                    """
                    UPDATE error_memory
                    SET success_count = success_count + 1,
                        last_seen = ?,
                        last_success = ?,
                        successful_patch = ?,
                        patch_description = ?,
                        root_cause = ?,
                        provider = ?
                    WHERE fingerprint = ?
                    """,
                    (now, now, patch_json, patch_description, root_cause, provider, fingerprint),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO error_memory
                    (fingerprint, error_type, normalized_message, affected_command,
                     root_cause, successful_patch, patch_type, patch_description,
                     provider, project_type, created_at, last_seen, last_success)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        fingerprint, error_type, normalized, command,
                        root_cause, patch_json, patch_type, patch_description,
                        provider, project_type, now, now, now,
                    ),
                )
            conn.commit()

    def record_failure(self, fingerprint: str):
        """Increment fail_count for a known fix that didn't work this time."""
        with self._conn() as conn:
            conn.execute(
                "UPDATE error_memory SET fail_count = fail_count + 1, last_seen = ? WHERE fingerprint = ?",
                (time.time(), fingerprint),
            )
            conn.commit()

    def record_seen(self, fingerprint: str, stderr: str, command: str, error_type: str = ""):
        """Record that we've seen this error (even before we have a fix)."""
        now = time.time()
        normalized = self._normalize_error(stderr)
        with self._conn() as conn:
            existing = conn.execute(
                "SELECT id FROM error_memory WHERE fingerprint = ?", (fingerprint,)
            ).fetchone()
            if not existing:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO error_memory
                    (fingerprint, error_type, normalized_message, affected_command, created_at, last_seen)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (fingerprint, error_type, normalized, command, now, now),
                )
            else:
                conn.execute(
                    "UPDATE error_memory SET last_seen = ? WHERE fingerprint = ?",
                    (now, fingerprint),
                )
            conn.commit()

    # ─── Stats ────────────────────────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        """Return memory statistics."""
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) as c FROM error_memory").fetchone()["c"]
            known = conn.execute(
                "SELECT COUNT(*) as c FROM error_memory WHERE success_count > 0"
            ).fetchone()["c"]
            hits = conn.execute(
                "SELECT SUM(success_count) as s FROM error_memory"
            ).fetchone()["s"] or 0
            top = conn.execute(
                """
                SELECT normalized_message, success_count, patch_description
                FROM error_memory
                WHERE success_count > 0
                ORDER BY success_count DESC
                LIMIT 5
                """
            ).fetchall()

        return {
            "total_errors_seen": total,
            "known_fixes": known,
            "total_auto_fixes_applied": hits,
            "top_fixes": [dict(r) for r in top],
        }

    def list_all(self) -> list:
        """Return all memory entries for display."""
        with self._conn() as conn:
            rows = conn.execute(
                """
                SELECT fingerprint, error_type, normalized_message, root_cause,
                       patch_description, success_count, fail_count, provider, last_seen
                FROM error_memory
                ORDER BY last_seen DESC
                LIMIT 100
                """
            ).fetchall()
        return [dict(r) for r in rows]
