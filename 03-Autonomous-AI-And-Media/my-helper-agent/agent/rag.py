import os
import re
import sqlite3
from pypdf import PdfReader

class DocumentRAG:
    """
    Lightweight, local Document Knowledge Base:
    - Extracts text from PDFs, TXT, MD, Code files
    - Chunks text into logical passages
    - Stores into SQLite for indexed retrieval
    """
    def __init__(self, db_path="storage/memory.db", docs_dir="storage/docs"):
        self.db_path = db_path
        self.docs_dir = os.path.abspath(docs_dir)
        os.makedirs(self.docs_dir, exist_ok=True)
        self._init_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_table(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS doc_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                page_or_sec TEXT,
                chunk_index INTEGER,
                content TEXT NOT NULL
            )
            """)
            conn.commit()

    def ingest_pdf(self, pdf_path: str) -> dict:
        full_path = os.path.abspath(pdf_path)
        if not os.path.exists(full_path):
            return {"success": False, "error": f"PDF not found: {pdf_path}"}
        
        try:
            reader = PdfReader(full_path)
            filename = os.path.basename(full_path)
            total_pages = len(reader.pages)
            chunks_added = 0

            with self._get_connection() as conn:
                cursor = conn.cursor()
                # Clear previous chunks of same file to avoid duplicates
                cursor.execute("DELETE FROM doc_chunks WHERE filename = ?", (filename,))

                for idx, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    clean_text = re.sub(r"\s+", " ", text).strip()
                    if len(clean_text) > 40:
                        # Chunk into 600-word blocks with slight overlap
                        words = clean_text.split()
                        chunk_size = 400
                        for i in range(0, len(words), chunk_size - 50):
                            chunk_words = words[i:i + chunk_size]
                            chunk_str = " ".join(chunk_words)
                            cursor.execute("""
                                INSERT INTO doc_chunks (filename, page_or_sec, chunk_index, content)
                                VALUES (?, ?, ?, ?)
                            """, (filename, f"Page {idx + 1}", chunks_added, chunk_str))
                            chunks_added += 1
                conn.commit()

            return {
                "success": True,
                "filename": filename,
                "total_pages": total_pages,
                "chunks_indexed": chunks_added
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search(self, query: str, limit: int = 4) -> list:
        """Finds most relevant document chunks matching query terms."""
        keywords = [k.lower() for k in re.findall(r"\w+", query) if len(k) > 2]
        if not keywords:
            return []

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT filename, page_or_sec, content FROM doc_chunks")
            rows = cursor.fetchall()

            scored = []
            for filename, page_or_sec, content in rows:
                content_lower = content.lower()
                score = sum(content_lower.count(k) for k in keywords)
                if score > 0:
                    scored.append((score, filename, page_or_sec, content))

            scored.sort(key=lambda x: x[0], reverse=True)
            results = []
            for score, filename, page_or_sec, content in scored[:limit]:
                results.append({
                    "filename": filename,
                    "location": page_or_sec,
                    "content": content[:800]
                })
            return results
