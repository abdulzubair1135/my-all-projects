import os
import re
from pathlib import Path
from typing import Union

# Reserved Windows device names
RESERVED_DEVICE_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
}

class SecurityException(Exception):
    pass

class PathGuard:
    """
    Guarantees all file and directory operations remain strictly confined to the project workspace.
    Guards against:
    - Directory traversal (../, ..\\)
    - Absolute paths (/etc/passwd, C:\\Windows\\System32)
    - Symlink / junction breakout
    - Windows reserved device names (CON, NUL, COM1, etc.)
    - UNC paths (\\\\server\\share)
    """

    @classmethod
    def validate_and_resolve(cls, workspace_root: Union[str, Path], relative_path: str) -> Path:
        if not relative_path:
            return Path(workspace_root).resolve()

        # Check for UNC or Windows device paths
        if relative_path.startswith(("\\\\", "//")):
            raise SecurityException(f"UNC paths are forbidden: {relative_path}")

        # Check device names in path parts
        parts = re.split(r"[\\/]", relative_path)
        for part in parts:
            name_no_ext = os.path.splitext(part)[0].upper()
            if name_no_ext in RESERVED_DEVICE_NAMES:
                raise SecurityException(f"Reserved Windows device name forbidden: {part}")

        # Normalize relative path
        norm_rel = os.path.normpath(relative_path).lstrip("/\\")
        if norm_rel.startswith("..") or "/../" in norm_rel or "\\..\\" in norm_rel:
            raise SecurityException(f"Path traversal detected: {relative_path}")

        workspace_path = Path(workspace_root).resolve()
        target_path = (workspace_path / norm_rel).resolve()

        # Check canonical realpath resolution (resolving any symlinks)
        try:
            # If target exists, resolve its realpath
            if target_path.exists():
                canonical_target = target_path.resolve(strict=True)
            else:
                # Find deepest existing parent to resolve realpath
                parent = target_path.parent
                while not parent.exists() and parent != parent.parent:
                    parent = parent.parent
                canonical_target = parent.resolve(strict=True)

            canonical_workspace = workspace_path.resolve(strict=True)

            # Check if canonical target is inside canonical workspace
            if not str(canonical_target).startswith(str(canonical_workspace)):
                raise SecurityException(f"Path breakout detected: {relative_path} resolves outside workspace")
        except FileNotFoundError:
            pass

        return target_path
