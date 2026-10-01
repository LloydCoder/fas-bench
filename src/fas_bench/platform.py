"""Phase 14 evaluation-platform contracts.

The platform layer is execution-provider neutral. It validates submissions and
creates deterministic evaluation jobs; secure execution remains delegated to
the Phase 9 provider.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum


class JobStatus(StrEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    POLICY_REJECTED = "POLICY_REJECTED"


@dataclass(frozen=True)
class EvaluationJob:
    benchmark_digest: str
    corpus_digest: str
    evaluator_digest: str
    scoring_digest: str
    submission_digest: str
    environment_digest: str
    policy_digest: str
    seed: int = 0

    def identity(self) -> str:
        payload = {
            "benchmark_digest": self.benchmark_digest,
            "corpus_digest": self.corpus_digest,
            "evaluator_digest": self.evaluator_digest,
            "scoring_digest": self.scoring_digest,
            "submission_digest": self.submission_digest,
            "environment_digest": self.environment_digest,
            "policy_digest": self.policy_digest,
            "seed": self.seed,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(encoded).hexdigest()


def validate_job(job: EvaluationJob) -> list[str]:
    errors = []
    for name in (
        "benchmark_digest",
        "corpus_digest",
        "evaluator_digest",
        "scoring_digest",
        "submission_digest",
        "environment_digest",
        "policy_digest",
    ):
        value = getattr(job, name)
        if not isinstance(value, str) or not value:
            errors.append(f"{name} must be a non-empty string")
    if job.seed < 0:
        errors.append("seed must be non-negative")
    return errors


def platform_gate(jobs: list[EvaluationJob]) -> dict:
    errors = [
        f"job-{index}: {error}"
        for index, job in enumerate(jobs, start=1)
        for error in validate_job(job)
    ]
    identities = [job.identity() for job in jobs]
    if len(identities) != len(set(identities)):
        errors.append("duplicate deterministic job identity")
    return {
        "phase": "14",
        "status": "PASS" if jobs and not errors else "FAIL",
        "job_count": len(jobs),
        "errors": sorted(set(errors)),
        "execution_provider": "PHASE9_SECURE_EVAL",
        "host_execution": False,
    }
