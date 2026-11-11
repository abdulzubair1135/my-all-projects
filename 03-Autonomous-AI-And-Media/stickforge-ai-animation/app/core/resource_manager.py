"""
Resource and Cache Manager for StickForge AI.
Monitors memory, disk usage, enforces cache limits, and cleans temp assets.
"""

from __future__ import annotations
import os
import shutil
import psutil
from pathlib import Path
from typing import Dict, Any

from app.core.config import CACHE_DIR, OUTPUT_DIR, get_config
from app.core.logging_manager import get_logger

logger = get_logger("resource_manager")


class ResourceManager:
    """Monitors system resources and manages application cache."""

    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir

    def get_system_stats(self) -> Dict[str, Any]:
        """Query CPU, RAM, and Disk metrics."""
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage(str(self.cache_dir))
        
        # Check GPU availability via torch or pycuda if available
        gpu_info = "Not Detected"
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_info = f"NVIDIA CUDA ({gpu_name})"
        except Exception:
            pass

        return {
            "cpu_count": psutil.cpu_count(logical=True),
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_total_gb": round(vm.total / (1024**3), 2),
            "ram_available_gb": round(vm.available / (1024**3), 2),
            "ram_used_percent": vm.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "gpu": gpu_info,
        }

    def get_cache_size_mb(self) -> float:
        """Calculate total size of cache folder."""
        total_bytes = 0
        if self.cache_dir.exists():
            for root, _, files in os.walk(self.cache_dir):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        total_bytes += os.path.getsize(fp)
                    except OSError:
                        pass
        return round(total_bytes / (1024 * 1024), 2)

    def enforce_cache_limits(self) -> int:
        """Purge oldest files if cache exceeds configured max_cache_mb."""
        config = get_config()
        max_mb = config.resource.max_cache_mb
        current_mb = self.get_cache_size_mb()

        if current_mb <= max_mb:
            return 0

        logger.info(f"Cache size ({current_mb} MB) exceeds limit ({max_mb} MB). Purging oldest items...")
        files = []
        for root, _, filenames in os.walk(self.cache_dir):
            for fn in filenames:
                fp = Path(root) / fn
                try:
                    files.append((fp, fp.stat().st_mtime))
                except OSError:
                    pass

        # Sort by oldest first
        files.sort(key=lambda x: x[1])
        removed_count = 0
        for fp, _ in files:
            try:
                fp.unlink()
                removed_count += 1
                if self.get_cache_size_mb() <= max_mb * 0.8:  # Purge down to 80%
                    break
            except Exception as e:
                logger.warning(f"Failed to remove cached file {fp}: {e}")

        logger.info(f"Purged {removed_count} cache files.")
        return removed_count

    def clear_cache(self) -> None:
        """Explicitly clear the cache directory without touching project files."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir, ignore_errors=True)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Application cache cleared.")


_resource_manager: ResourceManager | None = None


def get_resource_manager() -> ResourceManager:
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager
