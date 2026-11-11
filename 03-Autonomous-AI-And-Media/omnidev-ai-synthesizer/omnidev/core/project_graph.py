import ast
from pathlib import Path
from typing import Dict, Any, List, Optional
import config

class ProjectKnowledgeGraph:
    """
    AST-powered Project Knowledge Graph for OmniDev:
    Enables natural language code queries (e.g. 'Login ka code kaha hai?')
    by indexing classes, functions, endpoints, and database models.
    """
    def __init__(self, workspace_dir: Optional[Path] = None):
        self.workspace_dir = Path(workspace_dir or config.WORKSPACE_DIR)
        self.nodes: Dict[str, Dict[str, Any]] = {}

    def build_graph(self):
        self.nodes.clear()
        for py_file in self.workspace_dir.rglob("*.py"):
            if any(p in py_file.parts for p in ["node_modules", "venv", "__pycache__", ".git"]):
                continue
            rel_path = py_file.relative_to(self.workspace_dir).as_posix()
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(content, filename=rel_path)
                
                classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
                functions = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                
                self.nodes[rel_path] = {
                    "classes": classes,
                    "functions": functions,
                    "content": content
                }
            except Exception:
                pass

    def search_code_nl(self, query: str) -> List[Dict[str, Any]]:
        if not self.nodes:
            self.build_graph()

        keywords = [k.lower() for k in query.split() if len(k) > 2]
        matches = []

        for rel_path, data in self.nodes.items():
            score = 0
            low_p = rel_path.lower()
            for kw in keywords:
                if kw in low_p:
                    score += 5
                for cls in data["classes"]:
                    if kw in cls.lower():
                        score += 8
                for fn in data["functions"]:
                    if kw in fn.lower():
                        score += 6

            if score > 0:
                matches.append({
                    "file": rel_path,
                    "score": score,
                    "classes": data["classes"],
                    "functions": data["functions"][:5]
                })

        matches.sort(key=lambda m: m["score"], reverse=True)
        return matches
