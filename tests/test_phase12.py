from fas_bench.phase12 import (
    EvaluationRow,
    benchmark_accuracy,
    bootstrap_accuracy_interval,
    calibration_error,
    phase12_report,
    wilson_interval,
)


def _rows():
    return [
        EvaluationRow("system-a", "FAS-001", "CORRECT", "L1", 0.9),
        EvaluationRow("system-a", "FAS-002", "INCORRECT", "L2", 0.6),
        EvaluationRow("system-a", "FAS-003", "CORRECT", "L2", 0.8),
        EvaluationRow("system-a", "FAS-004", "CORRECT", "L3", 0.7),
    ]


def test_wilson_interval_is_bounded():
    low, high = wilson_interval(3, 4)
    assert 0 <= low <= high <= 1


def test_bootstrap_is_deterministic():
    rows = _rows()
    first = bootstrap_accuracy_interval(rows, iterations=100, seed=7)
    second = bootstrap_accuracy_interval(rows, iterations=100, seed=7)
    assert first == second


def test_calibration_error_is_bounded():
    value = calibration_error(_rows())
    assert 0 <= value <= 1


def test_phase12_report_does_not_claim_scientific_validation():
    result = phase12_report(_rows())
    assert result["status"] == "PASS"
    assert result["scientific_validation_claim"] is False
    assert benchmark_accuracy(_rows()) == 0.75
