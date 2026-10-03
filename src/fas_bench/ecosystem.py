"""Phase 21 submission, results, provenance, and governance contracts."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from enum import StrEnum


_SHA256 = 64


def _valid_digest(value: str) -> bool:
    return (
        isinstance(value, str)
        and len(value) == _SHA256
        and value == value.lower()
        and all(character in "0123456789abcdef" for character in value)
    )


class ResultStatus(StrEnum):
    VALID = "VALID"
    INVALID = "INVALID"
    INFRASTRUCTURE_FAILURE = "INFRASTRUCTURE_FAILURE"


class Lifecycle(StrEnum):
    PROPOSED = "PROPOSED"
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    VALIDATED = "VALIDATED"
    CALIBRATED = "CALIBRATED"
    CERTIFIED = "CERTIFIED"
    RELEASED = "RELEASED"
    MONITORED = "MONITORED"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"


_ALLOWED_TRANSITIONS = {
    Lifecycle.PROPOSED: {Lifecycle.DRAFT},
    Lifecycle.DRAFT: {Lifecycle.REVIEW},
    Lifecycle.REVIEW: {Lifecycle.VALIDATED, Lifecycle.DRAFT},
    Lifecycle.VALIDATED: {Lifecycle.CALIBRATED, Lifecycle.REVIEW},
    Lifecycle.CALIBRATED: {Lifecycle.CERTIFIED, Lifecycle.REVIEW},
    Lifecycle.CERTIFIED: {Lifecycle.RELEASED, Lifecycle.REVIEW},
    Lifecycle.RELEASED: {Lifecycle.MONITORED, Lifecycle.DEPRECATED},
    Lifecycle.MONITORED: {Lifecycle.DEPRECATED, Lifecycle.RETIRED},
    Lifecycle.DEPRECATED: {Lifecycle.RETIRED},
    Lifecycle.RETIRED: set(),
}


@dataclass(frozen=True)
class SubmissionManifest:
    system_id: str
    system_version: str
    model_id: str
    configuration_digest: str
    toolchain_digest: str
    environment_digest: str
    submission_digest: str
    adapter_version: str

    def identity(self) -> str:
        return hashlib.sha256(
            json.dumps(
                self.__dict__, sort_keys=True, separators=(",", ":")
            ).encode()
        ).hexdigest()

    def validate(self) -> list[str]:
        errors = []
        for name in (
            "system_id",
            "system_version",
            "model_id",
            "configuration_digest",
            "toolchain_digest",
            "environment_digest",
            "submission_digest",
            "adapter_version",
        ):
            if not getattr(self, name):
                errors.append(f"{name} is required")
        for name in (
            "configuration_digest",
            "toolchain_digest",
            "environment_digest",
            "submission_digest",
        ):
            if not _valid_digest(getattr(self, name)):
                errors.append(f"{name} must be a lowercase SHA-256 digest")
        return sorted(set(errors))


@dataclass(frozen=True)
class ResultRecord:
    result_id: str
    benchmark_digest: str
    submission_identity: str
    corpus_digest: str
    evaluator_digest: str
    score: float
    confidence_interval: tuple[float, float]
    status: ResultStatus
    provenance_identity: str
    cost: float | None = None
    latency_ms: float | None = None

    def validate(self) -> list[str]:
        errors: list[str] = []
        for name in (
            "result_id",
            "benchmark_digest",
            "submission_identity",
            "corpus_digest",
            "evaluator_digest",
            "provenance_identity",
        ):
            if not getattr(self, name):
                errors.append(f"{name} is required")
        for name in (
            "benchmark_digest",
            "corpus_digest",
            "evaluator_digest",
        ):
            if not _valid_digest(getattr(self, name)):
                errors.append(f"{name} must be a lowercase SHA-256 digest")
        if not _valid_digest(self.submission_identity):
            errors.append("submission_identity must be a lowercase SHA-256 digest")
        if not _valid_digest(self.provenance_identity):
            errors.append("provenance_identity must be a lowercase SHA-256 digest")
        if not math.isfinite(self.score) or not 0.0 <= self.score <= 1.0:
            errors.append("score must be finite and within [0,1]")
        if (
            len(self.confidence_interval) != 2
            or not all(math.isfinite(value) for value in self.confidence_interval)
        ):
            errors.append("confidence interval must contain two finite values")
        else:
            low, high = self.confidence_interval
            if not 0.0 <= low <= high <= 1.0:
                errors.append("confidence interval must be within [0,1]")
        if self.cost is not None and (
            not math.isfinite(self.cost) or self.cost < 0
        ):
            errors.append("cost must be a finite non-negative value")
        if self.latency_ms is not None and (
            not math.isfinite(self.latency_ms) or self.latency_ms < 0
        ):
            errors.append("latency_ms must be a finite non-negative value")
        return sorted(set(errors))


@dataclass(frozen=True)
class ProvenanceEdge:
    source: str
    target: str
    relation: str
    digest: str
    actor: str


def provenance_gate(edges: list[ProvenanceEdge]) -> dict:
    errors: list[str] = []
    for edge in edges:
        if not all(
            isinstance(value, str) and value.strip()
            for value in (edge.source, edge.target, edge.relation, edge.actor)
        ):
            errors.append(
                "provenance edges require non-empty source, target, relation, and actor"
            )
        if not _valid_digest(edge.digest):
            errors.append("provenance edge digest must be a lowercase SHA-256 digest")
        if edge.source == edge.target:
            errors.append("provenance edge source and target must differ")
    keys = {(e.source, e.target, e.relation) for e in edges}
    if len(keys) != len(edges):
        errors.append("duplicate provenance edge")
    return {
        "phase": "21",
        "status": "PASS" if edges and not errors else "FAIL",
        "edge_count": len(edges),
        "errors": sorted(set(errors)),
        "attestation_model": "content-addressed",
        "automatic_release_authority": False,
    }


def transition_allowed(current: Lifecycle, target: Lifecycle) -> bool:
    return target in _ALLOWED_TRANSITIONS[current]


def governance_transition(
    current: Lifecycle,
    target: Lifecycle,
    human_approved: bool = False,
) -> dict:
    allowed = transition_allowed(current, target)
    if target in {Lifecycle.CERTIFIED, Lifecycle.RELEASED} and not human_approved:
        allowed = False
    return {
        "from": current.value,
        "to": target.value,
        "allowed": allowed,
        "human_approval_required": target in {
            Lifecycle.CERTIFIED,
            Lifecycle.RELEASED,
        },
    }
