# Changelog

## Unreleased — Phase 5: Verdict & Finding Evaluator

CI validation is required before merge; no scoring fields are manufactured by Phase 5.

### Added
- Deterministic finding, claim, security-condition, and verdict evaluation consuming the Phase 4 evidence engine.
- Declarative verdict derivation from authoritative path state, effective controls, explicit conditions, and remediation state.
- Structured verdict reasoning, stable Phase 5 reason codes, evidence-support metadata, and deterministic evaluation fingerprints.
- Gold-case self-evaluation, adversarial submissions, contradiction handling, metamorphic invariants, confidence validation, tamper detection, and FAS-independence tests.
- Finding-evaluation CLI with strict mode.
- Phase 5 evaluation-result fields with scoring explicitly deferred to Phase 8.

### Normative clarifications
- A correct verdict with invalid or incomplete evidence is not fully supported.
- Severity and finding prose never determine exploitability.
- UNKNOWN is distinct from NOT_EXPLOITABLE; conditional exploitability requires explicit case conditions.
- Remediation failure and regression are distinct temporal states.


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

## Phase 3 — Release Candidate
- Added the initial FAS-001 through FAS-020 public development corpus.
- Added structured case ground truth, deterministic case oracles, corpus registry and manifest.
- Added corpus validation, immutable artifact digests, isolated oracle execution, and gold-case mutation gates.
- The corpus is not statistically representative and is not a hidden evaluation set.

## Unreleased — Phase 6: Attack-Path & Security-Graph Engine

### Added
- Deterministic graph domain API for validation, canonicalization, SHA-256 graph identity, path extraction, minimal security paths, alternate-path discovery, semantic comparison, metrics, and graph diffs.
- Security-graph schema extensions for abstraction levels, security relevance, aliases, graph evidence references, security semantics, trust-boundary references, and identity transitions.
- Finite graph/path/traversal limits and structured diagnostics for hostile submissions.
- Graph CLI commands for validation, normalization, digesting, path extraction, diffing, and comparison.
- All-20-case graph validation and self-consistency tests plus adversarial, metamorphic, determinism, and property tests.
- Evaluation-result graph contract for later composite scoring integration.

### Methodology
- Node/edge/path/boundary dimensions remain separate from verdict correctness.
- Graph scoring weights are explicit and versioned methodology configuration; they are not scientifically validated constants.
- Unsupported fabricated edges and contradictory security transitions cannot manufacture graph credit.


## Unreleased — Phase 7: Remediation & Regression Engine

- Added deterministic baseline/post-remediation security-state models and remediation oracle.
- Added semantic path lifecycle classification, equivalent-impact alternate-path detection, control weakening detection, functional-preservation checks, regression evaluation, evidence-integrity gating, content-derived run identity, and provisional raw remediation dimensions.
- Added remediation evaluation schema and CLI commands.
- Added adversarial, overblocking, cosmetic-fix, evidence-fabrication, alternate-path, regression, and all-20 remediation-artifact tests.
- Phase 7 does not execute candidate code; secure patch execution and isolation remain Phase 9 responsibilities.
