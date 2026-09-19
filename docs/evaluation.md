# FAS-Bench Evaluation

The evaluator will consume a benchmark case and a normalized system submission.

The evaluation pipeline is:

1. validate submission schema;
2. verify evidence references;
3. evaluate claims and verdicts;
4. compare attack paths;
5. evaluate impact;
6. evaluate remediation and regression;
7. calculate component metrics;
8. emit a reproducible evaluation result.

The evaluator must remain deterministic for a fixed benchmark version, case version, evaluator version, environment, and submission.

Scoring weights are provisional until validated empirically.
