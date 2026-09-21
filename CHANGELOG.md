# Changelog

All notable changes to FAS-Bench are recorded here. Historical benchmark semantics must remain interpretable through explicit versioning.

## Unreleased — Phase 10: Corpus, Contamination, Mutation & Release

### Added

- Content-addressed corpus validation and benchmark health diagnostics.
- Explicit case lifecycle and evaluation-eligibility primitives.
- Deterministic mutation operators with semantic-preservation guards.
- Contamination/leakage and FAS-independence audits.
- Versioned release-manifest generation and fail-closed verification.
- Corpus, release, mutation, contamination, and governance documentation.
- Immutable commit-SHA pinning for GitHub Actions references.
- Contributor-facing documentation, citation metadata, support guidance, and pull-request workflow.

### Integrity boundary

- The FAS-001 through FAS-020 corpus remains public development/practice data.
- The repository does not claim model-training contamination freedom.
- Hidden official evaluation material is not committed to the public repository.
- Release identity is content-derived rather than timestamp-derived.

### Limitations

- The current public corpus is not statistically representative.
- Security-changing mutation classes are not claimed as implemented until they have an authoritative oracle-backed validation path.
- Official held-out evaluation requires protected evaluation infrastructure outside the public artifact boundary.

## Unreleased — Phase 9: Secure Evaluation Harness & Reproducibility

### Added

- Fail-closed Docker execution with immutable image digest verification.
- Private PID/IPC/cgroup namespaces, read-only root, dropped capabilities, no-new-privileges, built-in seccomp, non-root execution, and bounded resources.
- Bounded streaming stdout/stderr collection.
- Content-derived run identity and cache-key primitives.
- Execution lifecycle, artifact collection, result-integrity verification, and reproducibility bundle primitives.
- Symlink/special-file/path-escape rejection and harness-computed artifact digests.

### Security boundary

- Candidate code never executes directly on the host.
- Network denial is mandatory in the current provider.
- Host credentials, Docker socket, arbitrary host mounts, and hidden gold data are not exposed to candidates.
- Cleanup and security-policy failures remain explicit and are not converted into candidate scores.

### Limitations

- Docker/Linux is the validated execution boundary; escape-proof isolation is not claimed.
- Full-corpus and adversarial security-boundary results must remain CI-verified.

## Unreleased — Phase 8: Scoring, Calibration & Benchmark Analytics

- Added deterministic finding, verdict, evidence, reachability, graph, remediation, calibration, integrity, and composite measurement APIs.
- Added versioned scoring policy, canonical result/report serialization, bootstrap uncertainty, stratification, and leave-one-case-out analysis.
- Added Phase 8 CLI commands and self-test/analytics/report workflows.
- Scoring weights remain provisional and the public corpus is not statistically representative.

## Unreleased — Phase 7: Remediation & Regression Engine

- Added deterministic baseline/post-remediation security-state models and remediation oracle.
- Added semantic path lifecycle classification, equivalent-impact alternate-path detection, control weakening detection, functional-preservation checks, regression evaluation, evidence-integrity gating, and content-derived run identity.
- Added remediation evaluation schema and CLI commands.
- Phase 7 does not execute candidate code; secure execution belongs to Phase 9.

## Unreleased — Phase 6: Attack-Path & Security-Graph Engine

- Added deterministic graph validation, canonicalization, identity, path extraction, alternate-path discovery, semantic comparison, graph diffs, finite traversal limits, and adversarial defenses.

## Unreleased — Phase 5: Verdict & Finding Evaluator

- Added deterministic finding, claim, security-condition, and verdict evaluation consuming the Phase 4 evidence engine.
- Preserved the distinction between UNKNOWN and NOT_EXPLOITABLE.
- Added explicit conditional exploitability semantics.

## Unreleased — Phase 4: Deterministic Evidence Engine

- Added deterministic evidence normalization, case-relative artifact resolution, structured fact verification, source-location verification, duplicate detection, coverage, and evidence-integrity metrics.

## Unreleased — Phase 3: Gold Cases & Ground Truth

- Added the initial public development corpus FAS-001 through FAS-020.
- Added deterministic case validation, oracle execution, provenance, integrity, and reproducibility controls.

## Unreleased — Phase 2: Schema & Data Model

- Added JSON Schema Draft 2020-12 contracts and offline semantic validation.

## 0.1.0 — Phase 1: Specification & Benchmark Contract

- Added the normative benchmark contract, taxonomy, verdict semantics, evidence model, graph model, remediation/regression semantics, reproducibility requirements, benchmark security model, contamination boundary, and FAS independence invariant.
