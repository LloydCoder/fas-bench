import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
DOCS = [
    "README.md", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md",
    "docs/specification.md", "docs/architecture.md", "docs/evaluation.md",
    "docs/methodology.md", "docs/threat-model.md", "cases/README.md",
    "schemas/README.md", "tests/README.md",
]


def test_markdown_local_links_resolve():
    missing = []
    for name in DOCS:
        text = (ROOT / name).read_text(encoding="utf-8")
        for target in re.findall(r"\\[[^\\]]+\\]\\(([^)#]+)(?:#[^)]+)?\\)", text):
            if "://" in target or target.startswith("mailto:"):
                continue
            target_path = (ROOT / name).parent / target
            if not target_path.exists():
                missing.append(f"{name} -> {target}")
    assert not missing, "Broken local Markdown links: " + ", ".join(missing)


def test_normative_spec_has_required_sections():
    text = (ROOT / "docs/specification.md").read_text(encoding="utf-8")
    required = [
        "Scope", "Non-goals", "Normative language", "Canonical taxonomy",
        "Difficulty model", "Verdict semantics", "Claim model", "Evidence model",
        "Attack graph model", "Effective security graph", "Remediation model",
        "Regression model", "Reproducibility contract", "Benchmark security",
        "Contamination resistance", "Ground-truth isolation", "Submission contract",
        "Ten-phase roadmap", "Phase 1 exit criteria",
    ]
    missing = [heading for heading in required if f"## {heading}" not in text]
    assert not missing, f"Specification sections missing: {missing}"


def test_no_unfinished_placeholder_language_in_normative_spec():
    text = (ROOT / "docs/specification.md").read_text(encoding="utf-8").lower()
    forbidden = ("tbd", "todo", "fixme", "draft / research validation")
    assert not any(term in text for term in forbidden)
