# Schemas

**Document role:** Phase 2 schema implementation guidance.  
**Authority:** docs/specification.md defines the semantics that schemas must encode.

Phase 1 intentionally does not implement the complete machine-readable schema package.

## Planned schema families

- case
- claim
- evidence
- attack-graph
- verdict
- submission
- evaluation-result
- provenance

Phase 2 MUST encode the canonical identifiers, enumerations, relationships, cardinalities, version fields, and compatibility rules defined by the Phase 1 specification.

Schemas MUST be versioned independently from implementation code and validated in CI.

## Phase 2 constraint

Schema implementation MUST NOT invent missing semantics. If the Phase 1 contract is ambiguous, the ambiguity must be resolved through a specification change before schema semantics are frozen.

## Ground truth

Expected results and hidden evaluation data MUST remain outside the evaluated-system input boundary. Public schemas must not accidentally package hidden ground truth.

## Current status

No claim is made in Phase 1 that the final schemas or schema engine exist.
