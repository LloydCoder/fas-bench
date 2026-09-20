from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from fas_bench.evidence import load_case
from fas_bench.evaluator import (
    evaluate_submission_document,
    resolve_security_condition,
)
from fas_bench.evaluator.errors import EvaluatorCaseError, EvaluatorSubmissionError
from fas_bench.validation import validate

ROOT = Path(__file__).parents[1]
CASES = ROOT / "cases"


def _gold_submission(case_id: str) -> dict:
    case = load_case(case_id, CASES)
    expected = case["root"] / "expected"
    claims = json.loads((expected / "claims.json").read_text(encoding="utf-8"))
    evidence = json.loads((expected / "evidence.json").read_text(encoding="utf-8"))
    finding = json.loads((expected / "findings.json").read_text(encoding="utf-8"))
    verdict = json.loads((expected / "verdict.json").read_text(encoding="utf-8"))
    graph = json.loads((expected / "attack_graph.json").read_text(encoding="utf-8"))
    remediation = json.loads((expected / "remediation.json").read_text(encoding="utf-8"))
    return {
        "benchmark_version": "0.1.0",
        "schema_version": "0.1",
        "submission_id": f"SUB-{case_id}",
        "case_id": case_id,
        "system": {"system_name": "Synthetic-System", "system_version": "1"},
        "verdict": verdict,
        "findings": [finding],
        "claims": [claims],
        "evidence": [evidence],
        "attack_paths": graph["paths"],
        "impact": {},
        "remediation": remediation,
        "verification": None,
    }


@pytest.mark.parametrize("number", range(1, 21))
def test_every_gold_case_self_evaluates(number: int):
    case_id = f"FAS-{number:03d}"
    result = evaluate_submission_document(_gold_submission(case_id), CASES)
    expected = json.loads((CASES / case_id / "expected/verdict.json").read_text(encoding="utf-8"))[
        "verdict"
    ]
    assert result.verdict.expected == expected
    assert result.verdict.verdict_correct
    assert result.verdict.verdict_supported
    assert result.finding.matched
    assert all(claim.status == "VERIFIED" for claim in result.claims)
    schema_result = validate(result.as_dict(), "evaluation-result")
    assert schema_result.status == "VALID", schema_result.errors


def test_expected_verdicts_are_derived_from_case_semantics():
    expected = {}
    for number in range(1, 21):
        case_id = f"FAS-{number:03d}"
        case = load_case(case_id, CASES)
        ground = {
            "claims": [
                json.loads((case["root"] / "expected/claims.json").read_text(encoding="utf-8"))
            ],
            "verdict": json.loads(
                (case["root"] / "expected/verdict.json").read_text(encoding="utf-8")
            ),
            "graph": json.loads(
                (case["root"] / "expected/attack_graph.json").read_text(encoding="utf-8")
            ),
            "remediation": json.loads(
                (case["root"] / "expected/remediation.json").read_text(encoding="utf-8")
            ),
        }
        condition = resolve_security_condition(case, ground)
        expected[case_id] = (condition.path_status, condition.effective_control_state)
    assert expected["FAS-001"] == ("BLOCKED", "EFFECTIVE")
    assert expected["FAS-002"] == ("VIABLE", "INEFFECTIVE_OR_BYPASSED")
    assert expected["FAS-020"] == ("VIABLE", "INEFFECTIVE_OR_BYPASSED")


def test_correct_verdict_without_evidence_is_not_fully_supported():
    submission = _gold_submission("FAS-002")
    submission["claims"][0]["related_evidence"] = []
    submission["findings"][0]["claim_ids"] = [submission["claims"][0]["claim_id"]]
    submission["evidence"] = []
    submission["verdict"]["evidence_ids"] = []
    result = evaluate_submission_document(submission, CASES)
    assert result.verdict.verdict_correct
    assert not result.verdict.verdict_supported
    assert result.evidence["missing_expected_evidence_count"] == 1


def test_correct_verdict_with_fabricated_evidence_is_not_fully_supported():
    submission = _gold_submission("FAS-002")
    submission["evidence"][0]["fact"] = dict(submission["evidence"][0]["fact"])
    submission["evidence"][0]["fact"]["value"] = "fabricated"
    result = evaluate_submission_document(submission, CASES)
    assert result.verdict.verdict_correct
    assert not result.verdict.verdict_supported
    assert result.evidence["invalid_evidence_count"] == 1


def test_wrong_verdict_with_correct_evidence_is_verdict_incorrect():
    submission = _gold_submission("FAS-002")
    submission["verdict"]["verdict"] = "NOT_EXPLOITABLE"
    result = evaluate_submission_document(submission, CASES)
    assert not result.verdict.verdict_correct
    assert result.evidence["verified_evidence_count"] == 1
    assert result.verdict.reason_code == "VERDICT_INCORRECT"


def test_false_positive_case_is_not_exploitable():
    result = evaluate_submission_document(_gold_submission("FAS-001"), CASES)
    assert result.verdict.expected == "NOT_EXPLOITABLE"
    assert result.verdict.verdict_supported


def test_conditional_case_preserves_explicit_precondition():
    result = evaluate_submission_document(_gold_submission("FAS-008"), CASES)
    assert result.verdict.expected == "CONDITIONALLY_EXPLOITABLE"
    assert result.security_condition.required_conditions
    assert result.security_condition.satisfied_conditions
    assert result.verdict.verdict_supported


