# fmt: off
# ruff: noqa: E501
from fas_bench.phase10 import build_release_manifest
from fas_bench.verification import verify_manifest_independently
from fas_bench.contract import BENCHMARK_VERSION, CASE_IDS
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
COMPONENTS=("pyproject.toml","src/fas_bench","schemas","cases","docs","README.md","SECURITY.md")

def test_manifest_reordering_does_not_change_identity():
    a=build_release_manifest(ROOT,"metamorphic",channel="release-candidate")
    b=dict(reversed(list(a.items())))
    assert verify_manifest_independently(ROOT,b,expected_benchmark_version=BENCHMARK_VERSION,expected_case_ids=tuple(CASE_IDS),required_components=COMPONENTS)["status"]=="PASS"
