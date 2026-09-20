# Changelog

## Unreleased — Phase 9: Secure Evaluation Harness & Reproducibility

### Added
- Fail-closed Docker execution with immutable image digest verification.
- Private PID/IPC/cgroup namespaces, read-only root, dropped capabilities, no-new-privileges, built-in seccomp, non-root execution, and bounded resources.
- Bounded streaming stdout/stderr collection so candidate output is not buffered without a limit.
- Content-derived run identity including benchmark, case manifest, submission, evaluator, scoring, environment, policy, and seed inputs.
- Content-addressed cache-key primitives that invalidate on score-affecting input changes.
- Explicit lifecycle state machine, orchestration boundary, artifact collector, result integrity verifier, and reproducibility bundle writer.
- Symlink/special-file/path escape rejection and harness-computed artifact digests.
- Phase 9 harness, sandbox, reproducibility, security, and contribution documentation.

### Security boundary
- Candidate code never executes directly on the host.
- Network-deny is mandatory in the current provider.
- Host credentials, Docker socket, arbitrary host mounts, and hidden gold data are not exposed to candidates.
- Cleanup and security-policy failures remain explicit and are not converted into candidate scores.

### Limitations
- Docker/Linux execution is the validated security boundary; escape-proof isolation is not claimed.
- The public FAS-001 through FAS-020 corpus remains development data, not hidden evaluation data.
- Docker-backed full-corpus, security-attack, and clean-install results must be verified by CI before Phase 9 is declared complete.

## Unreleased — Phase 8: Scoring, Calibration & Benchmark Analytics

### Added
- Deterministic finding, verdict, evidence, reachability, graph, remediation, calibration, integrity, and composite measurement APIs.
- Versioned scoring policy, canonical result/report serialization, deterministic bootstrap uncertainty, stratification, and leave-one-case-out analysis.
- Phase 8 CLI commands and self-test pipeline over the public 20-case development corpus.

### Limitations
- Scoring weights are provisional; the public 20-case corpus is not statistically representative or hidden.

## Unreleased — Phase 7: Remediation & Regression Engine

- Added deterministic baseline/post-remediation security-state models and remediation oracle.
- Added semantic path lifecycle classification, equivalent-impact alternate-path detection, control weakening detection, functional-preservation checks, regression evaluation, evidence-integrity gating, content-derived run identity, and provisional raw remediation dimensions.
- Added remediation evaluation schema and CLI commands.
- Phase 7 does not execute candidate code; secure patch execution and isolation remain Phase 9 responsibilities.

## Unreleased — Phase 6: Attack-Path & Security-Graph Engine

- Added deterministic graph validation, canonicalization, identity, path extraction, alternate-path discovery, semantic comparison, graph diffs, finite traversal limits, and adversarial defenses.

## Unreleased — Phase 5: Verdict & Finding Evaluator

- Added deterministic finding, claim, security-condition, and verdict evaluation consuming the Phase 4 evidence engine.
- UNKNOWN remains distinct from NOT_EXPLOITABLE and conditional exploitability requires explicit conditions.

## Unreleased — Phase 2: Schema & Data Model

- Added JSON Schema Draft 2020-12 contracts and offline semantic validation.

## 0.1.0 — Phase 1: Specification & Benchmark Contract

- Normative benchmark contract, taxonomy, verdict semantics, evidence model, graph model, remediation/regression semantics, reproducibility, security, contamination, and FAS independence.
# Changelog

## Phase 10 — Corpus, contamination, mutation and release

- Added content-addressed Phase 10 corpus validation and benchmark health diagnostics.
- Added explicit case lifecycle and evaluation eligibility primitives.
- Added deterministic mutation operators with semantic-preservation guards.
- Added contamination/leakage and FAS-independence audits.
- Added versioned release manifest generation and fail-closed verification.
- Added corpus, release, mutation, contamination, and governance documentation.
- Pinned GitHub Actions to full commit SHAs for immutable workflow references.
- Preserved the initial 20-case public development corpus and explicitly documented its statistical and contamination limitations.

