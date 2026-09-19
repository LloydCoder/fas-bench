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
