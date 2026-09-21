# Phase 7 — Remediation & Regression Engine

Phase 7 provides deterministic adjudication of remediation and regression using immutable baseline/post-remediation security states.

## Authority

The normative semantics are defined in [docs/specification.md](specification.md). This document explains the Phase 7 implementation boundary.

## Pipeline

Baseline state → post-remediation state → graph/path diff → alternate-path analysis → security-condition diff → security/functional tests → evidence-integrity gate → remediation/regression result.

## What Phase 7 establishes

A remediation assessment asks:

1. What security condition existed?
2. What path enabled the condition?
3. What changed?
4. Which control or boundary was introduced or changed?
5. Does the original path still exist?
6. Does an equivalent-impact alternate path exist?
7. Does the effective security boundary still hold?
8. Does the original impact remain possible?
9. Is the remediation supported by valid evidence and required tests?

A source-code diff alone is not a remediation verdict.

## Distinct outcomes

- **REMEDIATED** — the authoritative security condition is closed.
- **REMEDIATION_FAILED** — the condition remains, including through an equivalent-impact alternate path.
- **REGRESSED** — a previously secure/remediated property becomes insecure after a later state.
- **UNKNOWN** — the available authoritative evidence is insufficient.
- Infrastructure/evaluator failures remain separate from benchmark verdicts.

## Security boundary

Phase 7 consumes already-produced security states. It does not execute candidate code. Untrusted execution belongs to Phase 9.

## CLI

~~~text
fas-bench remediation validate <remediation.json>
fas-bench remediation evaluate --baseline <state.json> --post <state.json> --remediation <remediation.json>
fas-bench remediation diff --before <graph.json> --after <graph.json>
fas-bench remediation regression --previous <state.json> --current <state.json>
fas-bench remediation report <result.json>
~~~

## Scientific boundary

The remediation dimensions exposed by the engine are benchmark measurements, not proof of universal real-world remediation effectiveness. Empirical calibration remains a research responsibility of the measurement layer.
