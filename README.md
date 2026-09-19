# FAS-Bench

**Forensic Agent Security Benchmark**

FAS-Bench is an open benchmark for evaluating evidence-based security analysis by AI agents, scanners, security tools, and hybrid human/machine systems.

> **Scanners find signals. FAS-Bench measures whether a system can prove what those signals actually mean.**

## Phase 1 status

**Phase 1 — Specification & Benchmark Contract: complete on the phase-1 branch pending CI verification and merge.**

The normative contract is [docs/specification.md](docs/specification.md). It defines the benchmark vocabulary and boundaries that Phase 2 will encode.

FAS-Bench is not yet claiming a scientifically validated benchmark corpus, validated scoring weights, universal real-world generalization, or a production evaluator.

## Why this benchmark exists

A security tool can identify a suspicious sink while being wrong about reachability. It can report an IDOR without proving the authorization boundary. It can find a vulnerable dependency without determining whether the vulnerable functionality is reachable. It can call a remediation fixed while an alternate attack path remains.

AI security systems add another failure mode: persuasive but nonexistent evidence.

FAS-Bench evaluates the chain:

**signal → claim → evidence → reachability → security boundary → exploitability → attack path → impact → remediation → verification → regression**

## What FAS-Bench evaluates

- detection;
- investigation;
- evidence quality and integrity;
- reachability and data/control flow;
- authentication and authorization;
- AI-agent security;
- MCP security;
- supply-chain security;
- secrets and sensitive data;
- infrastructure/cloud controls;
- cross-component attack paths;
- remediation verification;
- regression detection;
- confidence calibration;
- efficiency.

## Independence from FAS

FAS-Bench is an independent benchmark.

**FAS is one candidate evaluated system, not the benchmark reference implementation.**

FAS-Bench MUST remain usable without FAS and MUST NOT import, require, execute, or derive ground truth from FAS. FAS can later be evaluated alongside other systems using the same contract.

## Canonical taxonomy

| ID | Category |
|---|---|
| C1 | Reachability |
| C2 | Data Flow / Taint |
| C3 | Authentication / Authorization |
| C4 | AI Agent Security |
| C5 | MCP Security |
| C6 | Supply Chain |
| C7 | Secrets / Sensitive Data |
| C8 | Infrastructure / Cloud |
| C9 | Cross-Component Attack Paths |
| C10 | Remediation / Regression |

Difficulty is structural:

**L1 Local → L2 Multi-function → L3 Multi-component → L4 Agentic → L5 Cross-system**

## Canonical verdicts

- EXPLOITABLE
- NOT_EXPLOITABLE
- CONDITIONALLY_EXPLOITABLE
- REMEDIATED
- REMEDIATION_FAILED
- REGRESSED
- UNKNOWN

UNKNOWN is intentionally distinct from NOT_EXPLOITABLE.

## Evidence-first evaluation

Evidence is a first-class benchmark object. Canonical evidence types include source/sink locations, transformations, data flow, configuration, dependencies, identities, permissions, policies, trust boundaries, runtime/network events, tool invocations, tests, remediation, environment state, and documentation.

Evidence roles are DIRECT, SUPPORTING, MISSING, and CONTRADICTORY. Verification states are VERIFIED, INVALID, UNRESOLVED, and CONTRADICTED.

A correct verdict supported by invalid evidence is not equivalent to a correct verdict supported by verified evidence.

## Attack paths and effective security

FAS-Bench evaluates security paths as graphs rather than prose alone.

Canonical graph nodes include actors, inputs, functions, services, processes, data, resources, tools, agents, MCP servers, identities, permissions, policies, network zones, trust boundaries, sinks, and impacts.

The benchmark distinguishes the **apparent graph** from the **effective security graph** after authentication, authorization, IAM, policies, network controls, sandboxing, validation, runtime restrictions, and other boundaries are applied.

## Initial case registry

The initial design registry contains:

FAS-001 Dead SSRF; FAS-002 Reachable SSRF; FAS-003 Sanitized Command Injection; FAS-004 Indirect Command Injection; FAS-005 IDOR; FAS-006 Authorization False Positive; FAS-007 Excessive Agent Capability; FAS-008 Agent Sandbox Boundary; FAS-009 MCP Tool Poisoning; FAS-010 Safe MCP Server; FAS-011 Malicious Dependency; FAS-012 Vulnerable but Unreachable Dependency; FAS-013 Revoked Secret; FAS-014 Live Credential Attack Path; FAS-015 Public Storage Exposure; FAS-016 Privilege Boundary; FAS-017 Multi-Service Compromise; FAS-018 Agent → CI/CD → Production; FAS-019 Verified Fix; FAS-020 Fake Fix / Alternate Path.

