# Tests

**Document role:** test architecture and Phase 1 verification guidance.  
**Authority:** docs/specification.md defines normative semantics.

Phase 1 tests verify repository-contract invariants rather than implementing the later evaluator.

## Test layers

- unit/ — future deterministic component tests;
- integration/ — future evaluator/schema integration tests;
- fixtures/ — small test-only fixtures;
- repository contract tests — canonical vocabulary, case registry, versions, documentation, roadmap, and independence;
- documentation tests — required sections and local Markdown-link integrity;
- package tests — import and version metadata.

## Required Phase 1 checks

The Phase 1 suite verifies:

- canonical verdict uniqueness;
- canonical category count and names;
- difficulty levels;
- evidence vocabulary;
- case ID format and uniqueness;
- exact initial case registry;
- gold-case membership;
- ten-phase roadmap;
- required documentation;
- benchmark/package version consistency;
- absence of prohibited obsolete verdict names;
- explicit FAS independence;
- required specification sections;
- local documentation links;
- absence of unfinished placeholder language in the normative specification.

Tests MUST validate semantics where practical and MUST NOT exist only to inflate coverage.

## Local CI parity

From a clean environment:

    python -m pip install -e ".[dev]"
    ruff format --check .
    ruff check .
    pytest
    python -m build
    python -m pip install --force-reinstall dist/*.whl
    python -c "import fas_bench; print(fas_bench.__version__)"

The CI workflow runs the equivalent checks on supported Python versions.
