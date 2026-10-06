# Contributing to FAS-Bench

FAS-Bench is an evidence-first security benchmark. Contributions must preserve deterministic semantics, evidence integrity, secure execution boundaries, reproducibility, benchmark independence, and historical comparability.

> [!IMPORTANT]
> [docs/specification.md](docs/specification.md) is the normative benchmark contract. Implementation or documentation changes must not silently redefine it.

## Development setup

Supported development baseline:

- Python 3.12+
- Git
- Docker for secure-execution integration tests

```bash
git clone https://github.com/LloydCoder/fas-bench.git
cd fas-bench
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Contribution flow

1. Fork the repository.
2. Create a focused branch from `main`.
3. Make the smallest coherent change.
4. Add or update tests and documentation.
5. Run the relevant local validation.
6. Commit with a clear message; Conventional Commits are recommended.
7. Open a pull request using the repository template.
8. Respond to review and keep CI green.

Do not bypass failing gates or rewrite benchmark truth merely to make a check pass.

## Validation

At minimum, run:

```bash
ruff format --check .
ruff check .
pytest
python -m build
fas-bench corpus validate
fas-bench contamination scan
fas-bench contamination independence
fas-bench benchmark doctor
```

Changes to release, secure execution, schemas, evaluators, or benchmark semantics require the narrower verification suites described in the relevant documentation.

## Benchmark independence

FAS-Bench MUST remain independent of evaluated products. It MUST NOT import, require, execute, or derive ground truth from FAS, ThreatFade, Tinlance, or another evaluated system.

Core evaluator behavior MUST be case-independent: do not branch on individual case IDs to manufacture expected outcomes.

## Case contributions

New or changed cases should include:

- a falsifiable security hypothesis;
- attacker model and assumptions;
- synthetic credentials only;
- controlled repository state;
- structured ground truth;
- deterministic oracle;
- expected evidence and verdict semantics where applicable;
- provenance and content identity;
- limitations and versioning information.

Public cases are development/practice data. Never commit hidden official answers.

## Evidence and evaluator contributions

Evidence must point to authoritative case artifacts and deterministic facts. Submitted evidence must never be executed.

Finding/verdict changes must preserve the distinction between `UNKNOWN` and `NOT_EXPLOITABLE` and include positive, negative, contradiction, missing-evidence, cross-case, and tamper coverage where relevant.

## Graph and remediation contributions

Graph changes must preserve canonicalization, finite traversal, semantic edge direction, evidence linkage, and deterministic identity.

Remediation changes must preserve baseline/post-remediation semantics, alternate-path analysis, control weakening detection, and regression classification.

## Secure execution contributions

Never run candidate or malicious benchmark code directly on the host.

Phase 9 execution changes must preserve:

- fail-closed behavior;
- immutable image references;
- network isolation;
- non-root execution;
- dropped capabilities;
- no-new-privileges;
- read-only root;
- bounded resources;
- isolated workspaces;
- artifact integrity validation.

Do not add privileged containers, Docker-socket mounts, arbitrary host mounts, real credentials, mutable security-boundary image tags, or host-execution fallbacks.

## Phase 10–21 contributions

Changes affecting corpus release, contamination, hidden evaluation, agentic scenarios, adversarial robustness, measurement science, provenance, or governance must update the applicable specification, tests, changelog, and compatibility notes.

Material CASE, ORACLE, SCHEMA, SCORING, EVALUATOR, HARNESS, RELEASE, or INFRASTRUCTURE changes require documented rationale and the review dimensions in [GOVERNANCE.md](GOVERNANCE.md).

## Documentation

Use the existing documentation layers and keep relative links working. Explain whether a statement is normative, implementation-specific, operational, or research-limitation content.

If implementation and documentation disagree, do not silently choose one. Reconcile the discrepancy and identify the normative source.

## Pull requests

A PR should state:

- what changed;
- why it changed;
- how it was validated;
- security/integrity impact;
- benchmark comparability impact;
- documentation and changelog impact.

See [.github/pull_request_template.md](.github/pull_request_template.md).
