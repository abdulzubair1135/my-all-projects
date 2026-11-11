import hashlib
import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

try:
    from security.path_guard import PathGuard, SecurityException
except ImportError:
    from ..security.path_guard import PathGuard, SecurityException

IGNORED_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__", ".pytest_cache", ".godot"}

BINARY_EXTENSIONS = {
    ".sqlite", ".sqlite3", ".db", ".bin", ".dat",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".svgz", ".bmp", ".tiff",
    ".zip", ".tar", ".gz", ".7z", ".rar", ".exe", ".dll", ".so", ".dylib",
    ".pyc", ".pyo", ".pyd", ".class", ".o", ".obj",
    ".mp3", ".wav", ".ogg", ".mp4", ".webm", ".avi",
    ".ttf", ".otf", ".woff", ".woff2", ".eot",
    ".pdf", ".docx", ".xlsx", ".pptx", ".lock"
}

BINARY_FILENAMES = {
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock"
}

class FileSystem:
    @staticmethod
    def compute_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @classmethod
    def read_file(cls, workspace_root: str, relative_path: str) -> Tuple[str, str]:
        """
        Reads file content and returns (content, sha256_hash).
        Guards against binary, sqlite, and null-byte files to prevent corrupting LLM prompts.
        """
        safe_path = PathGuard.validate_and_resolve(workspace_root, relative_path)
        if not safe_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")
        if safe_path.is_dir():
            raise IsADirectoryError(f"Path is a directory: {relative_path}")

        # Guard against binary extensions or filenames
        ext = safe_path.suffix.lower()
        name = safe_path.name.lower()
        if (
            ext in BINARY_EXTENSIONS or
            name in BINARY_FILENAMES or
            name.startswith(".agent_state") or
            name.startswith(".tmp_")
        ):
            return f"// [Binary/data file '{relative_path}' omitted from text context]", cls.compute_hash("")

        # Sniff first 1024 bytes for null bytes to detect ANY binary file
        try:
            with open(safe_path, "rb") as bf:
                chunk = bf.read(1024)
                if b"\x00" in chunk:
                    return f"// [Binary file '{relative_path}' omitted from text context]", cls.compute_hash("")
        except Exception:
            pass

        content = safe_path.read_text(encoding="utf-8", errors="replace")
        # Strip any rogue null bytes
        content = content.replace("\x00", "")
        return content, cls.compute_hash(content)

    @classmethod
    def write_file(cls, workspace_root: str, relative_path: str, content: str) -> str:
        """
        Atomically writes file content. Returns new SHA256 hash.
        """
        safe_path = PathGuard.validate_and_resolve(workspace_root, relative_path)
        safe_path.parent.mkdir(parents=True, exist_ok=True)

        temp_file = safe_path.parent / f".tmp_{safe_path.name}_{os.getpid()}"
        try:
            temp_file.write_text(content, encoding="utf-8")
            temp_file.replace(safe_path)
        except Exception:
            if temp_file.exists():
                temp_file.unlink(missing_ok=True)
            raise

        return cls.compute_hash(content)

    @classmethod
    def edit_file(
        cls,
        workspace_root: str,
        relative_path: str,
        content: Optional[str] = None,
        expected_hash: Optional[str] = None,
        patch: Optional[str] = None
    ) -> str:
        """
        Safely edits a file with conflict check against expected_hash.
        """
        safe_path = PathGuard.validate_and_resolve(workspace_root, relative_path)
        if not safe_path.exists():
            if content is not None:
                return cls.write_file(workspace_root, relative_path, content)
            raise FileNotFoundError(f"Cannot edit non-existent file: {relative_path}")

        current_content = safe_path.read_text(encoding="utf-8", errors="replace")
        current_hash = cls.compute_hash(current_content)

        if expected_hash and current_hash != expected_hash:
            raise ValueError(f"Conflict detected for {relative_path}: current hash {current_hash[:8]} does not match expected {expected_hash[:8]}")

        if content is not None:
            return cls.write_file(workspace_root, relative_path, content)

        if patch is not None:
            return cls.write_file(workspace_root, relative_path, patch)

        raise ValueError("Either content or patch must be provided for edit_file")

    @classmethod
    def delete_file(cls, workspace_root: str, relative_path: str) -> bool:
        safe_path = PathGuard.validate_and_resolve(workspace_root, relative_path)
        if not safe_path.exists():
            return False

        if safe_path.is_dir():
            shutil.rmtree(safe_path, ignore_errors=True)
        else:
            safe_path.unlink(missing_ok=True)
        return True

    @classmethod
    def mkdir(cls, workspace_root: str, relative_path: str) -> bool:
        safe_path = PathGuard.validate_and_resolve(workspace_root, relative_path)
        safe_path.mkdir(parents=True, exist_ok=True)
        return True

    @classmethod
    def list_files(cls, workspace_root: str, relative_path: str = "") -> List[Dict[str, Any]]:
        safe_path = PathGuard.validate_and_resolve(workspace_root, relative_path)
        if not safe_path.exists():
            return []

        results = []
        for root, dirs, files in os.walk(safe_path):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

            for f in files:
                full = Path(root) / f
                rel = full.relative_to(Path(workspace_root).resolve()).as_posix()
                ext = full.suffix.lower()
                name = full.name.lower()
                # Skip binary, lock, and internal state files
                if (
                    ext in BINARY_EXTENSIONS or
                    name in BINARY_FILENAMES or
                    name.startswith(".agent_state") or
                    name.startswith(".tmp_")
                ):
                    continue

                try:
                    stat = full.stat()
                    results.append({
                        "path": rel,
                        "size": stat.st_size,
                        "is_dir": False
                    })
                except Exception:
                    pass

        return results

    @classmethod
    def search_files(cls, workspace_root: str, query: str) -> List[str]:
        workspace = Path(workspace_root).resolve()
        matches = []
        for root, dirs, files in os.walk(workspace):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for f in files:
                full = Path(root) / f
                rel = full.relative_to(workspace).as_posix()
                if query.lower() in f.lower():
                    matches.append(rel)
                    continue
                try:
                    content = full.read_text(encoding="utf-8", errors="ignore")
                    if query in content:
                        matches.append(rel)
                except Exception:
                    pass
        return matches[:50]