@pytest.mark.parametrize(
    ("case_id", "expected"),
    [
        ("FAS-013", "REMEDIATED"),
        ("FAS-019", "REMEDIATED"),
        ("FAS-020", "REMEDIATION_FAILED"),
        ("FAS-012", "UNKNOWN"),
    ],
)
def test_remediation_and_unknown_semantics(case_id: str, expected: str):
    result = evaluate_submission_document(_gold_submission(case_id), CASES)
    assert result.verdict.expected == expected
    assert result.verdict.verdict_correct
    assert result.verdict.verdict_supported


def test_evidence_order_and_claim_order_do_not_change_verdict_or_fingerprint():
    submission = _gold_submission("FAS-004")
    first = evaluate_submission_document(copy.deepcopy(submission), CASES)
    reordered = copy.deepcopy(submission)
    reordered["claims"] = list(reversed(reordered["claims"]))
    reordered["evidence"] = list(reversed(reordered["evidence"]))
    reordered["findings"] = list(reversed(reordered["findings"]))
    second = evaluate_submission_document(reordered, CASES)
    assert first.verdict.as_dict() == second.verdict.as_dict()
    assert first.fingerprint == second.fingerprint


def test_finding_title_is_not_authoritative():
    submission = _gold_submission("FAS-006")
    first = evaluate_submission_document(copy.deepcopy(submission), CASES)
    submission["findings"][0]["title"] = "Completely different wording"
    second = evaluate_submission_document(submission, CASES)
    assert second.finding.matched
    assert second.verdict.verdict_correct
    assert first.fingerprint == second.fingerprint


def test_irrelevant_unknown_evidence_does_not_change_verdict():
    submission = _gold_submission("FAS-002")
    extra = copy.deepcopy(submission["evidence"][0])
    extra["evidence_id"] = "EVD-UNKNOWN"
    extra["fact"] = dict(extra["fact"])
    extra["fact"]["key"] = "not_expected"
    submission["evidence"].append(extra)
    result = evaluate_submission_document(submission, CASES)
    assert result.verdict.verdict_correct
    assert result.verdict.verdict_supported
    assert result.evidence["invalid_evidence_count"] == 1


def test_duplicate_evidence_cannot_inflate_support():
    submission = _gold_submission("FAS-002")
    duplicate = copy.deepcopy(submission["evidence"][0])
    duplicate["evidence_id"] = "EVD-002-DUP"
    submission["evidence"].append(duplicate)
    result = evaluate_submission_document(submission, CASES)
    assert result.verdict.verdict_supported
    assert result.evidence["duplicate_evidence_count"] == 1
    assert result.evidence["verified_evidence_count"] == 1


def test_contradictory_claims_block_full_verdict_support():
    submission = _gold_submission("FAS-002")
    contradictory = copy.deepcopy(submission["claims"][0])
    contradictory["claim_id"] = "CLM-002-CONTRADICT"
    contradictory["object"] = "The path is blocked"
    submission["claims"].append(contradictory)
    submission["verdict"]["claim_ids"].append(contradictory["claim_id"])
    result = evaluate_submission_document(submission, CASES)
    assert any(claim.status == "CONTRADICTED" for claim in result.claims)
    assert not result.verdict.verdict_supported


def test_cross_case_evidence_cannot_verify():
    submission = _gold_submission("FAS-001")
    submission["evidence"][0]["fact"] = dict(submission["evidence"][0]["fact"])
    submission["evidence"][0]["fact"]["artifact_path"] = "repository/state.json"
    submission["evidence"][0]["fact"]["value"] = "wrong-case-state"
    result = evaluate_submission_document(submission, CASES)
    assert result.evidence["verified_evidence_count"] == 0
    assert not result.verdict.verdict_supported


def test_wrong_case_id_is_rejected():
    submission = _gold_submission("FAS-001")
    submission["case_id"] = "FAS-002"
    with pytest.raises(EvaluatorCaseError):
        evaluate_submission_document(submission, CASES)


def test_confidence_nan_is_rejected():
    submission = _gold_submission("FAS-002")
    submission["verdict"]["confidence"] = math.nan
    with pytest.raises(EvaluatorSubmissionError):
        evaluate_submission_document(submission, CASES)


def test_authoritative_case_tampering_is_blocked(tmp_path: Path):
    import shutil

    copied = tmp_path / "cases"
    shutil.copytree(CASES, copied)
    state = copied / "FAS-002/repository/state.json"
    value = json.loads(state.read_text(encoding="utf-8"))
    value["security_condition"] = "tampered"
    state.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(Exception) as exc:
        evaluate_submission_document(_gold_submission("FAS-002"), copied)
    assert "integrity" in str(exc.value).lower()


def test_phase5_output_is_deterministic_and_scoring_is_deferred():
    result = evaluate_submission_document(_gold_submission("FAS-002"), CASES)
    payload = result.as_dict()
    assert payload["evaluation_phase"] == "PHASE_5_VERDICT"
    assert "final_score" not in payload
    assert payload["metadata"]["scoring_deferred_to_phase_8"] is True


def test_benchmark_package_has_no_fas_dependency():
    source = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in (ROOT / "src" / "fas_bench" / "evaluator").glob("*.py")
    )
    assert "threatfade" not in source
    assert "tinlance" not in source
    assert "import fas" not in source
