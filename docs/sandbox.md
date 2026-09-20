# Phase 9 Sandbox

## Filesystem

Per-run temporary directories contain separate input and output transport boundaries. Candidate input is read-only. Candidate workspace is an ephemeral tmpfs. Arbitrary host mounts are prohibited.

The collector rejects symlinks and special files and enforces artifact count and byte limits.

## Network

The default policy is network-deny. There is no host networking, Internet access, arbitrary DNS, or published port. Restricted network providers are a future extension and are not silently enabled.

## Process and privilege

Candidate execution uses private PID/IPC/cgroup namespaces, a non-root UID/GID, no-new-privileges, all capabilities dropped, and the Docker built-in seccomp profile. The harness does not claim escape-proof isolation.

## Resource governance

CPU, memory, PID count, open files, workspace, artifact count, artifact bytes, stdout/stderr, and execution time are bounded.

Timeout cleanup removes the container and its descendants through the container boundary. Cleanup failure is explicit and prevents a successful authoritative result.

## Credentials and gold data

The host environment is not inherited. Synthetic benchmark credentials must be supplied explicitly and must not grant real external access. Hidden gold data, evaluator source, scoring configuration, and private case assets must never be mounted into candidate environments.

## Observability

The harness observes process exit status, bounded stdout/stderr, artifact metadata and hashes, and execution policy metadata. It does not claim full kernel or encrypted-network observability.
