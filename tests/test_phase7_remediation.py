from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from fas_bench.graph import graph_digest
from fas_bench.remediation import (
    SecurityState,
    TestResult,
    evaluate_regression,
    evaluate_remediation,
)

ROOT = Path(__file__).parents[1]
CASES = ROOT / "cases"


def graph(case_id: str) -> dict:
    return json.loads(
        (CASES / case_id / "expected" / "attack_graph.json").read_text(encoding="utf-8")
    )


def remediation(case_id: str) -> dict:
    return json.loads(
        (CASES / case_id / "expected" / "remediation.json").read_text(encoding="utf-8")
    )


def state(
    case_id: str, status: str, graph_doc: dict, paths: list[dict], controls=None
) -> SecurityState:
    return SecurityState(
        state_id=f"{case_id}-{status}",
        case_id=case_id,
        condition_id=f"condition.{case_id}",
        condition_status=status,
        graph=graph_doc,
        paths=tuple(paths),
        controls=tuple(controls or ()),
        repository_digest=graph_digest(graph_doc),
        environment_digest="env-test",
        evidence_digest="evidence-test",
    )


def path(pid: str, status: str, impact: str = "impact", entry: str = "attacker") -> dict:
    return {
        "path_id": pid,
        "status": status,
        "impact_key": impact,
        "entry_key": entry,
        "security_condition_id": "condition.TEST",
    }


def test_complete_fix_requires_verified_evidence_and_functional_preservation():
    g = graph("FAS-019")
    baseline = state("FAS-019", "VIABLE", g, [path("P-019-001", "VIABLE")])
    post = state(
        "FAS-019",
        "BLOCKED",
        g,
        [path("P-019-001", "BLOCKED")],
        [{"control_id": "sig", "effective": True}],
    )
    result = evaluate_remediation(
        baseline,
        post,
        remediation("FAS-019"),
        security_tests=(
            TestResult("SEC-1", "SECURITY_POST_FIX_EXPLOIT_BLOCKED", "PASS"),
        ),
        functional_tests=(
            TestResult("FUN-1", "FUNCTIONAL_LEGITIMATE_BEHAVIOR", "PASS"),
        ),
        evidence=({"verification": "VERIFIED"},),
    )
    assert result.status == "REMEDIATED"
    assert result.path_status == "REMOVED"
    assert result.score == pytest.approx(1.0)


def test_fas020_alternate_path_invalidates_known_path_fix():
    g = graph("FAS-020")
    post = copy.deepcopy(g)
    post["paths"].append(
        {
            "path_id": "P-020-alt",
            "node_ids": list(g["paths"][0]["node_ids"]),
            "edge_ids": list(g["paths"][0]["edge_ids"]),
            "entry_node": g["paths"][0]["entry_node"],
            "impact_node": g["paths"][0]["impact_node"],
            "status": "VIABLE",
            "evidence_ids": ["EVD-020-001"],
            "impact_key": "impact",
            "entry_key": "alternate",
        }
    )
    baseline = state("FAS-020", "VIABLE", g, [path("P-020-001", "VIABLE")])
    post_paths = [
        path("P-020-001", "BLOCKED"),
        path("P-020-alt", "VIABLE", entry="alternate"),
    ]
    post_state = state("FAS-020", "BLOCKED", post, post_paths)
    result = evaluate_remediation(
        baseline,
        post_state,
        remediation("FAS-020"),
        security_tests=(
            TestResult("SEC-1", "SECURITY_POST_FIX_EXPLOIT_BLOCKED", "PASS"),
        ),
        functional_tests=(
            TestResult("FUN-1", "FUNCTIONAL_LEGITIMATE_BEHAVIOR", "PASS"),
        ),
        evidence=({"verification": "VERIFIED"},),
    )
    assert result.status == "REMEDIATION_FAILED"
    assert result.alternate_path_status == "REMAINS"
    assert any(
        x.classification == "EQUIVALENT_IMPACT" for x in result.alternate_paths
    )


