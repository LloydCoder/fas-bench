"""Phase 7 remediation and regression domain models."""

# ruff: noqa: I001
# Ruff 0.16.8 misclassifies this stdlib-only import block in this module.

# Ruff 0.16.8 I001 misclassifies this stdlib-only import block in this module.
# Keep the explicit stdlib import and suppress only the false-positive sorter diagnostic.

import dataclasses


TEST_STATUSES = {"PASS", "FAIL", "ERROR", "TIMEOUT", "NOT_APPLICABLE", "UNRESOLVED"}
PATH_LIFECYCLES = {"PRESENT", "REMOVED", "PERSISTING", "REPLACED", "REINTRODUCED", "UNKNOWN"}
ALTERNATE_CLASSES = {"EQUIVALENT_IMPACT", "LOWER_IMPACT", "HIGHER_IMPACT", "UNRELATED", "UNKNOWN"}
REMEDIATION_STATUSES = {
    "REMEDIATED",
    "REMEDIATION_FAILED",
    "CONDITIONALLY_REMEDIATED",
    "REGRESSED",
    "UNKNOWN",
    "BENCHMARK_ERROR",
}


@dataclasses.dataclass(frozen=True)
class TestResult:
    test_id: str
    test_type: str
    status: str
    expected: str | None = None
    observed: str | None = None
    evidence_ids: tuple[str, ...] = ()
    details: str | None = None

    def __post_init__(self) -> None:
        if self.status not in TEST_STATUSES:
            raise ValueError(f"unsupported test status: {self.status}")

    def as_dict(self) -> dict[str, object]:
        value = {
            "test_id": self.test_id,
            "test_type": self.test_type,
            "status": self.status,
            "evidence_ids": list(self.evidence_ids),
        }
        if self.expected is not None:
            value["expected"] = self.expected
        if self.observed is not None:
            value["observed"] = self.observed
        if self.details is not None:
            value["details"] = self.details
        return value


@dataclasses.dataclass(frozen=True)
class PathLifecycle:
    path_id: str
    lifecycle: str
    before_status: str | None
    after_status: str | None
    equivalent_path_id: str | None = None
    reason: str = ""

    def __post_init__(self) -> None:
        if self.lifecycle not in PATH_LIFECYCLES:
            raise ValueError(f"unsupported path lifecycle: {self.lifecycle}")

    def as_dict(self) -> dict[str, object]:
        return {
            "path_id": self.path_id,
            "lifecycle": self.lifecycle,
            "before_status": self.before_status,
            "after_status": self.after_status,
            "equivalent_path_id": self.equivalent_path_id,
            "reason": self.reason,
        }


@dataclasses.dataclass(frozen=True)
class AlternatePath:
    path_id: str
    classification: str
    impact_key: str
    entry_key: str
    reason: str

    def __post_init__(self) -> None:
        if self.classification not in ALTERNATE_CLASSES:
            raise ValueError(f"unsupported alternate-path classification: {self.classification}")

    def as_dict(self) -> dict[str, object]:
        return {
            "path_id": self.path_id,
            "classification": self.classification,
            "impact_key": self.impact_key,
            "entry_key": self.entry_key,
            "reason": self.reason,
        }


@dataclasses.dataclass(frozen=True)
class SecurityState:
    state_id: str
    case_id: str
    condition_id: str
    condition_status: str
    graph: dict[str, object]
    paths: tuple[dict[str, object], ...] = ()
    controls: tuple[dict[str, object], ...] = ()
    repository_digest: str | None = None
    environment_digest: str | None = None
    evidence_digest: str | None = None
    benchmark_version: str = "0.1.0"
    case_version: str = "0.1.0"

    def as_dict(self) -> dict[str, object]:
        return {
            "state_id": self.state_id,
            "case_id": self.case_id,
            "condition_id": self.condition_id,
            "condition_status": self.condition_status,
            "graph": self.graph,
            "paths": list(self.paths),
            "controls": list(self.controls),
            "repository_digest": self.repository_digest,
            "environment_digest": self.environment_digest,
            "evidence_digest": self.evidence_digest,
            "benchmark_version": self.benchmark_version,
            "case_version": self.case_version,
        }


@dataclasses.dataclass(frozen=True)
class RemediationResult:
    remediation_id: str
    case_id: str
    status: str
    original_condition_status: str
    path_status: str
    alternate_path_status: str
    security_test_status: str
    functional_test_status: str
    regression_status: str
    new_findings_status: str
    evidence_integrity: str
    path_lifecycles: tuple[PathLifecycle, ...] = ()
    alternate_paths: tuple[AlternatePath, ...] = ()
    graph_diff: dict[str, object] = dataclasses.field(default_factory=dict)
    security_condition_diff: dict[str, object] = dataclasses.field(default_factory=dict)
    security_controls: dict[str, object] = dataclasses.field(default_factory=dict)
    test_results: tuple[TestResult, ...] = ()
    dimensions: dict[str, float] = dataclasses.field(default_factory=dict)
    score: float | None = None
    diagnostics: tuple[str, ...] = ()
    provenance: dict[str, str] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.status not in REMEDIATION_STATUSES:
            raise ValueError(f"unsupported remediation status: {self.status}")

    def as_dict(self) -> dict[str, object]:
        value = {
            "remediation_id": self.remediation_id,
            "case_id": self.case_id,
            "status": self.status,
            "original_condition_status": self.original_condition_status,
            "path_status": self.path_status,
            "alternate_path_status": self.alternate_path_status,
            "security_test_status": self.security_test_status,
            "functional_test_status": self.functional_test_status,
            "regression_status": self.regression_status,
            "new_findings_status": self.new_findings_status,
            "evidence_integrity": self.evidence_integrity,
            "path_lifecycles": [x.as_dict() for x in self.path_lifecycles],
            "alternate_paths": [x.as_dict() for x in self.alternate_paths],
            "graph_diff": self.graph_diff,
            "security_condition_diff": self.security_condition_diff,
            "security_controls": self.security_controls,
            "security_tests": [
                x.as_dict() for x in self.test_results if x.test_type.startswith("SECURITY")
            ],
            "functional_tests": [
                x.as_dict() for x in self.test_results if x.test_type.startswith("FUNCTIONAL")
            ],
            "regression_tests": [
                x.as_dict() for x in self.test_results if x.test_type.startswith("REGRESSION")
            ],
            "new_finding_tests": [
                x.as_dict() for x in self.test_results if x.test_type.startswith("NEW_")
            ],
            "dimensions": self.dimensions,
            "diagnostics": list(self.diagnostics),
            "provenance": self.provenance,
        }
        if self.score is not None:
            value["score"] = self.score
        return value
