# ruff: noqa: I001

from fas_bench.verification import (
    independent_corpus_contract_check,
    independent_full_contract_check,
    independent_scoring_contract_check,
    independent_security_check,
)
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_independent_security_check_does_not_use_production_helpers():
    result = independent_security_check(ROOT)
    assert result["status"] == "PASS", result


def test_independent_corpus_contract_is_green():
    result = independent_corpus_contract_check(ROOT)
    assert result["status"] == "PASS", result


def test_independent_scoring_contract_is_green():
    result = independent_scoring_contract_check(ROOT)
    assert result["status"] == "PASS", result


def test_full_independent_contract_is_green():
    result = independent_full_contract_check(ROOT)
    assert result["status"] == "PASS", result
