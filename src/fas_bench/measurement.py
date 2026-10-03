"""Phase 20 benchmark measurement-science primitives."""
from __future__ import annotations

import math
import random
from collections import Counter
from dataclasses import dataclass


def wilson_interval(
    successes: int, total: int, z: float = 1.959963984540054
) -> tuple[float, float]:
    if total <= 0 or not 0 <= successes <= total:
        raise ValueError("successes and total must define a valid binomial sample")
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    half = z * math.sqrt(
        (p * (1 - p) + z * z / (4 * total)) / total
    ) / denom
    return max(0.0, center - half), min(1.0, center + half)


def deterministic_bootstrap(
    values: list[float], *, samples: int = 2000, seed: int = 0
) -> tuple[float, float]:
    if not values or samples < 1:
        raise ValueError("values and positive sample count are required")
    rng = random.Random(seed)
    means = [
        sum(rng.choice(values) for _ in values) / len(values)
        for _ in range(samples)
    ]
    means.sort()
    return (
        means[int(0.025 * samples)],
        means[min(samples - 1, int(0.975 * samples))],
    )


def cohens_kappa(left: list[str], right: list[str]) -> float:
    if not left or len(left) != len(right):
        raise ValueError("ratings must be non-empty and equally sized")
    n = len(left)
    observed = sum(a == b for a, b in zip(left, right)) / n
    labels = set(left) | set(right)
    expected = sum(
        (left.count(label) / n) * (right.count(label) / n)
        for label in labels
    )
    if expected == 1:
        return 1.0
    return (observed - expected) / (1 - expected)


@dataclass(frozen=True)
class ReliabilityReport:
    sample_count: int
    accuracy: float
    confidence_interval: tuple[float, float]
    inter_rater_kappa: float | None
    bootstrap_interval: tuple[float, float] | None
    benchmark_conditioned: bool = True


def reliability_report(
    outcomes: list[bool],
    *,
    reference: list[str] | None = None,
    observed: list[str] | None = None,
    bootstrap_samples: int = 2000,
    seed: int = 0,
) -> ReliabilityReport:
    if not outcomes:
        raise ValueError("outcomes must not be empty")
    if (reference is None) != (observed is None):
        raise ValueError("reference and observed must be supplied together")
    kappa = cohens_kappa(reference, observed) if reference is not None else None
    bootstrap = deterministic_bootstrap(
        [float(x) for x in outcomes],
        samples=bootstrap_samples,
        seed=seed,
    )
    return ReliabilityReport(
        sample_count=len(outcomes),
        accuracy=sum(outcomes) / len(outcomes),
        confidence_interval=wilson_interval(sum(outcomes), len(outcomes)),
        inter_rater_kappa=kappa,
        bootstrap_interval=bootstrap,
    )


def stratified_counts(labels: list[str]) -> dict[str, int]:
    return dict(sorted(Counter(labels).items()))
