# Benchmark Cases

Phase 3 establishes the initial **public development corpus** FAS-001 through FAS-020.

## Contract

Each case contains a security hypothesis, explicit attacker model, controlled environment, machine-readable expected claims/evidence/finding/attack-path/verdict/remediation artifacts, and a deterministic oracle.

Schema-valid, semantically-valid, reproducible, security-validated, and release-ready are distinct states.

## Ground-truth boundary

This repository intentionally exposes the development corpus and its ground truth. It is **not** a hidden evaluation set. Future evaluation must use held-out cases, undisclosed mutations, or private evaluation artifacts.

## Safety

Cases use synthetic credentials and controlled local state. No case may require access to real cloud accounts, host credentials, Docker sockets, production systems, or uncontrolled Internet destinations.

## Validation

`fas-bench cases validate-all` validates the corpus package and cross-references.

`fas-bench cases validate-gold` focuses the five gold cases: FAS-001, FAS-002, FAS-006, FAS-016, FAS-020.

`fas-bench cases reproduce FAS-001` executes the deterministic case oracle and compares its observed state with the structured expected verdict.\n\n`cases/coverage.json` records truthful category, difficulty, and verdict coverage for the public development corpus and is checked against the registry by corpus validation.

## Difficulty

The initial corpus deliberately spans L1_LOCAL through L5_CROSS_SYSTEM. It is not statistically balanced.

## Verdict coverage

The corpus includes EXPLOITABLE, NOT_EXPLOITABLE, CONDITIONALLY_EXPLOITABLE, REMEDIATED, REMEDIATION_FAILED, and UNKNOWN. REGRESSED is not represented by the initial 20 cases; a future regression case should be added rather than overloading another verdict.


## Oracle classes

The initial gold cases use DYNAMIC security-property validation through loopback-only synthetic services. Other cases may remain STATIC where runtime execution is not required. A dynamic oracle must demonstrate the security property itself, not merely process success.
