from pathlib import Path

from fas_bench.contract import BENCHMARK_VERSION, CASE_IDS
from fas_bench.phase10 import build_release_manifest
from fas_bench.verification import verify_manifest_independently

ROOT = Path(__file__).resolve().parents[2]
COMPONENTS = (
    "pyproject.toml",
    "src/fas_bench",
    "schemas",
    "cases",
    "docs",
    "README.md",
    "SECURITY.md",
)


def test_manifest_reordering_does_not_change_identity():
    manifest = build_release_manifest(ROOT, "metamorphic", channel="release-candidate")
    reordered = dict(reversed(list(manifest.items())))
    result = verify_manifest_independently(
        ROOT,
        reordered,
        expected_benchmark_version=BENCHMARK_VERSION,
        expected_case_ids=tuple(CASE_IDS),
        required_components=COMPONENTS,
    )
    assert result["status"] == "PASS"
