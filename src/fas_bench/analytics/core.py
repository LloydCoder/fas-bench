"""Deterministic aggregation, bootstrap, stratification and sensitivity analysis."""

from __future__ import annotations

import math
import random
from collections import defaultdict
from statistics import mean, median


def _finite(values):
    out = [float(x) for x in values]
    if not out or any(not math.isfinite(x) for x in out):
        raise ValueError("observations must be finite and non-empty")
    return out


def bootstrap(
    observations,
    metric=mean,
    *,
    n_resamples=2000,
    seed=0,
    confidence_level=0.95,
    method="percentile",
):
    x = _finite(observations)
    if (
        not isinstance(n_resamples, int)
        or n_resamples < 1
        or not 0 < confidence_level < 1
        or method != "percentile"
    ):
        raise ValueError("invalid bootstrap configuration")
    rng = random.Random(seed)
    n = len(x)
    samples = []
    for _ in range(n_resamples):
        value = float(metric([x[rng.randrange(n)] for _ in range(n)]))
        if not math.isfinite(value):
            raise ValueError("metric produced non-finite value")
        samples.append(value)
    samples.sort()
    alpha = (1 - confidence_level) / 2

    def q(p):
        return samples[min(len(samples) - 1, max(0, int(math.floor(p * (len(samples) - 1)))))]

    return {
        "estimate": float(metric(x)),
        "lower_bound": q(alpha),
        "upper_bound": q(1 - alpha),
        "n": n,
        "seed": seed,
        "n_resamples": n_resamples,
        "confidence_level": confidence_level,
        "method": method,
    }


def aggregate_cases(case_results):
    rows = list(case_results)
    if not rows:
        raise ValueError("no case results")
    scores = [
        float(r["case_score"])
        for r in rows
        if isinstance(r.get("case_score"), (int, float)) and math.isfinite(float(r["case_score"]))
    ]
    correct = [r["verdict_correct"] for r in rows if isinstance(r.get("verdict_correct"), bool)]
    groups = defaultdict(list)
    diffs = defaultdict(list)
    for r in rows:
        groups[str(r.get("category", "UNKNOWN"))].append(r)
        diffs[str(r.get("difficulty", "UNKNOWN"))].append(r)

    def strata(gs):
        return {
            k: {
                "n": len(v),
                "mean_case_score": mean(
                    [
                        float(x["case_score"])
                        for x in v
                        if isinstance(x.get("case_score"), (int, float))
                    ]
                )
                if any(isinstance(x.get("case_score"), (int, float)) for x in v)
                else None,
            }
            for k, v in sorted(gs.items())
        }

    return {
        "n_cases": len(rows),
        "evaluated_cases": len(scores),
        "macro_case_score": mean(scores) if scores else None,
        "verdict_accuracy": {
            "correct": sum(correct),
            "n": len(correct),
            "accuracy": sum(correct) / len(correct) if correct else None,
        },
        "stratification": {"category": strata(groups), "difficulty": strata(diffs)},
        "score_distribution": {
            "values": sorted(scores),
            "median": median(scores) if scores else None,
            "min": min(scores) if scores else None,
            "max": max(scores) if scores else None,
        },
    }


def stratify_cases(case_results, field, metric="case_score"):
    groups = defaultdict(list)
    for r in case_results:
        groups[str(r.get(field, "UNKNOWN"))].append(r)
    return {
        k: {
            "n": len(v),
            "mean": mean([float(x[metric]) for x in v if metric in x]),
            "values": [x[metric] for x in v if metric in x],
        }
        for k, v in sorted(groups.items())
    }


def sensitivity(case_results, weights):
    keys = {
        "evidence",
        "verdict",
        "reachability",
        "attack_path",
        "false_positive_resistance",
        "remediation",
        "calibration",
        "efficiency",
    }
    out = []
    for i, w in enumerate(weights):
        if set(w) != keys or any(v < 0 for v in w.values()) or sum(w.values()) <= 0:
            raise ValueError("invalid sensitivity weights")
        vals = []
        for r in case_results:
            c = r.get("score_components", {})
            vals.append(
                sum(float(c[k]["normalized"]) * w[k] for k in keys) / sum(w.values())
                if all(k in c for k in keys)
                else float("nan")
            )
        finite = [v for v in vals if math.isfinite(v)]
        out.append(
            {
                "configuration_index": i,
                "mean_score": mean(finite) if finite else None,
                "values": vals,
                "weights": dict(w),
            }
        )
    return out


def leave_one_out(case_results):
    rows = list(case_results)
    if len(rows) < 2:
        return []
    full = mean(float(r["case_score"]) for r in rows)
    return [
        {
            "case_id": r["case_id"],
            "metric_without_case": mean(
                float(x["case_score"]) for j, x in enumerate(rows) if j != i
            ),
            "delta": mean(float(x["case_score"]) for j, x in enumerate(rows) if j != i) - full,
        }
        for i, r in enumerate(rows)
    ]
