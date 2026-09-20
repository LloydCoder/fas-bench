# Phase 3 — Gold Cases & Ground Truth

Phase 3 turns the Phase 2 executable data contract into a controlled benchmark corpus.

## Corpus status

FAS-001 through FAS-020 are public development cases. Their ground truth is intentionally visible. This corpus is not a hidden evaluation set.

## Case contract

Every case defines:
- security hypothesis and attacker model;
- assets, boundaries, environment and limitations;
- case version independent from benchmark version;
- structured claims, evidence, finding, attack path, verdict and remediation;
- deterministic oracle;
- synthetic credentials and controlled networking;
- provenance and lifecycle state.

## Validation states

Schema-valid, semantically-valid, reproducible, security-validated and release-ready are distinct gates. The normative lifecycle is DRAFT → CONSTRUCTED → SELF-VALIDATED → INDEPENDENTLY_REVIEWED → REPRODUCIBLE → VALIDATED → RELEASE_CANDIDATE → RELEASED. The current public corpus remains IN_REVIEW until release gating is explicitly completed.

A case is not validated because a file exists or because a prose statement says it is vulnerable. The oracle must independently derive an observed security state and agree with structured ground truth.

## Gold cases

FAS-001, FAS-002, FAS-006, FAS-016 and FAS-020 receive enhanced validation, mutation testing, and metamorphic stability checks in the Phase 3 design. FAS-020 specifically represents original-path blocking plus an alternate viable path.

## Public/hidden boundary

The initial corpus is public development data. Future evaluation must use held-out cases, private ground truth, or undisclosed mutations. Public ground truth must never be described as contamination-resistant.

## Reproducibility

Case execution is network-independent by default, uses synthetic credentials, has deterministic state, and emits machine-readable oracle output. Dynamic cases in the initial corpus use a pinned Python container with network disabled, read-only case mounts, dropped capabilities, no-new-privileges, CPU/memory/PID limits, and deterministic cleanup. Future dynamic/containerized cases must preserve or strengthen these controls.

## Security

Intentionally vulnerable case semantics are constrained to synthetic state. No case is permitted to access host credentials, real cloud resources, production systems, Docker sockets, or uncontrolled Internet destinations.

## Future compatibility

Phase 3 produces the structured artifacts required by later evidence, evaluator, graph, remediation, scoring and secure-harness phases without redefining Phase 1 or Phase 2 vocabulary.
