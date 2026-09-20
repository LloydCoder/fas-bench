# FAS-Bench v0.1.0 — Normative Benchmark Specification

**Document role:** normative benchmark contract and highest-authority technical specification.  
**Status:** Normative contract; Phase 5 verdict/finding contract validated by CI.  
**Benchmark specification version:** 0.1.0  
**Schema version:** 0.1.0 (conceptual contract only; schemas are a Phase 2 deliverable)  
**Evaluator version:** 0.1.0 (contract identifier; evaluator implementation is later)  
**Case-set version:** 0.1.0 (validated public development corpus)  
**Submission format version:** 0.1.0 (conceptual contract; machine schema is Phase 2)

Other project documents may explain, summarize, or operationalize this contract. They MUST NOT redefine normative semantics. When a conflict exists, this specification controls.

## Phase 8 measurement contract

Phase 8 is the authoritative measurement layer above Phase 4–7 outputs. Normalized metrics are in [0,1]. It MUST preserve decomposition, missing-data semantics, evaluator errors, integrity caps, calibration diagnostics, uncertainty metadata, and versioned scoring configuration. Composite weights are provisional and research-configurable. Candidate-provided aggregate scores are non-authoritative. Benchmark results MUST NOT be presented as generalized real-world security effectiveness.

## Phase 4 evidence contract

Phase 4 defines deterministic evidence verification as a separate layer between benchmark ground truth and later verdict evaluation. Evidence MUST be normalized using only representation-level transformations, bound to case identity, resolved against authoritative case artifacts, and classified as VERIFIED, INVALID, UNRESOLVED, or CONTRADICTED without using an LLM oracle. Evidence identity MUST exclude presentation-only descriptions, evaluator verification labels, and evaluation timestamps. A verified evidence item establishes an underlying fact only; exploitability remains a later-phase conclusion.

## Scope

FAS-Bench (Forensic Agent Security Benchmark) evaluates whether a security-analysis system can move from a security signal to a defensible, evidence-backed security adjudication.

It is designed for AI agents, LLM systems, SAST/SCA tools, Semgrep-based systems, vulnerability-analysis systems, MCP-aware systems, autonomous coding/security agents, research prototypes, and hybrid human/machine pipelines.

The benchmark measures more than detection:

1. detection of security-relevant conditions;
2. investigation of code, data/control flow, configuration, identity, permissions, dependencies, runtime context, and controls;
3. independently verifiable evidence;
4. reachability and security-boundary reasoning;
5. exploitability adjudication;
6. attack-path reconstruction;
7. impact/blast-radius reasoning;
8. remediation verification;
9. regression detection;
10. confidence calibration and operational efficiency.

### Independence invariant

**FAS is one candidate evaluated system.** FAS-Bench MUST NOT import, require, execute, or derive ground truth from FAS. Benchmark correctness, scoring, cases, and evaluator behavior MUST remain meaningful if FAS disappears. FAS-specific implementation details MUST NOT be normative benchmark semantics.

## Non-goals

FAS-Bench is NOT:

- a vulnerability database;
- a replacement for CVE or CVSS;
- a generic code-quality benchmark;
- a benchmark of prose quality;
- a benchmark requiring one scanner, model, vendor, or agent framework;
- a benchmark requiring FAS;
- a benchmark that assumes every finding is exploitable;
- a benchmark that rewards hallucinated evidence;
- a benchmark where ground truth is inferred from evaluated-system output;
- a production security certification;
- a universal claim about real-world security performance;
- a leaderboard by default.

## Normative language

MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY are normative.

MUST/SHALL/REQUIRED are mandatory. MUST NOT/SHALL NOT are prohibited. SHOULD/SHOULD NOT are strong recommendations that require documented justification to ignore. MAY is optional.

## Benchmark philosophy

1. Evidence before prose.
2. Exploitability before severity.
3. Reachability matters.
4. Effective security boundaries matter.
5. Alternate paths matter.
6. Unknown is a valid result.
7. Ground truth must be independently testable.
8. The evaluator must not depend on the system being evaluated.
9. FAS-Bench must remain vendor- and tool-agnostic.
10. Security cases are hostile inputs.
11. Scores must expose component failure modes.
12. Empirical claims must be distinguished from architectural commitments.

A correct verdict supported by invalid evidence is not equivalent to a correct verdict supported by verified evidence. Evidence quality is independently evaluated.

## Canonical taxonomy

