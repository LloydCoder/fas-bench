# Phase 12 — Statistical Calibration and Benchmark Validity

Phase 12 adds transparent statistical primitives for benchmark analysis while
preserving the distinction between engineering output and scientific validation.

## Metrics

The implementation reports:

- fixed-corpus benchmark accuracy;
- Wilson uncertainty intervals for binomial outcomes;
- deterministic bootstrap intervals;
- item difficulty as observed error rate;
- stratified accuracy;
- confidence calibration error.

The bootstrap is seeded for reproducibility. The report records its method rather
than presenting an interval as universally valid under every sampling design.

## Measurement boundary

A benchmark-conditioned accuracy describes the evaluated corpus. It does not by
itself establish generalized accuracy for an unobserved population.

The public FAS-Bench corpus remains development data. The Phase 12 report
therefore emits a scientific_validation_claim value of false.

Future independent validation should test sampling assumptions, item dependence,
difficulty effects, inter-rater/oracle agreement, benchmark saturation, and
uncertainty under the intended evaluation population. Hierarchical models such
as GLMMs can be introduced when the empirical dataset is sufficient to justify
their assumptions.

## Exit contract

The Phase 12 implementation must be deterministic, auditable, explicit about
uncertainty, stratification, and sampling assumptions, and must not turn a
single aggregate score into an unsupported universal claim.
