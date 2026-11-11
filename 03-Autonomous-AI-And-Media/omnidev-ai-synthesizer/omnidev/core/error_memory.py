import re
import hashlib
import time
from typing import Optional, Dict, Any
from core.memory_vault import MemoryVault
from config import console

class ErrorMemory:
    """
    Error Fingerprinting & Failure Learning Engine for OmniDev.
    """
    def __init__(self, vault: Optional[MemoryVault] = None):
        self.vault = vault or MemoryVault()

    def normalize_error(self, raw_error: str) -> str:
        cleaned = re.sub(r"0x[0-9a-fA-F]+", "0xADDR", raw_error)
        cleaned = re.sub(r'File ".*?[/\\]([^/\\]+)", line \d+', r'File "\1", line LINE', cleaned)
        cleaned = re.sub(r"line \d+, in", "line LINE, in", cleaned)
        cleaned = re.sub(r"\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}", "TIMESTAMP", cleaned)
        return cleaned.strip()

    def generate_fingerprint(self, raw_error: str) -> str:
        normalized = self.normalize_error(raw_error)
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]

    def lookup_solution(self, raw_error: str) -> Optional[Dict[str, Any]]:
        fp = self.generate_fingerprint(raw_error)
        with self.vault._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM error_fingerprints WHERE fingerprint = ?", (fp,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def record_solution(self, raw_error: str, root_cause: str, patch: str, success: bool = True):
        fp = self.generate_fingerprint(raw_error)
        norm = self.normalize_error(raw_error)[:500]
        with self.vault._get_conn() as conn:
            cursor = conn.cursor()
            if success:
                cursor.execute("""
                    INSERT INTO error_fingerprints (fingerprint, error_type, normalized_message, root_cause, solution_patch, success_count, last_seen)
                    VALUES (?, ?, ?, ?, ?, 1, ?)
                    ON CONFLICT(fingerprint) DO UPDATE SET
                        solution_patch = excluded.solution_patch,
                        success_count = success_count + 1,
                        last_seen = excluded.last_seen
                """, (fp, "Runtime/Compiler", norm, root_cause, patch, time.time()))
            else:
                cursor.execute("""
                    INSERT INTO error_fingerprints (fingerprint, error_type, normalized_message, root_cause, solution_patch, failed_count, last_seen)
                    VALUES (?, ?, ?, ?, ?, 1, ?)
                    ON CONFLICT(fingerprint) DO UPDATE SET
                        failed_count = failed_count + 1,
                        last_seen = excluded.last_seen
                """, (fp, "Runtime/Compiler", norm, root_cause, patch, time.time()))
            conn.commit()
        try:
            console.print(f"[cyan]Indexed Error Fingerprint in Memory:[/cyan] {fp} (Success={success})")
        except Exception:
            pass