def test_cosmetic_fix_is_not_remediation():
    g = graph("FAS-002")
    baseline = state("FAS-002", "VIABLE", g, [path("P-002-001", "VIABLE")])
    post = copy.deepcopy(g)
    post["metadata"] = {"case_id": "FAS-002", "change": "variable rename"}
    post_state = state(
        "FAS-002", "VIABLE", post, [path("P-002-001", "VIABLE")]
    )
    result = evaluate_remediation(
        baseline,
        post_state,
        remediation("FAS-002"),
        security_tests=(
            TestResult("SEC-1", "SECURITY_POST_FIX_EXPLOIT_BLOCKED", "FAIL"),
        ),
        evidence=({"verification": "VERIFIED"},),
    )
    assert result.status == "REMEDIATION_FAILED"
    assert any(x.lifecycle == "PERSISTING" for x in result.path_lifecycles)


def test_overblocking_requires_functional_preservation():
    g = graph("FAS-019")
    baseline = state("FAS-019", "VIABLE", g, [path("P-019-001", "VIABLE")])
    post = state("FAS-019", "BLOCKED", g, [path("P-019-001", "BLOCKED")])
    result = evaluate_remediation(
        baseline,
        post,
        remediation("FAS-019"),
        security_tests=(
            TestResult("SEC-1", "SECURITY_POST_FIX_EXPLOIT_BLOCKED", "PASS"),
        ),
        functional_tests=(
            TestResult("FUN-1", "FUNCTIONAL_LEGITIMATE_BEHAVIOR", "FAIL"),
        ),
        evidence=({"verification": "VERIFIED"},),
    )
    assert result.status == "REMEDIATION_FAILED"


def test_unknown_is_not_remediated():
    g = graph("FAS-019")
    baseline = state("FAS-019", "VIABLE", g, [path("P-019-001", "VIABLE")])
    post = state("FAS-019", "BLOCKED", g, [path("P-019-001", "BLOCKED")])
    result = evaluate_remediation(
        baseline,
        post,
        remediation("FAS-019"),
        security_tests=(
            TestResult("SEC-1", "SECURITY_POST_FIX_EXPLOIT_BLOCKED", "UNRESOLVED"),
        ),
        evidence=({"verification": "UNRESOLVED"},),
    )
    assert result.status == "UNKNOWN"


def test_regression_detects_reopened_condition_and_weakened_control():
    g = graph("FAS-019")
    secure = state(
        "FAS-019",
        "BLOCKED",
        g,
        [path("P-019-001", "BLOCKED")],
        [{"control_id": "sig", "effective": True}],
    )
    regressed = state(
        "FAS-019",
        "VIABLE",
        g,
        [path("P-019-001", "VIABLE")],
        [{"control_id": "sig", "effective": False}],
    )
    result = evaluate_regression(secure, regressed)
    assert result["status"] == "REGRESSED"


def test_secure_refactor_is_not_regression():
    g = graph("FAS-019")
    secure = state(
        "FAS-019",
        "BLOCKED",
        g,
        [path("P-019-001", "BLOCKED")],
        [{"control_id": "sig", "effective": True}],
    )
    refactored = copy.deepcopy(g)
    refactored["nodes"][0]["name"] = "external-caller"
    current = state(
        "FAS-019",
        "BLOCKED",
        refactored,
        [path("P-019-001", "BLOCKED")],
        [{"control_id": "sig", "effective": True}],
    )
    result = evaluate_regression(secure, current)
    assert result["status"] == "NOT_REGRESSED"


def test_artifact_ordering_does_not_change_run_identity_or_graph_digest():
    g = graph("FAS-019")
    reordered = copy.deepcopy(g)
    reordered["nodes"].reverse()
    reordered["edges"].reverse()
    assert graph_digest(g) == graph_digest(reordered)


@pytest.mark.parametrize("number", range(1, 21))
def test_all_twenty_remediation_artifacts_are_loadable(number: int):
    case_id = f"FAS-{number:03d}"
    data = remediation(case_id)
    assert data["remediation_id"].startswith("REM-")
    assert data["original_path_ids"]
    assert data["verification_status"] in {
        "NOT_ASSESSED",
        "PROPOSED",
        "APPLIED",
        "VERIFIED",
        "FAILED",
        "PARTIAL",
    }
