"""
AURA System Configuration Module.
Hardware Target: RTX 2050 4GB VRAM, 16GB RAM, Windows
Local-first, Model-independent configuration.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Optional

BASE_DIR = Path(__file__).parent.resolve()

@dataclass
class HardwareConfig:
    target_gpu: str = "NVIDIA RTX 2050"
    vram_mb: int = 4096
    ram_gb: int = 16
    max_gpu_usage_percent: float = 85.0

@dataclass
class ModelConfig:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    fast_model: str = os.getenv("AURA_FAST_MODEL", "qwen3:1.7b")
    normal_model: str = os.getenv("AURA_NORMAL_MODEL", "qwen3:4b")
    heavy_model: str = os.getenv("AURA_HEAVY_MODEL", "qwen3.5:9b")
    default_backend: str = os.getenv("AURA_MODEL_BACKEND", "ollama")
    use_mock: bool = os.getenv("AURA_USE_MOCK_LLM", "false").lower() in ("true", "1", "yes")
    timeout_seconds: int = 60

@dataclass
class StorageConfig:
    db_path: Path = field(default_factory=lambda: BASE_DIR / "database" / "aura.db")
    logs_dir: Path = field(default_factory=lambda: BASE_DIR / "logs")
    workspace_dir: Path = field(default_factory=lambda: BASE_DIR / "workspace")
    backups_dir: Path = field(default_factory=lambda: BASE_DIR / "backups")

@dataclass
class SystemConfig:
    autonomy_level: int = int(os.getenv("AURA_AUTONOMY_LEVEL", "1"))  # 0: Think only, 1: Think+Local Files, 2: Browser/Sandbox, 3: Computer Control, 4: Controlled Self-Improvement
    max_task_retries: int = 3
    working_memory_max_items: int = 20
    log_level: str = os.getenv("AURA_LOG_LEVEL", "INFO")
    hardware: HardwareConfig = field(default_factory=HardwareConfig)
    models: ModelConfig = field(default_factory=ModelConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)

    def __post_init__(self):
        self.storage.logs_dir.mkdir(parents=True, exist_ok=True)
        self.storage.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.storage.backups_dir.mkdir(parents=True, exist_ok=True)
        self.storage.db_path.parent.mkdir(parents=True, exist_ok=True)

# Singleton global instance
config = SystemConfig()
