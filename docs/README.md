# FAS-Bench Documentation

This directory contains the technical documentation for FAS-Bench.

## Authority model

**docs/specification.md is the normative benchmark contract.**

Other documentation may explain implementation, operational procedures, contributor workflows, or research limitations, but it must not redefine benchmark semantics. If two documents disagree, reconcile the implementation/documentation and treat the specification as the source of normative truth.

## Documentation layers

### 1. Benchmark contract

- [Specification](specification.md) — taxonomy, case semantics, evidence, verdicts, graphs, remediation, reproducibility, security, and measurement boundaries.
- [Architecture](architecture.md) — repository/component architecture and implementation boundaries.

### 2. Evaluation engines

- [Evidence engine](evidence-engine.md)
- [Graph engine](graph-engine.md)
- [Phase 7 remediation](phase7-remediation.md)
- [Phase 8 scoring](phase8-scoring.md)
- [Phase 9 secure evaluation](phase9-secure-evaluation.md)

### 3. Phase 10 integrity and release

- [Corpus and release contract](phase10-corpus-release.md)
- [Mutation contract](phase10-mutation.md)
- [Contamination and gaming defense](phase10-contamination.md)
- [Release procedure](phase10-release.md)
- [Governance](phase10-governance.md)

### 4. Repository/community

- [Contributing](../CONTRIBUTING.md)
- [Security policy](../SECURITY.md)
- [Support](../SUPPORT.md)
- [Changelog](../CHANGELOG.md)
- [Citation](../CITATION.cff)

## Documentation rules

Every substantive change should answer:

1. What behavior changed?
2. Is the change normative or implementation-specific?
3. What tests or validation prove it?
4. Does it change benchmark comparability or historical interpretation?
5. Does the README, specification, phase documentation, changelog, or contributor guidance need reconciliation?

### Normative language

Use **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY** consistently with the specification.

### Scientific claims

Do not describe a provisional score, public-corpus result, or implementation feature as statistically validated unless the repository contains the empirical evidence supporting that statement.

### Public/hidden boundary

Never publish hidden evaluation answers, private evaluator material, real credentials, or artifacts that undermine contamination-resistant evaluation.

### Security

Benchmark cases and submissions are untrusted. Documentation examples must not encourage host execution, unrestricted networking, real credentials, privileged containers, Docker-socket mounts, or mutable security-boundary assumptions.
