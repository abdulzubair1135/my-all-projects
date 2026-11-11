import os
import shutil
import time
from pathlib import Path
from typing import Optional, List

class FileManager:
    """
    Handles reading, writing, precision patching, and safe backups of workspace files.
    """
    def __init__(self, workspace_dir: Optional[str | Path] = None):
        self.workspace_dir = Path(workspace_dir) if workspace_dir else Path.cwd()
        self.backup_dir = self.workspace_dir / ".omnidev_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, filepath: str | Path) -> Path:
        p = Path(filepath)
        if not p.is_absolute():
            p = self.workspace_dir / p
        return p

    def read_file(self, filepath: str | Path) -> str:
        target = self._resolve_path(filepath)
        if not target.exists():
            raise FileNotFoundError(f"File not found: {target}")
        return target.read_text(encoding="utf-8", errors="replace")

    def create_backup(self, filepath: str | Path) -> Optional[Path]:
        target = self._resolve_path(filepath)
        if not target.exists():
            return None
        timestamp = int(time.time() * 1000)
        rel_path = target.name
        backup_file = self.backup_dir / f"{rel_path}.{timestamp}.bak"
        shutil.copy2(target, backup_file)
        return backup_file

    def write_file(self, filepath: str | Path, content: str, create_backup: bool = True) -> Path:
        target = self._resolve_path(filepath)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and create_backup:
            self.create_backup(target)
        target.write_text(content, encoding="utf-8")
        return target

    def patch_file(self, filepath: str | Path, target_content: str, replacement_content: str) -> bool:
        """
        Performs precision string replacement on a file with automatic backup.
        """
        target = self._resolve_path(filepath)
        if not target.exists():
            raise FileNotFoundError(f"File not found: {target}")

        content = target.read_text(encoding="utf-8", errors="replace")
        if target_content not in content:
            return False

        self.create_backup(target)
        updated = content.replace(target_content, replacement_content, 1)
        target.write_text(updated, encoding="utf-8")
        return True

    def file_exists(self, filepath: str | Path) -> bool:
        return self._resolve_path(filepath).exists()

    def list_files(self, subpath: str | Path = "", extensions: Optional[List[str]] = None) -> List[Path]:
        base = self._resolve_path(subpath)
        if not base.exists():
            return []
        
        results = []
        ignored = {".git", ".venv", "venv", "__pycache__", "node_modules", ".omnidev_backups", "chrome_profile"}
        
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in ignored]
            for file in files:
                p = Path(root) / file
                if extensions:
                    if p.suffix.lower() in extensions:
                        results.append(p)
                else:
                    results.append(p)
        return results
