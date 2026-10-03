# Phase 19 — Adversarial & Robustness Evaluation

Phase 19 makes the benchmark itself an adversarial target. It evaluates whether
systems preserve benchmark-defined security invariants when inputs, evidence,
tools, repositories, or oracle-facing artifacts are manipulated.

## Attack classes

The initial contract covers prompt injection, evidence poisoning, tool-output
manipulation, repository deception, oracle tampering, sandbox attacks, and
benchmark gaming.

## Contract

Each adversarial case has an explicit mutation identity and authoritative oracle
identity. Infrastructure failure is never treated as a successful robustness
result. A PASS requires the observed invariant to match the case oracle.

The benchmark must test both candidate robustness and evaluator integrity. An
adversarial benchmark MUST NOT allow a candidate-controlled answer to become
ground truth.

## Boundary

This phase defines evaluation semantics; secure execution remains delegated to
the Phase 9 execution boundary. Oracle changes remain governed material changes
under Phase 13.1.