| ID | Category | Definition |
|---|---|---|
| C1 | Reachability | Whether a security-relevant operation or condition can actually be reached under stated assumptions. |
| C2 | Data Flow / Taint | Whether attacker-controlled or security-sensitive data flows to a relevant sink and what transformations occur. |
| C3 | Authentication / Authorization | Whether identity, authentication, authorization, IAM, policy, and privilege boundaries hold. |
| C4 | AI Agent Security | Security properties of agents, capabilities, autonomy, execution boundaries, memory, and tool use. |
| C5 | MCP Security | MCP tool/server trust, authorization, invocation, poisoning, and boundary behavior. |
| C6 | Supply Chain | Dependencies, installation/build behavior, package provenance, and reachable vulnerable or malicious components. |
| C7 | Secrets / Sensitive Data | Exposure, validity, revocation, access, handling, and exploitability of secrets or sensitive data. |
| C8 | Infrastructure / Cloud | Cloud/IAM/storage/network/resource-policy behavior and effective infrastructure controls. |
| C9 | Cross-Component Attack Paths | Security paths spanning components, services, identities, trust boundaries, or systems. |
| C10 | Remediation / Regression | Verification that fixes eliminate security conditions and detection of later reintroduction. |

Cases MAY have multiple categories. Each case MUST have one primary category and MAY have secondary categories. Secondary labels MUST NOT change the primary property being adjudicated.

## Difficulty model

Difficulty is structural security-reasoning complexity, not source-code size.

| Level | Definition |
|---|---|
| L1 Local | The condition can be established within a small local component with no material cross-boundary reasoning. |
| L2 Multi-function | Establishment requires multiple functions, indirect calls, transformations, or control/data-flow steps. |
| L3 Multi-component | Establishment requires multiple components or a meaningful authentication, authorization, network, IAM, or trust boundary. |
| L4 Agentic | Establishment materially depends on agent/tool/MCP behavior, delegated capability, sandboxing, or autonomous execution. |
| L5 Cross-system | Establishment requires a chain spanning multiple systems or trust domains and more than one security boundary. |

Case authors MUST justify the assigned level using these structural criteria.

## Case identity and registry

Case IDs are stable identifiers in the form FAS-NNN. IDs MUST be unique and MUST NOT be reused for a different security property after publication.

| ID | Case |
|---|---|
| FAS-001 | Dead SSRF |
| FAS-002 | Reachable SSRF |
| FAS-003 | Sanitized Command Injection |
| FAS-004 | Indirect Command Injection |
| FAS-005 | IDOR |
| FAS-006 | Authorization False Positive |
| FAS-007 | Excessive Agent Capability |
| FAS-008 | Agent Sandbox Boundary |
| FAS-009 | MCP Tool Poisoning |
| FAS-010 | Safe MCP Server |
| FAS-011 | Malicious Dependency |
| FAS-012 | Vulnerable but Unreachable Dependency |
| FAS-013 | Revoked Secret |
| FAS-014 | Live Credential Attack Path |
| FAS-015 | Public Storage Exposure |
| FAS-016 | Privilege Boundary |
| FAS-017 | Multi-Service Compromise |
| FAS-018 | Agent → CI/CD → Production |
| FAS-019 | Verified Fix |
| FAS-020 | Fake Fix / Alternate Path |

These are the Phase 3 public development cases. They are not a statistically representative sample, but their structured ground truth, integrity records, and reproducibility gates are validated by the Phase 3 CI contract.

### Initial gold cases

The designated initial gold cases are FAS-001, FAS-002, FAS-006, FAS-016, and FAS-020. They are intended to exercise positive exploitability, negative exploitability, authorization-boundary reasoning, effective security boundaries, and remediation/alternate-path reasoning. They are not claimed to be statistically representative.

## Security-condition model

FAS-Bench distinguishes:

- Signal — an observable pattern or event suggesting a security-relevant condition.
- Claim — an explicit assertion made by an evaluated system.
- Condition — the security property or prerequisite whose truth determines the case.
- Reachability — whether the relevant operation/path can be reached under stated assumptions.
- Security control — a mechanism that restricts, transforms, authenticates, authorizes, isolates, or otherwise constrains the path.
- Effective boundary — the security boundary after relevant controls and environmental assumptions are applied.
- Exploitability — whether the stated security impact can be exercised under benchmark assumptions.
- Impact — the security consequence and blast radius that follows from a valid path.
- Remediation — a change that establishes the relevant security property, not merely a textual diff.
- Regression — reintroduction of a previously eliminated security condition after a subsequent change.

