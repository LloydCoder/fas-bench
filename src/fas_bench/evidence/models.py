"""Small domain models used by the deterministic evidence engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EvidenceItemResult:
    evidence_id: str
    status: str
    reason_code: str
    matched_ground_truth: tuple[str, ...] = ()
    duplicate_of: str | None = None
    details: str | None = None

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "evidence_id": self.evidence_id,
            "status": self.status,
            "reason_code": self.reason_code,
            "matched_ground_truth": list(self.matched_ground_truth),
        }
        if self.duplicate_of is not None:
            result["duplicate_of"] = self.duplicate_of
        if self.details is not None:
            result["details"] = self.details
        return result


@dataclass(frozen=True)
class EvidenceVerificationResult:
    case_id: str
    submission_id: str
    benchmark_version: str
    evaluator_version: str
    items: tuple[EvidenceItemResult, ...] = field(default_factory=tuple)
    submitted: int = 0
    verified: int = 0
    invalid: int = 0
    unresolved: int = 0
    contradicted: int = 0
    missing_expected: int = 0
    duplicate: int = 0
    coverage: float = 0.0
    evidence_hallucination_rate: float = 0.0
    result_hash: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "submission_id": self.submission_id,
            "benchmark_version": self.benchmark_version,
            "evaluator_version": self.evaluator_version,
            "evidence": {
                "submitted": self.submitted,
                "verified": self.verified,
                "invalid": self.invalid,
                "unresolved": self.unresolved,
                "contradicted": self.contradicted,
                "missing_expected": self.missing_expected,
                "duplicate": self.duplicate,
            },
            "coverage": self.coverage,
            "evidence_hallucination_rate": self.evidence_hallucination_rate,
            "items": [item.as_dict() for item in self.items],
            "result_hash": self.result_hash,
        }
