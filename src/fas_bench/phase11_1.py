"""Phase 11.1 dynamic and agentic oracle contract."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

ORACLE_STATUSES = frozenset(
    {"PASS", "FAIL", "INCONCLUSIVE", "INFRASTRUCTURE_FAILURE", "POLICY_VIOLATION"}
)
OBSERVATION_TYPES = frozenset(
    {"REACHABILITY", "EXPLOITABILITY", "BOUNDARY", "REMEDIATION", "REGRESSION", "AGENTIC"}
)
REQUIRED_FIELDS = frozenset(
    {
        "oracle_id",
        "case_id",
        "observation_type",
        "status",
        "run_id",
        "input_digest",
        "artifact_manifest_digest",
        "policy_digest",
        "environment_digest",
        "observed_at",
    }
)


@dataclass(frozen=True)
class OracleObservation:
    oracle_id: str
    case_id: str
    observation_type: str
    status: str
    run_id: str
    input_digest: str
    artifact_manifest_digest: str
    policy_digest: str
    environment_digest: str
    observed_at: str
    evidence: tuple[dict[str, Any], ...] = ()

    def canonical_bytes(self) -> bytes:
        payload = {
            "oracle_id": self.oracle_id,
            "case_id": self.case_id,
            "observation_type": self.observation_type,
            "status": self.status,
            "run_id": self.run_id,
            "input_digest": self.input_digest,
            "artifact_manifest_digest": self.artifact_manifest_digest,
            "policy_digest": self.policy_digest,
            "environment_digest": self.environment_digest,
            "observed_at": self.observed_at,
            "evidence": list(self.evidence),
        }
        return json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode("utf-8")

    @property
    def observation_digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


def validate_observation(record: dict[str, Any]) -> list[str]:
    errors = [
        f"missing required oracle field: {field}"
        for field in sorted(REQUIRED_FIELDS - record.keys())
    ]
    if record.get("observation_type") not in OBSERVATION_TYPES:
        errors.append("invalid observation type")
    if record.get("status") not in ORACLE_STATUSES:
        errors.append("invalid oracle status")
    for field in (
        "oracle_id",
        "case_id",
        "run_id",
        "input_digest",
        "artifact_manifest_digest",
        "policy_digest",
        "environment_digest",
        "observed_at",
    ):
        if field in record and (not isinstance(record[field], str) or not record[field]):
            errors.append(f"{field} must be a non-empty string")
    evidence = record.get("evidence", [])
    if not isinstance(evidence, list) or any(not isinstance(item, dict) for item in evidence):
        errors.append("evidence must be a list of objects")
    if record.get("status") in {"PASS", "FAIL"} and not evidence:
        errors.append("PASS/FAIL observations require independently inspectable evidence")
    return sorted(set(errors))


def dynamic_oracle_gate(records: list[dict[str, Any]]) -> dict[str, Any]:
    errors = [
        f"{record.get('case_id')}: {error}"
        for record in records
        for error in validate_observation(record)
    ]
    return {
        "phase": "11.1",
        "status": "PASS" if not errors else "FAIL",
        "observation_count": len(records),
        "errors": sorted(set(errors)),
        "oracle_self_certifies_ground_truth": False,
        "requires_secure_execution_provider": True,
    }