Conceptual chain:

    Observed signal
          ↓
    Security claim
          ↓
    Reachability analysis
          ↓
    Control / boundary analysis
          ↓
    Attack-path reconstruction
          ↓
    Exploitability adjudication
          ↓
    Impact determination
          ↓
    Remediation verification
          ↓
    Regression detection

## Claim model

A claim is an explicit, independently testable assertion by an evaluated system. Examples include:

- attacker-controlled input reaches a sink;
- an endpoint is unauthenticated;
- an identity can invoke a tool;
- a resource is publicly readable;
- a dependency executes during installation;
- validation blocks an attacker-controlled value;
- an IAM permission enables escalation;
- a remediation breaks the original path;
- an alternate path remains.

Claims MUST be specific enough to map to benchmark artifacts or stated environment facts. The evaluator MUST NOT award evidence credit solely for persuasive prose.

## Evidence model

Canonical evidence types:

SOURCE_LOCATION, SINK_LOCATION, TRANSFORMATION, DATA_FLOW, CONFIGURATION, DEPENDENCY, IDENTITY, PERMISSION, POLICY, TRUST_BOUNDARY, RUNTIME_EVENT, NETWORK_EVENT, TOOL_INVOCATION, TEST_RESULT, REMEDIATION, ENVIRONMENT_STATE, DOCUMENTATION.

Evidence roles:

- DIRECT — directly establishes the claim.
- SUPPORTING — materially strengthens the claim but is not sufficient alone.
- MISSING — evidence required to establish the claim was not supplied.
- CONTRADICTORY — evidence conflicts with the claim.

Verification states:

- VERIFIED — evidence matches an observable benchmark artifact and supports the stated claim.
- INVALID — evidence is malformed, nonexistent, fabricated, or otherwise not verifiable.
- UNRESOLVED — verification cannot establish validity or invalidity.
- CONTRADICTED — benchmark evidence establishes a materially conflicting fact.

Valid evidence MUST identify a benchmark-observable fact, location, artifact, relationship, or recorded event. Systems MUST NOT fabricate source locations, functions, runtime output, test results, configuration, tool invocations, or other evidence.

Evidence validity is independently scored. A correct final verdict does not receive full evidence credit when its supporting evidence is invalid or insufficient.

## Verdict semantics

The only canonical benchmark verdicts are:

- EXPLOITABLE — the relevant security condition can be exercised under the stated attacker and environment assumptions.
- NOT_EXPLOITABLE — the claimed security impact cannot be produced under the stated assumptions because an effective control or missing prerequisite blocks the path.
- CONDITIONALLY_EXPLOITABLE — exploitation depends on an explicit prerequisite that is not universally satisfied.
- REMEDIATED — the original security condition has been demonstrably eliminated.
- REMEDIATION_FAILED — the proposed remediation does not eliminate the underlying condition or leaves a viable equivalent/alternate path.
- REGRESSED — a previously secure or remediated property has become exploitable again due to a later change.
- UNKNOWN — available evidence is insufficient to establish the security state.

UNKNOWN MUST NOT be collapsed into NOT_EXPLOITABLE. Absence of evidence is not evidence of absence.

## Attack graph model

Canonical node types:

ACTOR, INPUT, FUNCTION, SERVICE, PROCESS, DATA, RESOURCE, TOOL, AGENT, MCP_SERVER, IDENTITY, PERMISSION, POLICY, NETWORK_ZONE, TRUST_BOUNDARY, SINK, IMPACT.

Canonical edge types:

CONTROLS, FLOWS_TO, CALLS, READS, WRITES, INVOKES, AUTHENTICATES_AS, AUTHORIZED_BY, CROSSES, TRANSFORMS, REACHES, DEPENDS_ON, DEPLOYS_TO, TRIGGERS.

A node identity MUST be stable within a case and resolve to an observable entity or explicitly modeled benchmark entity. An edge is directed and MUST have defined semantics between endpoints.

A valid attack path is an ordered sequence of valid nodes and edges whose semantics permit the claimed transition under case assumptions. Incomplete paths MUST NOT be treated as complete exploitable paths. Alternative paths MUST be evaluated independently when they can preserve the same security impact.

## Effective security graph

FAS-Bench distinguishes the apparent graph from the effective security graph.

The apparent graph represents what source code, configuration, or declared relationships appear to permit.

