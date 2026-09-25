"""Offline JSON Schema and semantic validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from .contract import BENCHMARK_VERSION, CASE_IDS, SCHEMA_VERSION

PACKAGE_ROOT = Path(__file__).resolve().parent
ROOT = PACKAGE_ROOT.parents[1]
SCHEMA_ROOT = PACKAGE_ROOT / "schemas" if (PACKAGE_ROOT / "schemas").exists() else ROOT / "schemas"
FAMILY_PATHS = {
    name: SCHEMA_ROOT / f"{name}/v0.1/{name}.schema.json"
    for name in (
        "case",
        "claim",
        "evidence",
        "attack-graph",
        "verdict",
        "remediation",
        "submission",
        "evaluation-result",
        "remediation-evaluation",
        "release-manifest",
        "release-validation",
    )
}


@dataclass(frozen=True)
class ValidationErrorDetail:
    code: str
    path: str
    message: str
    schema_location: str | None = None
    instance_location: str | None = None


@dataclass(frozen=True)
class ValidationResult:
    status: str
    errors: tuple[ValidationErrorDetail, ...] = ()


def load_schema(family: str) -> dict[str, Any]:
    if family not in FAMILY_PATHS:
        raise ValueError(f"Unsupported schema family: {family}")
    return json.loads(FAMILY_PATHS[family].read_text(encoding="utf-8"))


def _registry() -> Registry:
    registry = Registry()
    paths = [SCHEMA_ROOT / "common/v0.1/common.schema.json", *FAMILY_PATHS.values()]
    for path in paths:
        document = json.loads(path.read_text(encoding="utf-8"))
        registry = registry.with_resource(document["$id"], Resource.from_contents(document))
    return registry


def validate_instance(document: dict[str, Any], family: str) -> ValidationResult:
    schema = load_schema(family)
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        return ValidationResult(
            "SCHEMA_INVALID",
            (ValidationErrorDetail("SCHEMA_INVALID", "$", str(exc)),),
        )

    validator = Draft202012Validator(
        schema,
        registry=_registry(),
        format_checker=FormatChecker(),
    )
    errors = tuple(
        sorted(validator.iter_errors(document), key=lambda error: list(error.absolute_path))
    )
    if not errors:
        return ValidationResult("VALID")

    details = tuple(
        ValidationErrorDetail(
            "SCHEMA_INVALID",
            ".".join(map(str, error.absolute_path)) or "$",
            error.message,
        )
        for error in errors
    )
    return ValidationResult("SCHEMA_INVALID", details)


def _error(code: str, path: str, message: str) -> ValidationErrorDetail:
    return ValidationErrorDetail(code, path, message)


def _index(items: list[dict[str, Any]], key: str):
    indexed: dict[str, dict[str, Any]] = {}
    errors: list[ValidationErrorDetail] = []
    for index, item in enumerate(items):
        identifier = item.get(key)
        if identifier in indexed:
            errors.append(
                _error(
                    "DUPLICATE_ID",
                    f"{key}s[{index}]",
                    f"duplicate identifier {identifier!r}",
                )
            )
        elif identifier is not None:
            indexed[identifier] = item
    return indexed, errors


def validate_semantics(
    document: dict[str, Any],
    family: str,
    case_ids: set[str] | None = None,
) -> ValidationResult:
    errors: list[ValidationErrorDetail] = []

    if document.get("benchmark_version") != BENCHMARK_VERSION:
        errors.append(
            _error("VERSION_MISMATCH", "benchmark_version", "unsupported benchmark version")
        )
    if document.get("schema_version") != SCHEMA_VERSION:
        errors.append(_error("VERSION_MISMATCH", "schema_version", "unsupported schema version"))

    if family == "case":
        return (
            ValidationResult("SEMANTIC_INVALID", tuple(errors))
            if errors
            else ValidationResult("VALID")
        )

    if family == "evidence":
        location = document.get("location", {})
        if (
            location.get("line_start") is not None
            and location.get("line_end") is not None
            and location["line_end"] < location["line_start"]
        ):
            errors.append(_error("SEMANTIC_INVALID", "location", "line_end must be >= line_start"))

    if family == "attack-graph":
        nodes, node_errors = _index(document.get("nodes", []), "node_id")
        edges, edge_errors = _index(document.get("edges", []), "edge_id")
        paths, path_errors = _index(document.get("paths", []), "path_id")
        errors.extend(node_errors + edge_errors + path_errors)

        for edge in document.get("edges", []):
            if edge["source"] not in nodes:
                errors.append(
                    _error(
                        "REFERENCE_INVALID",
                        "edges",
                        f"unknown source node {edge['source']!r}",
                    )
                )
            if edge["target"] not in nodes:
                errors.append(
                    _error(
                        "REFERENCE_INVALID",
                        "edges",
                        f"unknown target node {edge['target']!r}",
                    )
                )

        for path in document.get("paths", []):
            path_id = path["path_id"]
            if any(node not in nodes for node in path["node_ids"]):
                errors.append(_error("PATH_INVALID", path_id, "unknown path node"))
            if any(edge not in edges for edge in path["edge_ids"]):
                errors.append(_error("PATH_INVALID", path_id, "unknown path edge"))
            if path["entry_node"] not in nodes or path["impact_node"] not in nodes:
                errors.append(_error("PATH_INVALID", path_id, "invalid entry/impact node"))

            expected_edges = max(0, len(path["node_ids"]) - 1)
            if len(path["edge_ids"]) != expected_edges:
                errors.append(
                    _error(
                        "PATH_INVALID",
                        path_id,
                        "ordered path requires one edge per node transition",
                    )
                )

            for index, edge_id in enumerate(path["edge_ids"]):
                if edge_id not in edges or index + 1 >= len(path["node_ids"]):
                    continue
                edge = edges[edge_id]
                if (
                    edge["source"] != path["node_ids"][index]
                    or edge["target"] != path["node_ids"][index + 1]
                ):
                    errors.append(
                        _error(
                            "PATH_INVALID",
                            path_id,
                            f"edge {edge_id!r} contradicts node sequence",
                        )
                    )

    if family == "verdict":
        if document["verdict"] == "CONDITIONALLY_EXPLOITABLE" and not document.get("conditions"):
            errors.append(
                _error(
                    "MISSING_REQUIRED_DATA",
                    "conditions",
                    "conditional verdict requires explicit conditions",
                )
            )
        if document["verdict"] != "CONDITIONALLY_EXPLOITABLE" and document.get("conditions"):
            errors.append(
                _error(
                    "SEMANTIC_INVALID",
                    "conditions",
                    "conditions only apply to conditional exploitability",
                )
            )

    if family == "remediation":
        status = document["verification_status"]
        final_verdict = document["final_verdict"]
        if status == "VERIFIED" and final_verdict != "REMEDIATED":
            errors.append(
                _error(
                    "SEMANTIC_INVALID",
                    "final_verdict",
                    "VERIFIED remediation must end REMEDIATED",
                )
            )
        if status == "FAILED" and final_verdict != "REMEDIATION_FAILED":
            errors.append(
                _error(
                    "SEMANTIC_INVALID",
                    "final_verdict",
                    "FAILED remediation must end REMEDIATION_FAILED",
                )
            )
        if document.get("alternate_path_ids") and final_verdict == "REMEDIATED":
            errors.append(
                _error(
                    "SEMANTIC_INVALID",
                    "alternate_path_ids",
                    "alternate paths conflict with REMEDIATED",
                )
            )

    if family == "submission":
        if case_ids is not None and document["case_id"] not in case_ids:
            errors.append(_error("CASE_MISMATCH", "case_id", "case is not in benchmark registry"))

        claims, claim_errors = _index(document["claims"], "claim_id")
        evidence, evidence_errors = _index(document["evidence"], "evidence_id")
        paths, path_errors = _index(document["attack_paths"], "path_id")
        errors.extend(claim_errors + evidence_errors + path_errors)

        for claim in document["claims"]:
            for evidence_id in claim.get("related_evidence", []):
                if evidence_id not in evidence:
                    errors.append(
                        _error(
                            "REFERENCE_INVALID",
                            f"claims.{claim['claim_id']}.related_evidence",
                            f"unknown evidence {evidence_id!r}",
                        )
                    )

        for item in document["evidence"]:
            for claim_id in item.get("related_claims", []):
                if claim_id not in claims:
                    errors.append(
                        _error(
                            "REFERENCE_INVALID",
                            f"evidence.{item['evidence_id']}.related_claims",
                            f"unknown claim {claim_id!r}",
                        )
                    )

        verdict = document["verdict"]
        for claim_id in verdict["claim_ids"]:
            if claim_id not in claims:
                errors.append(
                    _error(
                        "REFERENCE_INVALID",
                        "verdict.claim_ids",
                        f"unknown claim {claim_id!r}",
                    )
                )
        for evidence_id in verdict["evidence_ids"]:
            if evidence_id not in evidence:
                errors.append(
                    _error(
                        "REFERENCE_INVALID",
                        "verdict.evidence_ids",
                        f"unknown evidence {evidence_id!r}",
                    )
                )
        for path_id in verdict["attack_path_ids"]:
            if path_id not in paths:
                errors.append(
                    _error(
                        "REFERENCE_INVALID",
                        "verdict.attack_path_ids",
                        f"unknown path {path_id!r}",
                    )
                )

        for path in document["attack_paths"]:
            expected_edges = max(0, len(path["node_ids"]) - 1)
            if len(path["edge_ids"]) != expected_edges:
                errors.append(
                    _error(
                        "PATH_INVALID",
                        path["path_id"],
                        "edge/node sequence mismatch",
                    )
                )

        remediation = document.get("remediation")
        if remediation:
            for claim_id in remediation["target_claim_ids"]:
                if claim_id not in claims:
                    errors.append(
                        _error(
                            "REFERENCE_INVALID",
                            "remediation.target_claim_ids",
                            f"unknown claim {claim_id!r}",
                        )
                    )
            referenced_paths = (
                remediation["original_path_ids"]
                + remediation["revalidated_path_ids"]
                + remediation["alternate_path_ids"]
            )
            for path_id in referenced_paths:
                if path_id not in paths:
                    errors.append(
                        _error(
                            "REFERENCE_INVALID",
                            "remediation.path_ids",
                            f"unknown path {path_id!r}",
                        )
                    )

    if family == "evaluation-result":
        components = (
            "finding_score",
            "verdict_score",
            "evidence_score",
            "reachability_score",
            "attack_path_score",
            "impact_score",
            "remediation_score",
            "calibration_score",
            "efficiency_score",
        )
        scoring_present = any(component in document for component in components) or any(
            key in document for key in ("final_score", "cap", "penalty")
        )
        if scoring_present:
            total = 0.0
            for component in components:
                value = document.get(component, {})
                contribution = value.get("contribution", 0)
                normalized = value.get("normalized", 0)
                weight = value.get("weight", 0)
                if abs(contribution - normalized * weight) > 1e-9:
                    errors.append(
                        _error(
                            "INTEGRITY_VIOLATION",
                            component,
                            "contribution must equal normalized multiplied by weight",
                        )
                    )
                total += contribution
            if not all(key in document for key in ("final_score", "cap", "penalty")):
                errors.append(
                    _error(
                        "MISSING_REQUIRED_DATA",
                        "scoring",
                        "scoring fields must be complete when any scoring field is present",
                    )
                )
            else:
                expected = max(0, min(document["cap"], total - document["penalty"]))
                if abs(expected - document["final_score"]) > 1e-9:
                    errors.append(
                        _error(
                            "INTEGRITY_VIOLATION",
                            "final_score",
                            "final score is not coherent with contributions, cap, and penalty",
                        )
                    )
        if document["validity"] != "VALID" and not document["errors"]:
            errors.append(
                _error(
                    "MISSING_REQUIRED_DATA",
                    "errors",
                    "non-valid result requires structured errors",
                )
            )

    if errors:
        return ValidationResult("SEMANTIC_INVALID", tuple(errors))
    return ValidationResult("VALID")


def validate(
    document: dict[str, Any],
    family: str,
    semantic: bool = True,
    case_ids: set[str] | None = None,
) -> ValidationResult:
    structural = validate_instance(document, family)
    if structural.status != "VALID" or not semantic:
        return structural
    return validate_semantics(document, family, case_ids or set(CASE_IDS))


def validate_case(document, **kwargs):
    return validate(document, "case", **kwargs)


def validate_claim(document, **kwargs):
    return validate(document, "claim", **kwargs)


def validate_evidence(document, **kwargs):
    return validate(document, "evidence", **kwargs)


def validate_attack_graph(document, **kwargs):
    return validate(document, "attack-graph", **kwargs)


def validate_verdict(document, **kwargs):
    return validate(document, "verdict", **kwargs)


def validate_remediation(document, **kwargs):
    return validate(document, "remediation", **kwargs)


def validate_submission(document, **kwargs):
    return validate(document, "submission", **kwargs)


def validate_evaluation_result(document, **kwargs):
    return validate(document, "evaluation-result", **kwargs)


def validate_file(
    path: Path,
    family: str,
    semantic: bool = True,
    case_ids: set[str] | None = None,
) -> ValidationResult:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return ValidationResult(
            "SCHEMA_INVALID",
            (_error("SCHEMA_INVALID", "$", f"invalid JSON: {exc}"),),
        )
    return validate(document, family, semantic, case_ids)
