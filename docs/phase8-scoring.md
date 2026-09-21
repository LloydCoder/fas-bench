# Phase 8 — Scoring, Calibration & Benchmark Analytics

Phase 8 is the measurement layer above the deterministic evidence, verdict, graph, and remediation engines.

## Authority

The normative semantics are defined in [docs/specification.md](specification.md). This document explains the measurement implementation boundary.

## Measurement principles

Phase 8:

- preserves decomposable component metrics;
- keeps evaluator/infrastructure errors distinct from candidate results;
- applies explicit evidence-integrity handling;
- records versioned scoring configuration;
- supports confidence calibration;
- supports uncertainty estimation;
- supports stratification and leave-one-case-out diagnostics;
- serializes results canonically;
- never treats candidate-provided aggregate scores as authoritative.

## Supported analysis

The measurement layer supports findings, verdicts, evidence, reachability, graph, remediation, calibration, integrity, and efficiency dimensions.

Confidence analysis supports Brier score, expected calibration error (ECE), reliability analysis, and confidence-conditioned error analysis.

Bootstrap uncertainty and leave-one-case-out analysis are available where the result structure permits them.

## Provisional methodology

Some weights and aggregate policies are explicitly **provisional**. They are configuration, not scientific truth.

Reports should expose component metrics and their uncertainty rather than hiding all behavior behind a single composite score.

The current public twenty-case corpus is not statistically representative, so it is not sufficient to validate universal score weights.

## CLI

~~~text
fas-bench score <submission>
fas-bench self-test
fas-bench analyze <results.json>
fas-bench report <results.json> --output <directory>
~~~

## Security boundary

Candidate submissions are untrusted data. The scoring/reporting layer must not execute candidate code, import candidate modules, accept candidate aggregate scores as ground truth, or allow candidate data to alter benchmark truth or scoring configuration.
