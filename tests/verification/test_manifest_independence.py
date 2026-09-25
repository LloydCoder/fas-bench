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


def verify(manifest):
    return verify_manifest_independently(
        ROOT,
        manifest,
        expected_benchmark_version=BENCHMARK_VERSION,
        expected_case_ids=tuple(CASE_IDS),
        required_components=COMPONENTS,
    )


def test_independent_manifest_verifier():
    manifest = build_release_manifest(ROOT, "verification-test", channel="release-candidate")
    assert verify(manifest)["status"] == "PASS"


def test_tampering_is_detected():
    manifest = build_release_manifest(ROOT, "verification-test", channel="release-candidate")
    manifest["component_digests"]["README.md"] = "0" * 64
    unsigned = {key: value for key, value in manifest.items() if key != "release_digest"}
    manifest["release_digest"] = hashlib.sha256(
        (
            json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            + "\n"
        ).encode()
    ).hexdigest()
    result = verify(manifest)
    assert result["status"] == "FAIL"
    assert "component digest mismatch: README.md" in result["errors"]


def test_validation_status_is_not_authority():
    manifest = build_release_manifest(ROOT, "verification-test", channel="release-candidate")
    manifest["validation_status"] = "INVALID"
    unsigned = {key: value for key, value in manifest.items() if key != "release_digest"}
    manifest["release_digest"] = hashlib.sha256(
        (
            json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
            + "\n"
        ).encode()
    ).hexdigest()
    assert verify(manifest)["status"] == "PASS"
