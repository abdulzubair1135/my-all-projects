"""
AURA PDF Reader Module.
Extracts clean text and metadata from PDF files and document streams.
"""

from pathlib import Path
from typing import Dict, Any, Optional
from core.logger import setup_logger

logger = setup_logger("PDFReader")

class PDFReader:
    def read_pdf(self, file_path: str, max_pages: int = 20) -> Dict[str, Any]:
        path = Path(file_path)
        logger.info(f"Reading PDF file: '{path}'")

        if not path.exists():
            return {"status": "error", "error": f"File not found: {path}", "text": ""}

        # Try pypdf / PyPDF2 / pdfplumber if installed
        try:
            import pypdf
            reader = pypdf.PdfReader(str(path))
            pages_text = []
            for idx, page in enumerate(reader.pages[:max_pages]):
                pages_text.append(f"--- Page {idx+1} ---\n" + page.extract_text())
            full_text = "\n".join(pages_text)
            return {
                "status": "success",
                "page_count": len(reader.pages),
                "text": full_text
            }
        except Exception as e:
            logger.debug(f"pypdf not available or error: {e}. Trying fallback text extraction.")

        # Basic fallback text stream extraction
        try:
            with open(path, "rb") as f:
                content = f.read().decode("latin-1", errors="ignore")
                import re
                text_blocks = re.findall(r'\((.*?)\)\s*Tj', content)
                clean_text = " ".join(text_blocks)
                return {
                    "status": "success",
                    "page_count": 1,
                    "text": clean_text[:10000]
                }
        except Exception as e:
            logger.error(f"Failed to read PDF '{path}': {e}")
            return {"status": "error", "error": str(e), "text": ""}

pdf_reader = PDFReader()
