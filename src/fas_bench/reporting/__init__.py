"""Phase 8 canonical result and report serialization."""

from __future__ import annotations

import hashlib
import json


def canonical_json(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )


def digest(value):
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def build_report(
    case_results,
    *,
    benchmark_version,
    evaluator_version,
    scoring_version,
    run_id,
    configuration,
    uncertainty=None,
):
    from ..analytics import aggregate_cases

    result = {
        "report_schema_version": "0.1",
        "benchmark_version": benchmark_version,
        "evaluator_version": evaluator_version,
        "scoring_version": scoring_version,
        "run_id": run_id,
        "case_results": case_results,
        "aggregate_metrics": aggregate_cases(case_results),
        "configuration": configuration,
        "uncertainty": uncertainty or {},
    }
    result["result_digest"] = digest(result)
    return result


def render_markdown(result):
    a = result["aggregate_metrics"]
    lines = [
        "# FAS-Bench Evaluation Report",
        "- Benchmark: {}".format(result["benchmark_version"]),
        "- Evaluator: {}".format(result["evaluator_version"]),
        "- Scoring: {}".format(result["scoring_version"]),
        "- Run: {}".format(result["run_id"]),
        "- Cases: {}/{}".format(a["evaluated_cases"], a["n_cases"]),
    ]
    if a["macro_case_score"] is not None:
        lines.append("- Macro case score: {:.4f}".format(a["macro_case_score"]))
    if a["verdict_accuracy"]["accuracy"] is not None:
        lines.append("- Verdict accuracy: {:.4f}".format(a["verdict_accuracy"]["accuracy"]))
    lines += [
        "",
        "## Limitations",
        "- Benchmark-case performance does not establish generalized real-world "
        "security effectiveness.",
        "- The initial public corpus is small and may contain correlated or authoring-related "
        "cases.",
        "- Scoring weights are provisional methodology configuration.",
    ]
    return "\n".join(lines) + "\n"


def write_report(result, output):
    output.mkdir(parents=True, exist_ok=True)
    (output / "results.json").write_text(canonical_json(result) + "\n", encoding="utf-8")
    (output / "case_results.jsonl").write_text(
        "".join(canonical_json(x) + "\n" for x in result["case_results"]), encoding="utf-8"
    )
    (output / "report.md").write_text(render_markdown(result), encoding="utf-8")
    (output / "manifest.json").write_text(
        canonical_json(
            {
                "result_digest": result["result_digest"],
                "run_id": result["run_id"],
                "benchmark_version": result["benchmark_version"],
                "evaluator_version": result["evaluator_version"],
                "scoring_version": result["scoring_version"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
