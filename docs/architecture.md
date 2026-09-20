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
