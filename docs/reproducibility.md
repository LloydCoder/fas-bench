# Phase 9 Reproducibility

FAS-Bench uses content-derived identities rather than timestamps or human-selected run IDs.

## Run identity

The authoritative identity incorporates benchmark digest, case-manifest digest, submission digest, evaluator digest, scoring digest, environment/container digest, execution-policy digest, and explicit seed.

A changed score-affecting input therefore changes the run identity.

## Cache identity

The cache key incorporates the same score-affecting inputs. A changed submission, case, evaluator, scoring configuration, environment, or policy cannot reuse the prior result.

Candidate-controlled run IDs are not cache keys.

## Result integrity

Artifacts are hashed by the harness. Results can be serialized into a reproducibility bundle containing result.json and result.sha256. Verification rejects malformed digests, unsafe artifact paths, duplicate artifact paths, and inconsistent terminal status/failure combinations.

## Determinism

The benchmark's authoritative domain evaluators remain deterministic. Candidate stochasticity is a separate concern and should be represented by explicit trial/seed policy rather than hidden averaging.

Wall-clock timestamps are diagnostic metadata and are excluded from the normalized result digest.

## Public versus private data

The current FAS-001 through FAS-020 corpus is public development data. It is not hidden ground truth. Future held-out evaluation must keep private gold data outside candidate-visible mounts and logs.
