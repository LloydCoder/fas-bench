# Phase 10 — Contamination and Gaming Defense

The public FAS-001..FAS-020 corpus is intentionally transparent for development. It is therefore unsuitable as a secret official test set.

Phase 10 establishes the separation required for future held-out evaluation:

- PUBLIC_DEVELOPMENT
- PUBLIC_PRACTICE
- HELD_OUT
- HIDDEN
- OFFICIAL

## Threats

The threat model includes direct memorization, derivative memorization, identifier memorization, template recognition, documentation leakage, Git-history leakage, artifact leakage, cache leakage, cross-run leakage, network retrieval, and benchmark-aware behavior.

The repository scanner is deterministic and checks paths and credential/private-key patterns. It is not a proof of model-training cleanliness.

## Official evaluation

Official evaluation must record evaluation mode, network policy, external lookup permission, hidden-set usage, benchmark version, and case-population digest. A result with network retrieval allowed is not equivalent to a fully offline result.

Invalid, incomplete, non-reproducible, infrastructure-failed, or policy-violating runs are distinct eligibility states and are not silently converted to zero or a security verdict.

## Gaming

Phase 8 scoring remains responsible for actual score semantics. Phase 10 supplies the corpus/mutation layer needed to test pathological strategies. No score changes are introduced solely to favor a desired strategy.
