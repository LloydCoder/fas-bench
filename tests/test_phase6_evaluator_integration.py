from __future__ import annotations

import copy
import json
from pathlib import Path

from fas_bench.evaluator import evaluate_submission_document
from fas_bench.evidence import load_case

ROOT = Path(__file__).parents[1]
CASES = ROOT / "cases"


def test_phase5_result_can_carry_phase6_graph_evaluation():
    case_id = "FAS-002"
    case = load_case(case_id, CASES)
    expected = case["root"] / "expected"
    submission = {
        "benchmark_version": "0.1.0",
        "schema_version": "0.1",
        "submission_id": "SUB-PHASE6-INTEGRATION",
        "case_id": case_id,
        "system": {"system_name": "Phase6Integration"},
        "verdict": json.loads((expected / "verdict.json").read_text(encoding="utf-8")),
        "findings": [json.loads((expected / "findings.json").read_text(encoding="utf-8"))],
        "claims": [json.loads((expected / "claims.json").read_text(encoding="utf-8"))],
        "evidence": [json.loads((expected / "evidence.json").read_text(encoding="utf-8"))],
        "attack_paths": [json.loads((expected / "attack_paths.json").read_text(encoding="utf-8"))],
        "attack_graph": json.loads((expected / "attack_graph.json").read_text(encoding="utf-8")),
        "impact": {},
        "remediation": json.loads((expected / "remediation.json").read_text(encoding="utf-8")),
        "verification": None,
    }
    result = evaluate_submission_document(submission, CASES)
    assert result.graph is not None
    assert result.graph["valid"] is True
    assert result.graph["graph_score"] == 1.0
    assert len(result.graph["unsupported_edges"]) == 0


def test_graph_evidence_linkage_is_score_relevant():
    case_id = "FAS-002"
    case = load_case(case_id, CASES)
    expected = case["root"] / "expected"
    submission = {
        "benchmark_version": "0.1.0",
        "schema_version": "0.1",
        "submission_id": "SUB-PHASE6-FABRICATED",
        "case_id": case_id,
        "system": {"system_name": "Phase6Integration"},
        "verdict": json.loads((expected / "verdict.json").read_text(encoding="utf-8")),
        "findings": [json.loads((expected / "findings.json").read_text(encoding="utf-8"))],
        "claims": [json.loads((expected / "claims.json").read_text(encoding="utf-8"))],
        "evidence": [json.loads((expected / "evidence.json").read_text(encoding="utf-8"))],
        "attack_paths": [json.loads((expected / "attack_paths.json").read_text(encoding="utf-8"))],
        "attack_graph": json.loads((expected / "attack_graph.json").read_text(encoding="utf-8")),
        "impact": {},
        "remediation": json.loads((expected / "remediation.json").read_text(encoding="utf-8")),
        "verification": None,
    }
    submission["attack_graph"] = copy.deepcopy(submission["attack_graph"])
    submission["attack_graph"]["edges"].append(
        {
            "edge_id": "E-002-FABRICATED",
            "type": "AUTHENTICATES_AS",
            "source": "N-002-input",
            "target": "N-002-impact",
            "evidence_ids": ["EVD-002-001"],
        }
    )
    result = evaluate_submission_document(submission, CASES)
    assert "E-002-FABRICATED" in result.graph["unsupported_edges"]
    assert result.graph["graph_score"] < 1.0
