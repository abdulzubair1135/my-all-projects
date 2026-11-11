"""
project_graph.py
Project Knowledge Graph for Autonomous Web-Agent IDE.

Extracts relationships between files, imports, components, and functions:
  Component -> File -> Function/Class -> API -> Service -> Test
Provides impact analysis, dependency traversal, and semantic file retrieval.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, List, Set, Optional


class ProjectGraph:
    """
    In-memory knowledge graph of a project's codebase.
    Tracks imports, exports, declared symbols, and provides impact analysis.
    """

    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.files: Dict[str, Dict[str, Any]] = {}
        # adjacency: file -> set of files it imports
        self.dependencies: Dict[str, Set[str]] = {}
        # reverse adjacency: file -> set of files that import it
        self.dependents: Dict[str, Set[str]] = {}
        # symbol table: symbol_name -> list of files defining it
        self.symbol_index: Dict[str, List[str]] = {}

    def build_graph(self):
        """Scans the workspace and builds the dependency and symbol graph."""
        self.files.clear()
        self.dependencies.clear()
        self.dependents.clear()
        self.symbol_index.clear()

        if not self.workspace_root.exists():
            return

        for p in self.workspace_root.rglob("*"):
            if p.is_file():
                rel = str(p.relative_to(self.workspace_root)).replace("\\", "/")
                # Skip heavy/ignored folders
                if any(ig in rel.split("/") for ig in ["node_modules", ".git", "dist", "build", ".venv", "__pycache__", ".uploads"]):
                    continue
                if p.suffix.lower() in [".js", ".jsx", ".ts", ".tsx", ".py", ".html", ".css", ".json"]:
                    self._index_file(p, rel)

        # Build reverse dependents
        for source, targets in self.dependencies.items():
            for target in targets:
                if target not in self.dependents:
                    self.dependents[target] = set()
                self.dependents[target].add(source)

    def _index_file(self, path: Path, rel_path: str):
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return

        imports = self._extract_imports(content, rel_path, path.suffix.lower())
        symbols = self._extract_symbols(content, path.suffix.lower())

        self.files[rel_path] = {
            "path": rel_path,
            "ext": path.suffix.lower(),
            "size": len(content),
            "imports": imports,
            "symbols": symbols,
        }

        self.dependencies[rel_path] = set(imports)

        for sym in symbols:
            if sym not in self.symbol_index:
                self.symbol_index[sym] = []
            self.symbol_index[sym].append(rel_path)

    def _extract_imports(self, content: str, current_file: str, ext: str) -> List[str]:
        """Extract imported file paths from source code."""
        resolved = []
        current_dir = Path(current_file).parent

        if ext in [".js", ".jsx", ".ts", ".tsx"]:
            # Match: import ... from './path' or require('./path')
            patterns = [
                r'(?:import|from)\s+[\'"](\.[^\'"]+)[\'"]',
                r'require\([\'"](\.[^\'"]+)[\'"]\)',
            ]
            for pat in patterns:
                for match in re.findall(pat, content):
                    res = self._resolve_relative_path(current_dir, match, [".js", ".jsx", ".ts", ".tsx", ".json", "/index.js", "/index.jsx"])
                    if res:
                        resolved.append(res)

        elif ext == ".py":
            # Match: from .module import or from ..module import
            for match in re.findall(r'from\s+(\.+[a-zA-Z0-9_]*)\s+import', content):
                # Local relative python import
                dots = len(match) - len(match.lstrip('.'))
                module_name = match.lstrip('.')
                target_dir = current_dir
                for _ in range(dots - 1):
                    target_dir = target_dir.parent
                cand = (target_dir / f"{module_name}.py").as_posix()
                if (self.workspace_root / cand).exists():
                    resolved.append(cand)

        return resolved

    def _resolve_relative_path(self, current_dir: Path, raw_import: str, candidate_exts: List[str]) -> Optional[str]:
        """Resolve a relative import like './Slide' to 'src/components/Slide.jsx'."""
        base = (current_dir / raw_import).as_posix()
        # Direct match with existing extension
        if (self.workspace_root / base).is_file():
            return base

        # Try candidate extensions
        for ext in candidate_exts:
            cand = base + ext
            if (self.workspace_root / cand).is_file():
                return cand

        return None

    def _extract_symbols(self, content: str, ext: str) -> List[str]:
        """Extract declared classes, functions, and React components."""
        symbols = []
        if ext in [".js", ".jsx", ".ts", ".tsx"]:
            # function names, component names, class names
            patterns = [
                r'export\s+(?:default\s+)?(?:function|class|const)\s+([A-Z][a-zA-Z0-9_]*)',
                r'function\s+([A-Z][a-zA-Z0-9_]*)',
                r'const\s+([A-Z][a-zA-Z0-9_]*)\s*=',
            ]
            for pat in patterns:
                for match in re.findall(pat, content):
                    if match not in symbols:
                        symbols.append(match)

        elif ext == ".py":
            patterns = [
                r'class\s+([A-Za-z0-9_]+)',
                r'def\s+([A-Za-z0-9_]+)',
            ]
            for pat in patterns:
                for match in re.findall(pat, content):
                    if match not in symbols:
                        symbols.append(match)

        return symbols

    def get_impacted_files(self, changed_file: str) -> List[str]:
        """Returns all files that depend on the changed file (directly or indirectly)."""
        visited = set()
        queue = [changed_file]
        while queue:
            curr = queue.pop(0)
            if curr not in visited:
                visited.add(curr)
                dependents = self.dependents.get(curr, set())
                for dep in dependents:
                    if dep not in visited:
                        queue.append(dep)
        visited.discard(changed_file)
        return list(visited)

    def find_relevant_files(self, query: str, limit: int = 8) -> List[str]:
        """
        Finds files most relevant to a user task or query
        using symbol matching, path keywords, and connectivity.
        """
        if not self.files:
            self.build_graph()

        q_lower = query.lower()
        words = re.findall(r'[a-zA-Z0-9_]+', q_lower)
        scores: Dict[str, float] = {}

        for rel, data in self.files.items():
            score = 0.0
            path_lower = rel.lower()

            # Path matches
            for w in words:
                if len(w) > 2 and w in path_lower:
                    score += 5.0

            # Symbol matches
            for sym in data.get("symbols", []):
                sym_lower = sym.lower()
                for w in words:
                    if len(w) > 2 and w in sym_lower:
                        score += 8.0

            # Core files get a small baseline
            if any(core in rel for core in ["App.jsx", "main.jsx", "index.html", "server.js", "main.py"]):
                score += 2.0

            if score > 0:
                scores[rel] = score

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [r[0] for r in ranked[:limit]]