The effective security graph represents what an attacker can actually cause after accounting for authentication, authorization, IAM, resource policies, SCPs, network policy, sandboxing, filesystem permissions, runtime restrictions, environment constraints, trust boundaries, validation, and policy enforcement.

A dangerous edge in the apparent graph MUST NOT by itself establish exploitability.

## Remediation model

Remediation is a security-property change, not merely a source-code diff. A remediation assessment MUST answer:

1. What condition existed?
2. What path enabled exploitation?
3. What changed?
4. Which control was introduced or changed?
5. Does the original path still exist?
6. Does an equivalent alternate path exist?
7. Does the security boundary still hold?
8. Does the impact remain possible?
9. Is the remediation actually effective?

FAS-019 and FAS-020 are intended to exercise these questions after ground-truth validation.

## Regression model

A regression is distinct from remediation failure.

    baseline state
        ↓
    established security property
        ↓
    subsequent change
        ↓
    re-evaluation
        ↓
    REGRESSED if the property is no longer valid

REGRESSED MUST NOT be used merely as a synonym for REMEDIATION_FAILED.

## Provisional scoring model

The initial scoring framework is explicitly PROVISIONAL:

| Dimension | Weight |
|---|---:|
| Finding identification | 10 |
| Verdict correctness | 20 |
| Evidence correctness | 20 |
| Reachability / security-boundary reasoning | 15 |
| Attack-path reconstruction | 15 |
| Impact / blast radius | 5 |
| Remediation assessment | 5 |
| Confidence calibration | 5 |
| Efficiency | 5 |
| Total | 100 |

Phase 8 MUST empirically validate, revise, or replace these weights. Phase 1 makes no scientific claim that they are optimal.

### Provisional evidence score

    EvidenceScore =
        0.35 × Validity
      + 0.30 × Relevance
      + 0.20 × Coverage
      + 0.15 × Specificity

Validity measures whether evidence is real and verifiable. Relevance measures support for the claim. Coverage measures how much of the required claim is supported. Specificity measures whether evidence identifies the precise artifact or relationship. This formula is provisional.

### Provisional attack-graph score

    GraphScore =
        0.30 × NodeF1
      + 0.35 × EdgeF1
      + 0.20 × PathCompleteness
      + 0.15 × BoundaryCrossingF1

This formula is provisional.

### Evidence integrity ratio

    EHR = invalid evidence claims / submitted evidence claims

Initial provisional policy:

- EHR ≤ 10%: no score cap;
- 10% < EHR ≤ 25%: maximum score 50;
- EHR > 25%: maximum score 25.

Systematic fabricated evidence MAY invalidate a submission. Phase 8 MUST empirically validate or revise this policy.

### Provisional composite metric

    0.20 Evidence
    0.20 Verdict
    0.15 Reachability
    0.15 AttackPath
    0.10 FalsePositiveResistance
    0.10 Remediation
    0.05 Calibration
    0.05 Efficiency

This is a research hypothesis, not an established scientific standard. Reports SHOULD expose component metrics rather than relying on the composite.

## Calibration

Confidence is distinct from correctness. Submissions SHOULD provide confidence for adjudicative claims.

The benchmark supports Brier score, expected calibration error (ECE), reliability analysis, and confidence-conditioned error analysis. High-confidence incorrect verdicts MUST NOT be treated as equivalent to calibrated uncertainty.

## Efficiency

Efficiency MAY be measured using wall-clock time, tool calls, tokens, compute, external requests, test executions, and cost where available.

Comparisons across materially different execution environments MUST include relevant environment metadata. Efficiency is not a security-correctness metric by itself.

## Reproducibility contract

A reproducible evaluation MUST record, where applicable:

- benchmark specification version;
- case-set and case version;
- evaluator version;
- submission format version;
- system/model identifier;
- system configuration;
- execution environment;
- dependency versions or lockfile;
- execution timestamp;
- random seed;
- hardware/runtime metadata;
- tool versions;
- network policy;
- container/image identity;
- dataset/content digests.

SWE-bench documents Docker-based evaluation and structured prediction/result artifacts, while SEC-bench documents reproducible Docker vulnerability instances and verification. FAS-Bench borrows this benchmark-engineering discipline, not their task semantics.

## Determinism

For a fixed benchmark, case, evaluator, submission, and environment, the following MUST be deterministic:

