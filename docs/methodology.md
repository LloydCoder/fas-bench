# FAS-Bench Methodology
**Role:** research methodology.
**Authority:** docs/specification.md.

## Signal, finding, claim, evidence, verdict
A signal is an observation. A finding groups a reported condition. A claim is an assertion. Evidence supports or contradicts the claim. A verdict adjudicates security state. These are intentionally separate so persuasive prose or scanner output cannot become verified truth automatically.

## Attack paths and effective security
Paths are ordered references over stable graph IDs. Controls can invalidate apparent paths; graph cycles are allowed, while path traversal is explicitly ordered.

## Remediation and regression
Remediation records a security-property change and revalidation. Regression records loss of a previously secure property. Neither is reduced to a generic finding label.

## Structural versus semantic validation
JSON Schema handles local structure. Semantic validation handles relationships that require multiple objects.

## Scientific validity
Scoring weights, evidence-integrity thresholds, generalization, taxonomy completeness, and contamination resistance remain provisional research questions.

## Phase 3 corpus methodology
The validated initial cases prioritize causal clarity and reproducibility over codebase size. Synthetic cases make effective security boundaries observable and deterministic. Ground truth is triangulated from structured claims/evidence, attack-path representation, and an oracle-derived observed state. The public development corpus does not remove contamination risk; future evaluation requires held-out cases or undisclosed mutations.


## Phase 3 validation methodology

The corpus is a controlled experimental set, not a statistical sample of real-world vulnerabilities. Gold cases combine structured security-model evidence with executable security-property tests. Dynamic oracles exercise local synthetic targets; mutation tests verify oracle sensitivity to security-semantic changes. Public ground truth is deliberately acknowledged as a contamination risk, so later evaluation must use held-out or undisclosed variants.


## Phase 4 methodology

FAS-Bench separates observation, evidence, claim, security property, and verdict. Phase 4 verifies only the evidence layer. Canonicalization removes representation differences without erasing security-relevant distinctions. Evidence identity is content-derived, duplicate evidence is preserved for auditability but cannot inflate coverage, and missing evidence is not treated as invalid evidence. Later phases consume the structured result rather than reimplementing evidence resolution.
