"""Phase 12 statistical calibration and benchmark-validity primitives."""

from __future__ import annotations

import math
import random
from collections import defaultdict
from dataclasses import dataclass
from statistics import mean
from typing import Iterable, Sequence

VALID_OUTCOMES = frozenset({"CORRECT", "INCORRECT"})


@dataclass(frozen=True)
class EvaluationRow:
    system_id: str
    case_id: str
    outcome: str
    stratum: str = "UNSPECIFIED"
    confidence: float | None = None

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.system_id or not self.case_id:
            errors.append("system_id and case_id must be non-empty")
        if self.outcome not in VALID_OUTCOMES:
            errors.append("outcome must be CORRECT or INCORRECT")
        if not self.stratum:
            errors.append("stratum must be non-empty")
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            errors.append("confidence must be between 0 and 1")
        return errors


def wilson_interval(
    successes: int, trials: int, z: float = 1.959963984540054
) -> tuple[float, float]:
    if trials <= 0 or successes < 0 or successes > trials:
        raise ValueError("invalid binomial counts")
    p = successes / trials
    denominator = 1.0 + z * z / trials
    centre = (p + z * z / (2 * trials)) / denominator
    margin = (
        z
        * math.sqrt((p * (1.0 - p) + z * z / (4 * trials)) / trials)
        / denominator
    )
    return max(0.0, centre - margin), min(1.0, centre + margin)


def benchmark_accuracy(rows: Sequence[EvaluationRow]) -> float:
    if not rows:
        raise ValueError("at least one evaluation row is required")
    return mean(row.outcome == "CORRECT" for row in rows)


def bootstrap_accuracy_interval(
    rows: Sequence[EvaluationRow],
    *,
    iterations: int = 2000,
    seed: int = 0,
    confidence: float = 0.95,
) -> tuple[float, float]:
    if not rows or iterations < 1 or not 0.0 < confidence < 1.0:
        raise ValueError("invalid bootstrap parameters")
    rng = random.Random(seed)
    values: list[float] = []
    size = len(rows)
    for _ in range(iterations):
        sample = [rows[rng.randrange(size)] for _ in range(size)]
        values.append(benchmark_accuracy(sample))
    values.sort()
    alpha = (1.0 - confidence) / 2.0
    low = values[min(len(values) - 1, math.floor(alpha * len(values)))]
    high_index = min(len(values) - 1, math.floor((1.0 - alpha) * len(values)))
    return low, values[high_index]


def item_difficulty(rows: Iterable[EvaluationRow]) -> dict[str, float]:
    grouped: dict[str, list[EvaluationRow]] = defaultdict(list)
    for row in rows:
        grouped[row.case_id].append(row)
    return {
        case_id: 1.0 - mean(row.outcome == "CORRECT" for row in group)
        for case_id, group in sorted(grouped.items())
    }


def stratified_accuracy(
    rows: Iterable[EvaluationRow],
) -> dict[str, dict[str, float | int]]:
    grouped: dict[str, list[EvaluationRow]] = defaultdict(list)
    for row in rows:
        grouped[row.stratum].append(row)
    result: dict[str, dict[str, float | int]] = {}
    for stratum, group in sorted(grouped.items()):
        result[stratum] = {
            "n": len(group),
            "accuracy": benchmark_accuracy(group),
        }
    return result


def calibration_error(rows: Iterable[EvaluationRow], bins: int = 10) -> float:
    if bins < 1:
        raise ValueError("bins must be positive")
    scored = [row for row in rows if row.confidence is not None]
    if not scored:
        raise ValueError("confidence values are required")
    total = 0.0
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        group = [
            row
            for row in scored
            if lower <= row.confidence < upper
            or (index == bins - 1 and row.confidence == upper)
        ]
        if group:
            accuracy = benchmark_accuracy(group)
            confidence = mean(row.confidence for row in group)
            total += len(group) / len(scored) * abs(accuracy - confidence)
    return total


def phase12_report(rows: Sequence[EvaluationRow]) -> dict:
    errors = [f"{row.case_id}: {error}" for row in rows for error in row.validate()]
    if not rows:
        errors.append("no evaluation rows")
    if errors:
        return {
            "phase": "12",
            "status": "FAIL",
            "errors": sorted(set(errors)),
            "scientific_validation_claim": False,
        }

    correct = sum(row.outcome == "CORRECT" for row in rows)
    return {
        "phase": "12",
        "status": "PASS",
        "n": len(rows),
        "accuracy": benchmark_accuracy(rows),
        "wilson_95": wilson_interval(correct, len(rows)),
        "bootstrap_95": bootstrap_accuracy_interval(rows),
        "item_difficulty": item_difficulty(rows),
        "strata": stratified_accuracy(rows),
        "scientific_validation_claim": False,
    }