- case identity;
- ground-truth evaluation;
- evidence verification;
- verdict evaluation;
- score calculation;
- graph normalization;
- schema validation once implemented.

If a component is intentionally nondeterministic, its randomness source and configuration MUST be recorded.

## Benchmark security

Benchmark cases are untrusted security artifacts. They MAY contain vulnerable code, malicious-looking instructions, synthetic credentials, poisoned dependencies, attacker-controlled files, exploit payloads, prompt injection, or malicious MCP descriptions.

Therefore:

- arbitrary case code MUST NOT execute directly on the evaluator host;
- dynamic execution MUST be isolated;
- outbound network access MUST default to denied unless a case explicitly requires controlled networking;
- credentials MUST be synthetic;
- production credentials MUST NOT be used;
- dependencies SHOULD be pinned;
- hidden ground truth MUST be separated from evaluated-system inputs;
- evaluator internals MUST be protected from evaluated systems;
- case integrity and provenance SHOULD be content-addressed;
- evaluation artifacts SHOULD record relevant hashes.

## Contamination resistance

The benchmark SHOULD support public development cases, held-out evaluation cases, hidden cases, semantic-preserving mutations, identifier renaming, architecture-preserving transformations, temporal splits, mutation variants, and leakage detection.

Publication of a case MUST NOT be treated as proof that contamination is solved. Contamination resistance is an empirical property to be measured later.

## Ground-truth isolation

Materials visible to an evaluated system MUST be distinct from hidden ground truth.

Future case/evaluation layouts MUST ensure that expected verdicts, hidden evidence, evaluator internals, and hidden tests are not accidentally included in the public analysis surface.

## Submission contract

The Phase 1 conceptual submission is structured, not prose-only:

    {
      "benchmark_version": "0.1.0",
      "case_id": "FAS-020",
      "verdict": "REMEDIATION_FAILED",
      "confidence": 0.87,
      "findings": [],
      "evidence": [],
      "attack_paths": [],
      "impact": {},
      "remediation": {},
      "verification": {}
    }

This is illustrative, not a Phase 2 JSON Schema. Phase 2 MUST encode required fields, types, identifiers, enumerations, cardinalities, and compatibility rules from this contract without silently changing semantics.

## Evaluation pipeline

The canonical pipeline is:

1. Reconnaissance — provide only permitted repository, environment, scenario, and task information.
2. Independent analysis — the evaluated system analyzes without hidden ground truth.
3. Structured result submission — the system emits a machine-readable result.
4. Deterministic evidence verification — evidence is checked against observable case artifacts.
5. Verdict evaluation — claims and verdicts are compared with ground truth.
6. Attack-path graph normalization/comparison — graph entities and relations are normalized and compared.
7. Remediation evaluation — remediation claims are checked against post-change state.
8. Regression evaluation — later changes are evaluated against established security properties.
9. Calibration and efficiency analysis — confidence and operational metrics are reported.

Later phases MUST preserve this conceptual ordering unless a specification revision explicitly changes it.

## Versioning and compatibility

The benchmark specification uses semantic versioning beginning at 0.1.0.

- Benchmark specification version — normative semantics.
- Schema version — machine-readable data contract.
- Evaluator version — evaluation implementation.
- Case-set version — published corpus composition.
- Submission format version — accepted result representation.

These identifiers MAY evolve independently but MUST be recorded together for an evaluation. A normative semantic change requires a benchmark specification version change. Schema-only compatible changes MAY advance schema version subject to Phase 2 compatibility rules.

The Python package version is 0.1.0 for Phase 1 and is an implementation release identifier; it does not supersede the benchmark specification.

## Research validity boundaries

Phase 1 distinguishes:

- Frozen architectural contract — concepts and terminology required for downstream implementation.
- Provisional research hypotheses — scoring weights, evidence caps, and composite formulas awaiting empirical validation.
- Empirically validated properties — claims supported by later controlled experiments and expert review.

The initial 20 cases are not claimed representative. The taxonomy is provisionally frozen to enable implementation, not claimed universally complete. The benchmark is not claimed to generalize to all real-world security analysis without validation.

## Ten-phase roadmap

### PHASE 1 — Specification & Benchmark Contract

Establish the normative contract, terminology, taxonomy, case identity, evidence philosophy, verdict semantics, graph model, remediation/regression semantics, security model, reproducibility, and governance.

### PHASE 2 — Schema & Data Model

Encode the Phase 1 contract as versioned machine-readable schemas and validation primitives.

