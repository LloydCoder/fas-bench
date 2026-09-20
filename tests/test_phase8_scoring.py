"""Phase 8 scoring and calibration tests."""

import pytest
from fas_bench.scoring.metrics import (
    binary_metrics,
    evidence_score,
    brier_score,
    expected_calibration_error,
    multiclass_brier,
)


def test_binary_metrics_known_values():
    m = binary_metrics(8, 2, 2)
    assert m["precision"] == 0.8
    assert m["recall"] == 0.8
    assert m["f1"] == 0.8


def test_evidence_weighted_formula():
    assert evidence_score(
        1, 0.5, 0.5, 1, {"validity": 0.35, "relevance": 0.30, "coverage": 0.20, "specificity": 0.15}
    ) == pytest.approx(0.8)


def test_brier_direction_and_extremes():
    assert brier_score([1], [True]) == 0
    assert brier_score([1], [False]) == 1


def test_ece_boundary_and_empty_bins():
    r = expected_calibration_error([0, 0.5, 1], [False, True, True], 2)
    assert r["bins"][0]["count"] == 1
    assert r["bins"][1]["count"] == 2
    assert 0 <= r["ece"] <= 1


@pytest.mark.parametrize("value", [-0.1, 1.1, float("nan"), float("inf")])
def test_invalid_confidence(value):
    with pytest.raises(ValueError):
        brier_score([value], [True])


def test_multiclass_brier():
    assert multiclass_brier([{"A": 1.0, "B": 0.0}], ["A"]) == 0
    with pytest.raises(ValueError):
        multiclass_brier([{"A": 0.8, "B": 0.3}], ["A"])
