# Phase 9 Harness

The Phase 9 harness is the fail-closed execution boundary for untrusted candidate workloads. Docker is the only execution provider in the current implementation.

## Lifecycle

CREATED -> VALIDATING -> PREPARING -> READY -> RUNNING -> COLLECTING -> EVALUATING -> SCORING -> FINALIZING -> COMPLETED

Terminal states include FAILED, CANCELLED, TIMED_OUT, INVALID, SECURITY_VIOLATION, PARTIAL, and CLEANUP_FAILED.

The orchestrator is intentionally thin: evidence, verdict, graph, remediation, scoring, and analytics remain authoritative in Phases 4–8.

## Container policy

Official execution requires an immutable @sha256: image reference. The runner verifies that the local image exposes the requested digest before execution.

The default container uses network none; private PID, IPC, and cgroup namespaces; read-only root; all Linux capabilities dropped; no-new-privileges; Docker built-in seccomp; non-root numeric UID/GID; bounded memory, CPU, PIDs, open files, workspace, artifacts, output, and wall-clock time; isolated input/workspace/output; and no inherited host environment.

No Docker socket, host path, host network, host PID namespace, or host credential directory is mounted.

## Artifact boundary

Candidate output is collected only from the dedicated output transport directory. Symlinks, sockets, FIFOs, devices, and other special files are rejected. Paths are canonicalized and bounded before hashing.

Candidate-provided hashes are never authoritative; the harness computes SHA-256 digests itself.

## Failure semantics

Infrastructure failures and security violations are not converted into benchmark scores. A compromised or unevaluable run remains explicitly unevaluable.

TIMEOUT, OUTPUT_LIMIT, SECURITY_VIOLATION, and cleanup failures are represented separately from an ordinary candidate process exit.

## Residual security assumptions

The host OS, Linux kernel, container runtime, hardware, and Docker daemon are part of the trusted computing base. Kernel/container-runtime vulnerabilities and physical host compromise are outside this Phase 9 boundary.
