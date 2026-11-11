import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

class AgentMemory:
    """
    Maintains session history, active tasks, modified files, and debugging attempts.
    """
    def __init__(self, storage_dir: Path):
        self.storage_dir = storage_dir
        self.history_file = self.storage_dir / ".omnidev_history.json"
        self.history: List[Dict[str, Any]] = []
        self._load()

    def _load(self):
        if self.history_file.exists():
            try:
                self.history = json.loads(self.history_file.read_text(encoding="utf-8"))
            except Exception:
                self.history = []

    def save(self):
        try:
            self.history_file.write_text(json.dumps(self.history, indent=2), encoding="utf-8")
        except Exception:
            pass

    def record_action(self, action_type: str, details: Dict[str, Any]):
        entry = {
            "timestamp": time.time(),
            "action": action_type,
            "details": details
        }
        self.history.append(entry)
        self.save()

    def get_recent_actions(self, limit: int = 10) -> List[Dict[str, Any]]:
        return self.history[-limit:]
