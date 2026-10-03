# Phase 20 — Measurement Science & Independent Validation

Phase 20 turns benchmark reliability into an explicit measurement layer.

## Included primitives

- Wilson uncertainty intervals for fixed-corpus proportions;
- deterministic bootstrap intervals;
- Cohen's kappa for paired categorical ratings;
- stratified population counts;
- machine-readable reliability reports.

## Scientific boundary

These calculations describe the measured benchmark population. They do not,
without an empirical sampling design, justify universal real-world claims.
Independent replication, external review, test-retest studies, power analysis,
and sensitivity analysis remain evidence-producing activities.

NIST treats reliable measurement and evaluation as foundational to trustworthy AI
technology assessment, while MLCommons has explicitly pursued benchmark
reliability research.

## Independence

Reference ratings and benchmark oracles remain separate from candidate output.
Agreement statistics cannot turn a candidate-controlled label into ground truth.
