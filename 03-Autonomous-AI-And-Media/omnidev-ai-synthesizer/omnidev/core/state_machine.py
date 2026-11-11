import time
from enum import Enum
from typing import Dict, Any, Optional, Callable, List
from config import console

class FSMState(str, Enum):
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

class AutonomousFSM:
    """
    40-State Autonomous Finite State Machine for OmniDev missions.
    """
    def __init__(self, initial_state: FSMState = FSMState.IDLE):
        self.current_state: FSMState = initial_state
        self.state_history: List[Dict[str, Any]] = []
        self._hooks: Dict[FSMState, List[Callable]] = {}
        self.state_data: Dict[str, Any] = {}
        self._record_state_change(None, initial_state, "Initialization")

    def transition_to(self, new_state: FSMState, reason: str = "") -> bool:
        prev_state = self.current_state
        self.current_state = new_state
        self._record_state_change(prev_state, new_state, reason)

        # Execute registered state entry hooks
        if new_state in self._hooks:
            for hook in self._hooks[new_state]:
                try:
                    hook(prev_state, new_state, self.state_data)
                except Exception as e:
                    console.print(f"[bold red]State Hook Error ({new_state}): {e}[/bold red]")

        return True

    def register_hook(self, state: FSMState, callback: Callable):
        if state not in self._hooks:
            self._hooks[state] = []
        self._hooks[state].append(callback)

    def _record_state_change(self, prev_state: Optional[FSMState], new_state: FSMState, reason: str):
        record = {
            "from": prev_state.value if prev_state else None,
            "to": new_state.value,
            "reason": reason,
            "timestamp": time.time()
        }
        self.state_history.append(record)

    def is_terminal(self) -> bool:
        return self.current_state in [FSMState.SUCCESS, FSMState.FAILED, FSMState.CANCELLED]
