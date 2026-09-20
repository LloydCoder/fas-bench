# fmt: off
# ruff: noqa: E501,UP035,UP037
from pathlib import Path

import pytest

from fas_bench.contract import CASE_IDS
from fas_bench.mutations import formatting_mutation, mutation_valid, rename_identifiers
from fas_bench.phase10 import (
    CaseLifecycle,
    LifecycleError,
    benchmark_health,
    build_release_manifest,
    canonical_json,
    corpus_stats,
    digest_tree,
    eligibility,
    scan_leakage,
    validate_case_phase10,
    validate_corpus,
    validate_release_manifest,
)

ROOT = Path(__file__).resolve().parents[1]


def test_phase10_validates_all_initial_cases():
    result = validate_corpus()
    assert result["status"] == "PASS"
    assert result["case_count"] == 20
    assert result["valid_count"] == 20
    assert result["errors"] == []


def test_phase10_case_records_are_content_addressed():
    result = validate_case_phase10("FAS-001")
    assert len(result["case_digest"]) == 64
    assert len(result["repository_digest"]) == 64


def test_lifecycle_rejects_illegal_transition():
    lifecycle = CaseLifecycle("FAS-001", "DRAFT")
    with pytest.raises(LifecycleError):
        lifecycle.transition("RELEASED")
    assert lifecycle.transition("AUTHOR_VALIDATION").state == "AUTHOR_VALIDATION"


def test_canonical_json_is_order_invariant():
    assert canonical_json({"b": 2, "a": 1}) == canonical_json({"a": 1, "b": 2})


def test_digest_changes_with_content(tmp_path):
    path = tmp_path / "x.txt"
    path.write_text("a", encoding="utf-8")
    first = digest_tree(tmp_path)
    path.write_text("b", encoding="utf-8")
    assert first != digest_tree(tmp_path)


def test_identifier_mutation_preserves_python_tokens():
    source = "user_input = 1\nprint(user_input)\n"
    mutated = rename_identifiers(source, {"user_input": "renamed_value"})
    assert "renamed_value" in mutated
    assert "user_input" not in mutated
    assert mutation_valid(source, mutated)


def test_formatting_mutation_preserves_ast():
    source = "x=1\nprint(x)\n"
    assert mutation_valid(source, formatting_mutation(source))


def test_stats_are_explicitly_nonrepresentative():
    stats = corpus_stats()
    assert stats["case_count"] == 20
    assert stats["statistical_representativeness_claim"] is False


def test_leakage_scanner_detects_forbidden_material(tmp_path):
    (tmp_path / ".env").write_text("x", encoding="utf-8")
    result = scan_leakage(tmp_path)
    assert result["status"] == "FAIL"
    assert result["findings"][0]["type"] == "FORBIDDEN_PATH"


def test_eligibility_never_converts_infrastructure_failure_to_verdict():
    assert eligibility(integrity_ok=True, infrastructure_ok=False, reproducible=True) == "INFRASTRUCTURE_FAILURE"
    assert eligibility(integrity_ok=False, infrastructure_ok=True, reproducible=True) == "INTEGRITY_FAILURE"


def test_release_manifest_is_content_addressed():
    manifest = build_release_manifest(ROOT, "0.1.0-phase10-dev")
    assert len(manifest["release_digest"]) == 64
    assert manifest["case_ids"] == list(CASE_IDS)
    result = validate_release_manifest(ROOT, manifest)
    assert result["status"] == "PASS", result["errors"]


def test_health_does_not_overclaim():
    health = benchmark_health(ROOT)
    assert health["corpus_validity"] == "PASS"
    assert health["statistical_representativeness_claim"] is False
