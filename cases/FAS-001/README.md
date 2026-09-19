# FAS-001 — Dead SSRF

## Purpose
An attacker-controlled URL reaches the outbound HTTP client, but the effective destination allowlist blocks unauthorized destinations.

## Security hypothesis
An attacker-controlled URL reaches the outbound HTTP client, but the effective destination allowlist blocks unauthorized destinations.

## Attacker model
Unauthenticated public attacker may submit one URL; cannot alter server policy or access the host network directly.

## Environment
Synthetic Linux/Python 3.12 model. No public-network dependency. Credentials are synthetic only.

## Oracle
The deterministic oracle evaluates the effective state in `repository/state.json` and emits machine-readable JSON. It does not import, execute, or derive truth from FAS.

## Ground truth
Structured expected artifacts encode claims, evidence, finding, attack path, verdict, and remediation. This README is explanatory only.

## Limitations
Controlled synthetic experiment; not a claim about production systems. The public initial corpus is a development corpus and is not contamination-resistant.

## Status
VALIDATED, subject to corpus-level CI and release gates.
