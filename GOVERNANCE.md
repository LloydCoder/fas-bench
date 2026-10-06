# FAS-Bench Governance

FAS-Bench is a security-measurement project. Governance protects benchmark integrity, scientific validity, reproducibility, and historical comparability.

## Authority

The normative benchmark contract is [docs/specification.md](docs/specification.md).

Governance defines how material changes are reviewed and released; it does not redefine benchmark semantics.

## Change classes

Material changes are classified as:

- CASE
- ORACLE
- SCHEMA
- SCORING
- EVALUATOR
- HARNESS
- RELEASE
- DOCUMENTATION
- INFRASTRUCTURE

Material CASE, ORACLE, SCHEMA, SCORING, EVALUATOR, HARNESS, RELEASE, or INFRASTRUCTURE changes require documented rationale, impact assessment, validation evidence, changelog treatment, and review before release.

## Required review dimensions

A material security or benchmark change requires evidence for:

1. security objective review;
2. oracle/ground-truth review;
3. security review;
4. reproducibility/integrity review.

Release approval is separate from implementation authorship.

## Ground-truth corrections

If an oracle is found to be wrong:

1. freeze the affected release for new official evaluations;
2. preserve the original case and historical release identity;
3. document the defect and evidence;
4. independently review the corrected oracle;
5. issue a new benchmark version;
6. identify affected historical results;
7. publish a correction notice when appropriate.

Historical benchmark identities must never be silently rewritten.

## Case retirement

Retirement records must include the reason, affected release range, retirement date, replacement case where applicable, and compatibility impact.

## Public and hidden evaluation

Public FAS-001–FAS-020 cases are development/practice data. They must not be represented as a secret or statistically representative official corpus.

Hidden official evaluation material must remain outside the public repository and release artifacts.

## Security disclosure

Follow [SECURITY.md](SECURITY.md). Do not publish hidden cases, evaluator-only material, credentials, or exploit details that could compromise official evaluation.

## Human approval

Automation can validate gates and produce evidence. It cannot manufacture human approval, certify scientific validity, or silently change historical benchmark truth.

## Maintainer responsibility

The repository owner and designated maintainers are responsible for repository administration, release approval, security response, and maintaining the accuracy of project metadata and community contacts.
