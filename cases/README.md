# Benchmark Cases

Cases are the primary benchmark units.

Each case should contain:

- repository or application fixture
- environment/configuration
- scenario metadata
- expected findings
- required evidence
- expected verdict
- expected attack path
- remediation state where applicable
- deterministic validation tests
- case documentation

## Case classes

- gold/ — expert-reviewed cases used to validate methodology and the evaluator.
- public/ — cases intended for development and public benchmarking.
- private/ — held-out evaluation material; it must not be committed to the public repository.

The public repository must never contain hidden ground truth intended to remain secret.
