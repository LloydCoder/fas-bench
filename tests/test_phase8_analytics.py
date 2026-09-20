"""Phase 8 analytics, reproducibility, adversarial and metamorphic tests."""

import json
from fas_bench.analytics import aggregate_cases, bootstrap, leave_one_out
from fas_bench.reporting import canonical_json, digest


def rows():
    return [
        {
            "case_id": "FAS-001",
            "case_score": 1.0,
            "verdict_correct": True,
            "category": "C1",
            "difficulty": "L1",
        },
        {
            "case_id": "FAS-002",
            "case_score": 0.5,
            "verdict_correct": False,
            "category": "C1",
            "difficulty": "L2",
        },
        {
            "case_id": "FAS-003",
            "case_score": 0.0,
            "verdict_correct": False,
            "category": "C2",
            "difficulty": "L3",
        },
    ]


def test_macro_micro_and_strata():
    a = aggregate_cases(rows())
    assert a["n_cases"] == 3
    assert a["macro_case_score"] == 0.5
    assert a["verdict_accuracy"]["accuracy"] == 1 / 3
    assert a["stratification"]["category"]["C1"]["n"] == 2


def test_bootstrap_determinism():
    a = bootstrap([0, 1, 0.5], n_resamples=100, seed=7)
    b = bootstrap([0, 1, 0.5], n_resamples=100, seed=7)
    assert a == b


def test_bootstrap_rejects_nonfinite():
    import pytest

    with pytest.raises(ValueError):
        bootstrap([1, float("nan")])


def test_leave_one_out():
    r = leave_one_out(rows())
    assert len(r) == 3
    assert r[0]["case_id"] == "FAS-001"


def test_canonical_serialization_and_hash_stability():
    value = {"b": 1, "a": [2, {"z": 3}]}
    assert canonical_json(value) == canonical_json(json.loads(canonical_json(value)))
    assert digest(value) == digest(json.loads(canonical_json(value)))


def test_case_order_invariance():
    a = aggregate_cases(rows())
    b = aggregate_cases(list(reversed(rows())))
    assert a == b


def test_score_decomposition_invariants():
    from fas_bench.scoring import ScoreComponent

    c = ScoreComponent("x", 0.8, 0.2, True, 0.16)
    assert c.as_dict()["contribution"] == 0.16
