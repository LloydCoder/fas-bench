# fmt: off
# ruff: noqa: E501
import hashlib, json
from pathlib import Path
from fas_bench.contract import BENCHMARK_VERSION, CASE_IDS
from fas_bench.phase10 import build_release_manifest
from fas_bench.verification import verify_manifest_independently
ROOT=Path(__file__).resolve().parents[2]
COMPONENTS=("pyproject.toml","src/fas_bench","schemas","cases","docs","README.md","SECURITY.md")

def verify(m):
    return verify_manifest_independently(ROOT,m,expected_benchmark_version=BENCHMARK_VERSION,expected_case_ids=tuple(CASE_IDS),required_components=COMPONENTS)

def test_independent_manifest_verifier():
    assert verify(build_release_manifest(ROOT,"verification-test",channel="release-candidate"))["status"]=="PASS"

def test_tampering_is_detected():
    m=build_release_manifest(ROOT,"verification-test",channel="release-candidate")
    m["component_digests"]["README.md"]="0"*64
    u={k:v for k,v in m.items() if k!="release_digest"}
    m["release_digest"]=hashlib.sha256((json.dumps(u,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()).hexdigest()
    r=verify(m)
    assert r["status"]=="FAIL" and "component digest mismatch: README.md" in r["errors"]

def test_validation_status_is_not_authority():
    m=build_release_manifest(ROOT,"verification-test",channel="release-candidate")
    m["validation_status"]="INVALID"
    u={k:v for k,v in m.items() if k!="release_digest"}
    m["release_digest"]=hashlib.sha256((json.dumps(u,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()).hexdigest()
    assert verify(m)["status"]=="PASS"
