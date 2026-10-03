"""Phase 19 adversarial and benchmark-gaming resistance contracts."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum


_SHA256 = 64


class AttackClass(StrEnum):
    PROMPT_INJECTION = "PROMPT_INJECTION"
    EVIDENCE_POISONING = "EVIDENCE_POISONING"
    TOOL_OUTPUT_MANIPULATION = "TOOL_OUTPUT_MANIPULATION"
    REPOSITORY_DECEPTION = "REPOSITORY_DECEPTION"
    ORACLE_TAMPERING = "ORACLE_TAMPERING"
    SANDBOX_ATTACK = "SANDBOX_ATTACK"
    GAMING = "GAMING"


class RobustnessStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"
    INFRASTRUCTURE_FAILURE = "INFRASTRUCTURE_FAILURE"


def _valid_digest(value: str) -> bool:
    return (
        isinstance(value, str)
        and len(value) == _SHA256
        and all(character in "0123456789abcdef" for character in value.lower())
    )


@dataclass(frozen=True)
class AdversarialCase:
    attack_id: str
    version: str
    attack_class: AttackClass
    target_surface: str
    expected_invariant: str
    mutation_digest: str
    oracle_digest: str

    def identity(self) -> str:
        payload = {
            "attack_id": self.attack_id,
            "version": self.version,
            "attack_class": self.attack_class.value,
            "target_surface": self.target_surface,
            "expected_invariant": self.expected_invariant,
            "mutation_digest": self.mutation_digest,
            "oracle_digest": self.oracle_digest,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


@dataclass(frozen=True)
class RobustnessResult:
    attack_id: str
    status: RobustnessStatus
    observed_invariant: str
    evidence_digest: str
    execution_identity: str


def validate_adversarial_case(case: AdversarialCase) -> list[str]:
    errors: list[str] = []
    for name in (
        "attack_id",
        "version",
        "target_surface",
        "expected_invariant",
        "mutation_digest",
        "oracle_digest",
    ):
        if not getattr(case, name).strip():
            errors.append(f"{name} is required")
    for name in ("mutation_digest", "oracle_digest"):
        if not _valid_digest(getattr(case, name)):
            errors.append(f"{name} must be a lowercase SHA-256 digest")
    return sorted(set(errors))


def _validate_result(result: RobustnessResult) -> list[str]:
    errors: list[str] = []
    if not result.attack_id.strip():
        errors.append("attack_id is required")
    if not result.observed_invariant.strip():
        errors.append("observed_invariant is required")
    if not _valid_digest(result.evidence_digest):
        errors.append("evidence_digest must be a lowercase SHA-256 digest")
    if not result.execution_identity.strip():
        errors.append("execution_identity is required")
    return errors


def robustness_gate(
    cases: list[AdversarialCase], results: list[RobustnessResult]
) -> dict:
    errors = [
        f"{case.attack_id}@{case.version}: {error}"
        for case in cases
        for error in validate_adversarial_case(case)
    ]
    errors.extend(
        f"result {result.attack_id}: {error}"
        for result in results
        for error in _validate_result(result)
    )
    case_keys = [(case.attack_id, case.version) for case in cases]
    if len(case_keys) != len(set(case_keys)):
        errors.append("duplicate attack_id/version")

    by_id = {}
    for result in results:
        if result.attack_id in by_id:
            errors.append(f"duplicate robustness result for {result.attack_id}")
        by_id[result.attack_id] = result

    expected_ids = {case.attack_id for case in cases}
    extra_ids = set(by_id) - expected_ids
    if extra_ids:
        errors.append("robustness results contain unknown attack IDs")

    for case in cases:
        result = by_id.get(case.attack_id)
        if result is None:
            errors.append(f"{case.attack_id}: missing robustness result")
        elif result.status != RobustnessStatus.PASS:
            errors.append(f"{case.attack_id}: robustness result is {result.status}")
        elif result.observed_invariant != case.expected_invariant:
            errors.append(f"{case.attack_id}: invariant mismatch")
    return {
        "phase": "19",
        "status": "PASS" if cases and not errors else "FAIL",
        "case_count": len(cases),
        "errors": sorted(set(errors)),
        "gaming_detection": True,
        "oracle_authority": "AUTHORITATIVE_CASE_ORACLE",
    }
