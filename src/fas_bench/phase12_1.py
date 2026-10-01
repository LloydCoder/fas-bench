"""Phase 12.1 independent-validation protocol and agreement primitives."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from statistics import mean

VALID_REVIEW_STATUSES = frozenset({"COMPLETE", "INCOMPLETE", "REJECTED"})


@dataclass(frozen=True)
class ReviewRecord:
    evaluator_id: str
    independence: bool
    blinded: bool
    case_count: int
    methodology_digest: str
    environment_digest: str
    status: str
    limitations: tuple[str, ...] = ()

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.evaluator_id:
            errors.append("evaluator_id is required")
        if not self.independence:
            errors.append("reviewer must be independent of benchmark implementation")
        if not self.blinded:
            errors.append("independent review must declare whether evaluation was blinded")
        if self.case_count < 1:
            errors.append("case_count must be positive")
        if not self.methodology_digest:
            errors.append("methodology_digest is required")
        if not self.environment_digest:
            errors.append("environment_digest is required")
        if self.status not in VALID_REVIEW_STATUSES:
            errors.append("invalid review status")
        return errors


def cohens_kappa(first: Sequence[str], second: Sequence[str]) -> float:
    if len(first) != len(second) or not first:
        raise ValueError("paired non-empty observations are required")
    agree = mean(a == b for a, b in zip(first, second, strict=True))
    labels = sorted(set(first) | set(second))
    expected = sum(
        (first.count(label) / len(first)) * (second.count(label) / len(second)) for label in labels
    )
    if expected == 1.0:
        return 1.0
    return (agree - expected) / (1.0 - expected)


def phase12_1_gate(records: Sequence[ReviewRecord]) -> dict:
    errors = [f"{r.evaluator_id}: {error}" for r in records for error in r.validate()]
    complete = sum(r.status == "COMPLETE" for r in records)
    return {
        "phase": "12.1",
        "status": "PASS" if records and not errors else "FAIL",
        "reviewer_count": len(records),
        "complete_reviewer_count": complete,
        "errors": sorted(set(errors)),
        "external_validation_claim": False,
        "requires_external_evidence": True,
    }
