"""Phase 16 benchmark test registry and specification contracts."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Mapping


class TestLifecycle(StrEnum):
    PROPOSED = "PROPOSED"
    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    VALIDATED = "VALIDATED"
    CALIBRATED = "CALIBRATED"
    CERTIFIED = "CERTIFIED"
    RELEASED = "RELEASED"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"


@dataclass(frozen=True)
class TestSpec:
    test_id: str
    version: str
    title: str
    objective: str
    primary_category: str
    difficulty: str
    oracle_type: str
    evidence_requirements: tuple[str, ...]
    prerequisites: tuple[str, ...] = ()
    lifecycle: TestLifecycle = TestLifecycle.DRAFT
    source_digest: str = ""

    def canonical(self) -> dict:
        data = asdict(self)
        data["lifecycle"] = self.lifecycle.value
        for key in ("evidence_requirements", "prerequisites"):
            data[key] = sorted(data[key])
        return data

    def identity(self) -> str:
        payload = json.dumps(
            self.canonical(), sort_keys=True, separators=(",", ":")
        ).encode()
        return hashlib.sha256(payload).hexdigest()


def validate_test_spec(spec: TestSpec) -> list[str]:
    errors: list[str] = []
    required = (
        "test_id", "version", "title", "objective",
        "primary_category", "difficulty", "oracle_type",
    )
    for name in required:
        value = getattr(spec, name)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{name} must be non-empty")
    if not spec.evidence_requirements:
        errors.append("evidence_requirements must not be empty")
    if spec.lifecycle in {TestLifecycle.RELEASED, TestLifecycle.CERTIFIED}:
        if not spec.source_digest:
            errors.append("released/certified tests require source_digest")
    return sorted(set(errors))


def registry_validate(specs: list[TestSpec]) -> dict:
    errors = [
        f"{spec.test_id}: {err}"
        for spec in specs
        for err in validate_test_spec(spec)
    ]
    ids = [spec.test_id for spec in specs]
    if len(ids) != len(set(ids)):
        errors.append("duplicate test_id")
    identities = [spec.identity() for spec in specs]
    if len(identities) != len(set(identities)):
        errors.append("duplicate test identity")
    return {
        "phase": "16",
        "status": "PASS" if specs and not errors else "FAIL",
        "test_count": len(specs),
        "errors": sorted(set(errors)),
        "release_authority": "GOVERNANCE",
    }


def coverage_matrix(specs: list[TestSpec]) -> Mapping[str, int]:
    result: dict[str, int] = {}
    for spec in specs:
        result[spec.primary_category] = result.get(spec.primary_category, 0) + 1
    return dict(sorted(result.items()))