Initial designated gold cases: FAS-001, FAS-002, FAS-006, FAS-016, FAS-020.

These are a design registry, not a scientifically validated corpus.

## Evaluation pipeline

1. Reconnaissance
2. Independent analysis
3. Structured result submission
4. Deterministic evidence verification
5. Verdict evaluation
6. Attack-path graph normalization/comparison
7. Remediation evaluation
8. Regression evaluation
9. Calibration and efficiency analysis

## Provisional scoring

The Phase 1 scoring weights are explicitly provisional and must be empirically validated in Phase 8. Reports should expose component metrics and failure modes rather than hiding them behind one aggregate score.

The benchmark also supports evidence-integrity measurement, Brier score, expected calibration error, reliability analysis, and efficiency metadata.

## Security and contamination

Benchmark cases are untrusted security artifacts. Dynamic execution must be isolated, outbound network access should default to denied, credentials must be synthetic, and hidden ground truth must remain outside the evaluated-system input boundary.

Planned contamination defenses include public development cases, held-out cases, hidden tests, semantic-preserving mutations, identifier renaming, architecture-preserving transformations, temporal splits, mutation variants, and leakage detection.

## Reproducibility

Evaluations should record benchmark/case/evaluator/submission versions, system/model metadata, configuration, environment, dependencies, timestamps, seeds, tool versions, network policy, container/image identity, and content digests.

## Documentation authority

1. [Normative specification](docs/specification.md)
2. [Architecture](docs/architecture.md)
3. [Evaluation](docs/evaluation.md)
4. [Methodology](docs/methodology.md)
5. [Threat model](docs/threat-model.md)
6. [Cases](cases/README.md)
7. [Schemas](schemas/README.md)
8. [Tests](tests/README.md)
9. [Contributing](CONTRIBUTING.md)
10. [Security](SECURITY.md)
11. [Changelog](CHANGELOG.md)

The specification is the only normative source.

## Ten-phase roadmap

1. Specification & Benchmark Contract
2. Schema & Data Model
3. Gold Cases & Ground Truth
4. Deterministic Evidence Engine
5. Verdict & Finding Evaluator
6. Attack-Path & Security-Graph Engine
7. Remediation & Regression Engine
8. Scoring, Calibration & Benchmark Analytics
9. Secure Evaluation Harness & Reproducibility
10. Benchmark Corpus, Contamination Defense & Release

Phase 1 defines the contract; later phases implement and validate it. Phase 1 deliberately does not build the complete evaluator or corpus.

## Repository structure

    fas-bench/
    ├── .github/workflows/ci.yml
    ├── cases/README.md
    ├── docs/
    │   ├── architecture.md
    │   ├── evaluation.md
    │   ├── methodology.md
    │   ├── specification.md
    │   └── threat-model.md
    ├── schemas/README.md
    ├── src/fas_bench/
    ├── tests/
    ├── CHANGELOG.md
    ├── CONTRIBUTING.md
    ├── LICENSE
    ├── README.md
    ├── SECURITY.md
    └── pyproject.toml

## Local CI parity

    python -m pip install -e ".[dev]"
    ruff format --check .
    ruff check .
    pytest
    python -m build
    python -m pip install --force-reinstall dist/*.whl
    python -c "import fas_bench; print(fas_bench.__version__)"

## Research positioning

FAS-Bench follows benchmark-engineering practices seen in projects such as [SEC-bench](https://github.com/SEC-bench/SEC-bench) and [SWE-bench](https://github.com/SWE-bench/SWE-bench), including reproducible environments and structured evaluation artifacts. Its task semantics are different: the central axis is evidence-grounded security adjudication and verification.

No claim of uniqueness, state-of-the-art performance, or scientific validation is made by Phase 1.

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) for benchmark-design governance and [SECURITY.md](SECURITY.md) for infrastructure and benchmark-integrity reporting.

## License

Apache License 2.0. See [LICENSE](LICENSE).

## Citation

A formal research citation will be published with the first research release. Until then:

**LloydCoder/fas-bench — FAS-Bench: Forensic Agent Security Benchmark**
