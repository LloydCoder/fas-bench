# Phase 12.1 — Independent Validation

Phase 12.1 establishes the protocol and machine-readable record needed for
external validation of FAS-Bench measurement claims.

## Required reviewer properties

A review record identifies:

- an evaluator distinct from the benchmark implementation team;
- whether review was blinded;
- the population evaluated;
- methodology and environment digests;
- completion status;
- explicit limitations.

## Agreement

The implementation includes Cohen's kappa for paired categorical judgments.
Agreement statistics are descriptive evidence about reviewer consistency; they
do not by themselves establish ground-truth correctness.

## Replication

An independent validation report should preserve the exact benchmark commit,
case-population digest, methodology digest, execution environment, oracle
versions, and limitations. Repeated evaluations should be independently
reproducible.

## Scientific boundary

The Phase 12.1 gate verifies the review-record contract. It does not fabricate
external reviewers, agreement, replication results, or scientific validity.
The output therefore explicitly records that no external-validation claim is
made by the implementation itself.
