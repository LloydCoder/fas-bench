# FAS-Bench v0.1 Specification

**Status:** Draft / research validation

The normative specification is being developed around:

- Case
- Scenario
- Claim
- Evidence
- Attack Graph
- Verdict
- Finding
- Remediation
- Submission
- Evaluation Result
- Provenance

## Normative principles

- Ground truth must be machine-readable.
- Evidence must be independently verifiable where possible.
- Verdicts must distinguish exploitability from mere reachability or vulnerability presence.
- Attack paths must represent meaningful security-boundary transitions.
- Remediation must be tested against alternate paths.
- Unknown is a valid outcome when evidence is insufficient.
- Scoring weights remain provisional until empirical validation.

## Planned schema package

- case.schema.json
- claim.schema.json
- evidence.schema.json
- attack_graph.schema.json
- verdict.schema.json
- submission.schema.json
- evaluation_result.schema.json
