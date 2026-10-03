"""Phase 19 adversarial and benchmark-gaming resistance contracts."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum


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
            "attack_id": self.attack_id, "version": self.version,
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
        "attack_id", "version", "target_surface", "expected_invariant",
        "mutation_digest", "oracle_digest",
    ):
        if not getattr(case, name):
            errors.append(f"{name} is required")
    if case.attack_class == AttackClass.ORACLE_TAMPERING and not case.oracle_digest:
        errors.append("oracle tampering cases require an oracle digest")
    return sorted(set(errors))


def robustness_gate(cases: list[AdversarialCase], results: list[RobustnessResult]) -> dict:
    errors = [f"{c.attack_id}: {e}" for c in cases for e in validate_adversarial_case(c)]
    by_id = {r.attack_id: r for r in results}
    for case in cases:
        result = by_id.get(case.attack_id)
        if result is None:
            errors.append(f"{case.attack_id}: missing robustness result")
        elif result.status == RobustnessStatus.INFRASTRUCTURE_FAILURE:
            errors.append(f"{case.attack_id}: infrastructure failure")
        elif result.status == RobustnessStatus.PASS and result.observed_invariant != case.expected_invariant:
            errors.append(f"{case.attack_id}: invariant mismatch")
    return {
        "phase": "19",
        "status": "PASS" if cases and not errors else "FAIL",
        "case_count": len(cases),
        "errors": sorted(set(errors)),
        "gaming_detection": True,
        "oracle_authority": "AUTHORITATIVE_CASE_ORACLE",
    }
