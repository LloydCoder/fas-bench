"""Phase 15 continuous benchmark-health and drift primitives."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping


def total_variation_distance(baseline: Mapping[str, int], current: Mapping[str, int]) -> float:
    base_total = sum(baseline.values())
    current_total = sum(current.values())
    if base_total <= 0 or current_total <= 0:
        raise ValueError("both populations must contain at least one item")
    keys = set(baseline) | set(current)
    return 0.5 * sum(
        abs(baseline.get(key, 0) / base_total - current.get(key, 0) / current_total) for key in keys
    )


def distribution(values: Iterable[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def detect_distribution_drift(
    baseline: Mapping[str, int],
    current: Mapping[str, int],
    *,
    threshold: float = 0.20,
) -> dict:
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")
    distance = total_variation_distance(baseline, current)
    return {
        "metric": "TOTAL_VARIATION_DISTANCE",
        "distance": distance,
        "threshold": threshold,
        "drift_detected": distance > threshold,
    }


def benchmark_health(
    *,
    categories: Mapping[str, int],
    difficulties: Mapping[str, int],
    validation_types: Mapping[str, int],
    contamination_status: str,
    corpus_digest: str,
) -> dict:
    errors = []
    for name, values in (
        ("categories", categories),
        ("difficulties", difficulties),
        ("validation_types", validation_types),
    ):
        if not values or sum(values.values()) <= 0:
            errors.append(f"{name} population is empty")
    if contamination_status not in {"PASS", "NOT_ASSESSED"}:
        errors.append("invalid contamination status")
    if not corpus_digest:
        errors.append("corpus_digest is required")
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": sorted(set(errors)),
        "corpus_digest": corpus_digest,
        "continuous_monitoring": True,
        "automatic_release_authority": False,
    }
