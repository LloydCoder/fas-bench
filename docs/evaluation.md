# FAS-Bench Evaluation

**Document role:** evaluation methodology and metric interpretation.  
**Authority:** docs/specification.md defines normative semantics; this document explains evaluation behavior.

## Evaluation objective

The evaluator determines whether a structured submission is supported by benchmark-observable evidence and whether its security conclusions match the case ground truth. It does not grade prose style.

## Canonical pipeline

1. **Reconnaissance** — permitted repository, environment, scenario, and task information.
2. **Independent analysis** — system analysis without hidden ground truth.
3. **Structured submission** — machine-readable findings, evidence, verdicts, paths, impact, remediation, and verification.
4. **Evidence verification** — resolve and classify submitted evidence.
5. **Verdict evaluation** — evaluate the canonical verdict against ground truth.
6. **Attack-path normalization/comparison** — normalize nodes/edges and compare valid paths.
7. **Remediation evaluation** — determine whether the underlying condition is eliminated.
8. **Regression evaluation** — test previously established security properties after subsequent changes.
9. **Calibration/efficiency analysis** — report confidence and operational measurements.

## Evidence-first evaluation

Evidence is scored independently from the final verdict. A correct verdict with fabricated or unverifiable evidence is not equivalent to a correct verdict with verified evidence.

The evaluator should distinguish direct, supporting, missing, and contradictory evidence and the verification states VERIFIED, INVALID, UNRESOLVED, and CONTRADICTED.

## Verdict evaluation

Only the seven canonical verdicts from the specification are valid:

EXPLOITABLE, NOT_EXPLOITABLE, CONDITIONALLY_EXPLOITABLE, REMEDIATED, REMEDIATION_FAILED, REGRESSED, UNKNOWN.

UNKNOWN is not a failure-mode alias for NOT_EXPLOITABLE.

## Graph evaluation

Graph evaluation compares submitted security paths with the expected effective security graph. Apparent code/configuration relationships are not sufficient when a real security boundary blocks the transition.

The provisional graph score is:

GraphScore = 0.30 × NodeF1 + 0.35 × EdgeF1 + 0.20 × PathCompleteness + 0.15 × BoundaryCrossingF1.

These weights are provisional and must be empirically validated in Phase 8.

## Provisional scoring

The Phase 1 weights are a research hypothesis, not a validated scientific standard. Reports should expose finding identification, verdict correctness, evidence quality, reachability/security-boundary reasoning, attack paths, impact, remediation, calibration, efficiency, false-positive resistance, and evidence-integrity measures separately.

## Calibration

Confidence must be evaluated separately from correctness. Supported metrics include Brier score, expected calibration error, reliability analysis, and confidence-conditioned error analysis.

## Efficiency

Record wall-clock time, tool calls, tokens, compute, external requests, test executions, and cost where available. Cross-system comparisons must include relevant environment metadata.

## Determinism and provenance

For a fixed benchmark, case, evaluator, submission, and environment, evidence verification, verdict evaluation, graph normalization, and score calculation must be deterministic. Intentional nondeterminism must be recorded.

Evaluation records should include benchmark/case/evaluator/submission versions, system/model metadata, environment, dependencies, timestamps, seeds, tools, network policy, image identity, and content digests.

## Scientific limitations

Phase 1 does not establish statistical validity, optimal score weights, real-world generalization, or contamination resistance. Those properties require empirical work in later phases.
