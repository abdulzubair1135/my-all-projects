import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from config import console

class DatabaseTool:
    """
    Database Engine for OmniDev:
    Inspects schemas, queries data safely, creates migrations, and seeds records.
    """
    @staticmethod
    def inspect_sqlite_schema(db_path: Path) -> Dict[str, Any]:
        if not db_path.exists():
            return {"success": False, "error": "Database file not found"}

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = {row[0]: row[1] for row in cursor.fetchall()}
            conn.close()
            return {"success": True, "tables": tables}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def run_safe_query(db_path: Path, query: str, max_rows: int = 50) -> Dict[str, Any]:
        # Block destructive queries
        low = query.lower().strip()
        if any(w in low for w in ["drop table", "truncate", "delete from", "alter table", "update"]):
            return {"success": False, "error": "Destructive queries blocked in read-only runner."}

        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            rows = [dict(row) for row in cursor.fetchmany(max_rows)]
            conn.close()
            return {"success": True, "row_count": len(rows), "rows": rows}
        except Exception as e:
            return {"success": False, "error": str(e)}
