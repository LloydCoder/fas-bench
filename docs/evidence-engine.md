# Phase 4 — Deterministic Evidence Engine

Phase 4 provides the evidence-verification substrate. It verifies whether a submitted evidence record corresponds to a fact that can be checked against the authoritative case artifacts. It does **not** decide the final security verdict.

## Pipeline

Case loader → case integrity → expected evidence → submission parser → normalization → resolver → verifier → relationship/duplicate analysis → coverage and integrity result.

## Evidence semantics

A verified evidence item establishes only the underlying fact represented by the evidence. It does not establish exploitability, attack-path viability, remediation success, or the final benchmark verdict.

The engine preserves these states:

- `VERIFIED` — the submitted evidence matches an authoritative case fact.
- `INVALID` — the evidence conflicts with an authoritative fact or contains an invalid reference.
- `UNRESOLVED` — the evaluator cannot deterministically establish the requested fact.
- `CONTRADICTED` — the evidence is explicitly classified as conflicting evidence.

Evidence roles remain `DIRECT`, `SUPPORTING`, `MISSING`, and `CONTRADICTORY`.

## Structured facts

Evidence may contain a structured `fact` with `artifact_path`, `key`, `operator`, and `value`. The artifact is resolved relative to the case root and the value is read from the benchmark-controlled artifact. The evaluator never executes submitted evidence content.

## Source locations

Locations are checked against the case repository. The engine verifies repository-relative path safety, file existence, valid line ranges, optional column ranges, Python symbols where deterministic AST inspection is possible, and optional exact snippets.

A valid line is not automatically a valid sink, source, or data-flow claim.

## Deterministic identity

Evidence identity is a SHA-256 digest of canonical evidence semantics. Presentation-only differences such as JSON key order and repository-relative path normalization do not change identity. Material differences such as line numbers, values, paths, or relationships do.

Evidence IDs themselves are excluded from identity so duplicate facts cannot inflate coverage.

## Coverage and integrity

The result preserves raw counts for submitted, verified, invalid, unresolved, contradicted, missing, and duplicate evidence. Evidence Hallucination Rate is invalid divided by submitted, with zero submissions producing 0.0.

Coverage is calculated against expected evidence roles rather than raw submission volume.

## Security boundary

Case paths are resolved beneath the declared case root. Absolute paths, traversal, NUL-containing paths, and resolved symlink escapes are rejected. Submission data remains data and is never evaluated as Python, shell, or another executable language.

Case integrity is checked before expected evidence is trusted. An integrity failure is an evaluator failure, not a security verdict.

## Phase boundary

Phase 4 intentionally does not score exploitability, attack paths, remediation, regression, calibration, or composite benchmark performance. Those later phases consume this normalized evidence result rather than reimplementing evidence resolution.


## Phase 5 handoff

The evidence engine is the sole source of submitted-evidence verification for Phase 5. Verdict evaluation consumes its VERIFIED/INVALID/UNRESOLVED/CONTRADICTED states, coverage, duplicate handling, and integrity statistics and does not reimplement artifact resolution or evidence identity.
