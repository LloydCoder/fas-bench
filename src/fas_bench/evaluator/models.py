"""Structured Phase 5 evaluation results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


CLAIM_STATUSES = ("VERIFIED", "INVALID", "UNRESOLVED", "CONTRADICTED", "MISSING")
PRECONDITION_STATUSES = ("SATISFIED", "UNSATISFIED", "CONDITIONAL", "UNKNOWN")


@dataclass(frozen=True)
class ClaimEvaluation:
    claim_id: str
    status: str
    expected_claim_id: str | None = None
    reason_code: str = "CLAIM_UNSUPPORTED"
    evidence_ids: tuple[str, ...] = ()
    details: str | None = None

    def as_dict(self) -> dict[str, Any]:
        value = {
            "claim_id": self.claim_id,
            "status": self.status,
            "reason_code": self.reason_code,
            "evidence_ids": list(self.evidence_ids),
        }
        if self.expected_claim_id is not None:
            value["expected_claim_id"] = self.expected_claim_id
        if self.details:
            value["details"] = self.details
        return value


@dataclass(frozen=True)
class FindingEvaluation:
    finding_id: str
    matched: bool
    category_supported: bool
    claims_supported: bool
    evidence_supported: bool
    verdict_claimed: str
    expected_verdict: str
    reason_code: str
    details: str | None = None

    def as_dict(self) -> dict[str, Any]:
        value = {
            "finding_id": self.finding_id,
            "matched": self.matched,
            "category_supported": self.category_supported,
            "claims_supported": self.claims_supported,
            "evidence_supported": self.evidence_supported,
            "verdict_claimed": self.verdict_claimed,
            "expected_verdict": self.expected_verdict,
            "reason_code": self.reason_code,
        }
        if self.details:
            value["details"] = self.details
        return value


@dataclass(frozen=True)
class SecurityCondition:
    path_id: str
    path_status: str
    security_property: str
    effective_control_state: str
    required_conditions: tuple[str, ...] = ()
    satisfied_conditions: tuple[str, ...] = ()
    unsatisfied_conditions: tuple[str, ...] = ()
    unknown_conditions: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "path_id": self.path_id,
            "path_status": self.path_status,
            "security_property": self.security_property,
            "effective_control_state": self.effective_control_state,
            "required_conditions": list(self.required_conditions),
            "satisfied_conditions": list(self.satisfied_conditions),
            "unsatisfied_conditions": list(self.unsatisfied_conditions),
            "unknown_conditions": list(self.unknown_conditions),
        }


@dataclass(frozen=True)
class VerdictEvaluation:
    submitted: str
    expected: str
    verdict_correct: bool
    verdict_supported: bool
    reason_code: str
    supporting_claims: tuple[str, ...] = ()
    blocking_claims: tuple[str, ...] = ()
    required_conditions: tuple[str, ...] = ()
    satisfied_conditions: tuple[str, ...] = ()
    unsatisfied_conditions: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    details: str | None = None

    def as_dict(self) -> dict[str, Any]:
        value = {
            "submitted": self.submitted,
            "expected": self.expected,
            "verdict_correct": self.verdict_correct,
            "verdict_supported": self.verdict_supported,
            "reason_code": self.reason_code,
            "supporting_claims": list(self.supporting_claims),
            "blocking_claims": list(self.blocking_claims),
            "required_conditions": list(self.required_conditions),
            "satisfied_conditions": list(self.satisfied_conditions),
            "unsatisfied_conditions": list(self.unsatisfied_conditions),
            "evidence_ids": list(self.evidence_ids),
        }
        if self.details:
            value["details"] = self.details
        return value


@dataclass(frozen=True)
class FindingEvaluationResult:
    evaluation_id: str
    case_id: str
    submission_id: str
    benchmark_version: str
    schema_version: str
    expected_verdict: str
    finding: FindingEvaluation
    claims: tuple[ClaimEvaluation, ...]
    security_condition: SecurityCondition
    verdict: VerdictEvaluation
    evidence: dict[str, Any]
    fingerprint: str
    errors: tuple[dict[str, str], ...] = ()
    warnings: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {
            "evaluation_phase": "PHASE_5_VERDICT",
            "evaluation_id": self.evaluation_id,
            "case_id": self.case_id,
            "submission_id": self.submission_id,
            "benchmark_version": self.benchmark_version,
            "schema_version": self.schema_version,
            "validity": "VALID",
            "expected_verdict": self.expected_verdict,
            "finding_evaluation": self.finding.as_dict(),
            "claim_evaluations": [claim.as_dict() for claim in self.claims],
            "security_condition": self.security_condition.as_dict(),
            "verdict_evaluation": self.verdict.as_dict(),
            "evidence": self.evidence,
            "fingerprint": self.fingerprint,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "metadata": {"scoring_deferred_to_phase_8": True},
        }
