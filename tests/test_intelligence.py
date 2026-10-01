from fas_bench.intelligence import (
    benchmark_health,
    detect_distribution_drift,
    distribution,
    total_variation_distance,
)


def test_total_variation_distance_is_zero_for_equal_distributions():
    assert total_variation_distance({"A": 5, "B": 5}, {"A": 5, "B": 5}) == 0


def test_drift_detection_is_explicit():
    result = detect_distribution_drift({"A": 9, "B": 1}, {"A": 1, "B": 9})
    assert result["drift_detected"] is True


def test_distribution_is_deterministic():
    assert distribution(["B", "A", "B"]) == {"A": 1, "B": 2}


def test_health_never_grants_automatic_release_authority():
    result = benchmark_health(
        categories={"C1": 10},
        difficulties={"L1": 10},
        validation_types={"DYNAMIC": 10},
        contamination_status="PASS",
        corpus_digest="a" * 64,
    )
    assert result["status"] == "PASS"
    assert result["automatic_release_authority"] is False
