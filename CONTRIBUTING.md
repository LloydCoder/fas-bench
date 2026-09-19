# Contributing to FAS-Bench

**Document role:** contribution workflow and governance.  
**Authority:** docs/specification.md is the normative benchmark contract.

FAS-Bench contributions must be reproducible, reviewable, independently defined, and safe to execute.

## Benchmark-design principles

Contributors should preserve evidence-first evaluation, exploitability adjudication, effective security boundaries, alternate-path analysis, uncertainty, reproducibility, and independence from any evaluated system.

## Case contributions

For substantial cases or case families, open an issue describing:

- stable case identifier or proposed identifier;
- primary and secondary categories;
- capability being evaluated;
- security condition;
- attacker/environment assumptions;
- expected verdict;
- false-positive or false-negative trap;
- required evidence;
- attack-path expectation;
- remediation/regression behavior;
- deterministic validation strategy;
- difficulty level and structural justification;
- contamination considerations;
- provenance/licensing.

A case MUST use synthetic credentials and MUST NOT target real external systems.

## Ground truth

Case ground truth must be independently established. Contributors MUST NOT derive benchmark truth from the output of a system being evaluated. Ground truth must distinguish observable evidence from interpretation.

## Normative changes

Contributors MUST NOT silently change scoring semantics, verdict meanings, taxonomy, difficulty definitions, or other normative rules while adding cases or implementation code.

Normative changes require a specification review and an explicit benchmark-version decision.

## Engineering requirements

Changes should include appropriate tests and documentation. CI must remain green. Formatting, linting, tests, package build/import, and repository-contract validation are required for merge.

## Independence requirement

FAS-Bench MUST remain usable without FAS. Contributions MUST NOT add an import, runtime dependency, scoring dependency, or ground-truth dependency on FAS.

## Security

Treat benchmark cases and dependencies as untrusted. Do not execute arbitrary case code on the host. Report infrastructure/evaluator vulnerabilities privately when public disclosure could compromise benchmark integrity.

## Versioning

Every evaluation-relevant change must identify the applicable benchmark, schema, evaluator, case-set, and submission-format versions. Changes to normative semantics require specification-version review.
