# -*- coding: utf-8 -*-
"""
zip_chunker.py
Multi-Part ZIP Archiving & Workspace Packaging Engine for Autonomous Web-Agent IDE.

Features:
1. Complete workspace packaging including code, assets, images, configs.
2. Intelligent multi-part chunking if total archive size exceeds provider upload limits (e.g. 40MB).
3. Manifest generation with SHA-256 integrity verification.
4. Fast directory topology extraction for AI prompt context.
"""

import os
import io
import json
import zipfile
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "dist",
    "build", ".uploads", ".checkpoints", ".snapshots", ".cache", ".godot"
}


def generate_workspace_topology(workspace_root: str, max_depth: int = 5) -> str:
    """Generate a clean directory topology tree of the workspace."""
    root = Path(workspace_root).resolve()
    lines = [f"{root.name}/"]

    def _walk(curr: Path, prefix: str = "", depth: int = 0):
        if depth > max_depth:
            return
        try:
            items = sorted(list(curr.iterdir()), key=lambda x: (not x.is_dir(), x.name.lower()))
        except Exception:
            return

        visible = [item for item in items if item.name not in IGNORE_DIRS and not item.name.startswith(".agent")]
        for idx, item in enumerate(visible):
            is_last = (idx == len(visible) - 1)
            connector = "└── " if is_last else "├── "
            child_prefix = "    " if is_last else "│   "

            if item.is_dir():
                lines.append(f"{prefix}{connector}{item.name}/")
                _walk(item, prefix + child_prefix, depth + 1)
            else:
                size_kb = item.stat().st_size / 1024
                lines.append(f"{prefix}{connector}{item.name} ({size_kb:.1f} KB)")

    _walk(root)
    return "\n".join(lines)


def create_chunked_zip(
    workspace_root: str,
    output_dir: Optional[str] = None,
    max_chunk_mb: float = 38.0,
    prefix_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a complete ZIP of the workspace.
    If the archive exceeds max_chunk_mb, autonomously split into multi-part chunks.
    
    Returns:
        {
            "is_chunked": bool,
            "archive_paths": List[str],
            "total_size_mb": float,
            "parts_count": int,
            "manifest_path": Optional[str],
            "topology": str
        }
    """
    ws = Path(workspace_root).resolve()
    dest_dir = Path(output_dir).resolve() if output_dir else ws.parent
    dest_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = prefix_name or f"{ws.name}_{timestamp}"
    single_zip_path = dest_dir / f"{base_name}.zip"

    # Step 1: Gather all files
    files_to_zip = []
    for p in ws.rglob("*"):
        if p.is_file() and not any(ig in p.parts for ig in IGNORE_DIRS):
            files_to_zip.append(p)

    # Step 2: Build standard archive in memory/temp file
    with zipfile.ZipFile(single_zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for p in files_to_zip:
            rel = p.relative_to(ws)
            zf.write(p, str(rel))

    total_size = single_zip_path.stat().st_size
    total_size_mb = total_size / (1024 * 1024)
    max_chunk_bytes = int(max_chunk_mb * 1024 * 1024)

    topology = generate_workspace_topology(str(ws))

    # Case A: File fits in one chunk (< max_chunk_mb)
    if total_size <= max_chunk_bytes:
        return {
            "is_chunked": False,
            "archive_paths": [str(single_zip_path)],
            "total_size_mb": round(total_size_mb, 2),
            "parts_count": 1,
            "manifest_path": None,
            "topology": topology
        }

    # Case B: Exceeds threshold (e.g. > 40MB) -> Split into multi-part chunks
    chunk_paths = []
    manifest_parts = []
    chunk_idx = 1

    with open(single_zip_path, "rb") as src:
        while True:
            chunk_data = src.read(max_chunk_bytes)
            if not chunk_data:
                break
            part_filename = f"{base_name}.part{chunk_idx:03d}.zip"
            part_path = dest_dir / part_filename
            with open(part_path, "wb") as part_file:
                part_file.write(chunk_data)

            sha256 = hashlib.sha256(chunk_data).hexdigest()
            chunk_paths.append(str(part_path))
            manifest_parts.append({
                "part": chunk_idx,
                "filename": part_filename,
                "size_bytes": len(chunk_data),
                "size_mb": round(len(chunk_data) / (1024 * 1024), 2),
                "sha256": sha256
            })
            chunk_idx += 1

    # Remove single oversized zip to save disk space
    try:
        single_zip_path.unlink()
    except Exception:
        pass

    # Generate Manifest
    manifest_data = {
        "project_name": ws.name,
        "timestamp": timestamp,
        "total_size_mb": round(total_size_mb, 2),
        "total_parts": len(chunk_paths),
        "parts": manifest_parts,
        "reassembly_instructions": {
            "windows_cmd": f"copy /b {'+'.join(p['filename'] for p in manifest_parts)} {base_name}_restored.zip",
            "linux_sh": f"cat {' '.join(p['filename'] for p in manifest_parts)} > {base_name}_restored.zip"
        }
    }

    manifest_path = dest_dir / f"{base_name}_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    return {
        "is_chunked": True,
        "archive_paths": chunk_paths,
        "total_size_mb": round(total_size_mb, 2),
        "parts_count": len(chunk_paths),
        "manifest_path": str(manifest_path),
        "topology": topology
    }
