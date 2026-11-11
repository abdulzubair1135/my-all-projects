import os
import zipfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from config import console, WORKSPACE_DIR

class ProjectPackager:
    """
    Intelligent Project Packager for OmniDev:
    1. Bundles complete codebase (sources, assets, images, audio, configs) into clean zip archives.
    2. Excludes build junk (.git, __pycache__, node_modules, .pytest_cache).
    3. Handles DeepSeek 40MB upload limit: If project exceeds 35MB, splits into multi-part zips
       (project_part1.zip, project_part2.zip) or selective core + asset archives.
    4. Provides ready-to-upload zip paths for DeepSeek Web attachment.
    """
    IGNORE_DIRS = {
        ".git", "__pycache__", "node_modules", ".pytest_cache", ".venv", "venv",
        "build", "obj", ".idea", ".vscode", ".gemini"
    }
    IGNORE_EXTS = {".pyc", ".pyo", ".pyd", ".tmp", ".log"}

    def __init__(self, workspace_dir: Optional[Path] = None):
        self.workspace_dir = Path(workspace_dir or WORKSPACE_DIR)
        self.zips_dir = self.workspace_dir / ".omnidev_packages"
        self.zips_dir.mkdir(parents=True, exist_ok=True)

    def package_directory(self, target_dir: Path, archive_name: Optional[str] = None, max_part_size_mb: int = 35) -> List[Path]:
        target_dir = Path(target_dir).resolve()
        if not target_dir.exists():
            raise FileNotFoundError(f"Target directory does not exist: {target_dir}")

        clean_name = archive_name or target_dir.name or "project_package"
        max_bytes = max_part_size_mb * 1024 * 1024

        console.print(f"[bold cyan]📦 Packaging project:[/bold cyan] '{target_dir.name}' for DeepSeek upload...")

        # Collect all eligible files
        files_to_pack = []
        total_uncompressed_bytes = 0

        for root, dirs, files in os.walk(target_dir):
            # Exclude ignored directories in-place
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS and not d.startswith(".")]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in self.IGNORE_EXTS or file.startswith("."):
                    continue
                try:
                    fsize = file_path.stat().st_size
                    total_uncompressed_bytes += fsize
                    rel_path = file_path.relative_to(target_dir)
                    files_to_pack.append((file_path, rel_path, fsize))
                except Exception:
                    continue

        if not files_to_pack:
            console.print("[yellow]⚠️ No files found to package.[/yellow]")
            return []

        # Sort files: code & config files first, then large media/assets
        files_to_pack.sort(key=lambda x: (x[0].suffix.lower() in ['.png', '.jpg', '.mp3', '.wav', '.zip'], x[2]))

        # Create zip file(s)
        generated_zips: List[Path] = []
        current_part = 1
        current_zip_path = self.zips_dir / f"{clean_name}.zip"
        
        # Test if single zip fits within limit
        temp_zip = self.zips_dir / f"{clean_name}_temp.zip"
        with zipfile.ZipFile(temp_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for file_path, rel_path, _ in files_to_pack:
                zf.write(file_path, arcname=str(rel_path))

        single_zip_size = temp_zip.stat().st_size

        if single_zip_size <= max_bytes:
            if current_zip_path.exists():
                current_zip_path.unlink()
            shutil.move(str(temp_zip), str(current_zip_path))
            generated_zips.append(current_zip_path)
            size_mb = single_zip_size / (1024 * 1024)
            console.print(f"[bold green]✓ Created single archive:[/bold green] {current_zip_path.name} ({size_mb:.2f} MB)")
        else:
            # Need chunking / splitting
            temp_zip.unlink()
            console.print(f"[yellow]⚡ Project size ({single_zip_size / (1024*1024):.1f} MB) exceeds {max_part_size_mb}MB limit! Splitting into multi-part zips...[/yellow]")
            
            current_bytes = 0
            current_part_files = []
            
            for file_path, rel_path, fsize in files_to_pack:
                if current_bytes + fsize > max_bytes and current_part_files:
                    # Write out current part
                    part_zip_path = self.zips_dir / f"{clean_name}_part{current_part}.zip"
                    with zipfile.ZipFile(part_zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
                        for f_p, r_p in current_part_files:
                            zf.write(f_p, arcname=str(r_p))
                    generated_zips.append(part_zip_path)
                    part_mb = part_zip_path.stat().st_size / (1024 * 1024)
                    console.print(f"[green]✓ Part {current_part} created:[/green] {part_zip_path.name} ({part_mb:.2f} MB)")
                    
                    current_part += 1
                    current_bytes = 0
                    current_part_files = []

                current_part_files.append((file_path, rel_path))
                current_bytes += fsize

            if current_part_files:
                part_zip_path = self.zips_dir / f"{clean_name}_part{current_part}.zip"
                with zipfile.ZipFile(part_zip_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
                    for f_p, r_p in current_part_files:
                        zf.write(f_p, arcname=str(r_p))
                generated_zips.append(part_zip_path)
                part_mb = part_zip_path.stat().st_size / (1024 * 1024)
                console.print(f"[green]✓ Part {current_part} created:[/green] {part_zip_path.name} ({part_mb:.2f} MB)")

        return generated_zips
