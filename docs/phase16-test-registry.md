# Phase 16 — Benchmark Test Registry & Specification Engine

Phase 16 makes the benchmark test itself a first-class, versioned artifact. A
test specification records its objective, taxonomy, difficulty, oracle type,
evidence requirements, prerequisites, lifecycle state, and source identity.

## Contract

A registry MUST provide deterministic test identity, reject duplicate
test_id/version pairs while allowing historical versions of the same test_id,
record lifecycle state, and distinguish test specification from execution and
release authority. Certified or released tests require a canonical SHA-256
source digest. Requirement lists MUST contain non-empty, unique entries.

Lifecycle transitions are explicit and monotonic through the governed
PROPOSED → DRAFT → REVIEW → VALIDATED → CALIBRATED → CERTIFIED → RELEASED
path, with review/rework and deprecation/retirement paths. A retired test
cannot be reopened through the registry contract.

The registry does not execute candidates, determine ground truth, or approve
releases. Execution remains in Phase 9/14 and approval remains governed by
Phase 13.1.

## Scientific boundary

A registry improves traceability and coverage accounting; it does not by itself
establish that a test population is representative or statistically valid.
