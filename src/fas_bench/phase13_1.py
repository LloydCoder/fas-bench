"""Phase 13.1 governance and release-approval contract."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

CHANGE_CLASSES = frozenset(
    {
        "CASE",
        "ORACLE",
        "SCHEMA",
        "SCORING",
        "EVALUATOR",
        "HARNESS",
        "RELEASE",
        "DOCUMENTATION",
        "INFRASTRUCTURE",
    }
)
REVIEW_DIMENSIONS = (
    "security_objective",
    "oracle_ground_truth",
    "security",
    "reproducibility_integrity",
)


def validate_change_record(record: Mapping[str, object]) -> list[str]:
    errors: list[str] = []
    if record.get("change_class") not in CHANGE_CLASSES:
        errors.append("invalid change_class")
    for field in ("rationale", "impact_assessment", "validation_evidence", "changelog_entry"):
        if not isinstance(record.get(field), str) or not record[field]:
            errors.append(f"{field} is required")
    reviews = record.get("reviews")
    if not isinstance(reviews, Mapping):
        errors.append("reviews must be a mapping")
    else:
        for dimension in REVIEW_DIMENSIONS:
            if reviews.get(dimension) is not True:
                errors.append(f"required review missing: {dimension}")
    if record.get("approval") is not True:
        errors.append("release/change approval is required")
    return sorted(set(errors))


def governance_gate(
    records: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    errors = [
        f"record-{index}: {error}"
        for index, record in enumerate(records, start=1)
        for error in validate_change_record(record)
    ]
    return {
        "phase": "13.1",
        "status": "PASS" if records and not errors else "FAIL",
        "record_count": len(records),
        "errors": sorted(set(errors)),
        "governance_claim": False,
        "requires_human_approval": True,
    }
