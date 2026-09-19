# FAS-Bench Threat Model
**Role:** benchmark security and research threat model.
**Authority:** docs/specification.md.

## Phase 2 schema threats
Threats include oversized objects, pathological nesting, enormous arrays, graph-size denial of service, duplicate identifiers, reference explosion, malicious artifact metadata, parser differentials, unsupported versions, remote $ref dependencies, and evaluator denial of service.

## Controls
Validation is data-only; artifact content is never executed; arbitrary remote references are not retrieved; top-level contract objects are closed; IDs and references are semantically checked; deployment-specific size/depth/graph limits should be bounded.

## Ground-truth protection
Expected verdicts, hidden evidence, evaluator internals, and hidden tests remain outside the public submission contract.

## Limits
Phase 2 does not prove sandbox security, evaluator integrity, contamination resistance, or scientific validity. Those are later-phase empirical/security concerns.
