# FAS-Bench Architecture

## Purpose

FAS-Bench is an independent evaluation layer for security-analysis systems.

The benchmark is organized around six major layers:

1. Case layer — repository, environment, scenario, and validation fixtures.
2. Ground-truth layer — claims, evidence requirements, verdicts, attack graphs, and remediation state.
3. Submission layer — normalized results emitted by an evaluated system.
4. Verification layer — deterministic checks against observable benchmark artifacts.
5. Scoring layer — multidimensional metrics and calibration.
6. Provenance layer — versions, hashes, environments, and execution metadata.

## Independence invariant

The evaluator must not depend on FAS or any other evaluated system.

The benchmark contract is the interface between the case and the system under test.

## Primary flow

case → analysis → structured submission → evidence verification → verdict evaluation → graph evaluation → remediation verification → metrics

## Security boundary

Case repositories, prompts, dependencies, and runtime fixtures are untrusted.

Evaluation environments must isolate benchmark execution from the host and from unrelated workloads.

## Current implementation status

Architecture is defined; implementation is intentionally staged behind schema and gold-case validation.
