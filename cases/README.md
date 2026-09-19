# Benchmark Cases

**Document role:** case-authoring and corpus guidance.  
**Authority:** docs/specification.md defines case semantics and canonical terminology.

Cases are the primary benchmark units. A case defines a security property, scenario, environment assumptions, observable artifacts, evidence requirements, and expected security state.

## Initial registry

The Phase 1 registry contains FAS-001 through FAS-020 exactly as listed in the normative specification. The registry is a design inventory, not a validated corpus.

Initial gold cases: FAS-001, FAS-002, FAS-006, FAS-016, FAS-020.

## Case requirements

A future case SHOULD contain:

- stable case identifier;
- primary and optional secondary taxonomy categories;
- difficulty level with structural justification;
- repository/application fixture;
- scenario and attacker assumptions;
- environment/configuration;
- explicit security condition;
- claims and required evidence;
- expected verdict;
- effective attack path and relevant boundaries;
- remediation/regression state where applicable;
- deterministic validation tests;
- provenance and content hashes where applicable.

Ground truth must be independently established and must not be generated from the output of the system being evaluated.

## Case classes

- gold/ — reviewed cases used to validate methodology and evaluator behavior;
- public/ — cases intentionally available for development or public evaluation;
- private/ — held-out evaluation material; hidden ground truth MUST NOT be committed to the public repository.

## Safety

Cases are untrusted security artifacts. Contributors MUST use synthetic credentials, avoid real targets, and document any dynamic execution requirements. Case fixtures MUST NOT require production secrets or uncontrolled external network access.

## Ground-truth separation

Materials visible to an evaluated system MUST remain separate from hidden expected results, evaluator internals, and hidden tests. Public release does not by itself solve contamination.

## Contributions

Normative changes to categories, verdicts, scoring, or other benchmark semantics require specification review. Adding a case must not silently modify benchmark semantics.
