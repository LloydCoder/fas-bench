# FAS-Bench

**Forensic Agent Security Benchmark**

> **Scanners find signals. FAS-Bench measures whether a system can prove what those signals actually mean.**

[![CI](https://github.com/LloydCoder/fas-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/LloydCoder/fas-bench/actions/workflows/ci.yml)
[![Security](https://github.com/LloydCoder/fas-bench/actions/workflows/security.yml/badge.svg)](https://github.com/LloydCoder/fas-bench/actions/workflows/security.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-%3E%3D3.12-blue.svg)](pyproject.toml)

**Status:** Phase 10 — corpus integrity, contamination defense, mutation, governance, and release infrastructure are implemented in the public development repository. The current public corpus is **development/practice data, not a hidden official evaluation set**.

FAS-Bench is an independent, evidence-first benchmark for evaluating AI agents, security scanners, SAST/SCA systems, LLM-based security tools, MCP-aware systems, autonomous coding agents, and hybrid human/machine security-analysis pipelines.

## Why FAS-Bench exists

Most security benchmarks stop at detection: *did the system flag something?*

FAS-Bench evaluates the harder question:

> **Can the system establish, with independently verifiable evidence, whether the claimed security condition is actually reachable, exploitable, controlled, remediated, or regressed?**

The benchmark separates:

**signal → claim → evidence → reachability → effective security boundary → attack path → exploitability → impact → remediation → regression**

That separation is deliberate. A plausible explanation is not evidence. A source-level pattern is not automatically an exploitable path. A correct verdict supported by fabricated evidence is not equivalent to a correct verdict supported by verified evidence.

## What FAS-Bench measures

FAS-Bench is designed to measure multiple dimensions of security reasoning:

- **Finding identification** — did the system identify the relevant security condition?
- **Evidence correctness** — can submitted evidence be independently verified?
- **Reachability** — can the relevant operation/path actually be reached?
- **Security-boundary reasoning** — do authentication, authorization, IAM, network, sandbox, policy, and runtime controls change the effective path?
- **Attack-path reconstruction** — can the system reconstruct the ordered security-relevant path?
- **Exploitability adjudication** — is the claimed impact actually exercisable under the case assumptions?
- **Impact reasoning** — what security consequence and blast radius follow from a valid path?
- **Remediation verification** — did the change eliminate the underlying condition?
- **Regression detection** — did a later change reintroduce the condition?
- **Confidence calibration** — does confidence correspond to correctness and uncertainty?
- **Efficiency** — what time, tool, token, compute, or execution resources were required when those measurements are available?

The benchmark is intentionally **not** a benchmark of prose quality.

## Benchmark scope

FAS-Bench can evaluate systems including:

- AI security agents and autonomous coding agents
- LLM security-analysis systems
- SAST and SCA tools
- Semgrep-based systems
- vulnerability-analysis and triage systems
- MCP-aware security systems
- research prototypes
- hybrid human/machine pipelines

It is tool-agnostic by design.

### Independence is a hard invariant

FAS-Bench does **not** depend on FAS.

FAS is one candidate system that may be evaluated by the benchmark. The benchmark MUST remain meaningful if FAS disappears. FAS-Bench must not import, require, execute, or derive ground truth from FAS, ThreatFade, Tinlance, or another evaluated product.

## Canonical taxonomy

| ID | Category | What it tests |
|---|---|---|
| C1 | Reachability | Whether a security-relevant operation or condition is actually reachable |
| C2 | Data Flow / Taint | Whether relevant data reaches a security-sensitive sink and how it is transformed |
| C3 | Authentication / Authorization | Identity, privilege, IAM, policy, and authorization boundaries |
| C4 | AI Agent Security | Agent capabilities, autonomy, memory, execution, and delegated authority |
| C5 | MCP Security | Tool/server trust, authorization, invocation, poisoning, and boundary behavior |
| C6 | Supply Chain | Dependencies, provenance, installation/build behavior, and reachable components |
| C7 | Secrets / Sensitive Data | Exposure, validity, revocation, access, and exploitability |
| C8 | Infrastructure / Cloud | Cloud/IAM/storage/network/resource-policy behavior |
| C9 | Cross-Component Attack Paths | Security paths spanning components, identities, trust boundaries, or systems |
| C10 | Remediation / Regression | Fix verification and detection of later security regressions |

Cases may cover multiple categories, but each case has one primary category.

## Difficulty model

Difficulty describes **security-reasoning complexity**, not source-code size.

| Level | Meaning |
|---|---|
| L1 | Local |
| L2 | Multi-function |
| L3 | Multi-component |
| L4 | Agentic |
| L5 | Cross-system |

See the normative specification for the exact criteria.

## Canonical verdicts

FAS-Bench distinguishes:

- EXPLOITABLE
- NOT_EXPLOITABLE
- CONDITIONALLY_EXPLOITABLE
- REMEDIATED
- REMEDIATION_FAILED
- REGRESSED
- UNKNOWN

**UNKNOWN is not NOT_EXPLOITABLE.** Insufficient evidence must remain distinguishable from evidence that establishes a blocked path.

## Current public corpus

The initial corpus contains **FAS-001 through FAS-020**.

The cases cover examples such as:

- dead vs reachable SSRF
- sanitized and indirect command injection
- IDOR and authorization false positives
- excessive agent capability and sandbox boundaries
- MCP tool poisoning and safe MCP behavior
- malicious and unreachable dependencies
- revoked vs live credentials
- public storage exposure
- privilege boundaries
- multi-service compromise
- agent → CI/CD → production paths
- verified fixes and alternate-path failures

The public cases are valuable for development and reproducibility, but their transparency makes them unsuitable as a secret official test set.

## Architecture

FAS-Bench is layered so that each measurement can be inspected independently:

~~~text
                    ┌─────────────────────────────┐
                    │       Evaluated System      │
                    │ AI agent / scanner / tool   │
                    └──────────────┬──────────────┘
                                   │ submission
                                   ▼
┌──────────┐   ┌──────────┐   ┌────────────┐   ┌─────────────┐
│  Cases   │──▶│ Evidence │──▶│   Finding  │──▶│ Security    │
│ & Oracle │   │  Engine  │   │  / Verdict │   │ Graph       │
└──────────┘   └──────────┘   └────────────┘   └──────┬──────┘
                                                       │
                                                       ▼
                                             ┌──────────────────┐
                                             │ Remediation /    │
                                             │ Regression       │
                                             └────────┬─────────┘
                                                      │
                                                      ▼
                                             ┌──────────────────┐
                                             │ Scoring /        │
                                             │ Calibration      │
                                             └────────┬─────────┘
                                                      │
                                                      ▼
                                             ┌──────────────────┐
                                             │ Secure Evaluation│
                                             │ Harness          │
                                             └────────┬─────────┘
                                                      │
                                                      ▼
                                             ┌──────────────────┐
                                             │ Corpus / Release │
                                             │ Integrity        │
                                             └──────────────────┘
~~~

The implementation roadmap is:

1. Specification & Benchmark Contract
2. Schema & Data Model
3. Gold Cases & Ground Truth
4. Deterministic Evidence Engine
5. Verdict & Finding Evaluator
6. Attack-Path & Security-Graph Engine
7. Remediation & Regression Engine
8. Scoring, Calibration & Benchmark Analytics
9. Secure Evaluation Harness & Reproducibility
10. Corpus, Contamination Defense, Mutation & Release

The normative semantics live in [docs/specification.md](docs/specification.md). Other documents explain or operationalize the specification; they must not silently redefine it.

## Security and trust model

Benchmark inputs are treated as untrusted security artifacts.

The repository is designed around:

- deterministic validation
- content-derived identities and digests
- fail-closed secure execution
- immutable container image references for dynamic execution
- network isolation in the current execution provider
- non-root execution
- dropped Linux capabilities
- no-new-privileges
- read-only container roots
- bounded CPU, memory, PIDs, time, and output
- isolated workspaces and artifact validation
- no host credential or Docker-socket exposure
- explicit infrastructure-failure states
- contamination and independence audits

Container isolation is **not** claimed to be escape-proof. The host kernel, runtime, hardware, and Docker daemon remain part of the trusted computing base.

Read [SECURITY.md](SECURITY.md) before working with benchmark cases or the secure evaluation harness.

## Quick start

### Requirements

- Python **3.12+**
- Git
- Docker for Phase 9 secure-execution integration tests

### Install for development

~~~bash
git clone https://github.com/LloydCoder/fas-bench.git
cd fas-bench

python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
~~~

Windows PowerShell:

~~~powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
~~~

### Run the core checks

~~~bash
ruff format --check .
ruff check .
pytest
python -m build
~~~

### Validate the public corpus

~~~bash
fas-bench cases validate-all
fas-bench cases validate-gold
fas-bench corpus validate
fas-bench corpus stats
fas-bench benchmark doctor
~~~

### Inspect benchmark health and integrity

~~~bash
fas-bench contamination scan
fas-bench contamination independence
fas-bench health
~~~

### Work with evidence and findings

~~~bash
fas-bench evidence validate tests/fixtures/integrated/FAS-001.json --case FAS-001 --json

fas-bench evaluate finding \
  --case FAS-002 \
  --submission tests/fixtures/phase5/FAS-001-gold.json \
  --json
~~~

### Work with graphs

~~~bash
fas-bench graph validate <graph.json>
fas-bench graph normalize <graph.json>
fas-bench graph digest <graph.json>
fas-bench graph paths <graph.json>
fas-bench graph diff <before.json> <after.json>
fas-bench graph compare --expected <expected.json> --submission <submission.json>
~~~

### Work with scoring and analytics

~~~bash
fas-bench score <submission>
fas-bench self-test
fas-bench analyze <results.json>
fas-bench report <results.json> --output <directory>
~~~

### Work with Phase 10 releases

~~~bash
fas-bench corpus validate
fas-bench benchmark release --version 0.1.0-phase10-dev
fas-bench release verify <manifest.json>
~~~

Release identity is content-derived. A timestamp or directory name is not sufficient to establish release identity.

## Evidence-first by design

FAS-Bench separates four important states:

~~~text
schema-valid
    ≠
semantically-valid
    ≠
evidence-supported
    ≠
benchmark-correct
~~~

The evidence engine verifies claims against authoritative case artifacts. It does not use an LLM as an oracle.

A verified evidence item establishes an underlying fact; it does not automatically establish exploitability or the final verdict.

## Public vs hidden evaluation

The repository intentionally distinguishes development data from official evaluation data.

~~~text
PUBLIC_DEVELOPMENT
PUBLIC_PRACTICE
      │
      │ development / reproducibility
      ▼
HELD_OUT / HIDDEN / OFFICIAL
      │
      │ contamination-resistant evaluation
      ▼
official benchmark result
~~~

The current public repository does **not** contain a secret official evaluation corpus.

The contamination scanner can detect repository-level leakage patterns and forbidden artifacts. It cannot prove that a model has never encountered benchmark-related material during training.

Official evaluation should additionally record the benchmark version, case-population digest, network policy, external lookup policy, hidden-set usage, execution environment, and relevant reproducibility metadata.

## Scoring and scientific boundaries

FAS-Bench exposes decomposable metrics rather than treating one composite number as the whole story.

The scoring layer supports finding, verdict, evidence, reachability, graph, remediation, calibration, integrity, and efficiency measurements.

Some scoring weights and policies remain **provisional research configuration**. They are not presented as scientifically validated universal weights.

The public twenty-case corpus is not statistically representative. FAS-Bench does not currently claim universal real-world security effectiveness, model-training contamination freedom, or cross-platform reproducibility under every environment.

Those boundaries are features of a credible benchmark, not omissions.

## Documentation map

Start with the document that matches your task:

| Need | Document |
|---|---|
| Understand the benchmark contract | [Specification](docs/specification.md) |
| Understand repository architecture | [Architecture](docs/architecture.md) |
| Understand evidence evaluation | [Evidence engine docs](docs/evidence-engine.md) |
| Understand graph evaluation | [Graph engine docs](docs/graph-engine.md) |
| Understand remediation/regression | [Phase 7 docs](docs/phase7-remediation.md) |
| Understand scoring/calibration | [Phase 8 docs](docs/phase8-scoring.md) |
| Understand secure execution | [Phase 9 docs](docs/phase9-secure-evaluation.md) |
| Understand corpus/release lifecycle | [Phase 10 corpus/release](docs/phase10-corpus-release.md) |
| Understand mutation | [Phase 10 mutation](docs/phase10-mutation.md) |
| Understand contamination defense | [Phase 10 contamination](docs/phase10-contamination.md) |
| Understand release procedure | [Phase 10 release](docs/phase10-release.md) |
| Understand governance | [Phase 10 governance](docs/phase10-governance.md) |
| Contribute code/cases/docs | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Report vulnerabilities | [SECURITY.md](SECURITY.md) |
| Get project help | [SUPPORT.md](SUPPORT.md) |
| Cite the project | [CITATION.cff](CITATION.cff) |
| See project history | [CHANGELOG.md](CHANGELOG.md) |

A complete documentation index is available at [docs/README.md](docs/README.md).

## Contributing

FAS-Bench is intentionally built so security researchers, benchmark engineers, application-security engineers, AI/agent researchers, and developers can contribute without first understanding the entire repository.

Useful contribution paths include:

- **New benchmark cases** — add falsifiable security hypotheses with deterministic ground truth.
- **Evidence improvements** — strengthen deterministic verification and evidence semantics.
- **Evaluator improvements** — add case-independent finding/verdict logic and adversarial tests.
- **Graph work** — improve canonicalization, path reasoning, semantic matching, and boundary analysis.
- **Remediation work** — improve alternate-path and regression analysis.
- **Measurement science** — validate calibration, uncertainty, stratification, and scoring methodology.
- **Harness security** — harden isolation, artifact integrity, resource controls, and reproducibility.
- **Corpus integrity** — improve contamination detection, mutation validation, release manifests, and governance.
- **Documentation** — improve clarity, examples, tutorials, and contributor onboarding.

Good first contributions should be small, testable, and tied to an issue or clearly scoped change.

Before opening a PR, read [CONTRIBUTING.md](CONTRIBUTING.md).

## Design principles

FAS-Bench is governed by a small set of non-negotiable principles:

1. **Evidence before prose.**
2. **Exploitability before severity.**
3. **Reachability matters.**
4. **Effective security boundaries matter.**
5. **Alternate paths matter.**
6. **UNKNOWN is a valid result.**
7. **Ground truth must be independently testable.**
8. **The evaluator must not depend on the evaluated system.**
9. **Benchmark inputs are hostile data.**
10. **Scores must expose failure modes.**
11. **Empirical claims must be distinguished from architectural commitments.**
12. **Historical results must remain interpretable through explicit versioning.**

## Project maturity

FAS-Bench is an active research/engineering benchmark project.

Phase 10 substantially strengthens the repository's corpus integrity, release, mutation, contamination-defense, and governance foundations. That does **not** mean every scientific question has been solved.

In particular, the project still treats the following as research areas requiring empirical evidence:

- statistical representativeness of the case population
- human-agreement studies
- empirical benchmark saturation
- temporal contamination measurement
- large-scale cross-model evaluation
- validation of scoring weights
- independently operated hidden evaluation infrastructure
- long-term reproducibility across heterogeneous platforms

The project deliberately documents these limits instead of turning implementation maturity into unsupported scientific claims.

## License

FAS-Bench is released under the [Apache License 2.0](LICENSE).

## Citation

If FAS-Bench contributes to research, evaluation, or a published benchmark comparison, please cite it using [CITATION.cff](CITATION.cff).

---

**FAS-Bench is built around a simple standard: if a security system makes a claim, the benchmark should make it possible to ask, “What evidence proves it?”**
