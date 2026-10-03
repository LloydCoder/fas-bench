# Contributing to FAS-Bench
**Authority:** docs/specification.md.

Contributions must preserve evidence-first evaluation, exploitability semantics, effective security boundaries, alternate-path analysis, reproducibility, and independence from evaluated systems.

## Phase 2 contract
Schema changes require tests, fixtures, documentation, and compatibility review. New semantics must be proposed as specification changes.

## Independence
FAS-Bench MUST NOT import, require, execute, or derive ground truth from FAS.

## Security
Treat benchmark inputs as untrusted. Do not execute case code on the host, use real credentials, or allow uncontrolled external networking.

## CI
Formatting, linting, tests, schema validation, build, package import, and repository consistency checks must remain green.

## Phase 3 case contributions
New or changed cases must include a falsifiable security hypothesis, explicit attacker model, synthetic credentials only, controlled environment, structured ground truth, deterministic oracle, limitations, and case version. Public cases are development data; do not commit hidden evaluation answers.

## Phase 4 evidence contributions
Evidence changes must remain deterministic and benchmark-independent. New expected evidence must identify an authoritative case artifact and structured fact where the fact can be deterministically observed. Never execute submission evidence fields.

## Phase 5 evaluator contributions
Finding and verdict semantics must remain deterministic and case-independent. Core evaluator code MUST NOT branch on individual case IDs. Changes must include positive, negative, contradiction, missing-evidence, cross-case, metamorphic, and tamper tests where applicable.

## Phase 6 graph contributions
Graph changes must preserve deterministic canonicalization, finite traversal limits, semantic edge direction, evidence linkage, and FAS independence.

## Phase 9 harness contributions
Never run malicious benchmark cases or candidate code directly on the host. Use the secure evaluation harness and a pinned immutable image.

Phase 9 changes must preserve fail-closed behavior. Do not add host execution fallbacks, unrestricted network access, privileged containers, Docker-socket mounts, inherited host environments, real credentials, or mutable image tags.

Security-sensitive changes should include isolation, resource, artifact-integrity, cache-identity, timeout, cleanup, and reproducibility tests. Docker-backed tests must run only in a disposable CI/local environment intended for the harness.

Before opening a PR, run the complete test suite, formatting and lint checks, package build/install, corpus validation, and the Docker-backed Phase 9 checks available in CI.


## Phase 10.1 security and release contributions

Changes touching evidence verification, release manifests, canonicalization, secure execution, environment policy, lifecycle state, or GitHub Actions must include a focused regression test and preserve fail-closed behavior. Never trust candidate-provided hashes, lifecycle declarations, or aggregate scores as benchmark authority. Do not introduce unbounded execution, candidate-specific coupling, hidden-corpus leakage, or secret material.

## Phase 10 case and release contributions

New cases require a security objective, taxonomy, difficulty, fixture, oracle, expected evidence/verdict/graph/remediation state where applicable, provenance, licensing review, deterministic validation, and content digests. A case is not RELEASED merely because its directory exists or its legacy metadata says VALIDATED.

Mutation contributions must declare their semantic relation and include a validation path. Renaming identifiers is not by itself evidence of security-semantic preservation; the trusted validator/oracle must establish that relationship.

Release changes require corpus validation, contamination scanning, independence checks, manifest generation, manifest verification, and documentation/changelog updates. Do not publish hidden ground truth in the public package.


## Phase 10.2 verification contributions

Changes to critical semantics should include an independently derived expected property where practical. Do not construct an oracle by calling the production implementation and asserting that result against itself.

Reference checks should be small, obvious, deterministic, and auditable. Differential tests must investigate divergences rather than automatically choosing the production implementation as correct. Metamorphic tests should document the semantic relation they enforce.

Release changes must run both the normal release verifier and the independent verifier. Certification must be derived from observed checks; never edit a certification report or manifest status to make a release pass.

Reproducibility-sensitive changes must not depend on local paths, hostnames, timestamps, usernames, uncontrolled environment variables, filesystem enumeration order, or hidden local state.

## Phase 11–15 measurement, platform, and governance contributions

Phase 11 case/mutation changes must preserve authoritative-oracle validation and
must not turn mutation generation into ground truth.

Phase 11.1 runtime/agentic oracle changes must emit observations with execution,
artifact, policy, and environment identities. Oracle output MUST NOT silently
become the final benchmark verdict.

Phase 12 measurement changes must report uncertainty, assumptions, and
stratification. Do not present public-corpus measurements as generalized
population estimates without supporting empirical methodology.

Phase 12.1 validation changes must distinguish internal protocol checks from
actual external review. The repository must never fabricate independent
reviewer evidence, replication results, or scientific validation.

Phase 13 release-security changes must preserve signed provenance, SBOM
attestation, dependency auditing, secret scanning, reproducible builds, and
independent verification. Do not weaken a release gate to make CI green.

Phase 13.1 governance changes must preserve explicit human approval and
historical release identities. Corrections create new identities rather than
silently rewriting historical benchmark results.

Phase 14 platform changes must keep candidate execution outside the platform
control plane and delegate untrusted execution to the Phase 9 secure provider.
Job identities must be content-derived.

Phase 15 monitoring changes may raise drift or benchmark-health signals but
MUST NOT automatically mutate gold truth, scoring weights, corpus identities,
or release state.


## Phase 16–21 advanced benchmark contributions

Phase 16 test specifications must include an objective, taxonomy, difficulty,
oracle type, evidence requirements, lifecycle state, and deterministic source
identity where certification or release requires it.

Phase 17 hidden-corpus changes must preserve access separation, temporal
boundaries, contamination assessment, and the rule that private official
answers never enter the public repository.

Phase 18 scenario changes must bind every event to the scenario environment and
preserve deterministic ordering and content-derived identity.

Phase 19 adversarial cases must declare the attack class, expected invariant,
mutation identity, and authoritative oracle. Infrastructure failures must never
be treated as robustness passes.

Phase 20 measurement changes must preserve deterministic uncertainty and
agreement calculations and clearly distinguish benchmark-conditioned results
from population-general claims.

Phase 21 submission/result/provenance changes must preserve candidate
independence, content-addressed identities, provenance completeness, and human
approval for certification and release.