### PHASE 3 — Gold Cases & Ground Truth

Construct and independently validate gold cases, including evidence and security-property ground truth.

### PHASE 4 — Deterministic Evidence Engine

Implement evidence resolution, validation, provenance checks, and integrity evaluation.

### PHASE 5 — Verdict & Finding Evaluator

Implement finding/claim matching and canonical verdict adjudication.

### PHASE 6 — Attack-Path & Security-Graph Engine

Implement graph normalization, path evaluation, effective-boundary modeling, and graph scoring.

### PHASE 7 — Remediation & Regression Engine

Implement fix verification, alternate-path analysis, baseline comparisons, and regression detection.

### PHASE 8 — Scoring, Calibration & Benchmark Analytics

Implement and empirically validate component metrics, weights, calibration analysis, evidence-integrity policy, and aggregate reporting.

### PHASE 9 — Secure Evaluation Harness & Reproducibility

Implement isolated execution, provenance capture, deterministic orchestration, artifact integrity, and reproducible environments.

### PHASE 10 — Benchmark Corpus, Contamination Defense & Release

Expand and validate the corpus, establish contamination defenses and held-out evaluation sets, perform release validation, and publish methodology/results.

Dependencies are sequential: Phase 2 depends on Phase 1; Phase 3 depends on the stable case/schema contract; Phases 4–7 consume those semantics; Phase 8 depends on evaluator outputs; Phase 9 secures the complete evaluation flow; Phase 10 depends on empirical validation and release controls.

## Architecture boundaries

Phase 1 defines semantics only. It MUST NOT prematurely implement the complete evaluator, evidence engine, graph engine, scoring engine, final 20 repositories, public leaderboard, benchmark optimization of FAS, or production certification.

## Phase 1 exit criteria

Phase 1 is complete only when:

- scope and non-goals are defined;
- normative language is defined;
- taxonomy and difficulty model are stable;
- case identity and registry are reconciled;
- verdict semantics are canonical;
- claim/evidence models are defined;
- attack graph and effective security graph are defined;
- remediation/regression semantics are distinct;
- submission and evaluation pipeline are defined;
- provisional scoring is explicitly labeled;
- calibration and efficiency are defined;
- reproducibility and determinism are defined;
- benchmark security, contamination, and ground-truth isolation are defined;
- versioning and independence are explicit;
- required documentation is reconciled;
- semantic repository checks and CI are green;
- no hidden dependency on FAS exists;
- Phase 2 can implement schemas without inventing missing semantics.

## Change control

Normative changes MUST be proposed as specification changes and reviewed as benchmark-contract changes. Case contributors MUST NOT silently change scoring semantics, verdict meanings, category definitions, or other normative rules.

## Conformance statement

A Phase 1-conforming FAS-Bench repository is one in which this specification is the authoritative semantic contract, implementation artifacts do not contradict it, and downstream phases can encode and execute the contract without redefining its core concepts.


## Scope
FAS-Bench evaluates evidence-grounded security adjudication by AI agents, scanners, security tools, and hybrid systems.

## Non-goals
It is not a CVE/CVSS replacement, prose benchmark, production certification, or FAS-dependent benchmark.

## Normative language
MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY retain their conventional normative meanings.

## Canonical taxonomy
The ten machine-readable category values are C1_REACHABILITY through C10_REMEDIATION_REGRESSION as defined by the schema common definitions.

## Difficulty model
L1_LOCAL through L5_CROSS_SYSTEM encode structural reasoning complexity, not source-code size.

## Verdict semantics
The seven canonical verdicts are EXPLOITABLE, NOT_EXPLOITABLE, CONDITIONALLY_EXPLOITABLE, REMEDIATED, REMEDIATION_FAILED, REGRESSED, and UNKNOWN.

## Claim model
A claim is an explicit assertion. It is not evidence and is not a verdict.

## Evidence model
Evidence is a structured observation that can support or contradict a claim. Verification state is independent of the final verdict.

## Attack graph model
Graphs use stable node and edge IDs rather than recursive object nesting. Cycles are permitted in graphs.

## Effective security graph
Controls and boundaries can block an apparent path. Exploitability is determined from the effective graph, not source relationships alone.

## Remediation model
Remediation records the security-property change, affected claims and paths, verification status, and final verdict.

## Regression model
Regression records a previously secure property becoming insecure after a subsequent change and is distinct from remediation failure.

