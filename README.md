# FAS-Bench
**Forensic Agent Security Benchmark**

> Scanners find signals. FAS-Bench measures whether a system can prove what those signals actually mean.

## Status
**Phase 2 — Schema & Data Model: implementation in progress until CI verification and merge.**

FAS-Bench is an independent benchmark. FAS is one candidate evaluated system and is not a dependency, reference implementation, or source of ground truth.

## Phase 2 contract
The Phase 1 conceptual contract is now encoded as JSON Schema Draft 2020-12 families under schemas/. Shared definitions centralize canonical IDs and enums. Python semantic validation handles cross-object references, graph/path integrity, version compatibility, remediation consistency, conditional verdicts, and evaluation-result arithmetic.

## Validation states
Schema-valid != semantically-valid != benchmark-correct.

## Public/hidden boundary
Submissions contain system beliefs and structured evidence. They must not contain expected verdicts or hidden evaluator truth. Public case metadata remains separate from hidden ground truth.

## Canonical categories
C1_REACHABILITY, C2_DATA_FLOW_TAINT, C3_AUTHENTICATION_AUTHORIZATION, C4_AI_AGENT_SECURITY, C5_MCP_SECURITY, C6_SUPPLY_CHAIN, C7_SECRETS_SENSITIVE_DATA, C8_INFRASTRUCTURE_CLOUD, C9_CROSS_COMPONENT_ATTACK_PATHS, C10_REMEDIATION_REGRESSION.

## Canonical difficulty
L1_LOCAL, L2_MULTI_FUNCTION, L3_MULTI_COMPONENT, L4_AGENTIC, L5_CROSS_SYSTEM.

## Canonical verdicts
EXPLOITABLE, NOT_EXPLOITABLE, CONDITIONALLY_EXPLOITABLE, REMEDIATED, REMEDIATION_FAILED, REGRESSED, UNKNOWN.

## Local CI parity
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
pytest
python -m build
python -m pip install --force-reinstall dist/*.whl
python -c "import fas_bench; print(fas_bench.__version__)"

## Roadmap
1. Specification & Benchmark Contract
2. Schema & Data Model
3. Gold Cases & Ground Truth
4. Deterministic Evidence Engine
5. Verdict & Finding Evaluator
6. Attack-Path & Security-Graph Engine
7. Remediation & Regression Engine
8. Scoring, Calibration & Benchmark Analytics
9. Secure Evaluation Harness & Reproducibility
10. Benchmark Corpus, Contamination Defense & Release
