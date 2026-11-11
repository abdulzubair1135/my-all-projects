import os
import shutil
import time

class FileTool:
    """
    Safe file operations with automatic backups for code files.
    """
    def __init__(self, workspace_root=None, backup_dir="storage/backups"):
        self.workspace_root = os.path.abspath(workspace_root or os.getcwd())
        self.backup_dir = os.path.abspath(backup_dir)
        os.makedirs(self.backup_dir, exist_ok=True)

    def _resolve(self, filepath: str) -> str:
        if os.path.isabs(filepath):
            return filepath
        return os.path.abspath(os.path.join(self.workspace_root, filepath))

    def read_file(self, filepath: str) -> dict:
        full_path = self._resolve(filepath)
        if not os.path.exists(full_path):
            return {"success": False, "content": "", "error": f"File not found: {filepath}"}
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            return {"success": True, "content": content, "error": None}
        except Exception as e:
            return {"success": False, "content": "", "error": str(e)}

    def write_file(self, filepath: str, content: str, make_backup: bool = True) -> dict:
        full_path = self._resolve(filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Automatic checkpoint/backup before overwriting
        if make_backup and os.path.exists(full_path):
            filename = os.path.basename(full_path)
            ts = int(time.time())
            backup_path = os.path.join(self.backup_dir, f"{filename}_{ts}.bak")
            try:
                shutil.copy2(full_path, backup_path)
            except Exception:
                pass

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {"success": True, "path": full_path, "error": None}
        except Exception as e:
            return {"success": False, "path": full_path, "error": str(e)}

    def list_dir(self, dirpath: str = ".") -> dict:
        full_path = self._resolve(dirpath)
        if not os.path.exists(full_path):
            return {"success": False, "items": [], "error": "Directory does not exist"}
        try:
            items = []
            for entry in os.scandir(full_path):
                items.append({
                    "name": entry.name,
                    "is_dir": entry.is_dir(),
                    "size_bytes": entry.stat().st_size if not entry.is_dir() else 0
                })
            return {"success": True, "items": items, "error": None}
        except Exception as e:
            return {"success": False, "items": [], "error": str(e)}
