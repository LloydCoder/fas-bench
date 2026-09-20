# Phase 8 — Scoring, Calibration & Benchmark Analytics

Phase 8 is the deterministic measurement layer above the Phase 4 evidence, Phase 5 verdict, Phase 6 graph, and Phase 7 remediation outputs.

## Measurement contract

All normalized authoritative scores use [0,1]. Presentation may use percentages, but aggregation occurs before display rounding. Missing, unavailable, not-applicable, evaluator error, and candidate failure remain distinct.

Core dimensions are finding identification, verdict correctness, evidence quality, reachability, attack-path reconstruction, impact, remediation/regression verification, calibration, efficiency telemetry, and evidence integrity.

### Evidence score

The provisional v0.1 evidence score is:

0.35 validity + 0.30 relevance + 0.20 coverage + 0.15 specificity

The weights are versioned configuration in the packaged Phase 8 scoring resource, not scientifically validated constants.

### Integrity policy

Evidence hallucination/integrity rate is invalid submitted evidence divided by submitted evidence. The v0.1 policy applies no cap through 0.10, a 0.50 maximum through 0.25, and a 0.25 maximum above 0.25. The result preserves the uncapped score, rate, cap, and final score.

### Graph score

Phase 8 consumes the Phase 6 graph comparison output. It does not reimplement graph matching.

### Calibration

Binary confidence targets verdict correctness. Brier score and ECE are lower-is-better diagnostics. The calibration component is explicitly transformed to a higher-is-better score as (1-Brier + 1-ECE) / 2. Ten fixed bins are used by v0.1; confidence 1.0 belongs to the final bin.

Multiclass probability distributions are validated without silent renormalization and use multiclass Brier scoring.

### Aggregation and uncertainty

Case-level results are preserved. Macro case score is the arithmetic mean of successful case scores; verdict accuracy preserves numerator and denominator. Deterministic percentile bootstrap uses a recorded seed and resample count. Leave-one-case-out analysis is a diagnostic, not evidence of generalization.

### Composite

The configured v0.1 composite uses the Phase 8 provisional weights. Unavailable efficiency telemetry is excluded from the composite denominator rather than treated as zero. The component decomposition remains authoritative; the composite must never be treated as a standalone scientific conclusion.

## Reproducibility

Canonical JSON uses sorted keys, stable separators, UTF-8, and disallows NaN/Infinity. Reports include benchmark/evaluator/scoring versions, case results, configuration, run identity, and a result digest.

## Security boundary

Candidate JSON is untrusted. Phase 8 performs no candidate code execution and never treats candidate-provided aggregate scores as authoritative. Gold artifacts are read only from benchmark case data. Path and resource enforcement remains part of the earlier graph/evidence contracts and the Phase 9 secure evaluation harness.

## Limitations

The initial public corpus has 20 development cases and is not a statistically representative sample of real-world vulnerabilities. Cases may be correlated and the public corpus is not a hidden evaluation set. Scoring weights are provisional. Benchmark performance does not establish production security effectiveness or generalized real-world detection rates.
