"""Phase 11 corpus-quality and mutation-integrity gates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .contract import CASE_IDS
from .mutations import SEMANTIC_CLASSES

SECURITY_CHANGING = frozenset(SEMANTIC_CLASSES) - {
    "SEMANTICALLY_EQUIVALENT",
    "INVALID",
}
REQUIRED_CASE_FIELDS = frozenset(
    {"case_id", "category", "difficulty", "provenance", "validation_type"}
)


@dataclass(frozen=True)
class CorpusProfile:
    case_count: int
    categories: dict[str, int]
    difficulties: dict[str, int]
    validation_types: dict[str, int]
    provenance: dict[str, int]
    lifecycle: dict[str, int]
    public_case_ids: tuple[str, ...]

    @property
    def engineering_ready(self) -> bool:
        return (
            self.case_count > 0
            and bool(self.categories)
            and bool(self.difficulties)
            and bool(self.validation_types)
            and bool(self.provenance)
        )


def _counts(records: Iterable[dict], key: str) -> dict[str, int]:
    out = {}
    for record in records:
        value = str(record.get(key, "MISSING"))
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items()))


def profile_cases(records: Iterable[dict]) -> CorpusProfile:
    rows = tuple(records)
    return CorpusProfile(
        len(rows),
        _counts(rows, "category"),
        _counts(rows, "difficulty"),
        _counts(rows, "validation_type"),
        _counts(rows, "provenance"),
        _counts(rows, "phase10_lifecycle"),
        tuple(sorted(str(r.get("case_id", "")) for r in rows)),
    )


def validate_case_record_shape(record: dict) -> list[str]:
    errors = [
        f"missing required corpus field: {field}"
        for field in sorted(REQUIRED_CASE_FIELDS - record.keys())
    ]
    if record.get("case_id") not in CASE_IDS:
        errors.append(f"case outside canonical corpus: {record.get('case_id')!r}")
    if record.get("difficulty") not in {
        "L1_LOCAL",
        "L2_MULTI_FUNCTION",
        "L3_MULTI_COMPONENT",
        "L4_AGENTIC",
        "L5_CROSS_SYSTEM",
    }:
        errors.append("invalid difficulty level")
    return errors


def validate_mutation_semantics(
    *,
    semantic_class: str,
    source_before: bytes,
    source_after: bytes,
    oracle: Callable[[bytes, bytes], bool] | None,
) -> tuple[bool, str]:
    if semantic_class not in SEMANTIC_CLASSES:
        return False, "unknown semantic class"
    if semantic_class == "INVALID":
        return False, "INVALID mutations cannot enter an evaluation corpus"
    if not source_after:
        return False, "empty mutation artifact"
    if semantic_class == "SEMANTICALLY_EQUIVALENT":
        if oracle is not None and not oracle(source_before, source_after):
            return False, "equivalence oracle rejected mutation"
        return True, "validated"
    if oracle is None:
        return False, "security-changing mutation requires an authoritative oracle"
    if not oracle(source_before, source_after):
        return False, "authoritative oracle rejected security relation"
    return True, "validated"


def phase11_gate(records: Iterable[dict]) -> dict:
    rows = tuple(records)
    errors = [
        f"{r.get('case_id')}: {e}"
        for r in rows
        for e in validate_case_record_shape(r)
    ]
    profile = profile_cases(rows)
    if not profile.engineering_ready:
        errors.append("corpus profile is not engineering-ready")
    return {
        "phase": "11",
        "status": "PASS" if not errors else "FAIL",
        "case_count": profile.case_count,
        "profile": {
            "categories": profile.categories,
            "difficulties": profile.difficulties,
            "validation_types": profile.validation_types,
            "provenance": profile.provenance,
            "lifecycle": profile.lifecycle,
        },
        "errors": sorted(set(errors)),
        "statistical_representativeness_claim": False,
    }
