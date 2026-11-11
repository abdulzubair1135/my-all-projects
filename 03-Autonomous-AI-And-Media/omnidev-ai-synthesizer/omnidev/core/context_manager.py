import zipfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import config

class ContextManager:
    """
    Context Management & Token Optimization Engine for OmniDev.
    """
    def __init__(self, workspace_dir: Optional[Path] = None):
        self.workspace_dir = Path(workspace_dir or config.WORKSPACE_DIR)

    def estimate_tokens(self, text: str) -> int:
        return len(text) // 4

    def select_relevant_context(self, task_description: str, max_tokens: int = 16000) -> str:
        files = list(self.workspace_dir.rglob("*.*"))
        ranked_files = []
        keywords = [k.lower() for k in task_description.split() if len(k) > 3]

        for p in files:
            if any(part in p.parts for part in ["node_modules", "venv", ".git", "__pycache__"]):
                continue
            if p.suffix in [".py", ".html", ".js", ".css", ".kt", ".java", ".json", ".sql"]:
                rel = p.relative_to(self.workspace_dir).as_posix()
                score = sum(5 for kw in keywords if kw in rel.lower())
                ranked_files.append((score, p, rel))

        ranked_files.sort(key=lambda x: x[0], reverse=True)

        chunks = []
        curr_tokens = 0

        for _, full_path, rel in ranked_files:
            try:
                content = full_path.read_text(encoding="utf-8", errors="ignore")
                toks = self.estimate_tokens(content)
                if curr_tokens + toks <= max_tokens:
                    chunks.append(f"--- FILE: {rel} ---\n{content}\n")
                    curr_tokens += toks
            except Exception:
                pass

        return "\n".join(chunks)