## Reproducibility contract
Benchmark, schema, case, submission, evaluator, system, environment, tooling, timestamp, seed, and content-digest metadata are recorded where available.

## Benchmark security
Case data is untrusted. Validation is data-only, offline, and must not execute artifacts or fetch attacker-controlled references.

## Contamination resistance
Public development cases, held-out cases, mutations, temporal splits, and leakage detection remain future empirical controls; Phase 2 does not claim they are solved.

## Ground-truth isolation
Expected security state and evaluator-only evidence are not part of ordinary system submissions.

## Submission contract
A submission contains system metadata, verdict, findings, claims, evidence, attack paths, impact, remediation, and verification. It expresses the evaluated system's belief and must not contain expected verdict fields.

## Evaluation-result contract
Evaluation results may contain validity, component metrics, normalized scores, contributions, caps, penalties, structured errors, warnings, and final score. Score semantics remain provisional until Phase 8.

## Versioning and compatibility
Benchmark version is 0.1.0; schema family version is 0.1. Breaking schema changes require a new version directory.

## Phase 1 exit criteria
Phase 1 properties are represented in this specification and were verified before the Phase 2 schema implementation. Phase 2 adds executable structure without introducing a dependency on FAS.

## Phase 2 exit criteria
All required schema families, semantic validation, fixtures, documentation, package integration, and CI checks must be green before Phase 2 is declared complete.

## Evaluator-only ground-truth schema
The evaluator-only schema at `schemas/ground-truth/v0.1/ground-truth.schema.json` can represent expected verdicts, expected claims/evidence, attack paths, remediation, and regression. It is a data contract only; Phase 3 still owns the actual gold corpus and empirical ground-truth validation. It MUST NOT be used as the public submission schema.


## Phase 3 — Validated Case Corpus

Phase 3 adds the public development corpus FAS-001 through FAS-020. Cases carry independent case versions, explicit attacker models, controlled environments, structured ground truth, deterministic oracles, and distinct validation states. Public ground truth is not a hidden evaluation set. See docs/phase3.md for the normative Phase 3 contract.


## Phase 3 — Gold Cases & Ground Truth

Phase 3 operationalizes the case registry into a public development corpus. The initial corpus contains FAS-001 through FAS-020. The corpus is explicitly public development data, not a hidden evaluation set.

### Case lifecycle

DRAFT → CONSTRUCTED → SELF-VALIDATED → INDEPENDENTLY_REVIEWED → REPRODUCIBLE → VALIDATED → RELEASE_CANDIDATE → RELEASED. Schema validity, semantic validity, reproducibility, security validation, and release readiness are distinct gates. A case is not VALIDATED solely because its files validate.

### Case contract

Each case defines a falsifiable security hypothesis, attacker model, assets and boundaries, environment, security condition, structured ground truth, attack path, remediation state where applicable, oracle, provenance, limitations, and independent case version. Synthetic credentials and controlled local state are required for the initial corpus.

### Oracle contract

Oracles return machine-readable PASS/FAIL/ERROR/INCONCLUSIVE outcomes and independently exercise the security property. Dynamic cases use isolated local services and must not require public-network access. Remediation cases verify both baseline and post-change security state; alternate paths are evaluated independently.

### Reproducibility and integrity

Case validation records case-set/version metadata, environment version, oracle version, and content-derived artifact digests. Volatile execution timestamps are excluded from canonical case digests. Released cases require immutable content-derived digests.

### Public and hidden corpus model

The initial public corpus intentionally exposes ground truth. Future benchmark evaluation must use held-out cases, private ground truth, or undisclosed mutations. Public cases must never be described as contamination-resistant.


## Phase 5 — Verdict & Finding Evaluator

Phase 5 is the deterministic adjudication layer after evidence verification. A **finding** is a structured report of a security-relevant condition; a **claim** is an explicit assertion; **verified evidence** establishes an observable fact; a **security condition** is the set of reachability, control, boundary, and precondition facts whose truth determines the case; and a **verdict** is the resulting benchmark security state.

### Verdict semantics

