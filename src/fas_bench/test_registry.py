"""Phase 16 benchmark test registry and specification contracts."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from enum import StrEnum


_SHA256 = 64


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


_ALLOWED_TRANSITIONS = {
    TestLifecycle.PROPOSED: {TestLifecycle.DRAFT},
    TestLifecycle.DRAFT: {TestLifecycle.REVIEW},
    TestLifecycle.REVIEW: {TestLifecycle.VALIDATED, TestLifecycle.DRAFT},
    TestLifecycle.VALIDATED: {TestLifecycle.CALIBRATED, TestLifecycle.REVIEW},
    TestLifecycle.CALIBRATED: {TestLifecycle.CERTIFIED, TestLifecycle.REVIEW},
    TestLifecycle.CERTIFIED: {TestLifecycle.RELEASED, TestLifecycle.REVIEW},
    TestLifecycle.RELEASED: {TestLifecycle.DEPRECATED},
    TestLifecycle.DEPRECATED: {TestLifecycle.RETIRED},
    TestLifecycle.RETIRED: set(),
}


def _valid_digest(value: str) -> bool:
    return (
        isinstance(value, str)
        and len(value) == _SHA256
        and value == value.lower()
        and all(character in "0123456789abcdef" for character in value)
    )


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
        data["lifecycle"] = (
            self.lifecycle.value
            if isinstance(self.lifecycle, TestLifecycle)
            else str(self.lifecycle)
        )
        for key in ("evidence_requirements", "prerequisites"):
            data[key] = sorted(data[key])
        return data

    def identity(self) -> str:
        data = self.canonical()
        data.pop("lifecycle")
        payload = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(payload).hexdigest()


def validate_test_spec(spec: TestSpec) -> list[str]:
    errors: list[str] = []
    required = (
        "test_id",
        "version",
        "title",
        "objective",
        "primary_category",
        "difficulty",
        "oracle_type",
    )
    for name in required:
        value = getattr(spec, name)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{name} must be non-empty")

    for name, values in (
        ("evidence_requirements", spec.evidence_requirements),
        ("prerequisites", spec.prerequisites),
    ):
        if any(not isinstance(value, str) or not value.strip() for value in values):
            errors.append(f"{name} entries must be non-empty strings")
        if len(values) != len(set(values)):
            errors.append(f"{name} must not contain duplicates")

    if not spec.evidence_requirements:
        errors.append("evidence_requirements must not be empty")

    if not isinstance(spec.lifecycle, TestLifecycle):
        errors.append("lifecycle must be a valid TestLifecycle")
    elif spec.lifecycle in {TestLifecycle.CERTIFIED, TestLifecycle.RELEASED}:
        if not _valid_digest(spec.source_digest):
            errors.append("certified/released tests require a lowercase SHA-256 source_digest")

    return sorted(set(errors))


def registry_validate(specs: list[TestSpec]) -> dict:
    errors = [
        f"{spec.test_id}@{spec.version}: {err}"
        for spec in specs
        for err in validate_test_spec(spec)
    ]
    versions = [(spec.test_id, spec.version) for spec in specs]
    if len(versions) != len(set(versions)):
        errors.append("duplicate test_id/version")
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


def lifecycle_transition_allowed(current: TestLifecycle, target: TestLifecycle) -> bool:
    return target in _ALLOWED_TRANSITIONS[current]


def coverage_matrix(specs: list[TestSpec]) -> Mapping[str, int]:
    result: dict[str, int] = {}
    for spec in specs:
        result[spec.primary_category] = result.get(spec.primary_category, 0) + 1
    return dict(sorted(result.items()))
