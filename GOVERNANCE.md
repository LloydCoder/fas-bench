# FAS-Bench Governance

FAS-Bench is a security measurement project. Governance protects benchmark
integrity, scientific validity, reproducibility, and historical comparability.

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

Material CASE, ORACLE, SCHEMA, SCORING, EVALUATOR, HARNESS, RELEASE, or
INFRASTRUCTURE changes require documented rationale, impact assessment,
validation evidence, changelog treatment, and review before release.

## Required review dimensions

A material change requires evidence for:

1. security objective review;
2. oracle/ground-truth review;
3. security review;
4. reproducibility/integrity review.

Release approval is separate from implementation authorship.

## Ground-truth corrections

If a case oracle is found to be wrong:

1. freeze the affected release for new official evaluations;
2. preserve the original case and historical release identity;
3. document the defect and evidence;
4. independently review the corrected oracle;
5. issue a new benchmark version;
6. identify affected historical results;
7. publish a correction notice.

Historical benchmark identities must not be silently rewritten.

## Case retirement

Retirement records must include the reason, affected release range, retirement
date, replacement case when applicable, and compatibility impact.

## Security and disclosure

Do not publish hidden cases, evaluator-only material, credentials, or exploit
details that would compromise an official held-out evaluation. Security
vulnerabilities follow SECURITY.md.

## Research integrity

Public development results must not be represented as statistically validated
or official hidden-set results. Benchmark reports must preserve benchmark
version, case-population identity, execution environment, evaluator version,
scoring configuration, and relevant limitations.

## Release approval

A release is publishable only when its automated release gates are green and
the required governance record has been reviewed by the designated human
maintainers. Automation cannot manufacture human approval.
