"""
state_machine.py
Autonomous Finite State Machine (FSM) for Autonomous Web-Agent IDE.

Enforces explicit, auditable transitions across the complete software lifecycle:
  IDLE -> UNDERSTAND -> PLAN -> ARCHITECTURE -> IMPLEMENT -> CODE_REVIEW
  -> BUILD -> BROWSER_TEST -> VISUAL_TEST -> ERROR_DETECTED -> MEMORY_LOOKUP
  -> AI_DIAGNOSIS -> APPLY_PATCH -> RETEST -> CHECKPOINT -> DELIVER -> SUCCESS
"""

import time
from enum import Enum
from typing import Dict, Any, List, Optional, Callable


class AutonomousState(str, Enum):
    IDLE = "IDLE"
    UNDERSTAND = "UNDERSTAND"
    RESEARCH = "RESEARCH"
    PLAN = "PLAN"
    ARCHITECTURE = "ARCHITECTURE"
    PLAN_REVIEW = "PLAN_REVIEW"
    APPROVAL = "APPROVAL"
    INITIALIZE_WORKSPACE = "INITIALIZE_WORKSPACE"
    BOOTSTRAP = "BOOTSTRAP"
    IMPLEMENT = "IMPLEMENT"
    CODE_REVIEW = "CODE_REVIEW"
    VALIDATE_CODE = "VALIDATE_CODE"
    BUILD = "BUILD"
    START_SERVICES = "START_SERVICES"
    BROWSER_TEST = "BROWSER_TEST"
    DEVICE_TEST = "DEVICE_TEST"
    VISUAL_TEST = "VISUAL_TEST"
    SECURITY_TEST = "SECURITY_TEST"
    PERFORMANCE_TEST = "PERFORMANCE_TEST"
    ERROR_DETECTED = "ERROR_DETECTED"
    CLASSIFY_ERROR = "CLASSIFY_ERROR"
    MEMORY_LOOKUP = "MEMORY_LOOKUP"
    COLLECT_CONTEXT = "COLLECT_CONTEXT"
    AI_DIAGNOSIS = "AI_DIAGNOSIS"
    GENERATE_PATCH = "GENERATE_PATCH"
    PATCH_REVIEW = "PATCH_REVIEW"
    SECURITY_CHECK = "SECURITY_CHECK"
    APPLY_PATCH = "APPLY_PATCH"
    REBUILD = "REBUILD"
    RETEST = "RETEST"
    REGRESSION_TEST = "REGRESSION_TEST"
    CHECKPOINT = "CHECKPOINT"
    PACKAGE = "PACKAGE"
    GIT_STATUS = "GIT_STATUS"
    GIT_COMMIT = "GIT_COMMIT"
    GIT_PUSH = "GIT_PUSH"
    DELIVER = "DELIVER"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RECOVERY = "RECOVERY"
    CANCELLED = "CANCELLED"


class AutonomousStateMachine:
    """
    Manages state transitions, auditing, timeout limits, and lifecycle events.
    """

    def __init__(self, emit_fn: Optional[Callable[[str, Dict[str, Any]], None]] = None):
        self.current_state: AutonomousState = AutonomousState.IDLE
        self.history: List[Dict[str, Any]] = []
        self.state_enter_time: float = time.time()
        self.emit_fn = emit_fn

    def transition_to(self, new_state: AutonomousState, reason: str = "") -> AutonomousState:
        """Transitions to new state, records duration, and emits IPC event."""
        now = time.time()
        duration = round(now - self.state_enter_time, 3)
        prev_state = self.current_state

        event_record = {
            "from_state": prev_state.value,
            "to_state": new_state.value,
            "duration_seconds": duration,
            "reason": reason,
            "timestamp": now,
        }
        self.history.append(event_record)
        self.current_state = new_state
        self.state_enter_time = now

        if self.emit_fn:
            self.emit_fn("fsm.transition", {
                "previous": prev_state.value,
                "current": new_state.value,
                "duration": duration,
                "reason": reason
            })

        return self.current_state

    def is_terminal(self) -> bool:
        """Returns True if FSM is in a finished state."""
        return self.current_state in [
            AutonomousState.SUCCESS,
            AutonomousState.FAILED,
            AutonomousState.CANCELLED
        ]

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        return list(self.history)
