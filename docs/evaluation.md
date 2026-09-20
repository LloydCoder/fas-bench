# FAS-Bench Evaluation
**Role:** evaluation methodology and metric interpretation.
**Authority:** docs/specification.md.

## Schema validation
Every serialized object is first checked against its Draft 2020-12 family schema.

## Semantic validation
Cross-object references, graph/path relationships, version compatibility, conditional verdict semantics, remediation consistency, and evaluation arithmetic are checked by Python.

## Invalid submission handling
Structural failures are SCHEMA_INVALID. Cross-object failures are SEMANTIC_INVALID. Errors contain deterministic codes and paths.

## Evidence integrity
Evidence is independently represented from findings and verdicts. Phase 4 determines whether submitted evidence is actually observable and valid. Phase 5 consumes those results to adjudicate findings and verdicts.

## Evaluation-result structure
Raw, normalized, weighted, capped, penalized, and invalid components are represented separately. Phase 8 will define and validate scoring policy.

## Version compatibility
Benchmark version 0.1.0 and schema family version 0.1 are currently supported.

## Determinism
Given identical inputs, schema resources, validator version, and configuration, validation produces deterministic results.

## Phase 3 case validation
The initial corpus is public development data. Corpus validation checks registry consistency, Phase 2 schemas, semantic references, attack graphs, structured verdicts, remediation semantics, and deterministic oracle agreement. This is distinct from evaluating a system under test; expected truth is not exposed to the evaluated system in future hidden splits.


## Phase 3 corpus gates

Before a case is marked VALIDATED, the corpus validator checks the Phase 2 schema contract, semantic references, expected finding/verdict agreement, attack-path representation, registry consistency, and oracle agreement. Dynamic gold cases additionally require executable security-property checks and mutation sensitivity. ERROR and INCONCLUSIVE oracle outcomes are never converted into security verdicts.


## Phase 4 evidence verification

Evidence verification is deterministic and case-authoritative. Submitted evidence is normalized before identity comparison; source locations are resolved beneath the case root; structured facts are read from benchmark-controlled artifacts; duplicate facts do not inflate coverage. `VERIFIED` establishes an underlying fact only. `INVALID`, `UNRESOLVED`, and `CONTRADICTED` remain distinct outcomes. Evidence Hallucination Rate is the raw invalid-evidence count divided by submitted evidence count, with zero submissions producing 0.0. Evaluator errors remain evaluator errors and are never converted into security verdicts.


## Phase 5 verdict evaluation

The evaluator derives the authoritative verdict from declarative case state rather than comparing labels alone. It resolves structured claim matches, consumes verified evidence, derives the security condition from the authoritative path/control/condition/remediation data, and evaluates the submitted verdict separately.

The result exposes:
- finding matched/category/claim/evidence support;
- per-claim VERIFIED, INVALID, UNRESOLVED, CONTRADICTED, or MISSING state;
- reachability/path status and effective-control state;
- explicit preconditions;
- verdict correctness and verdict support;
- stable reason code and structured supporting/blocking facts;
- evidence integrity and coverage;
- deterministic fingerprint.

Severity and confidence do not determine correctness. Confidence is preserved and validated independently. Final benchmark scoring is deferred to Phase 8.


## Phase 6 graph evaluation

A graph submission is parsed as untrusted JSON and evaluated without executing submission content. Validation precedes matching. Node matching uses semantic type and conservative normalized identity; edges use matched endpoint identity plus edge type; path matching requires ordered structural continuity.

Reported dimensions are Node Precision/Recall/F1, Edge Precision/Recall/F1, Path Completeness, Boundary Crossing Precision/Recall/F1, unsupported edges, contradictory edges, missing transitions, and Graph Score. Graph Score does not replace verdict correctness.

Serialization, node-order, and edge-order changes are intentionally non-semantic. Security-critical identity, authorization, control, trust-boundary, sink, impact, and capability distinctions remain material. Finite limits prevent path-explosion and graph-bomb denial of service.

Graph diffing reports added/removed/changed nodes and edges for remediation/regression consumers; it does not independently declare remediation success.


## Phase 7 evaluation

The remediation result is multidimensional rather than a single opaque verdict. It exposes security-condition resolution, attack-path resolution, alternate-path resolution, control effectiveness, security-test success, functional preservation, regression resistance, and evidence integrity. The provisional score is the unweighted arithmetic mean of these raw dimensions and is explicitly versioned for later calibration.

A test status of ERROR, TIMEOUT, or UNRESOLVED is not a security pass. Missing required security tests do not manufacture remediation credit. Candidate self-reports are never authoritative.
