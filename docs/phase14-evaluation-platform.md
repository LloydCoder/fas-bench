# Phase 14 — Evaluation Platform Contract

Phase 14 turns the benchmark core into an evaluation-platform contract without
coupling the benchmark to a specific hosted service.

## Job identity

An evaluation job binds:

- benchmark identity;
- corpus identity;
- evaluator identity;
- scoring identity;
- submission identity;
- environment identity;
- execution-policy identity;
- deterministic seed.

The resulting SHA-256 job identity is content-derived. A timestamp, queue
position, or URL is not an evaluation identity.

## Execution boundary

The platform layer validates and schedules evaluation jobs. It never executes
candidate code directly on the host and never replaces the Phase 9 secure
execution provider.

A hosted service can use this contract for:

- submission registration;
- queueing;
- worker scheduling;
- result storage;
- reproducibility;
- evaluation status;
- organization/team access control.

## Trust boundary

The service control plane, execution workers, artifact storage, hidden corpus,
and evaluator implementation are separate trust domains. Hidden evaluation
material must remain outside public benchmark packages.

## Exit contract

The Phase 14 implementation must provide deterministic job identity,
submission/policy validation, explicit execution-provider boundaries, and
machine-readable job status semantics.
