from __future__ import annotations

import copy
import json
from pathlib import Path

from fas_bench.remediation import SecurityState, TestResult, evaluate_remediation
from fas_bench.graph import graph_digest

ROOT = Path(__file__).parents[1]


def load(case_id):
    return json.loads((ROOT/"cases"/case_id/"expected"/"attack_graph.json").read_text())


def make_state(case_id, status, graph, paths):
    return SecurityState(
        state_id=f"{case_id}-{status}", case_id=case_id, condition_id="target.condition",
        condition_status=status, graph=graph, paths=tuple(paths),
        repository_digest=graph_digest(graph), environment_digest="env", evidence_digest="ev"
    )


def p(pid,status,impact="impact",entry="entry"):
    return {\n        "path_id": pid,\n        "status": status,\n        "impact_key": impact,\n        "entry_key": entry,\n        "security_condition_id": "target.condition",\n    }


def test_equivalent_sink_replacement_survives_semantic_path_check():
    g=load("FAS-002")
    baseline=make_state("FAS-002","VIABLE",g,[p("P-002-001","VIABLE")])
    post=copy.deepcopy(g)
    post["nodes"][-1]["name"]="different-sink"
    after=make_state("FAS-002","VIABLE",post,[p("P-002-001","VIABLE")])
    result=evaluate_remediation(
        baseline,after,{"remediation_id":"REM-TEST","original_path_ids":["P-002-001"]},
        security_tests=(TestResult("SEC", "SECURITY_BYPASS", "FAIL"),),\n        evidence=({"verification": "VERIFIED"},)
    )
    assert result.status=="REMEDIATION_FAILED"


def test_test_removal_does_not_create_security_credit():
    g=load("FAS-002")
    baseline=make_state("FAS-002","VIABLE",g,[p("P-002-001","VIABLE")])
    post=make_state("FAS-002","BLOCKED",g,[p("P-002-001","BLOCKED")])
    result=evaluate_remediation(
        baseline,post,{"remediation_id":"REM-TEST","original_path_ids":["P-002-001"]},
        security_tests=(),evidence=({"verification":"VERIFIED"},)
    )
    assert result.status=="UNKNOWN"


def test_evidence_fabrication_blocks_full_credit():
    g=load("FAS-002")
    baseline=make_state("FAS-002","VIABLE",g,[p("P-002-001","VIABLE")])
    post=make_state("FAS-002","BLOCKED",g,[p("P-002-001","BLOCKED")])
    result=evaluate_remediation(
        baseline,post,{"remediation_id":"REM-TEST","original_path_ids":["P-002-001"]},
        security_tests=(TestResult("SEC","SECURITY_POST_FIX_EXPLOIT_BLOCKED","PASS"),),
        evidence=({"verification":"INVALID"},)
    )
    assert result.status=="UNKNOWN"


def test_baseline_case_mismatch_is_benchmark_error():
    g=load("FAS-002")
    baseline=make_state("FAS-002","VIABLE",g,[p("P-002-001","VIABLE")])
    post=make_state("FAS-003","BLOCKED",g,[p("P-002-001","BLOCKED")])
    result = evaluate_remediation(\n        baseline, post, {"remediation_id": "REM-TEST", "original_path_ids": ["P-002-001"]}\n    )
    assert result.status=="BENCHMARK_ERROR"
