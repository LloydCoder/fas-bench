# FAS-Bench Architecture
**Role:** architecture and implementation model.
**Authority:** docs/specification.md.

## Phase 2 validation flow
Public Case Data → Schema Validation → Semantic Validation → Evaluation Pipeline → Scoring / Results.

## Submission
Submission contains Claims, Evidence, Findings, Verdict, Attack Paths, Impact, Remediation, and Verification.

## Trust boundaries
Public benchmark inputs are distinct from evaluator-only ground truth. A submission cannot declare expected ground truth.

## Independence
FAS-Bench remains independent of FAS. FAS is only a candidate evaluated system.

## Data-contract layers
Schemas encode serialized structure. Semantic validators encode cross-object invariants. Later evaluator phases consume these stable objects without redefining their identity.

## Phase 2 to later phases
Phase 3 constructs, validates, and reproduces gold cases; Phase 4 verifies evidence; Phase 5 can adjudicate findings and verdicts; Phase 6 can normalize graphs; Phase 7 can evaluate remediation/regression; Phase 8 can consume evaluation-result metrics; Phase 9 can add secure execution; Phase 10 can publish the corpus.


## Phase 3 case pipeline

Case Definition → Schema Validation → Semantic Validation → Environment/State Construction → Oracle Execution → Ground-Truth Validation → Release Gate.

The case corpus is independent of FAS and is designed to remain valid if FAS is removed.


## Phase 3 architecture

Case Definition → Schema Validation → Semantic Validation → Environment Construction → Oracle Execution → Ground-Truth Validation → Integrity/Reproducibility Gate → Release Gate.

Gold cases receive enhanced dynamic validation and mutation sensitivity checks. The Phase 3 oracle runner uses a pinned Python image, network isolation, read-only case mounts, dropped capabilities, resource limits, and deterministic cleanup. The public corpus remains development data; future hidden evaluation must use held-out cases or undisclosed mutations.


## Phase 4 evidence pipeline

Phase 4 establishes a deterministic evidence substrate: Case → Integrity Verification → Ground Truth Evidence → Submission Parsing → Canonical Normalization → Safe Resolution → Evidence Verification → Relationship/Duplicate Analysis → Coverage/Integrity Result. Phase 5 consumes these results for verdict evaluation; Phase 4 does not adjudicate exploitability.


## Phase 5 verdict pipeline

Phase 5 consumes the Phase 4 evidence result without duplicating its verification logic:

Submission → Finding Parser → Claim Resolver → Verified Evidence → Security Condition Resolver → Reachability/Control/Precondition Analysis → Exploitability Adjudication → Verdict Resolver → Structured Verdict Reasoning → Evaluation Result.

Finding identity is structured rather than title-based. Claim matching uses structured claim properties. Security-condition state is derived from declarative case path status, explicit conditions, and remediation state. The evaluator derives the authoritative verdict from those facts and checks the submission's verdict independently. No LLM, FAS runtime, scanner output, or case-ID branch is authoritative.

Phase 5 exposes finding correctness, claim status, evidence support/integrity, verdict correctness/support, security-condition facts, and a deterministic fingerprint. Final composite scoring is deferred to Phase 8.


## Phase 6 graph architecture

Phase 6 inserts a first-class graph substrate after evidence/claim adjudication:

Case → Evidence → Claims → Security Graph → Effective Security Graph → Attack Paths → Boundary/Control Analysis → Verdict/Scoring → Remediation/Regression

The graph engine owns canonical graph representation, deterministic validation, identity, traversal limits, path analysis, graph matching, and graph diffing. Phase 4 remains the sole evidence-verification authority; Phase 5 remains the verdict/finding adjudication layer. Phase 6 does not hard-code individual case identifiers.


## Phase 7 architecture

Baseline security state → post-remediation security state → graph/path diff → alternate-path analysis → security-condition diff → security/functional/regression tests → evidence-integrity gate → remediation verdict.

Phase 4 owns evidence verification; Phase 5 owns finding/verdict adjudication; Phase 6 owns graph semantics; Phase 7 owns remediation/regression adjudication; Phase 9 will own untrusted candidate execution and sandboxing. Phase 7 never imports or executes FAS.
