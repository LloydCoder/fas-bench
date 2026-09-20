# Phase 9 — Secure Evaluation Harness & Reproducibility

Phase 9 is the execution trust boundary for hostile candidate workloads. It is deliberately fail-closed: the benchmark never falls back to direct host execution when isolation is unavailable.

## Security contract
- Docker is the only execution backend in v0.1; the daemon and image must be available before execution.
- Images must be referenced by immutable @sha256: digest.
- Network is disabled; the container root filesystem is read-only.
- All Linux capabilities are dropped and no-new-privileges is enabled.
- Candidate processes run as a non-root numeric UID/GID.
- PID, CPU, memory, workspace/tmpfs, timeout, and captured-output limits are mandatory.
- Candidate code receives no repository secrets, GitHub token, Docker socket, host workspace, or arbitrary host path.
- Candidate input is copied into a read-only /input; writable /workspace and /output are ephemeral tmpfs filesystems.
- Candidate commands are passed as argv without a shell and replace the image entrypoint.
- Each run receives a content-derived run identifier and UTC/C locale environment.
- Output artifacts are hashed before cleanup and a canonical manifest digest is recorded.
- Timeout and cleanup failures remain explicit execution states.

## Reproducibility
A run identity is derived from case ID, submission ID, input digest, and execution policy. Results preserve policy, timestamps, status, exit code, captured output, artifact hashes, and input digest. Re-running the same immutable image/policy/input yields an independently inspectable run.

## Failure semantics
ISOLATION_UNAVAILABLE, IMAGE_UNAVAILABLE, INPUT_INVALID, TIMEOUT, OUTPUT_LIMIT, and EXECUTION_FAILED are not security verdicts. The evaluator must not convert infrastructure or evaluator failure into an exploitable/not-exploitable conclusion.

## Design boundary
Phase 4 remains evidence authority; Phase 5 verdict authority; Phase 6 graph authority; Phase 7 remediation authority; Phase 8 measurement authority. Phase 9 executes only the workload required by an execution contract and records the resulting observations.

The harness retains Docker's default seccomp profile rather than weakening it, and combines it with network isolation, capability dropping, no-new-privileges, and resource constraints.
