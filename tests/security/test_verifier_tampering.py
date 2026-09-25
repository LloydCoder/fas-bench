import hashlib
import json
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


def test_source_tamper_is_detected_by_digest():
    manifest = build_release_manifest(ROOT, "security-test", channel="release-candidate")
    altered = dict(manifest)
    altered["component_digests"] = dict(manifest["component_digests"])
    altered["component_digests"]["README.md"] = "0" * 64
    unsigned = {key: value for key, value in altered.items() if key != "release_digest"}
    altered["release_digest"] = hashlib.sha256(
        (
            json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            + "\n"
        ).encode()
    ).hexdigest()
    result = verify_manifest_independently(
        ROOT,
        altered,
        expected_benchmark_version=BENCHMARK_VERSION,
        expected_case_ids=tuple(CASE_IDS),
        required_components=COMPONENTS,
    )
    assert result["status"] == "FAIL"
