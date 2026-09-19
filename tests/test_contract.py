from pathlib import Path

from fas_bench.contract import (
    BENCHMARK_VERSION,
    CASE_IDS,
    CASE_REGISTRY,
    CATEGORIES,
    DIFFICULTY_LEVELS,
    EVIDENCE_ROLES,
    EVIDENCE_STATES,
    EVIDENCE_TYPES,
    GOLD_CASE_IDS,
    ROADMAP,
    VERDICTS,
)

ROOT = Path(__file__).parents[1]


def test_canonical_vocabularies_are_unique_and_stable():
    assert len(VERDICTS) == 7 and len(set(VERDICTS)) == 7
    assert len(CATEGORIES) == 10 and len(set(CATEGORIES)) == 10
    assert DIFFICULTY_LEVELS == (
        "L1 Local",
        "L2 Multi-function",
        "L3 Multi-component",
        "L4 Agentic",
        "L5 Cross-system",
    )
    assert len(EVIDENCE_TYPES) == 18
    assert EVIDENCE_ROLES == ("DIRECT", "SUPPORTING", "MISSING", "CONTRADICTORY")
    assert EVIDENCE_STATES == ("VERIFIED", "INVALID", "UNRESOLVED", "CONTRADICTED")


def test_case_registry_is_complete_unique_and_formatted():
    ids = [case_id for case_id, _ in CASE_REGISTRY]
    assert ids == list(CASE_IDS)
    assert len(ids) == len(set(ids))
    assert all(
        case_id.startswith("FAS-") and len(case_id) == 7 and case_id[4:].isdigit()
        for case_id in ids
    )
    assert set(GOLD_CASE_IDS) == {"FAS-001", "FAS-002", "FAS-006", "FAS-016", "FAS-020"}
    assert set(GOLD_CASE_IDS) <= set(ids)


def test_required_documentation_exists():
    required = [
        "README.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "docs/specification.md",
        "docs/architecture.md",
        "docs/evaluation.md",
        "docs/methodology.md",
        "docs/threat-model.md",
        "cases/README.md",
        "schemas/README.md",
        "tests/README.md",
        "pyproject.toml",
        ".github/workflows/ci.yml",
    ]
    missing = [path for path in required if not (ROOT / path).is_file()]
    assert not missing, f"Missing required Phase 1 files: {missing}"


def test_roadmap_has_exactly_ten_phases():
    assert len(ROADMAP) == 10
    assert all(item.startswith("PHASE ") for item in ROADMAP)
    specification = (ROOT / "docs/specification.md").read_text(encoding="utf-8")
    for phase in ROADMAP:
        assert phase in specification


def test_benchmark_version_is_consistent():
    assert BENCHMARK_VERSION == "0.1.0"
    init = (ROOT / "src/fas_bench/__init__.py").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    specification = (ROOT / "docs/specification.md").read_text(encoding="utf-8")
    assert '__version__ = "0.1.0"' in init
    assert 'version = "0.1.0"' in pyproject
    assert "Benchmark specification version: **0.1.0**" in specification


def test_documents_do_not_redefine_old_verdicts_or_taxonomy():
    docs = [
        "README.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "docs/specification.md",
        "docs/architecture.md",
        "docs/evaluation.md",
        "docs/methodology.md",
        "docs/threat-model.md",
        "cases/README.md",
        "schemas/README.md",
        "tests/README.md",
    ]
    forbidden = ("FALSE_POSITIVE", "TRUE_POSITIVE", "PARTIALLY_EXPLOITABLE")
    for path in docs:
        text = (ROOT / path).read_text(encoding="utf-8")
        assert not any(term in text for term in forbidden), path


def test_fas_independence_is_explicit():
    specification = (ROOT / "docs/specification.md").read_text(encoding="utf-8")
    assert "FAS is one candidate evaluated system" in specification
    assert "MUST NOT import, require, execute, or derive ground truth from FAS" in specification
