# Phase 10.2 Verification Model

FAS-Bench has three distinct layers: the benchmark implementation, an independent verification layer, and release certification.

Independent verification is deliberately narrow. It derives expected properties from normative invariants and separately implemented checks rather than calling the production release verifier to obtain the expected answer.

## Independently checked in Phase 10.2

- canonical JSON determinism and rejection of non-finite numbers
- component and release-manifest digest integrity
- public corpus population identity
- path and line-range reference semantics
- graph identity and bounded score invariants
- tamper detection and certification anti-spoofing

## Boundaries

The complete evaluator, graph engine, remediation adjudication and statistical policy remain implementation-derived and require additional external review. Ground-truth scientific validity, training-contamination freedom, host/kernel/Docker security and statistical representativeness cannot be established by repository self-tests.

The public FAS-001 through FAS-020 corpus is development/practice data, not a hidden official evaluation corpus.
