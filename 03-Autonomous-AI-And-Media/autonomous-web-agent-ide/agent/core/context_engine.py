"""
context_engine.py
Smart Context Selection Engine for Autonomous Web-Agent IDE.

Selects only the most relevant, high-signal files and code snippets
for a given task or error, avoiding context window bloat and token waste.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from core.project_graph import ProjectGraph
    from execution.filesystem import FileSystem
    from security.secret_scanner import SecretScanner
except ImportError:
    from .project_graph import ProjectGraph
    from ..execution.filesystem import FileSystem
    from ..security.secret_scanner import SecretScanner


MAX_SNIPPET_BYTES = 6000
MAX_TOTAL_CONTEXT_CHARS = 35000


class ContextEngine:
    """
    Intelligent context curator.
    Uses ProjectGraph, task queries, and error stacktraces to assemble
    a focused, token-optimized context packet for LLM reasoning.
    """

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.graph = ProjectGraph(workspace_root)

    def select_context(
        self,
        task: Dict[str, Any],
        recent_commands: List[Dict[str, Any]] = None,
        error_context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Assembles a prioritized, secret-redacted context string for the prompt.
        """
        self.graph.build_graph()

        task_title = task.get("title", "")
        task_desc = task.get("description", "")
        query = f"{task_title} {task_desc}"

        # 1. Rank relevant files using knowledge graph
        relevant_files = self.graph.find_relevant_files(query, limit=6)

        # 2. Add configuration and entry point files
        configs = ["package.json", "requirements.txt", "vite.config.js", "src/App.jsx", "main.py"]
        for cfg in configs:
            if (self.workspace_root / cfg).is_file() and cfg not in relevant_files:
                relevant_files.append(cfg)

        # 3. Add impacted files if editing an existing component
        if relevant_files:
            impacted = self.graph.get_impacted_files(relevant_files[0])
            for imp in impacted[:2]:
                if imp not in relevant_files:
                    relevant_files.append(imp)

        # 4. Extract clean, secret-redacted snippets
        file_snippets = {}
        for rel_path in relevant_files[:8]:
            try:
                content, _ = FileSystem.read_file(str(self.workspace_root), rel_path)
                if content and not SecretScanner.is_forbidden_file(rel_path):
                    redacted, _ = SecretScanner.scan_and_redact(content[:MAX_SNIPPET_BYTES])
                    file_snippets[rel_path] = redacted
            except Exception:
                pass

        # 5. Build focused context object
        context_data = {
            "task": {
                "id": task.get("id"),
                "title": task_title,
                "description": task_desc,
            },
            "relevant_files": list(file_snippets.keys()),
            "file_contents": file_snippets,
        }

        if recent_commands:
            context_data["recent_commands"] = recent_commands[-2:]

        if error_context:
            context_data["active_error"] = error_context

        serialized = json.dumps(context_data, indent=2)
        redacted_final, _ = SecretScanner.scan_and_redact(serialized)

        if len(redacted_final) > MAX_TOTAL_CONTEXT_CHARS:
            redacted_final = redacted_final[:MAX_TOTAL_CONTEXT_CHARS] + "\n...[Context truncated for brevity]..."

        return redacted_final
