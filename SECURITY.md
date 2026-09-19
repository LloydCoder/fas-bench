# Security Policy
**Authority:** docs/specification.md.

FAS-Bench contains intentional security cases and untrusted benchmark artifacts.

## Reporting
Report infrastructure, evaluator, dependency, CI, or benchmark-integrity vulnerabilities privately to the repository maintainer when public disclosure could compromise evaluation integrity.

## Phase 2 validator security
The validator must process data only. It must not execute artifacts, import submitted modules, trust case-provided schemas, follow attacker-controlled filesystem instructions, or fetch arbitrary remote references.

## Schema threats
Oversized objects, pathological nesting, duplicate IDs, reference explosions, parser differentials, unsupported schema versions, malicious metadata, and denial-of-service are considered in the Phase 2 threat model.

## Ground truth
Hidden truth and evaluator-only material must not be exposed through public fixtures or normal submissions.