- **EXPLOITABLE** — the authoritative security condition is supported, the viable path is reachable, required attacker capability and preconditions hold, and effective controls do not prevent the stated security-property violation.
- **NOT_EXPLOITABLE** — an apparent signal/path exists, but an effective security control, boundary, or lack of reachability prevents the stated security-property violation.
- **CONDITIONALLY_EXPLOITABLE** — the case explicitly defines a security condition whose exploitability depends on one or more stated, represented preconditions. It is not a synonym for uncertainty.
- **REMEDIATED** — authoritative remediation verification establishes that the original security condition is actually broken, not merely that a code change exists.
- **REMEDIATION_FAILED** — the proposed remediation does not eliminate the security condition, including when an alternate viable path remains.
- **REGRESSED** — a security condition that was previously remediated becomes exploitable again under the benchmark's temporal/version semantics.
- **UNKNOWN** — authoritative evidence is insufficient to adjudicate exploitability. UNKNOWN is not equivalent to NOT_EXPLOITABLE and MUST NOT be used for evaluator errors or malformed cases.

### Evidence dependency

Verdict correctness and verdict support are independent dimensions. A submitted verdict can match the authoritative verdict while lacking verified evidence; such a result is verdict-correct but evidence-unsupported and MUST remain distinguishable for later scoring. Conversely, verified facts can support the underlying condition while a submitted verdict is incorrect.

### Effective controls and boundaries

Control presence is not control effectiveness. Authentication is distinct from authorization. Presence is distinct from reachability. The evaluator uses authoritative case path/control/condition state and verified evidence; it does not infer exploitability from severity, CWE labels, titles, or scanner output.

### Conditional and remediation reasoning

Conditional verdicts require explicit case conditions. Remediation verdicts consume the existing remediation contract; Phase 5 does not implement the later full remediation/regression engine. A verified original-path block can establish REMEDIATED, while a verified alternate path can establish REMEDIATION_FAILED. Temporal previous/current verdict metadata provides the seam for REGRESSED.

### Phase 5 exit criteria

Phase 5 requires deterministic finding and claim matching, security-condition resolution, reachability/control/precondition adjudication, evidence dependency, structured verdict reasoning, stable reason codes, adversarial and metamorphic tests, all 20 public development cases self-evaluating, and CI validation. Final composite scoring remains deferred to Phase 8.


## Phase 6 — Security Graph and Attack-Path Contract

A security graph is a directed, evidence-aware graph of canonical security entities and relationships. Node identity, edge semantics, abstraction, trust boundaries, controls, and attack paths are distinct concepts.

Graph validation MUST reject duplicate identifiers, dangling references, unsupported versions/types, malformed paths, cross-case references, and configured resource-limit violations. Graph canonicalization MUST be independent of JSON object/array presentation ordering, and graph identity MUST be computed from canonical serialization.

An attack path is an ordered node/edge chain with an entry and impact endpoint. Path completeness requires the security-relevant transitions necessary to establish the case condition; shortest-path length alone is not authoritative. Trust-boundary and control relationships are separately measurable.

The Phase 6 provisional graph score is 0.30 NodeF1 + 0.35 EdgeF1 + 0.20 PathCompleteness + 0.15 BoundaryCrossingF1. The weighting is versioned methodology configuration and is explicitly not scientifically validated by the current public development corpus.

Unsupported or contradictory submitted graph facts MUST remain distinguishable from evaluator failure and MUST NOT be converted into a security verdict.


## Phase 7 normative definitions

A verified remediation requires independent closure of the declared security condition, removal or effective blocking of all required original paths, consideration of equivalent-impact alternate paths, valid remediation evidence, required security tests and required functional-preservation tests that PASS, and no benchmark-defined regression.

A cosmetic change is not a remediation. A partial fix that leaves an equivalent-impact route is a remediation failure. Conditional remediation is reserved for explicitly declared benchmark conditions. UNKNOWN means the oracle cannot establish closure; evaluator failure and invalid benchmark state remain distinct.

Regression is semantic: a previously blocked condition or effective control becomes materially weaker or exploitable after a later state. Textual diffs alone are not sufficient.

Case-specific truth remains declarative. Evaluator code must not branch on case identifiers.


## Phase 9 normative execution contract
Phase 9 is the sole benchmark execution trust boundary. Candidate workloads MUST execute only through a validated isolation backend. The v0.1 backend is Docker and MUST use an immutable image digest, network disabled, read-only root filesystem, all capabilities dropped, no-new-privileges, non-root UID/GID, bounded CPU/memory/PIDs/time/output, and ephemeral writable workspaces. The harness MUST fail closed when isolation or the immutable image is unavailable. Host execution, Docker-socket mounts, arbitrary host paths, repository credentials, and candidate-controlled aggregate results are prohibited. Infrastructure failures MUST remain distinct from security verdicts.
