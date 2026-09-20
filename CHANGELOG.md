# Changelog

All notable changes to FAS-Bench are documented here.

## Unreleased — Phase 2: Schema & Data Model

### Added
- JSON Schema Draft 2020-12 contracts for case, claim, evidence, attack graph, verdict, remediation, submission, and evaluation result.
- Shared canonical definitions for IDs, enums, timestamps, confidence, severity, provenance, impact, graph objects, findings, verification, and score components.
- Offline semantic validation with deterministic structured errors.
- Valid/invalid contract fixtures and integrated FAS-001, FAS-002, FAS-006, FAS-016, and FAS-020 fixture coverage.
- CLI validation command and CI schema/meta-validation gates.
- Public case registry metadata.

### Clarifications
- Benchmark version is 0.1.0; schema family version is 0.1.
- Schema-valid, semantically-valid, and benchmark-correct are distinct states.
- Public submissions contain system beliefs, not hidden expected verdicts.
- Scoring arithmetic is structurally represented but remains provisional until Phase 8.

## 0.1.0 — Phase 1: Specification & Benchmark Contract
- Normative benchmark contract, canonical taxonomy, verdict semantics, evidence model, graph model, remediation/regression semantics, reproducibility, security, contamination, and FAS independence.

## Phase 3 — Validated
- Added the initial FAS-001 through FAS-020 public development corpus.
- Added structured case ground truth, deterministic case oracles, corpus registry and manifest.
- Added corpus validation, immutable artifact digests, isolated oracle execution, and gold-case mutation gates.
- The corpus is not statistically representative and is not a hidden evaluation set.
