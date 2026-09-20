# fmt: off
# ruff: noqa: E701,E702,I001,UP035
from __future__ import annotations

from enum import StrEnum


class LifecycleState(StrEnum):
    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    PREPARING = "PREPARING"
    READY = "READY"
    RUNNING = "RUNNING"
    COLLECTING = "COLLECTING"
    EVALUATING = "EVALUATING"
    SCORING = "SCORING"
    FINALIZING = "FINALIZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMED_OUT = "TIMED_OUT"
    INVALID = "INVALID"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    PARTIAL = "PARTIAL"
    CLEANUP_FAILED = "CLEANUP_FAILED"


_ALLOWED = {
    LifecycleState.CREATED: {LifecycleState.VALIDATING, LifecycleState.CANCELLED, LifecycleState.INVALID},
    LifecycleState.VALIDATING: {LifecycleState.PREPARING, LifecycleState.FAILED, LifecycleState.INVALID, LifecycleState.CANCELLED},
    LifecycleState.PREPARING: {LifecycleState.READY, LifecycleState.FAILED, LifecycleState.SECURITY_VIOLATION, LifecycleState.CANCELLED},
    LifecycleState.READY: {LifecycleState.RUNNING, LifecycleState.CANCELLED},
    LifecycleState.RUNNING: {LifecycleState.COLLECTING, LifecycleState.FAILED, LifecycleState.TIMED_OUT, LifecycleState.SECURITY_VIOLATION, LifecycleState.CANCELLED},
    LifecycleState.COLLECTING: {LifecycleState.EVALUATING, LifecycleState.FAILED, LifecycleState.CLEANUP_FAILED},
    LifecycleState.EVALUATING: {LifecycleState.SCORING, LifecycleState.FAILED},
    LifecycleState.SCORING: {LifecycleState.FINALIZING, LifecycleState.FAILED},
    LifecycleState.FINALIZING: {LifecycleState.COMPLETED, LifecycleState.PARTIAL, LifecycleState.FAILED, LifecycleState.CLEANUP_FAILED},
}


class LifecycleError(ValueError):
    pass


class RunLifecycle:
    def __init__(self, state: LifecycleState = LifecycleState.CREATED):
        self.state = state

    def transition(self, target: LifecycleState) -> LifecycleState:
        if target not in _ALLOWED.get(self.state, set()):
            raise LifecycleError(f"illegal lifecycle transition {self.state} -> {target}")
        self.state = target
        return self.state

    def can_transition(self, target: LifecycleState) -> bool:
        return target in _ALLOWED.get(self.state, set())
