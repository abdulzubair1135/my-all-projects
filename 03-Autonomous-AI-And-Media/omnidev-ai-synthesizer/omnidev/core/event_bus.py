import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field
from pathlib import Path
from config import OUTPUTS_DIR

@dataclass
class Event:
    event_type: str
    data: Dict[str, Any]
    mission_id: Optional[str] = None
    task_id: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "mission_id": self.mission_id,
            "task_id": self.task_id,
            "data": self.data
        }

class EventBus:
    """
    Event Bus for OmniDev real-time observability and event streaming.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._subscribers = {}
            cls._instance._wildcard_subscribers = []
            cls._instance._event_history = []
            cls._instance._log_file = OUTPUTS_DIR / "events.jsonl"
        return cls._instance

    def subscribe(self, event_type: str, callback: Callable[[Event], Any]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def subscribe_all(self, callback: Callable[[Event], Any]):
        self._wildcard_subscribers.append(callback)

    def publish(self, event_type: str, data: Dict[str, Any], mission_id: Optional[str] = None, task_id: Optional[str] = None) -> Event:
        event = Event(event_type=event_type, data=data, mission_id=mission_id, task_id=task_id)
        self._event_history.append(event)
        
        try:
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event.to_dict()) + "\n")
        except Exception:
            pass

        if event_type in self._subscribers:
            for cb in self._subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(cb):
                        asyncio.create_task(cb(event))
                    else:
                        cb(event)
                except Exception as e:
                    print(f"[EventBus Error] Callback failed for {event_type}: {e}")

        for cb in self._wildcard_subscribers:
            try:
                if asyncio.iscoroutinefunction(cb):
                    asyncio.create_task(cb(event))
                else:
                    cb(event)
            except Exception as e:
                print(f"[EventBus Error] Wildcard callback failed: {e}")

        return event

event_bus = EventBus()
