"""Deterministic Phase 7 remediation and regression oracle."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ..contract import EVALUATOR_VERSION
from ..graph import compare_graphs, diff_graphs, graph_digest, validate_graph
from .models import AlternatePath, PathLifecycle, RemediationResult, SecurityState, TestResult

REMEDIATION_ENGINE_VERSION = "0.1.0"
REMEDIATION_SCHEMA_VERSION = "0.1"
REMEDIATION_SCORING_VERSION = "0.1.0"


def _path_map(state: SecurityState) -> dict[str, dict[str, Any]]:
    return {p["path_id"]: p for p in state.paths}


def _status(path: dict[str, Any] | None) -> str | None:
    return path.get("status") if path else None


def _impact_key(path: dict[str, Any]) -> str:
    return str(path.get("impact_key") or path.get("impact_node") or path.get("impact_class") or "")


def _entry_key(path: dict[str, Any]) -> str:
    return str(path.get("entry_key") or path.get("entry_node") or path.get("entry_class") or "")


def _path_equivalent(before: dict[str, Any], after: dict[str, Any]) -> bool:
    before_condition = before.get("security_condition_id", before.get("condition_id"))
    after_condition = after.get("security_condition_id", after.get("condition_id"))
    if before_condition and after_condition and before_condition != after_condition:
        return False
    impact = _impact_key(before)
    return bool(impact) and impact == _impact_key(after)


def _classify_alternates(
    baseline: SecurityState, post: SecurityState, original_ids: set[str]
) -> tuple[AlternatePath, ...]:
    baseline_paths = _path_map(baseline)
    result: list[AlternatePath] = []
    original_impacts = {
        _impact_key(path) for pid, path in baseline_paths.items() if pid in original_ids
    }
    for path in post.paths:
        if path.get("path_id") in original_ids or path.get("status") not in {"VIABLE", "COMPLETE"}:
            continue
        impact = _impact_key(path)
        if not impact or impact not in original_impacts:
            classification = "UNKNOWN" if not impact else "UNRELATED"
        else:
            baseline_equivalent = any(
                _path_equivalent(before, path)
                for pid, before in baseline_paths.items()
                if pid in original_ids
            )
            classification = "EQUIVALENT_IMPACT" if baseline_equivalent else "HIGHER_IMPACT"
        result.append(
            AlternatePath(
                path_id=path["path_id"],
                classification=classification,
                impact_key=impact,
                entry_key=_entry_key(path),
                reason="post-remediation viable path shares the target security impact",
            )
        )
    return tuple(sorted(result, key=lambda item: item.path_id))


def _path_lifecycles(baseline: SecurityState, post: SecurityState, original_ids: set[str]):
    before = _path_map(baseline)
    after = _path_map(post)
    result: list[PathLifecycle] = []
    for pid in sorted(original_ids):
        b, a = before.get(pid), after.get(pid)
        bs, ass = _status(b), _status(a)
        if b is None:
            result.append(PathLifecycle(pid, "UNKNOWN", None, ass, reason="baseline path missing"))
        elif a is None:
            result.append(
                PathLifecycle(pid, "REMOVED", bs, None, reason="path absent after remediation")
            )
        elif bs in {"VIABLE", "COMPLETE"} and ass in {"BLOCKED", "INCOMPLETE"}:
            result.append(
                PathLifecycle(
                    pid, "REMOVED", bs, ass, reason="path remains represented but is blocked"
                )
            )
        elif bs in {"BLOCKED", "INCOMPLETE"} and ass in {"VIABLE", "COMPLETE"}:
            result.append(
                PathLifecycle(
                    pid, "REINTRODUCED", bs, ass, reason="previously blocked path became viable"
                )
            )
        elif bs == ass:
            result.append(
                PathLifecycle(pid, "PERSISTING", bs, ass, reason="security path status persisted")
            )
        else:
            result.append(
                PathLifecycle(
                    pid,
                    "UNKNOWN",
                    bs,
                    ass,
                    reason="path transition is not deterministically classified",
                )
            )
    return tuple(result)


def _aggregate_tests(tests: tuple[TestResult, ...], prefix: str) -> str:
    selected = [t.status for t in tests if t.test_type.startswith(prefix)]
    if not selected:
        return "NOT_ASSESSED"
    if any(x in {"ERROR", "TIMEOUT", "UNRESOLVED"} for x in selected):
        return "UNRESOLVED"
    if any(x == "FAIL" for x in selected):
        return "FAIL"
    return "PASS"


def _evidence_integrity(evidence: tuple[dict[str, Any], ...]) -> str:
    if not evidence:
        return "UNRESOLVED"
    states = {item.get("verification") for item in evidence}
    if "INVALID" in states or "CONTRADICTED" in states:
        return "INVALID"
    if states == {"VERIFIED"}:
        return "VERIFIED"
    return "UNRESOLVED"


def _control_diff(before: SecurityState, after: SecurityState) -> dict[str, Any]:
    b = {str(x.get("control_id", x.get("name", i))): x for i, x in enumerate(before.controls)}
    a = {str(x.get("control_id", x.get("name", i))): x for i, x in enumerate(after.controls)}
    removed = sorted(set(b) - set(a))
    added = sorted(set(a) - set(b))
    weakened: list[str] = [key for key in removed if b[key].get("effective") is True]
    strengthened: list[str] = []
    for key in sorted(set(b) & set(a)):
        old = b[key].get("effective")
        new = a[key].get("effective")
        if old is True and new is False:
            weakened.append(key)
        elif old is False and new is True:
            strengthened.append(key)
    return {
        "added": added,
        "removed": removed,
        "weakened": weakened,
        "strengthened": strengthened,
    }


def _security_condition_diff(baseline: SecurityState, post: SecurityState) -> dict[str, Any]:
    return {
        "condition_id": baseline.condition_id,
        "before": baseline.condition_status,
        "after": post.condition_status,
        "closed": baseline.condition_status in {"VIABLE", "EXPLOITABLE", "REACHABLE"}
        and post.condition_status in {"BLOCKED", "NOT_EXPLOITABLE", "CLOSED"},
        "reopened": baseline.condition_status in {"BLOCKED", "NOT_EXPLOITABLE", "CLOSED"}
        and post.condition_status in {"VIABLE", "EXPLOITABLE", "REACHABLE"},
    }


def _result_score(dimensions: dict[str, float]) -> float:
    return round(sum(dimensions.values()) / len(dimensions), 12) if dimensions else 0.0


def evaluate_remediation(
    baseline: SecurityState,
    post: SecurityState,
    remediation: dict[str, Any],
    *,
    security_tests: tuple[TestResult, ...] = (),
    evidence: tuple[dict[str, Any], ...] = (),
    functional_tests: tuple[TestResult, ...] = (),
    regression_tests: tuple[TestResult, ...] = (),
    new_finding_tests: tuple[TestResult, ...] = (),
) -> RemediationResult:
    diagnostics: list[str] = []
    if baseline.case_id != post.case_id:
        return _benchmark_error(remediation, baseline.case_id, "baseline/post case mismatch")
    if baseline.case_version != post.case_version:
        return _benchmark_error(remediation, baseline.case_id, "case version mismatch")
    if (
        baseline.environment_digest is not None
        and post.environment_digest is not None
        and baseline.environment_digest != post.environment_digest
    ):
        return _benchmark_error(remediation, baseline.case_id, "baseline/post environment mismatch")
    if baseline.condition_id != post.condition_id:
        return _benchmark_error(
            remediation, baseline.case_id, "security-condition identity mismatch"
        )
    if baseline.benchmark_version != post.benchmark_version:
        return _benchmark_error(remediation, baseline.case_id, "benchmark version mismatch")
    bv = validate_graph(baseline.graph, case_id=baseline.case_id)
    pv = validate_graph(post.graph, case_id=post.case_id)
    if not bv.valid or not pv.valid:
        return _benchmark_error(
            remediation, baseline.case_id, "invalid baseline or post-remediation graph"
        )
    for state_name, state in (("baseline", baseline), ("post-remediation", post)):
        seen_path_ids: set[str] = set()
        for item in state.paths:
            path_id = item.get("path_id")
            if not path_id or path_id in seen_path_ids:
                return _benchmark_error(
                    remediation, baseline.case_id, f"{state_name} contains duplicate or missing path id"
                )
            seen_path_ids.add(path_id)
            condition_ref = item.get("security_condition_id", item.get("condition_id"))
            if condition_ref is not None and condition_ref != state.condition_id:
                return _benchmark_error(
                    remediation,
                    baseline.case_id,
                    f"{state_name} path {path_id} references a different security condition",
                )
    original_ids = set(remediation.get("original_path_ids", []))
    if not original_ids:
        return _benchmark_error(
            remediation, baseline.case_id, "no remediation target paths declared"
        )
    lifecycles = _path_lifecycles(baseline, post, original_ids)
    alternates = _classify_alternates(baseline, post, original_ids)
    security_status = _aggregate_tests(tuple(security_tests), "SECURITY")
    functional_status = _aggregate_tests(tuple(functional_tests), "FUNCTIONAL")
    regression_status = _aggregate_tests(tuple(regression_tests), "REGRESSION")
    new_status = _aggregate_tests(tuple(new_finding_tests), "NEW_")
    all_tests = (
        tuple(security_tests)
        + tuple(functional_tests)
        + tuple(regression_tests)
        + tuple(new_finding_tests)
    )
    evidence_status = _evidence_integrity(evidence)
    controls = _control_diff(baseline, post)
    condition_diff = _security_condition_diff(baseline, post)
    graph_diff = diff_graphs(baseline.graph, post.graph)
    graph_compare = compare_graphs(baseline.graph, post.graph, case_id=baseline.case_id)
    if controls["weakened"]:
        diagnostics.append("security-critical control weakened")
    if alternates:
        diagnostics.append("viable alternate path remains")
    if any(x.lifecycle in {"PERSISTING", "REINTRODUCED"} for x in lifecycles):
        diagnostics.append("original attack path remains viable")
    if security_status == "FAIL":
        diagnostics.append("required security test failed")
    if functional_status == "FAIL":
        diagnostics.append("required functional test failed")
    if evidence_status != "VERIFIED":
        diagnostics.append("remediation evidence is not fully verified")
    if regression_status == "FAIL":
        diagnostics.append("regression test failed")
    if new_status == "FAIL":
        diagnostics.append("new-finding test failed")

    path_closed = bool(lifecycles) and all(x.lifecycle == "REMOVED" for x in lifecycles)
    alternate_closed = not any(
        x.classification in {"EQUIVALENT_IMPACT", "HIGHER_IMPACT"} for x in alternates
    )
    security_ok = security_status == "PASS"
    functional_ok = functional_status == "PASS"
    regression_ok = regression_status in {"PASS", "NOT_ASSESSED"}
    new_ok = new_status in {"PASS", "NOT_ASSESSED"}
    controls_ok = not controls["weakened"]
    conditional = bool(remediation.get("conditions")) or post.condition_status == "CONDITIONAL"
    unknown = (
        any(
            status == "UNRESOLVED"
            for status in (security_status, functional_status, regression_status, new_status)
        )
        or evidence_status == "UNRESOLVED"
    )
    failed = (
        any(x.lifecycle in {"PERSISTING", "REINTRODUCED"} for x in lifecycles)
        or not alternate_closed
        or security_status == "FAIL"
        or functional_status == "FAIL"
        or regression_status == "FAIL"
        or new_status == "FAIL"
        or not controls_ok
    )
    if unknown and not failed:
        status = "UNKNOWN"
    elif failed:
        status = "REMEDIATION_FAILED"
    elif conditional:
        status = "CONDITIONALLY_REMEDIATED"
    elif (
        condition_diff["closed"]
        and path_closed
        and alternate_closed
        and security_ok
        and functional_ok
        and regression_ok
        and new_ok
        and controls_ok
        and evidence_status == "VERIFIED"
    ):
        status = "REMEDIATED"
    else:
        status = "UNKNOWN"

    dimensions = {
        "security_condition_resolution": 1.0 if condition_diff["closed"] else 0.0,
        "attack_path_resolution": 1.0 if path_closed else 0.0,
        "alternate_path_resolution": 1.0 if alternate_closed else 0.0,
        "control_effectiveness": 1.0 if controls_ok else 0.0,
        "security_test_success": 1.0 if security_ok else 0.0,
        "functional_preservation": 1.0 if functional_ok else 0.0,
        "regression_resistance": 1.0 if regression_ok else 0.0,
        "evidence_integrity": 1.0 if evidence_status == "VERIFIED" else 0.0,
    }
    provenance = {
        "benchmark_version": baseline.benchmark_version,
        "case_version": baseline.case_version,
        "baseline_graph_digest": graph_digest(baseline.graph),
        "post_graph_digest": graph_digest(post.graph),
        "evaluator_version": EVALUATOR_VERSION,
        "remediation_engine_version": REMEDIATION_ENGINE_VERSION,
        "remediation_schema_version": REMEDIATION_SCHEMA_VERSION,
        "normalization_version": graph_compare.versions["normalization_version"],
        "scoring_version": REMEDIATION_SCORING_VERSION,
    }
    run_material = {
        "benchmark_version": baseline.benchmark_version,
        "case_id": baseline.case_id,
        "remediation_id": remediation.get("remediation_id"),
        "baseline_graph_digest": provenance["baseline_graph_digest"],
        "post_graph_digest": provenance["post_graph_digest"],
        "evidence_digest": baseline.evidence_digest,
        "environment_digest": baseline.environment_digest,
        "evaluator_version": EVALUATOR_VERSION,
    }
    provenance["evaluation_run_id"] = (
        "EVAL-"
        + hashlib.sha256(
            json.dumps(run_material, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()[:24]
    )
    return RemediationResult(
        remediation_id=remediation["remediation_id"],
        case_id=baseline.case_id,
        status=status,
        original_condition_status=baseline.condition_status,
        path_status="REMOVED" if path_closed else "PERSISTING",
        alternate_path_status="CLOSED" if alternate_closed else "REMAINS",
        security_test_status=security_status,
        functional_test_status=functional_status,
        regression_status=regression_status,
        new_findings_status=new_status,
        evidence_integrity=evidence_status,
        path_lifecycles=lifecycles,
        alternate_paths=alternates,
        graph_diff=graph_diff,
        security_condition_diff=condition_diff,
        security_controls=controls,
        test_results=all_tests,
        dimensions=dimensions,
        score=_result_score(dimensions),
        diagnostics=tuple(diagnostics),
        provenance=provenance,
    )


def evaluate_regression(
    previous: SecurityState,
    current: SecurityState,
    *,
    security_tests: tuple[TestResult, ...] = (),
) -> dict[str, Any]:
    if previous.case_id != current.case_id or previous.condition_id != current.condition_id:
        return {
            "status": "BENCHMARK_ERROR",
            "reason": "incompatible regression baseline",
        }
    pv = validate_graph(previous.graph, case_id=previous.case_id)
    cv = validate_graph(current.graph, case_id=current.case_id)
    if not pv.valid or not cv.valid:
        return {"status": "BENCHMARK_ERROR", "reason": "invalid regression graph"}
    condition = _security_condition_diff(previous, current)
    controls = _control_diff(previous, current)
    tests = _aggregate_tests(security_tests, "REGRESSION")
    regressed = condition["reopened"] or bool(controls["weakened"])
    if tests in {"FAIL", "PASS"}:
        regressed = regressed or tests == "FAIL"
    if tests in {"UNRESOLVED"}:
        status = "UNKNOWN"
    else:
        status = "REGRESSED" if regressed else "NOT_REGRESSED"
    return {
        "status": status,
        "condition_diff": condition,
        "control_diff": controls,
        "graph_diff": diff_graphs(previous.graph, current.graph),
        "graph_digests": {
            "previous": graph_digest(previous.graph),
            "current": graph_digest(current.graph),
        },
        "test_status": tests,
        "evaluator_version": REMEDIATION_ENGINE_VERSION,
    }


def _benchmark_error(remediation: dict[str, Any], case_id: str, message: str) -> RemediationResult:
    return RemediationResult(
        remediation_id=str(remediation.get("remediation_id", "REM-INVALID")),
        case_id=case_id,
        status="BENCHMARK_ERROR",
        original_condition_status="UNKNOWN",
        path_status="UNKNOWN",
        alternate_path_status="UNKNOWN",
        security_test_status="UNRESOLVED",
        functional_test_status="UNRESOLVED",
        regression_status="UNRESOLVED",
        new_findings_status="UNRESOLVED",
        evidence_integrity="UNRESOLVED",
        diagnostics=(message,),
    )
