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

## Benchmark case isolation
Intentionally vulnerable semantics are confined to synthetic case state. Cases must not access host credentials, Docker sockets, real cloud accounts, production systems, or uncontrolled Internet destinations. Case oracles emit structured machine-readable results and must not expose hidden evaluation truth. Report infrastructure vulnerabilities separately from intentionally vulnerable benchmark semantics.
