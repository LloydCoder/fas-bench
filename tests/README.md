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
