from __future__ import annotations

import json
from pathlib import Path

import pytest

from fas_bench.evidence import (
    calculate_coverage,
    calculate_integrity,
    evidence_identity,
    load_case,
    load_submission,
    normalize_evidence,
    verify_evidence,
)
from fas_bench.evidence.errors import CaseLoadError

ROOT = Path(__file__).parents[1]
CASES = ROOT / "cases"


def test_all_twenty_gold_evidence_records_verify():
    for number in range(1, 21):
        case_id = f"FAS-{number:03d}"
        case = load_case(case_id, CASES)
        result = verify_evidence(case, case["expected_evidence"])
        assert result.verified == 1, (case_id, result.as_dict())
        assert result.invalid == 0, (case_id, result.as_dict())
        assert result.unresolved == 0, (case_id, result.as_dict())
        assert result.missing_expected == 0, (case_id, result.as_dict())
        assert result.coverage == 1.0, (case_id, result.as_dict())


def test_evidence_identity_is_order_and_key_order_invariant():
    first = {
        "evidence_id": "EVD-001",
        "type": "SOURCE_LOCATION",
        "role": "DIRECT",
        "verification": "VERIFIED",
        "description": "x",
        "location": {"file": "./repository/app.py", "line_start": 2, "line_end": 2},
        "related_claims": ["CLM-2", "CLM-1"],
    }
    second = {
        "description": "x",
        "related_claims": ["CLM-1", "CLM-2"],
        "verification": "VERIFIED",
        "role": "DIRECT",
        "type": "SOURCE_LOCATION",
        "evidence_id": "EVD-999",
        "location": {"line_end": 2, "line_start": 2, "file": "repository/app.py"},
    }
    assert evidence_identity(first) == evidence_identity(second)
    first["description"] = "different prose"
    first["verification"] = "INVALID"
    first["observed_at"] = "2026-09-20T00:00:00Z"
    assert evidence_identity(first) == evidence_identity(second)
    assert normalize_evidence(first)["location"]["file"] == "repository/app.py"


def test_material_location_change_changes_identity():
    evidence = {
        "evidence_id": "EVD-001",
        "type": "SOURCE_LOCATION",
        "role": "DIRECT",
        "verification": "VERIFIED",
        "description": "x",
        "location": {"file": "repository/app.py", "line_start": 2, "line_end": 2},
    }
    changed = dict(evidence)
    changed["location"] = {"file": "repository/app.py", "line_start": 3, "line_end": 3}
    assert evidence_identity(evidence) != evidence_identity(changed)


def test_path_traversal_is_rejected():
    case = load_case("FAS-001", CASES)
    submission = dict(case["expected_evidence"][0])
    submission["location"] = dict(submission["location"])
    submission["location"]["file"] = "../outside.json"
    result = verify_evidence(case, [submission])
    assert result.invalid == 1
    assert result.items[0].reason_code == "EVIDENCE_INVALID_PATH"


def test_wrong_fact_is_rejected():
    case = load_case("FAS-001", CASES)
    submission = dict(case["expected_evidence"][0])
    submission["fact"] = dict(submission["fact"])
    submission["fact"]["value"] = True
    result = verify_evidence(case, [submission])
    assert result.invalid == 1
    assert result.items[0].reason_code == "EVIDENCE_VALUE_MISMATCH"


def test_cross_case_fact_cannot_verify():
    case = load_case("FAS-001", CASES)
    submission = dict(case["expected_evidence"][0])
    submission["fact"] = dict(submission["fact"])
    submission["fact"]["artifact_path"] = "cases/FAS-002/repository/state.json"
    result = verify_evidence(case, [submission])
    assert result.invalid == 1


def test_duplicate_evidence_does_not_inflate_counts():
    case = load_case("FAS-001", CASES)
    evidence = case["expected_evidence"][0]
    duplicate = dict(evidence)
    duplicate["evidence_id"] = "EVD-001-DUP"
    result = verify_evidence(case, [evidence, duplicate])
    assert result.verified == 1
    assert result.duplicate == 1
    assert result.invalid == 1


def test_missing_evidence_is_distinct_from_invalid():
    case = load_case("FAS-001", CASES)
    result = verify_evidence(case, [])
    assert result.submitted == 0
    assert result.missing_expected == 1
    assert result.invalid == 0
    assert result.evidence_hallucination_rate == 0.0


def test_integrity_zero_evidence_is_safe():
    assert calculate_integrity(0, 0)["evidence_hallucination_rate"] == 0.0


def test_coverage_requires_expected_evidence():
    expected = [{"evidence_id": "EVD-1", "role": "DIRECT"}]
    assert calculate_coverage(expected, [], set()) == 0.0
    assert calculate_coverage(expected, [], {"EVD-1"}) == 1.0


@pytest.mark.parametrize("number", range(1, 21))
def test_expected_fact_is_real_case_state(number: int):
    case_id = f"FAS-{number:03d}"
    evidence = json.loads((CASES / case_id / "expected/evidence.json").read_text(encoding="utf-8"))
    fact = evidence["fact"]
    state = json.loads((CASES / case_id / fact["artifact_path"]).read_text(encoding="utf-8"))
    assert state[fact["key"]] == fact["value"]


def test_relationship_mutation_is_rejected():
    case = load_case("FAS-001", CASES)
    submission = dict(case["expected_evidence"][0])
    submission["related_claims"] = ["CLM-not-the-gold-claim"]
    result = verify_evidence(case, [submission])
    assert result.invalid == 1
    assert result.items[0].reason_code == "EVIDENCE_RELATIONSHIP_MISMATCH"


def test_absolute_and_nul_paths_are_rejected(tmp_path: Path):
    from fas_bench.evidence.resolver import safe_resolve

    with pytest.raises(CaseLoadError):
        safe_resolve(tmp_path, "/etc/passwd")
    with pytest.raises(CaseLoadError):
        safe_resolve(tmp_path, "bad\\x00path")


def test_symlink_escape_is_rejected(tmp_path: Path):
    root = tmp_path / "case"
    outside = tmp_path / "outside.txt"
    root.mkdir()
    outside.write_text("secret", encoding="utf-8")
    link = root / "escape.txt"
    link.symlink_to(outside)
    with pytest.raises(CaseLoadError):
        from fas_bench.evidence.resolver import safe_resolve
        safe_resolve(root, "escape.txt")


def test_malformed_submission_is_rejected(tmp_path: Path):
    path = tmp_path / "submission.json"
    path.write_text("{not-json", encoding="utf-8")
    with pytest.raises(Exception):
        load_submission(path)


def test_benchmark_package_has_no_evaluated-system_dependency():
    source = "\\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in (ROOT / "src" / "fas_bench" / "evidence").glob("*.py")
    )
    assert "threatfade" not in source
    assert "tinlance" not in source
    assert "import fas" not in source
