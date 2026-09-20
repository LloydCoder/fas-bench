# fmt: off
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

from .lifecycle import LifecycleState, RunLifecycle
from .runner import SecureRunner
from .models import ExecutionRequest, ExecutionResult


@dataclass(frozen=True)
class CaseExecution:
    case_id: str
    attempt_id: str
    result: ExecutionResult


class EvaluationOrchestrator:
    """Thin orchestration layer; Phase 4–8 remain authoritative for domain evaluation."""

    def __init__(self, runner: SecureRunner, artifact_root: Path):
        self.runner = runner
        self.artifact_root = Path(artifact_root)

    def execute_case(self, request: ExecutionRequest, *, attempt_id: str = "attempt-001") -> CaseExecution:
        lifecycle = RunLifecycle()
        lifecycle.transition(LifecycleState.VALIDATING)
        lifecycle.transition(LifecycleState.PREPARING)
        lifecycle.transition(LifecycleState.READY)
        lifecycle.transition(LifecycleState.RUNNING)
        result = self.runner.execute(request)
        lifecycle.transition(
            LifecycleState.TIMED_OUT if result.status == "TIMEOUT"
            else LifecycleState.SECURITY_VIOLATION if result.status == "SECURITY_VIOLATION"
            else LifecycleState.FAILED if result.status not in {"SUCCESS", "OUTPUT_LIMIT"}
            else LifecycleState.COLLECTING
        )
        if lifecycle.state == LifecycleState.COLLECTING:
            lifecycle.transition(LifecycleState.EVALUATING)
            lifecycle.transition(LifecycleState.SCORING)
            lifecycle.transition(LifecycleState.FINALIZING)
            lifecycle.transition(LifecycleState.COMPLETED if result.cleanup_ok else LifecycleState.CLEANUP_FAILED)
        return CaseExecution(request.case_id, attempt_id, result)
