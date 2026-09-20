# FAS-Bench
**Forensic Agent Security Benchmark**

> Scanners find signals. FAS-Bench measures whether a system can prove what those signals actually mean.

## Status
**Phase 5 — Verdict & Finding Evaluator: CI-validated implementation candidate.**

FAS-Bench is an independent benchmark. FAS is one candidate evaluated system and is not a dependency, reference implementation, or source of ground truth.

## Phase 5 verdict & finding evaluator

The deterministic evidence engine verifies submitted evidence against authoritative case artifacts. It canonicalizes evidence, computes stable content-derived identities, safely resolves case-relative artifacts, verifies structured facts and source locations, detects duplicates and relationship mismatches, and reports verified/invalid/unresolved/contradicted/missing evidence with raw coverage and integrity statistics. A verified evidence item establishes an underlying fact; it does not by itself establish exploitability or the final security verdict.

Phase 5 deterministically evaluates findings, claims, verified evidence, security-condition state, effective controls, preconditions, remediation seams, and the submitted verdict. Verdict correctness and evidence support remain separate outputs; Phase 5 does not assign the final benchmark score.

Finding evaluation command:

`fas-bench evaluate finding --case FAS-002 --submission tests/fixtures/phase5/FAS-001-gold.json --json`

Evidence validation command:

`fas-bench evidence validate tests/fixtures/integrated/FAS-001.json --case FAS-001 --json`

## Phase 3 corpus

The CI-validated initial public development corpus contains FAS-001 through FAS-020. Each case defines a security hypothesis, attacker model, controlled environment, structured expected claims/evidence/finding/attack path/verdict/remediation, and a deterministic oracle. The public corpus is intentionally not treated as a hidden evaluation set; future evaluation requires held-out or mutated cases.

Case commands:

`fas-bench cases validate-all`

`fas-bench cases validate-gold`

`fas-bench cases reproduce FAS-001`

## Phase 2 contract
The Phase 1 conceptual contract is now encoded as JSON Schema Draft 2020-12 families under schemas/. Shared definitions centralize canonical IDs and enums. Python semantic validation handles cross-object references, graph/path integrity, version compatibility, remediation consistency, conditional verdicts, and evaluation-result arithmetic.

## Validation states
Schema-valid != semantically-valid != benchmark-correct.

## Public/hidden boundary
The FAS-001 through FAS-020 corpus is public development data, so its gold facts are not a hidden evaluation set. The evidence engine does not expose additional hidden truth through diagnostics. Future benchmark releases must use held-out or otherwise contamination-resistant evaluation data.

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
