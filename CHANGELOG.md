# Changelog

All notable changes to FAS-Bench are documented here.

## 0.1.0 — Phase 1: Specification & Benchmark Contract

### Added

- Normative FAS-Bench benchmark specification.
- Canonical taxonomy, difficulty model, verdict semantics, claim/evidence model, attack graph model, effective security graph, remediation and regression semantics.
- Initial 20-case design registry and five designated gold cases.
- Explicit benchmark independence requirements.
- Reproducibility, determinism, benchmark-security, contamination, and ground-truth isolation requirements.
- Repository-contract validation tests.
- Documentation consistency tests.
- CI for formatting, linting, tests, package build/import, and repository-contract validation.
- Development tooling metadata for Python 3.12 and 3.13.

### Clarifications

- Scoring weights, evidence score, graph score, evidence-integrity threshold, and composite metric are explicitly provisional research hypotheses.
- The initial case registry is not presented as a validated or statistically representative corpus.
- Phase 1 does not implement the complete evaluator, schema engine, evidence engine, graph engine, scoring engine, or secure evaluation harness.

## Unreleased

Future changes will be recorded against the applicable benchmark specification version and phase. Normative semantic changes require specification review.
