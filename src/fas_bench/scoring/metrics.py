"""Pure deterministic scoring primitives."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence


def normalize_score(value: float, *, lower_is_better=False) -> float:
    value = float(value)
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError("score must be finite in [0,1]")
    return 1 - value if lower_is_better else value


def _f1(p, r):
    return 2 * p * r / (p + r) if p + r else 0.0


def binary_metrics(tp, fp, fn, tn=0):
    if any(not isinstance(x, int) or x < 0 for x in (tp, fp, fn, tn)):
        raise ValueError("counts must be non-negative integers")
    precision = tp / (tp + fp) if tp + fp else (1.0 if tp + fp + fn == 0 else 0.0)
    recall = tp / (tp + fn) if tp + fn else (1.0 if tp + fp + fn == 0 else 0.0)
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": precision,
        "recall": recall,
        "f1": _f1(precision, recall),
    }


def evidence_score(validity, relevance, coverage, specificity, weights):
    values = {
        "validity": validity,
        "relevance": relevance,
        "coverage": coverage,
        "specificity": specificity,
    }
    if (
        set(weights) != set(values)
        or any(not 0 <= float(v) <= 1 for v in values.values())
        or any(float(v) < 0 for v in weights.values())
    ):
        raise ValueError("invalid evidence metric or weights")
    total = sum(weights.values())
    return sum(values[k] * weights[k] for k in values) / total if total else 0.0


def brier_score(confidences: Sequence[float], outcomes: Sequence[bool | int | float]):
    if len(confidences) != len(outcomes) or not confidences:
        raise ValueError("confidence/outcome length mismatch")
    if any(not math.isfinite(float(c)) or not 0 <= float(c) <= 1 for c in confidences):
        raise ValueError("confidence must be finite in [0,1]")
    return sum(
        (float(c) - (1.0 if bool(o) else 0.0)) ** 2
        for c, o in zip(confidences, outcomes, strict=True)
    ) / len(confidences)


def expected_calibration_error(confidences, outcomes, bins=10):
    if (
        len(confidences) != len(outcomes)
        or not confidences
        or not isinstance(bins, int)
        or bins < 1
    ):
        raise ValueError("invalid calibration input")
    bucket = [{"sum_conf": 0.0, "sum_out": 0.0, "count": 0} for _ in range(bins)]
    for c, o in zip(confidences, outcomes, strict=True):
        c = float(c)
        if not math.isfinite(c) or not 0 <= c <= 1:
            raise ValueError("confidence must be finite in [0,1]")
        i = min(bins - 1, int(math.floor(c * bins)))
        bucket[i]["sum_conf"] += c
        bucket[i]["sum_out"] += 1.0 if bool(o) else 0.0
        bucket[i]["count"] += 1
    rows = []
    ece = 0.0
    n = len(confidences)
    for i, b in enumerate(bucket):
        count = b["count"]
        mc = b["sum_conf"] / count if count else None
        acc = b["sum_out"] / count if count else None
        gap = abs(mc - acc) if count else None
        if count:
            ece += (count / n) * gap
        rows.append(
            {
                "bin": i,
                "lower": i / bins,
                "upper": (i + 1) / bins,
                "mean_confidence": mc,
                "accuracy": acc,
                "count": count,
                "gap": gap,
            }
        )
    return {
        "ece": ece,
        "bins": rows,
        "bin_count": bins,
        "edge_rule": "[lower,upper), with confidence=1 in final bin",
    }


def multiclass_brier(probabilities, outcomes):
    if len(probabilities) != len(outcomes) or not probabilities:
        raise ValueError("probability/outcome length mismatch")
    classes = sorted({c for p in probabilities for c in p} | set(outcomes))
    total = 0.0
    for p, y in zip(probabilities, outcomes, strict=True):
        if (
            set(p) != set(classes)
            or any(not math.isfinite(float(v)) or not 0 <= float(v) <= 1 for v in p.values())
            or abs(sum(p.values()) - 1) > 1e-9
        ):
            raise ValueError("invalid probability distribution")
        total += sum((p[c] - (1 if c == y else 0)) ** 2 for c in classes)
    return total / len(probabilities)


def confusion_matrix(predicted: Iterable[str], actual: Iterable[str]):
    p = list(predicted)
    a = list(actual)
    if len(p) != len(a):
        raise ValueError("length mismatch")
    labels = sorted(set(p) | set(a))
    return {
        g: {c: sum(1 for x, y in zip(p, a, strict=True) if x == c and y == g) for c in labels}
        for g in labels
    }
