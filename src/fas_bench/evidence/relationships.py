"""Deterministic evidence relationship checks."""

from __future__ import annotations

from typing import Any

_REFERENCE_FIELDS = (
    "related_claims",
    "related_findings",
    "related_nodes",
    "related_edges",
    "related_paths",
    "related_remediations",
)


def relationship_errors(
    evidence: dict[str, Any],
    expected: dict[str, Any] | None = None,
    submission: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if expected is not None:
        for field in _REFERENCE_FIELDS:
            expected_values = set(expected.get(field) or [])
            actual_values = set(evidence.get(field) or [])
            if expected_values != actual_values:
                errors.append(field)
    if submission is not None:
        collections = {
            "related_claims": {item["claim_id"] for item in submission.get("claims", [])},
            "related_findings": {item["finding_id"] for item in submission.get("findings", [])},
            "related_paths": {item["path_id"] for item in submission.get("attack_paths", [])},
        }
        for field, known in collections.items():
            for value in evidence.get(field) or []:
                if value not in known:
                    errors.append(f"{field}:{value}")
    return sorted(set(errors))
