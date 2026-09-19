# Contributing to FAS-Bench

FAS-Bench is a security benchmark, so contributions must be reproducible, reviewable, and safe to execute.

## Before contributing a case

Open an issue for substantial new cases or case families. Include:

- security category
- intended capability being evaluated
- expected verdict
- false-positive or false-negative trap
- required evidence
- attack-path expectation
- remediation requirement
- deterministic validation strategy
- difficulty level
- contamination considerations

## Case requirements

A benchmark case should:

1. have a stable identifier;
2. have explicit machine-readable ground truth;
3. define the relevant environment and assumptions;
4. identify required evidence;
5. provide deterministic validation where feasible;
6. avoid relying on prose-only grading;
7. use synthetic credentials and attacker-controlled artifacts;
8. avoid external network dependencies unless explicitly isolated;
9. document licensing and provenance for third-party material.

## Security

Treat every benchmark case as untrusted input. Never execute case code directly on a development or evaluation host.

Report benchmark or evaluator security issues privately when disclosure could compromise the benchmark or evaluator.
