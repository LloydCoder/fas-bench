# FAS-Bench Documentation

FAS-Bench documentation is organized so readers can learn, accomplish a task, understand the system, or look up a precise contract without confusing those purposes.

> [!IMPORTANT]
> [specification.md](specification.md) is the normative benchmark contract. Other documents explain implementation, operations, contribution workflows, or research limitations and must not silently redefine benchmark semantics.

## Start here

| Goal | Read |
|---|---|
| Run the project | [README](../README.md) |
| Understand benchmark semantics | [Specification](specification.md) |
| Understand implementation boundaries | [Architecture](architecture.md) |
| Reproduce an evaluation | [Reproducibility](reproducibility.md) |
| Understand secure execution | [Phase 9](phase9-secure-evaluation.md) |
| Understand release integrity | [Release certification](release-certification.md) |
| Contribute | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| Report a vulnerability | [SECURITY.md](../SECURITY.md) |

## Tutorials

Tutorials are short paths from a clean checkout to a working result.

- [Repository quick start](../README.md#quick-start)
- [Validation and usage](../README.md#usage)
- [Reproducibility contract](reproducibility.md)

Public FAS-001–FAS-020 execution is development/practice work, not official hidden-set evaluation.

## How-to guides

- [Evidence validation](evidence-engine.md)
- [Graph validation and path analysis](graph-engine.md)
- [Remediation and regression](phase7-remediation.md)
- [Scoring and analytics](phase8-scoring.md)
- [Secure evaluation](phase9-secure-evaluation.md)
- [Corpus and release](phase10-corpus-release.md)
- [Mutation](phase10-mutation.md)
- [Contamination and gaming defense](phase10-contamination.md)
- [Release procedure](phase10-release.md)
- [Independent verification](phase10-2-verification.md)
- [Phase 11 corpus expansion](phase11-corpus-expansion.md)
- [Phase 11.1 dynamic oracles](phase11-1-dynamic-oracles.md)
- [Phase 12 statistical calibration](phase12-statistical-calibration.md)
- [Phase 12.1 independent validation](phase12-1-independent-validation.md)
- [Phase 13 enterprise hardening](phase13-enterprise-hardening.md)
- [Phase 13.1 governance](phase13-1-governance.md)
- [Phase 14 evaluation platform](phase14-evaluation-platform.md)
- [Phase 15 continuous benchmark intelligence](phase15-continuous-benchmark-intelligence.md)
- [Phase 16 test registry](phase16-test-registry.md)
- [Phase 17 hidden evaluation](phase17-hidden-contamination.md)
- [Phase 18 agentic evaluation](phase18-agentic-evaluation.md)
- [Phase 19 adversarial robustness](phase19-adversarial-robustness.md)
- [Phase 20 measurement science](phase20-measurement-science.md)
- [Phase 21 evaluation ecosystem](phase21-evaluation-ecosystem.md)

## Explanation

- [Architecture](architecture.md)
- [Threat model](threat-model.md)
- [Trust model](trust-model.md)
- [Verification model](verification-model.md)
- [Specification](specification.md)
- [Phase 10.2 verification matrix](phase10-2-verification-matrix.md)

## Reference

- [Schemas](../schemas/)
- [Tests](../tests/README.md)
- [Citation](../CITATION.cff)
- [Changelog](../CHANGELOG.md)
- [Governance](../GOVERNANCE.md)
- [Security policy](../SECURITY.md)
- [Support](../SUPPORT.md)

## Documentation rules

1. Normative semantics belong in the specification.
2. Implementation documentation describes current behavior and must be reconciled when behavior changes.
3. Operational procedures should be reproducible from a clean checkout.
4. Scientific claims must include supporting evidence and limitations.
5. Relative repository links are preferred.
6. Credentials, hidden evaluation answers, and sensitive security artifacts must never be documented in a way that exposes them.

## LLM-friendly navigation

See [llms.txt](../llms.txt) for a concise machine-readable map of authoritative project entry points.
