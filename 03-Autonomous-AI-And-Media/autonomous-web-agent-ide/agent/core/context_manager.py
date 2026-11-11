import json
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    from execution.filesystem import FileSystem
    from security.secret_scanner import SecretScanner
except ImportError:
    from ..execution.filesystem import FileSystem
    from ..security.secret_scanner import SecretScanner

MAX_FILE_PREVIEW_BYTES = 12000
MAX_TOTAL_CONTEXT_CHARS = 45000

class ContextManager:
    @staticmethod
    def generate_tree_structure(files: List[Dict[str, Any]]) -> str:
        """
        Generates a clean visual ASCII directory tree of the workspace.
        """
        tree_lines = ["📁 WORKSPACE ROOT TOPOLOGY:"]
        for f in files[:50]:
            path = f["path"]
            parts = path.split("/")
            indent = "  " * (len(parts) - 1)
            tree_lines.append(f"{indent}├── {parts[-1]}")
        return "\n".join(tree_lines)

    @staticmethod
    def build_task_context(
        workspace_root: str,
        current_task: Dict[str, Any],
        recent_commands: List[Dict[str, Any]],
        error_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Builds a comprehensive, secret-scrubbed context prompt for DeepSeek R1.
        """
        files = FileSystem.list_files(workspace_root)
        tree_diagram = ContextManager.generate_tree_structure(files)
        file_tree_summary = [f["path"] for f in files[:50]]

        # Dynamic relevance extraction using ProjectGraph
        important_paths = ["package.json", "requirements.txt", "index.html", "vite.config.js"]
        try:
            from core.project_graph import ProjectGraph
            graph = ProjectGraph(workspace_root)
            graph.build_graph()
            task_query = f"{current_task.get('title', '')} {current_task.get('description', '')}"
            smart_files = graph.find_relevant_files(task_query, limit=8)
            for sf in smart_files:
                if sf not in important_paths:
                    important_paths.append(sf)
        except Exception:
            # Fallback to key source candidates
            for cand in ["src/App.jsx", "src/main.jsx", "src/index.css", "main.py"]:
                if (Path(workspace_root) / cand).is_file() and cand not in important_paths:
                    important_paths.append(cand)

        # Include recently modified files
        for f in files[:8]:
            if f["path"] not in important_paths:
                important_paths.append(f["path"])

        file_previews = {}
        for p in important_paths:
            try:
                content, _ = FileSystem.read_file(workspace_root, p)
                if content.startswith("// [Binary"):
                    continue
                if not SecretScanner.is_forbidden_file(p):
                    redacted, _ = SecretScanner.scan_and_redact(content[:MAX_FILE_PREVIEW_BYTES])
                    file_previews[p] = redacted
            except Exception:
                pass

        context_obj = {
            "current_task": {
                "id": current_task.get("id"),
                "title": current_task.get("title"),
                "description": current_task.get("description")
            },
            "workspace_topology": tree_diagram,
            "all_workspace_files": file_tree_summary,
            "existing_file_contents": file_previews,
            "recent_commands": recent_commands[-3:],
            "error_context": error_context
        }

        context_str = json.dumps(context_obj, indent=2)
        redacted_context, _ = SecretScanner.scan_and_redact(context_str)

        # Scrub any rogue null bytes or escaped null byte representations
        redacted_context = redacted_context.replace("\x00", "").replace("\\u0000", "")

        if len(redacted_context) > MAX_TOTAL_CONTEXT_CHARS:
            redacted_context = redacted_context[:MAX_TOTAL_CONTEXT_CHARS] + "\n...[Context truncated]..."

        return redacted_context
