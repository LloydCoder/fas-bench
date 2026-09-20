# Tests
**Role:** test architecture and Phase 2 verification guidance.

## Test levels
1. Schema syntax and Draft 2020-12 meta-validation.
2. Valid and invalid fixture validation.
3. Cross-schema semantic validation.
4. Graph/path consistency.
5. Evaluation-result score integrity.
6. Package and repository consistency.

## Local CI parity
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
pytest
python -m build
python -m pip install --force-reinstall dist/*.whl
python -c "import fas_bench; print(fas_bench.__version__)"

## Phase 3
`test_phase3_cases.py` validates the complete case registry, package contracts, deterministic oracle agreement, and gold-case mutation sensitivity.


## Phase 5 tests

`tests/test_phase5_evaluator.py` covers 20-case gold self-evaluation, false-positive resistance, conditional and remediation semantics, evidence-to-verdict dependency, contradictory claims, cross-case contamination, confidence validation, tamper detection, deterministic fingerprints, and metamorphic invariants.


## Phase 6 tests

Tests/test_phase6_graph.py covers all 20 public graphs, graph self-consistency, empty/saturated submissions, fabricated and reversed edges, duplicates, dangling references, path continuity, cycles, traversal limits, semantic identifier variation, graph diffing, and minimal paths. Tests/test_phase6_properties.py covers canonicalization idempotence, permutation-invariant digests, identity diffs, and score reflexivity.


## Phase 7 tests

Tests cover complete remediation, alternate-path failure, cosmetic fixes, overblocking, UNKNOWN, regression, secure refactoring, evidence fabrication, test removal/absence, state/version identity, schema validation, versioned fixtures, and all twenty remediation artifacts.
