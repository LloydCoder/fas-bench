# Phase 17 — Official Hidden Evaluation & Contamination Defense

Phase 17 separates public development/practice data from private official and
held-out evaluation populations and makes contamination status explicit.

## Contract

Official corpora MUST have controlled access, a content-derived identity, a
temporal boundary, and an explicit contamination assessment. SUSPECTED or
CONFIRMED contamination blocks official release until governance resolves it.

Contamination findings are evidence-bearing observations, not proof of
training-data history. A repository scan cannot prove that a model has never
seen a test artifact.

The public repository MUST NOT contain official answers, private evaluator
material, credentials, or artifacts that defeat the hidden-test boundary.

## Research basis

Mature benchmark programs commonly separate practice material from hidden
official tests to reduce overfitting and preserve credible evaluation. MLCommons
documents this pattern explicitly for AILuminate. citeturn0search8turn0search13
