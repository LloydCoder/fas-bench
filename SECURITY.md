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

## Phase 5 evaluator security
The finding evaluator treats submissions as hostile data. It validates finite confidence values, requires case integrity before trusting ground truth, preserves cross-case identity, never executes submitted evidence, separates evaluator errors from UNKNOWN, and does not use evaluated-system output as ground truth.

## Phase 6 evaluator security
Graph submissions are untrusted data. The graph engine performs safe JSON parsing only, never executes submission content, and enforces finite graph/path/traversal limits.

## Benchmark scoring security
Phase 8 candidate submissions are untrusted data. The scoring/reporting layer must not execute candidate code, import candidate modules, accept candidate aggregate scores as authoritative, or permit candidate data to alter gold truth or scoring configuration.

## Phase 9 secure execution
Candidate workloads and hostile case artifacts are never executed directly on the host. The v0.1 execution provider is Docker and is fail-closed when the daemon or immutable image is unavailable.

The Phase 9 boundary requires an immutable image digest, network denial, private namespaces, read-only root, dropped capabilities, no-new-privileges, built-in seccomp, non-root execution, bounded resources, isolated input/workspace/output, bounded stdout/stderr, and post-run artifact validation.

The harness rejects symlinks and special output files, never inherits the host environment, never mounts the Docker socket or host credential directories, and computes artifact hashes itself.

Container isolation is not claimed to be escape-proof. The host kernel, container runtime, hardware, and Docker daemon remain trusted-computing-base assumptions. Physical host compromise and unknown kernel/runtime vulnerabilities are outside the supported boundary.
