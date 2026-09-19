# FAS-Bench

**FAS-Bench (Forensic Agent Security Benchmark)** is an open, evidence-first benchmark for evaluating whether AI agents, security scanners, and security-analysis systems can **detect, investigate, prove, and verify security findings**.

> **Scanners find signals. FAS-Bench measures whether a system can prove what those signals actually mean.**

[![Status](https://img.shields.io/badge/status-research%20prototype-blue)](https://github.com/LloydCoder/fas-bench)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)

## Why FAS-Bench?

A security tool can correctly identify a suspicious sink and still be wrong about whether an attacker can reach it.

It can report an IDOR without proving the authorization boundary.

It can identify a vulnerable dependency without determining whether the vulnerable functionality is reachable.

It can report a remediation as fixed because one path disappeared while an alternate path remains exploitable.

And an AI security agent can produce a convincing explanation backed by inaccurate or nonexistent evidence.

FAS-Bench is designed to measure these distinctions explicitly.

The benchmark evaluates more than "did the system find a vulnerability?"

It evaluates whether the system can establish a defensible chain from:

**signal → evidence → reachability → security boundary → exploitability → attack path → impact → remediation → verification**

## What FAS-Bench evaluates

FAS-Bench is designed to evaluate five core capabilities:

| Capability | Question |
|---|---|
| **Detect** | Did the system identify the relevant security condition? |
| **Investigate** | Did it trace the relevant code, data, identity, configuration, and trust boundaries? |
| **Prove / Disprove** | Did it correctly establish whether exploitation is possible under the stated environment? |
| **Reconstruct** | Did it recover the meaningful attack path and impact rather than only naming a vulnerability class? |
| **Verify** | Did it determine whether remediation actually removed the vulnerability, including alternate or residual paths? |

The benchmark deliberately rewards **evidence-backed correctness**, not persuasive prose.

## Core principle

A useful security benchmark must distinguish:

1. Correct finding + correct evidence
2. Correct finding + invalid or insufficient evidence
3. Incorrect finding + plausible-looking evidence
4. Correct vulnerability class + incorrect exploitability conclusion
5. Correct original finding + failed remediation verification
6. Correct uncertainty when the available evidence is insufficient

The evaluator therefore treats evidence and reasoning as first-class benchmark objects.

> **Correct verdict + invalid evidence must score materially below correct verdict + verified evidence.**

Likewise:

> **A signal detector that cannot adjudicate exploitability should not receive the same credit as a system that proves the security condition.**

## Benchmark scope

FAS-Bench targets modern software and security-analysis systems, including:

- AI security agents
- LLM coding agents
- autonomous security agents
- SAST and code-analysis systems
- SCA/dependency scanners
- rule-based security analyzers
- Semgrep-based systems
- vulnerability-management systems
- MCP-aware security systems
- hybrid human + machine systems
- research prototypes
- future security-analysis systems

FAS-Bench is **tool-agnostic**.

It does not require FAS, Semgrep, Snyk, MCP, a particular LLM, or a particular agent framework.

**FAS is one system that may be evaluated by FAS-Bench, not the benchmark's reference implementation.**

## Initial security taxonomy

| ID | Category | Focus |
|---|---|---|
| C1 | Reachability | Whether a security-sensitive operation is actually reachable |
| C2 | Data Flow / Taint | Whether attacker-controlled data reaches a security-sensitive sink |
| C3 | Authentication / Authorization | Identity, access-control, and privilege-boundary reasoning |
| C4 | AI Agent Security | Agent capabilities, execution boundaries, and unsafe autonomy |
| C5 | MCP Security | Tool exposure, authorization, poisoning, and trust boundaries |
| C6 | Supply Chain | Dependencies, build/install behavior, and reachable vulnerable components |
| C7 | Secrets / Sensitive Data | Credential exposure, validity, access, and current exploitability |
| C8 | Infrastructure / Cloud | IAM, storage, network, policy, and effective permissions |
| C9 | Cross-Component Attack Paths | Multi-service and multi-trust-boundary compromise chains |
| C10 | Remediation / Regression | Fix verification, residual paths, and regressions |

## Verdict model

FAS-Bench uses explicit verdicts rather than vague severity labels:

- EXPLOITABLE
- NOT_EXPLOITABLE
- CONDITIONALLY_EXPLOITABLE
- REMEDIATED
- REMEDIATION_FAILED
- REGRESSED
- UNKNOWN

The distinction is intentional.

A vulnerable-looking function behind a proven authorization boundary is not equivalent to an exploitable endpoint. A revoked credential found in repository history is not equivalent to a currently usable credential.

## Evidence model

Benchmark submissions are expected to cite evidence that can be independently checked.

Evidence may include:

- source locations
- symbols and call sites
- AST facts
- data-flow relationships
- source/sink relationships
- transformations and sanitization
- dependency metadata
- configuration
- identity information
- permissions
- authorization policies
- trust boundaries
- runtime events
- network observations
- tool invocations
- test results
- remediation changes
- environment state
- relevant documentation

Evidence is classified by role:

- **Direct** — directly establishes a claim
- **Supporting** — strengthens a claim but is not sufficient by itself
- **Missing** — evidence required by the claim but not supplied
- **Contradictory** — evidence that conflicts with the claim

The evaluator independently verifies submitted evidence wherever deterministic verification is possible.

## Attack-path model

FAS-Bench models security reasoning as a graph rather than only as a text explanation.

A path can include:

**actor → input → function → service → identity → permission → policy → resource → sink → impact**

Graph elements can represent actors, inputs, functions, processes, services, data, resources, tools, agents, MCP servers, identities, permissions, policies, network zones, trust boundaries, sinks, and impacts.

Edges capture relationships such as:

- CALLS
- FLOWS_TO
- READS
- WRITES
- INVOKES
- AUTHENTICATES_AS
- AUTHORIZED_BY
- CROSSES
- TRANSFORMS
- REACHES
- DEPENDS_ON
- TRIGGERS

This makes multi-step reasoning measurable and comparable across systems.

## Difficulty model

| Level | Description |
|---|---|
| **L1** | Local reasoning within a small component |
| **L2** | Multi-function or indirect data/control flow |
| **L3** | Multi-component or security-boundary reasoning |
| **L4** | Agentic, tool, or MCP-mediated reasoning |
| **L5** | Cross-system attack paths spanning multiple trust boundaries |

Difficulty is not intended to mean merely "more lines of code." A small case with a subtle authorization boundary can be harder than a large repository with an obvious vulnerable sink.

## Initial case families

The first benchmark architecture includes:

- dead / blocked SSRF
- reachable SSRF
- sanitized command injection
- indirect command injection
- IDOR
- authorization false positives
- excessive agent capability
- agent sandbox boundaries
- MCP tool poisoning
- safe MCP server design
- malicious dependencies
- unreachable vulnerable dependencies
- revoked secrets
- live credentials
- public storage exposure
- effective IAM privilege boundaries
- multi-service compromise
- agent → CI/CD → production attack paths
- verified remediation
- failed remediation with an alternate path

The initial corpus is intentionally small and controlled. It will be expanded only after the evaluation model and ground truth are validated.

## Case architecture

A benchmark case is designed around machine-verifiable ground truth rather than a prose answer key.

Target structure:

    case/
    ├── repository/
    ├── environment/
    ├── scenario.yaml
    ├── expected/
    │   ├── findings.json
    │   ├── evidence.json
    │   ├── attack_paths.json
    │   ├── remediation.json
    │   └── verdict.json
    ├── tests/
    └── README.md

The exact schema is versioned independently from case content.

## Evaluation pipeline

1. **Reconnaissance** — permitted repository, environment, and task information.
2. **Independent analysis** — the system performs its security analysis without hidden ground truth.
3. **Structured submission** — the system emits a machine-readable result.
4. **Evidence verification** — submitted evidence is checked against the benchmark instance.
5. **Verdict evaluation** — findings are compared with ground truth.
6. **Attack-path evaluation** — submitted paths are normalized and compared with the expected security graph.
7. **Remediation evaluation** — fix claims are checked against the post-remediation state.
8. **Regression evaluation** — previously closed paths are tested for reintroduction or alternate paths.
9. **Calibration and efficiency analysis** — confidence, cost, runtime, and operational metrics are reported separately.

## Scoring philosophy

FAS-Bench is intentionally **multi-dimensional**.

A single leaderboard number can hide important failure modes, so the benchmark should report:

- finding identification
- verdict correctness
- evidence validity and coverage
- reachability reasoning
- security-boundary reasoning
- attack-path completeness
- impact reconstruction
- remediation verification
- confidence calibration
- efficiency
- false-positive resistance
- evidence hallucination rate

The v0.1 scoring weights are provisional and must be empirically validated against expert-reviewed gold cases before being presented as scientifically final.

## Benchmark integrity

A security benchmark must also defend itself.

Cases can contain intentionally vulnerable code, malicious-looking instructions, fake credentials, poisoned dependencies, or attacker-controlled artifacts.

Therefore:

- benchmark cases are untrusted test data
- case execution must be isolated
- arbitrary case code must never execute directly on the evaluator host
- dynamic tests must run in controlled environments
- benchmark credentials must be synthetic
- outbound network access should be denied by default
- hidden ground truth must not be exposed to evaluated systems
- evaluation artifacts should be content-addressed where practical
- dependency versions should be pinned
- benchmark and evaluator versions must be recorded

Public benchmark artifacts should be designed so that publication does not automatically disclose every hidden evaluation signal.

## Reproducibility

Every evaluation should be attributable to an explicit versioned environment.

The intended provenance record includes:

- benchmark version
- case version
- evaluator version
- result-schema version
- dataset digest
- ground-truth digest
- environment version
- dependency lockfile
- container/image identifier where applicable
- model and agent metadata
- tool configuration
- execution configuration

The goal is that a result can be independently reproduced and audited rather than treated as an opaque leaderboard number.

## Contamination resistance

Because FAS-Bench is public, benchmark contamination is a first-class research concern.

Planned mechanisms include:

- public development cases
- held-out evaluation cases
- hidden tests
- architecture-preserving mutations
- identifier renaming
- semantic-preserving transformations
- temporal splits
- mutation-based variants
- leakage detection
- controlled private evaluation sets

The benchmark should measure whether a system learned security reasoning rather than whether it memorized a case identifier or answer.

## Research positioning

FAS-Bench is adjacent to, but deliberately different from, existing security benchmarks.

**SEC-bench** evaluates LLM agents on real-world software security tasks, including proof-of-concept generation and vulnerability patching. It emphasizes reproducible vulnerability instances and automated evaluation. See the SEC-bench repository and NeurIPS 2025 paper.

Other projects evaluate cybersecurity reasoning or autonomous-agent security behavior. FAS-Bench is intended to focus specifically on the evidentiary adjudication problem: whether a reported security condition is actually exploitable, what attack path enables it, and whether remediation really closes that path.

## Project status

**Current status: Architecture / research prototype**

The repository has been created and the formal benchmark architecture is being established.

The project is **not yet claiming a validated benchmark score, production-ready evaluator, or scientifically validated weighting scheme**.

Current priorities:

- [ ] Freeze v0.1 formal specification
- [ ] Define machine-readable schemas
- [ ] Implement the five gold-standard cases
- [ ] Implement deterministic evidence verification
- [ ] Implement verdict evaluation
- [ ] Implement attack-path normalization/comparison
- [ ] Implement remediation verification
- [ ] Validate scoring against expert-reviewed cases
- [ ] Establish reproducible evaluation environments
- [ ] Build the initial public benchmark corpus
- [ ] Establish held-out evaluation infrastructure
- [ ] Publish benchmark methodology and results

## Repository structure

Target repository structure:

    fas-bench/
    ├── .github/
    │   └── workflows/
    ├── cases/
    │   ├── gold/
    │   ├── public/
    │   └── README.md
    ├── docs/
    │   ├── architecture.md
    │   ├── specification.md
    │   ├── evaluation.md
    │   ├── methodology.md
    │   └── threat-model.md
    ├── evaluator/
    ├── schemas/
    │   ├── case/
    │   ├── claim/
    │   ├── evidence/
    │   ├── attack-graph/
    │   ├── verdict/
    │   └── submission/
    ├── src/
    │   └── fas_bench/
    ├── tests/
    │   ├── unit/
    │   ├── integration/
    │   └── fixtures/
    ├── CHANGELOG.md
    ├── CONTRIBUTING.md
    ├── LICENSE
    ├── README.md
    └── pyproject.toml

## Design principles

1. **Evidence before prose**
2. **Exploitability before severity**
3. **Reachability matters**
4. **Effective security boundaries matter**
5. **Alternate paths matter**
6. **Uncertainty is a valid result**
7. **Ground truth must be independently testable**
8. **The evaluator must not depend on the system being evaluated**
9. **FAS-Bench must remain vendor- and tool-agnostic**
10. **Public benchmark claims require reproducible evidence**
11. **Security cases must be treated as hostile inputs**
12. **A benchmark score must expose its failure modes**

## Relationship to FAS

FAS-Bench and FAS are separate projects.

- **FAS** is a security-analysis system intended to perform evidence-first security analysis.
- **FAS-Bench** is the independent benchmark used to evaluate security-analysis systems.

FAS-Bench must remain capable of evaluating FAS against competing approaches without requiring FAS-specific concepts in the benchmark contract.

This separation is essential for research credibility.

## Contributing

Contributions are welcome, particularly:

- new benchmark cases
- adversarial case mutations
- evidence-verification strategies
- attack-path normalization
- remediation tests
- evaluator implementations
- reproducibility tooling
- independent validation
- benchmark methodology reviews

New cases should include machine-readable ground truth and deterministic validation wherever possible.

Before contributing a large case family, open an issue describing:

- the security property
- the intended false-positive trap
- the expected verdict
- required evidence
- validation strategy
- difficulty level
- contamination considerations

## License

FAS-Bench is licensed under the Apache License 2.0. See LICENSE.

## Citation

A formal citation will be published with the first research release.

Until then, reference the repository:

**LloydCoder/fas-bench — FAS-Bench: Forensic Agent Security Benchmark**

## Core thesis

> **A security finding is not proven because a scanner reported it.**
>
> **A vulnerability is proven when the evidence establishes the relevant path, security conditions, and impact — and survives attempts to disprove it.**

FAS-Bench exists to measure that distinction.
