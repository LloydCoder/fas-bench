# Phase 13.1 — Governance and Ecosystem Contract

Phase 13.1 converts the existing Phase 10 governance foundations into a
machine-checkable change-control contract and a documented maintainer process.

## Governance record

A material change record contains:

- change class;
- rationale;
- impact assessment;
- validation evidence;
- changelog entry;
- security-objective review;
- oracle/ground-truth review;
- security review;
- reproducibility/integrity review;
- explicit approval.

The implementation validates the record shape but never creates approval.

## Release and correction lifecycle

A benchmark release is a versioned measurement artifact. Corrections create a
new identity; they do not rewrite historical releases.

Case retirement preserves the retirement reason and affected releases. Oracle
corrections identify affected results so consumers can decide whether to
rerun historical evaluations.

## Ecosystem contract

Contributors must preserve benchmark independence. Evaluated systems,
FAS, ThreatFade, Tinlance, and other products remain external candidates rather
than hidden dependencies of the benchmark.

External evaluators should record exact source, corpus, evaluator, scoring,
execution, and environment identities.

## Enterprise boundary

Phase 13.1 does not claim that repository automation replaces human governance,
legal review, independent scientific review, or organizational incident
response.
