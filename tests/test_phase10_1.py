# fmt: off
import json
from pathlib import Path
import pytest

from fas_bench.canonical import canonical_json
from fas_bench.evidence.resolver import verify_location
from fas_bench.phase10 import build_release_manifest, digest_tree, validate_release_manifest
from fas_bench.secure_eval.models import ExecutionPolicy
from fas_bench.secure_eval.runner import SecureRunner

ROOT=Path(__file__).resolve().parents[1]

def test_canonical_json_rejects_non_finite_values():
    with pytest.raises(ValueError):
        canonical_json({"x": float("nan")})
    with pytest.raises(ValueError):
        canonical_json({"x": float("inf")})

def test_release_verifier_does_not_trust_validation_status():
    manifest=build_release_manifest(ROOT,"test",channel="release-candidate")
    manifest["validation_status"]="INVALID"
    assert validate_release_manifest(ROOT,manifest)["status"]=="PASS"

def test_release_verifier_detects_component_tampering():
    manifest=build_release_manifest(ROOT,"test",channel="release-candidate")
    manifest["component_digests"]["README.md"]="0"*64
    result=validate_release_manifest(ROOT,manifest)
    assert result["status"]=="FAIL"
    assert "component digest mismatch: README.md" in result["errors"]

def test_official_channel_requires_external_held_out_corpus():
    manifest=build_release_manifest(ROOT,"test",channel="release-candidate")
    manifest["channel"]="official"
    manifest["release_digest"]=__import__("hashlib").sha256(
        canonical_json({k:v for k,v in manifest.items() if k!="release_digest"})
    ).hexdigest()
    result=validate_release_manifest(ROOT,manifest)
    assert result["status"]=="FAIL"
    assert any("held-out corpus" in e for e in result["errors"])

def test_exact_symbol_range_and_snippet_binding(tmp_path):
    case=tmp_path
    src=case/"sample.py"
    src.write_text("def outside():\n    return 1\n\ndef target():\n    return 2\n",encoding="utf-8")
    status,reason=verify_location(case,{"file":"sample.py","line_start":1,"line_end":2,"symbol":"target"})
    assert (status,reason)==("INVALID","EVIDENCE_INVALID_SYMBOL")
    status,reason=verify_location(case,{"file":"sample.py","line_start":4,"line_end":5,"symbol":"target","snippet":"def target():\n    return 2"})
    assert status=="VERIFIED"
    status,reason=verify_location(case,{"file":"sample.py","line_start":4,"line_end":5,"symbol":"target","snippet":"def outside():\n    return 1"})
    assert (status,reason)==("INVALID","EVIDENCE_SNIPPET_MISMATCH")

def test_digest_tree_excludes_symlinks(tmp_path):
    root=tmp_path
    (root/"a.txt").write_bytes(b"a")
    (root/"link").symlink_to(root/"a.txt")
    assert digest_tree(root)==digest_tree(root/".."/root.name)

def test_environment_authority_is_not_overridable():
    policy=ExecutionPolicy("python:3.12-slim@sha256:"+"a"*64)
    runner=SecureRunner(policy,docker_binary="not-a-real-docker")
    assert not runner._validate_environment({"fas_bench_run_id":"x"})
    assert not runner._validate_environment({"FAS_BENCH_CASE_ID":"x"})
    assert not runner._validate_environment({"OpenAI_API_KEY":"x"})
    assert not runner._validate_environment({"github_token":"x"})
    assert runner._validate_environment({"SAFE_VALUE":"x"})
