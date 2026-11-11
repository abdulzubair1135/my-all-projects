import os
import subprocess
import threading
import time
import psutil

class ResourceManager:
    """
    Hardware and Memory Guard tailored for:
    - AMD Ryzen 7 7435HS
    - 16GB RAM
    - NVIDIA GeForce RTX 2050 (4GB VRAM)
    """
    _gpu_lock = threading.Lock()

    @staticmethod
    def get_system_stats():
        """Returns current RAM, CPU, and GPU stats."""
        vm = psutil.virtual_memory()
        ram_total_gb = round(vm.total / (1024 ** 3), 2)
        ram_avail_gb = round(vm.available / (1024 ** 3), 2)
        ram_percent = vm.percent

        gpu_info = ResourceManager.get_gpu_stats()

        return {
            "ram_total_gb": ram_total_gb,
            "ram_avail_gb": ram_avail_gb,
            "ram_percent": ram_percent,
            "gpu": gpu_info
        }

    @staticmethod
    def get_gpu_stats():
        """Queries nvidia-smi for VRAM usage."""
        try:
            cmd = [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,memory.free,temperature.gpu,utilization.gpu",
                "--format=csv,noheader,nounits"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                parts = [p.strip() for p in result.stdout.strip().split(",")]
                return {
                    "available": True,
                    "name": parts[0],
                    "total_mb": int(parts[1]),
                    "used_mb": int(parts[2]),
                    "free_mb": int(parts[3]),
                    "temp_c": int(parts[4]),
                    "util_percent": int(parts[5])
                }
        except Exception:
            pass

        return {
            "available": False,
            "name": "N/A",
            "total_mb": 0,
            "used_mb": 0,
            "free_mb": 0,
            "temp_c": 0,
            "util_percent": 0
        }

    @staticmethod
    def can_run_heavy_task(required_vram_mb=1500, required_ram_mb=1500):
        """Checks if hardware has enough headroom for a task without crashing."""
        stats = ResourceManager.get_system_stats()
        ram_avail_mb = stats["ram_avail_gb"] * 1024
        gpu = stats["gpu"]

        if ram_avail_mb < required_ram_mb:
            return False, f"Low System RAM ({round(ram_avail_mb)}MB free, need {required_ram_mb}MB)"

        if gpu["available"] and gpu["free_mb"] < required_vram_mb:
            return False, f"Low GPU VRAM ({gpu['free_mb']}MB free, need {required_vram_mb}MB)"

        return True, "Resource check passed"

    @classmethod
    def acquire_gpu_lock(cls, timeout=120):
        """Acquires lock so only one heavy GPU process runs at a time."""
        return cls._gpu_lock.acquire(timeout=timeout)

    @classmethod
    def release_gpu_lock(cls):
        """Releases the GPU workload lock."""
        if cls._gpu_lock.locked():
            try:
                cls._gpu_lock.release()
            except RuntimeError:
                pass

    @staticmethod
    def unload_ollama_model(model_name="qwen3.5:4b"):
        """Frees Ollama VRAM/RAM immediately."""
        try:
            subprocess.run(["ollama", "stop", model_name], capture_output=True, timeout=10)
        except Exception:
            pass

    @staticmethod
    def cleanup():
        """Performs general memory hygiene."""
        ResourceManager.release_gpu_lock()
