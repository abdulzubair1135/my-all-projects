import ast
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

class CodebaseInspector:
    """
    Inspects an existing codebase to understand its structure, languages,
    entry points, exported symbols (functions, classes), and architecture.
    """
    def __init__(self, root_dir: Optional[str | Path] = None):
        self.root_dir = Path(root_dir) if root_dir else Path.cwd()
        self.ignored_dirs = {
            ".git", ".venv", "venv", "__pycache__", "node_modules",
            ".omnidev_backups", "chrome_profile", ".idea", ".vscode", "dist", "build"
        }

    def detect_project_type(self) -> Dict[str, Any]:
        """
        Detects primary languages and frameworks.
        """
        info = {
            "type": "unknown",
            "frameworks": [],
            "dependencies": [],
            "entry_points": []
        }

        # Check Python
        req_file = self.root_dir / "requirements.txt"
        pyproject = self.root_dir / "pyproject.toml"
        package_json = self.root_dir / "package.json"

        if req_file.exists():
            info["type"] = "python"
            content = req_file.read_text(encoding="utf-8", errors="ignore").lower()
            if "fastapi" in content:
                info["frameworks"].append("FastAPI")
            if "flask" in content:
                info["frameworks"].append("Flask")
            if "django" in content:
                info["frameworks"].append("Django")
            if "uvicorn" in content:
                info["frameworks"].append("Uvicorn")

        if package_json.exists():
            try:
                pkg_data = json.loads(package_json.read_text(encoding="utf-8", errors="ignore"))
                info["type"] = "node"
                deps = {**pkg_data.get("dependencies", {}), **pkg_data.get("devDependencies", {})}
                if "express" in deps:
                    info["frameworks"].append("Express")
                if "react" in deps:
                    info["frameworks"].append("React")
                if "next" in deps:
                    info["frameworks"].append("Next.js")
            except Exception:
                pass

        # Detect entry points
        candidates = ["main.py", "app.py", "server.py", "run.py", "index.js", "server.js", "app.js", "index.html"]
        for c in candidates:
            if (self.root_dir / c).exists():
                info["entry_points"].append(c)

        return info

    def parse_python_symbols(self, file_path: Path) -> Dict[str, Any]:
        """
        Extracts classes, functions, and imports from a Python file using AST.
        """
        symbols = {"classes": [], "functions": [], "imports": []}
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
                    symbols["classes"].append({"name": node.name, "methods": methods})
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Top-level functions only
                    if node in tree.body:
                        symbols["functions"].append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        symbols["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        symbols["imports"].append(node.module)
        except Exception:
            pass
        return symbols

    def scan_directory_tree(self, max_files: int = 60) -> List[str]:
        """
        Returns a list of relative paths for all relevant project files.
        """
        file_list = []
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            for file in files:
                full_p = Path(root) / file
                rel_p = full_p.relative_to(self.root_dir)
                file_list.append(str(rel_p).replace("\\", "/"))
                if len(file_list) >= max_files:
                    return file_list
        return file_list

    def generate_context_summary(self) -> str:
        """
        Generates a concise markdown summary of the existing project for LLM context.
        """
        proj_info = self.detect_project_type()
        tree = self.scan_directory_tree()

        summary_lines = [
            f"# Existing Project Context",
            f"- Project Type: {proj_info['type'].upper()}",
            f"- Frameworks: {', '.join(proj_info['frameworks']) if proj_info['frameworks'] else 'None detected'}",
            f"- Entry Points: {', '.join(proj_info['entry_points']) if proj_info['entry_points'] else 'None detected'}",
            f"\n## Project Files ({len(tree)} files):",
        ]
        for f in tree[:40]:
            summary_lines.append(f"  - `{f}`")

        # Parse key python files
        py_files = [f for f in tree if f.endswith(".py")][:10]
        if py_files:
            summary_lines.append("\n## Python Symbols & Structures:")
            for pf in py_files:
                symbols = self.parse_python_symbols(self.root_dir / pf)
                if symbols["classes"] or symbols["functions"]:
                    summary_lines.append(f"### `{pf}`")
                    for cls in symbols["classes"]:
                        methods_str = f" (methods: {', '.join(cls['methods'])})" if cls['methods'] else ""
                        summary_lines.append(f"  - class `{cls['name']}`{methods_str}")
                    for fn in symbols["functions"]:
                        summary_lines.append(f"  - def `{fn}()`")

        return "\n".join(summary_lines)


class ProjectContextBuilder:
    """
    Builds 100% comprehensive, production-grade project context bundles (.omnidev_bundle.txt)
    and prompt contexts for LLM brains (DeepSeek, Gemini).
    """

    IGNORED_DIRS = {
        ".git", ".godot", ".venv", "venv", "__pycache__", "node_modules",
        ".omnidev_backups", ".omnidev_logs", "chrome_profile", ".idea", ".vscode", "dist", "build"
    }

    IGNORED_EXTENSIONS = {
        ".import", ".uid", ".tmp", ".log", ".pyc"
    }

    @classmethod
    def format_size(cls, size_bytes: int) -> str:
        """Formats byte size into readable string."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    @classmethod
    def generate_ascii_tree(cls, root_dir: Path) -> str:
        """Generates a clean ASCII tree representation of the project hierarchy."""
        root_dir = Path(root_dir)
        lines = [f"📁 {root_dir.name}/"]

        def _walk(dir_path: Path, current_prefix: str):
            try:
                entries = sorted([
                    e for e in dir_path.iterdir()
                    if e.name not in cls.IGNORED_DIRS
                    and not any(e.name.endswith(ext) for ext in cls.IGNORED_EXTENSIONS)
                    and not e.name.startswith(".omnidev_bundle")
                ], key=lambda x: (not x.is_dir(), x.name.lower()))
            except Exception:
                return

            total = len(entries)
            for i, entry in enumerate(entries):
                is_last = (i == total - 1)
                connector = "└── " if is_last else "├── "
                sub_prefix = "    " if is_last else "│   "

                if entry.is_dir():
                    lines.append(f"{current_prefix}{connector}📁 {entry.name}/")
                    _walk(entry, current_prefix + sub_prefix)
                else:
                    try:
                        sz = cls.format_size(entry.stat().st_size)
                    except Exception:
                        sz = ""
                    lines.append(f"{current_prefix}{connector}{entry.name} ({sz})")

        _walk(root_dir, "  ")
        return "\n".join(lines)

    @classmethod
    def scan_asset_inventory(cls, root_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scans and categorizes every asset file in the project with its res:// path,
        type, size, and GDScript loading syntax.
        """
        import re
        root_dir = Path(root_dir)
        inventory: Dict[str, List[Dict[str, Any]]] = {
            "textures": [],
            "audio": [],
            "models_3d": [],
            "fonts": [],
            "shaders": [],
            "scenes": [],
            "data": []
        }

        for p in root_dir.rglob("*"):
            if not p.is_file():
                continue
            if any(part in cls.IGNORED_DIRS for part in p.parts):
                continue
            if any(p.name.endswith(ext) for ext in cls.IGNORED_EXTENSIONS):
                continue
            if p.name.startswith(".omnidev_bundle"):
                continue

            rel = p.relative_to(root_dir).as_posix()
            res_path = f"res://{rel}"
            ext = p.suffix.lower()
            try:
                size_str = cls.format_size(p.stat().st_size)
            except Exception:
                size_str = "0 B"

            # 1. Textures & 2D Sprites
            if ext in [".png", ".jpg", ".jpeg", ".svg", ".webp", ".bmp", ".tga"]:
                inventory["textures"].append({
                    "path": res_path,
                    "rel_path": rel,
                    "name": p.name,
                    "format": ext.upper().lstrip("."),
                    "size": size_str,
                    "gd_load": f'load("{res_path}")'
                })

            # 2. Audio & Sound Effects
            elif ext in [".wav", ".ogg", ".mp3", ".flac"]:
                inventory["audio"].append({
                    "path": res_path,
                    "rel_path": rel,
                    "name": p.name,
                    "format": ext.upper().lstrip("."),
                    "size": size_str,
                    "gd_load": f'preload("{res_path}")'
                })

            # 3. 3D Models & Meshes
            elif ext in [".obj", ".gltf", ".glb", ".fbx", ".dae"]:
                inventory["models_3d"].append({
                    "path": res_path,
                    "rel_path": rel,
                    "name": p.name,
                    "format": ext.upper().lstrip("."),
                    "size": size_str,
                    "gd_load": f'load("{res_path}")'
                })

            # 4. Fonts & Themes
            elif ext in [".ttf", ".otf", ".woff", ".woff2", ".theme", ".tres"]:
                if "font" in rel.lower() or ext in [".ttf", ".otf", ".woff", ".woff2"]:
                    inventory["fonts"].append({
                        "path": res_path,
                        "rel_path": rel,
                        "name": p.name,
                        "format": ext.upper().lstrip("."),
                        "size": size_str
                    })

            # 5. Shaders & Materials
            elif ext in [".gdshader", ".shader", ".material"]:
                inventory["shaders"].append({
                    "path": res_path,
                    "rel_path": rel,
                    "name": p.name,
                    "format": ext.upper().lstrip("."),
                    "size": size_str,
                    "gd_load": f'preload("{res_path}")'
                })

            # 6. Scenes
            elif ext == ".tscn":
                inventory["scenes"].append({
                    "path": res_path,
                    "rel_path": rel,
                    "name": p.name,
                    "size": size_str,
                    "gd_load": f'preload("{res_path}")'
                })

            # 7. Data files
            elif ext in [".json", ".csv", ".xml", ".cfg", ".ini"]:
                inventory["data"].append({
                    "path": res_path,
                    "rel_path": rel,
                    "name": p.name,
                    "format": ext.upper().lstrip("."),
                    "size": size_str
                })

        return inventory

    @classmethod
    def parse_godot_scene_tree(cls, tscn_path: Path) -> Dict[str, Any]:
        """
        Parses a Godot .tscn file and extracts its node hierarchy, types,
        parent-child paths, and attached scripts.
        """
        import re
        tree_info = {
            "root_node": "Unknown",
            "root_type": "Node",
            "nodes": [],
            "script": None
        }
        try:
            content = tscn_path.read_text(encoding="utf-8", errors="ignore")
            ext_resources = {}
            for res_id, rtype, rpath in re.findall(r'\[ext_resource\s+type="([^"]+)"\s+(?:uid="[^"]*"\s+)?path="([^"]+)"\s+id="([^"]+)"\]', content):
                ext_resources[res_id] = {"type": rtype, "path": rpath}

            node_pattern = r'\[node\s+name="([^"]+)"\s+type="([^"]+)"(?:\s+parent="([^"]+)")?(?:[^\]]*script=ExtResource\("([^"]+)"\))?[^\]]*\]'
            for match in re.finditer(node_pattern, content):
                n_name = match.group(1)
                n_type = match.group(2)
                n_parent = match.group(3)
                n_script_id = match.group(4)

                script_path = ext_resources.get(n_script_id, {}).get("path") if n_script_id else None

                node_entry = {
                    "name": n_name,
                    "type": n_type,
                    "parent": n_parent or ".",
                    "script": script_path
                }
                tree_info["nodes"].append(node_entry)

                if n_parent is None or n_parent == ".":
                    tree_info["root_node"] = n_name
                    tree_info["root_type"] = n_type
                    if script_path:
                        tree_info["script"] = script_path
        except Exception:
            pass
        return tree_info

    @classmethod
    def build_project_bundle(cls, project_dir: Path) -> str:
        """
        Generates the 100% complete .omnidev_bundle.txt containing all project assets,
        visual tree, scene architectures, settings, and full source code.
        """
        project_dir = Path(project_dir).resolve()
        is_godot = (project_dir / "project.godot").exists() or any(f.suffix == ".gd" for f in project_dir.rglob("*.*"))
        
        sections = []

        # ==================== SECTION 1: HEADER & METADATA ====================
        sections.append("=" * 80)
        sections.append(f"OMNIDEV AI MASTER PROJECT BUNDLE: {project_dir.name.upper()}")
        sections.append(f"Root Directory: {project_dir.as_posix()}")
        sections.append(f"Project Type: {'Godot 4.x Sovereign Engine' if is_godot else 'Full-Stack / Python / Web Application'}")
        sections.append("=" * 80 + "\n")

        # ==================== SECTION 2: ASCII DIRECTORY TREE ====================
        sections.append("=== 1. COMPLETE PROJECT DIRECTORY & FILE TREE ===")
        sections.append(cls.generate_ascii_tree(project_dir))
        sections.append("\n" + "=" * 80 + "\n")

        # ==================== SECTION 3: ASSET & RESOURCE INVENTORY ====================
        inventory = cls.scan_asset_inventory(project_dir)
        sections.append("=== 2. COMPREHENSIVE ASSET & RESOURCE CATALOG ===")
        
        # Textures
        if inventory["textures"]:
            sections.append("\n🎨 [TEXTURES & 2D SPRITES]:")
            for t in inventory["textures"]:
                sections.append(f"  • {t['path']} ({t['format']}, {t['size']}) -> GDScript Load: {t['gd_load']}")
        else:
            sections.append("\n🎨 [TEXTURES & 2D SPRITES]: (None)")

        # Audio
        if inventory["audio"]:
            sections.append("\n🔊 [AUDIO & SOUND EFFECTS]:")
            for a in inventory["audio"]:
                sections.append(f"  • {a['path']} ({a['format']}, {a['size']}) -> GDScript Load: {a['gd_load']}")
        else:
            sections.append("\n🔊 [AUDIO & SOUND EFFECTS]: (None)")

        # 3D Models
        if inventory["models_3d"]:
            sections.append("\n🧊 [3D MODELS & MESHES]:")
            for m in inventory["models_3d"]:
                sections.append(f"  • {m['path']} ({m['format']}, {m['size']}) -> GDScript Load: {m['gd_load']}")

        # Shaders
        if inventory["shaders"]:
            sections.append("\n🔮 [SHADERS & MATERIALS]:")
            for s in inventory["shaders"]:
                sections.append(f"  • {s['path']} ({s['format']}, {s['size']}) -> GDScript Load: {s['gd_load']}")

        # Scenes
        if inventory["scenes"]:
            sections.append("\n🎬 [SCENE FILES (.tscn)]:")
            for sc in inventory["scenes"]:
                sections.append(f"  • {sc['path']} ({sc['size']}) -> GDScript Load: {sc['gd_load']}")

        # Data files
        if inventory["data"]:
            sections.append("\n📄 [DATA & CONFIG FILES]:")
            for d in inventory["data"]:
                sections.append(f"  • {d['path']} ({d['format']}, {d['size']})")

        sections.append("\n" + "=" * 80 + "\n")

        # ==================== SECTION 4: SCENE NODE HIERARCHIES (FOR GODOT) ====================
        if is_godot:
            sections.append("=== 3. GODOT SCENE NODE TREES & PATH MAPPINGS ===")
            tscn_files = list(project_dir.rglob("*.tscn"))
            for tscn in tscn_files:
                if any(part in cls.IGNORED_DIRS for part in tscn.parts):
                    continue
                rel_tscn = tscn.relative_to(project_dir).as_posix()
                tree = cls.parse_godot_scene_tree(tscn)
                sections.append(f"\n🎬 SCENE: res://{rel_tscn} (Root: {tree['root_node']} [{tree['root_type']}])")
                if tree.get("script"):
                    sections.append(f"   Attached Script: {tree['script']}")
                sections.append("   Node Tree Hierarchy:")
                for n in tree["nodes"]:
                    parent_str = f" (parent: {n['parent']})" if n['parent'] != "." else " [ROOT]"
                    script_str = f" -> Script: {n['script']}" if n['script'] else ""
                    sections.append(f"     • {n['name']} [{n['type']}]{parent_str}{script_str}")
            sections.append("\n" + "=" * 80 + "\n")

        # ==================== SECTION 5: PROJECT SETTINGS & CONFIG ====================
        proj_godot = project_dir / "project.godot"
        if proj_godot.exists():
            sections.append("=== 4. GODOT PROJECT CONFIGURATION (project.godot) ===")
            sections.append(proj_godot.read_text(encoding="utf-8", errors="ignore").strip())
            sections.append("\n" + "=" * 80 + "\n")

        # ==================== SECTION 6: FULL SOURCE CODE OF ALL CODE FILES ====================
        sections.append("=== 5. COMPLETE SOURCE CODE REPOSITORY ===")

        # Collect all code files
        def file_priority(p: Path):
            if p.suffix == ".gd": return 0
            if p.suffix == ".tscn": return 1
            if p.suffix == ".gdshader": return 2
            if p.name == "project.godot": return 3
            if p.suffix == ".py": return 4
            if p.suffix in [".html", ".js", ".css"]: return 5
            return 10

        all_code_files = []
        for ext in ["*.gd", "*.tscn", "*.gdshader", "*.tres", "*.py", "*.html", "*.css", "*.js", "*.json", "*.bat", "*.sh"]:
            all_code_files.extend(list(project_dir.rglob(ext)))

        # Clean duplicates & ignored files
        valid_code_files = []
        for f in set(all_code_files):
            if any(part in cls.IGNORED_DIRS for part in f.parts):
                continue
            if any(bad in f.name for bad in [".git", "gdscript", "text", ".omnidev_bundle"]):
                continue
            if any(part in ["cenes", "cripts"] for part in f.parts):
                continue
            valid_code_files.append(f)

        valid_code_files = sorted(valid_code_files, key=file_priority)

        for f in valid_code_files:
            try:
                rel = f.relative_to(project_dir).as_posix()
                content = f.read_text(encoding="utf-8", errors="ignore")
                sections.append(f"\n--- FILE: {rel} ---")
                sections.append(content)
                sections.append("")
            except Exception:
                pass

        return "\n".join(sections)

    @classmethod
    def write_bundle_file(cls, project_dir: Path) -> Path:
        """Writes .omnidev_bundle.txt in project root and returns its path."""
        project_dir = Path(project_dir).resolve()
        bundle_content = cls.build_project_bundle(project_dir)
        target_path = project_dir / ".omnidev_bundle.txt"
        target_path.write_text(bundle_content, encoding="utf-8")
        return target_path

