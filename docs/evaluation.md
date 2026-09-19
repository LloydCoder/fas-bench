# FAS-Bench Evaluation
**Role:** evaluation methodology and metric interpretation.
**Authority:** docs/specification.md.

## Schema validation
Every serialized object is first checked against its Draft 2020-12 family schema.

## Semantic validation
Cross-object references, graph/path relationships, version compatibility, conditional verdict semantics, remediation consistency, and evaluation arithmetic are checked by Python.

## Invalid submission handling
Structural failures are SCHEMA_INVALID. Cross-object failures are SEMANTIC_INVALID. Errors contain deterministic codes and paths.

## Evidence integrity
Evidence is independently represented from findings and verdicts. Phase 4 will determine whether submitted evidence is actually observable and valid.

## Evaluation-result structure
Raw, normalized, weighted, capped, penalized, and invalid components are represented separately. Phase 8 will define and validate scoring policy.

## Version compatibility
Benchmark version 0.1.0 and schema family version 0.1 are currently supported.

## Determinism
Given identical inputs, schema resources, validator version, and configuration, validation produces deterministic results.
