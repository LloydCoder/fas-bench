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
    SCHEMA_VERSION,
    VERDICTS,
)

ROOT = Path(__file__).parents[1]


def test_canonical_vocabularies_are_unique_and_stable():
    assert len(VERDICTS) == 7 and len(set(VERDICTS)) == 7
    assert len(CATEGORIES) == 10 and len(set(CATEGORIES)) == 10
    assert DIFFICULTY_LEVELS == (
        "L1_LOCAL",
        "L2_MULTI_FUNCTION",
        "L3_MULTI_COMPONENT",
        "L4_AGENTIC",
        "L5_CROSS_SYSTEM",
    )
    assert len(EVIDENCE_TYPES) == 17
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
        "docs/evidence-engine.md",
        "cases/README.md",
        "cases/registry.json",
        "schemas/README.md",
        "tests/README.md",
        "pyproject.toml",
        ".github/workflows/ci.yml",
    ]
    assert not [path for path in required if not (ROOT / path).is_file()]


def test_roadmap_has_ten_phases():
    assert len(ROADMAP) == 10
    text = (ROOT / "docs/specification.md").read_text(encoding="utf-8")
    assert all(phase in text for phase in ROADMAP)


def test_versions_are_consistent():
    assert BENCHMARK_VERSION == "0.1.0"
    assert SCHEMA_VERSION == "0.1"
    init = (ROOT / "src/fas_bench/__init__.py").read_text()
    pyproject = (ROOT / "pyproject.toml").read_text()
    spec = (ROOT / "docs/specification.md").read_text()
    assert '__version__ = "0.1.0"' in init
    assert 'version="0.1.0"' in pyproject
    assert "Benchmark specification version:** 0.1.0" in spec


def test_no_old_verdict_names():
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
        assert not any(term in (ROOT / path).read_text(encoding="utf-8") for term in forbidden)


def test_fas_independence_is_explicit():
    text = (ROOT / "docs/specification.md").read_text(encoding="utf-8")
    assert "FAS is one candidate evaluated system" in text
    assert "MUST NOT import, require, execute, or derive ground truth from FAS" in text


def test_python_vocabulary_is_derived_from_common_schema():
    import json

    common = json.loads(
        (ROOT / "schemas/common/v0.1/common.schema.json").read_text(encoding="utf-8")
    )["$defs"]
    from fas_bench.contract import CLAIM_TYPES, EDGE_TYPES, NODE_TYPES, REASON_CODES

    assert CATEGORIES == tuple(common["Category"]["enum"])
    assert VERDICTS == tuple(common["Verdict"]["enum"])
    assert DIFFICULTY_LEVELS == tuple(common["Difficulty"]["enum"])
    assert EVIDENCE_TYPES == tuple(common["EvidenceType"]["enum"])
    assert EVIDENCE_ROLES == tuple(common["EvidenceRole"]["enum"])
    assert EVIDENCE_STATES == tuple(common["EvidenceVerification"]["enum"])
    assert CLAIM_TYPES == tuple(common["ClaimType"]["enum"])
    assert REASON_CODES == tuple(common["ReasonCode"]["enum"])
    assert NODE_TYPES == tuple(common["NodeType"]["enum"])
    assert EDGE_TYPES == tuple(common["EdgeType"]["enum"])
