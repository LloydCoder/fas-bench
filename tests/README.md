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
