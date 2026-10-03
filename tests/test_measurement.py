import pytest

from fas_bench.measurement import (
    cohens_kappa,
    deterministic_bootstrap,
    reliability_report,
    stratified_counts,
    wilson_interval,
)


def test_wilson_interval_is_bounded():
    low, high = wilson_interval(8, 10)
    assert 0 <= low <= high <= 1


def test_wilson_rejects_invalid_z():
    with pytest.raises(ValueError):
        wilson_interval(8, 10, z=0)


def test_bootstrap_is_deterministic():
    first = deterministic_bootstrap([0.0, 1.0, 1.0], samples=100, seed=7)
    second = deterministic_bootstrap([0.0, 1.0, 1.0], samples=100, seed=7)
    assert first == second


def test_bootstrap_rejects_non_finite_values():
    with pytest.raises(ValueError):
        deterministic_bootstrap([0.0, float("nan")])


def test_perfect_kappa():
    assert cohens_kappa(["A", "B", "A"], ["A", "B", "A"]) == 1.0


def test_constant_disagreement_is_not_perfect_agreement():
    assert cohens_kappa(["A", "A"], ["B", "B"]) == 0.0


def test_reliability_report_preserves_benchmark_boundary():
    report = reliability_report(
        [True, False, True],
        reference=["A", "B", "A"],
        observed=["A", "B", "A"],
        bootstrap_samples=100,
    )
    assert report.benchmark_conditioned is True
    assert report.inter_rater_kappa == 1.0


def test_reliability_report_requires_boolean_outcomes():
    with pytest.raises(ValueError):
        reliability_report([1, 0, 1])


def test_stratified_counts_sorted():
    assert stratified_counts(["B", "A", "B"]) == {"A": 1, "B": 2}
