"""
Thread-safe publish-subscribe Event Bus for StickForge AI.
Coordinates async events across UI and background workers.
"""

from __future__ import annotations
from typing import Any, Callable, Dict, List
import threading
from app.core.logging_manager import get_logger

logger = get_logger("event_bus")


class EventBus:
    """Publish-subscribe event bus supporting multiple subscribers per topic."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[..., Any]]] = {}
        self._lock = threading.RLock()

    def subscribe(self, event_type: str, handler: Callable[..., Any]) -> None:
        """Register a handler for a given event type."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            if handler not in self._subscribers[event_type]:
                self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: Callable[..., Any]) -> None:
        """Unregister a handler for an event type."""
        with self._lock:
            if event_type in self._subscribers and handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)

    def publish(self, event_type: str, **kwargs: Any) -> None:
        """Publish an event to all registered subscribers."""
        with self._lock:
            handlers = list(self._subscribers.get(event_type, []))

        for handler in handlers:
            try:
                handler(**kwargs)
            except Exception as e:
                logger.error(f"Error handling event '{event_type}' in {handler}: {e}", exc_info=True)


# Global singleton
_event_bus = EventBus()


def get_event_bus() -> EventBus:
    return _event_bus
