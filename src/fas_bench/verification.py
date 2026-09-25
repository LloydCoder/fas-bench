# ruff: noqa: E501
"""Independent Phase 10.2 verification primitives."""
from __future__ import annotations
import hashlib, json, os, platform, subprocess, sys
from pathlib import Path
from typing import Any

CERTIFICATION_POLICY = "FAS-BENCH-CERTIFICATION-V1"

def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")

def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()

def digest_tree(root: Path) -> str:
    root = root.resolve()
    entries = []
    for path in root.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in Path(rel).parts):
            continue
        entries.append((rel, path.read_bytes()))
    h = hashlib.sha256()
    for rel, data in sorted(entries):
        h.update(rel.encode("utf-8")); h.update(b"\0")
        h.update(hashlib.sha256(data).digest()); h.update(b"\0")
    return h.hexdigest()

def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _component_digest(root: Path, name: str) -> str | None:
    path = root / name
    if path.is_dir(): return digest_tree(path)
    if path.is_file(): return _sha256_file(path)
    return None

def verify_manifest_independently(root: Path, manifest: dict[str, Any], *,
    expected_benchmark_version: str, expected_case_ids: tuple[str, ...],
    required_components: tuple[str, ...]) -> dict[str, Any]:
    errors = []
    if manifest.get("benchmark_version") != expected_benchmark_version:
        errors.append("benchmark version mismatch")
    if tuple(manifest.get("case_ids", ())) != expected_case_ids:
        errors.append("case population mismatch")
    for component in required_components:
        declared = manifest.get("component_digests", {}).get(component)
        actual = _component_digest(root, component)
        if actual is None: errors.append(f"missing component: {component}")
        elif declared != actual: errors.append(f"component digest mismatch: {component}")
    unsigned = {k: v for k, v in manifest.items() if k != "release_digest"}
    if manifest.get("release_digest") != sha256_json(unsigned):
        errors.append("release digest mismatch")
    if manifest.get("channel") == "official":
        errors.append("official channel requires externally controlled held-out corpus")
    if manifest.get("hidden_ground_truth") is True:
        errors.append("public verifier rejects self-declared hidden ground truth")
    return {"status": "PASS" if not errors else "FAIL", "errors": sorted(set(errors))}

def reference_line_range(text: str, start: int, end: int) -> str:
    if start < 1 or end < start: raise ValueError("invalid line range")
    lines = text.splitlines()
    if end > len(lines): raise ValueError("line range exceeds artifact")
    return "\n".join(lines[start - 1:end])

def reference_path(root: Path, candidate: str) -> Path:
    if not isinstance(candidate, str) or not candidate or "\x00" in candidate:
        raise ValueError("invalid path")
    raw = Path(candidate)
    if raw.is_absolute(): raise ValueError("absolute path rejected")
    resolved, base = (root / raw).resolve(), root.resolve()
    if resolved != base and base not in resolved.parents: raise ValueError("path escapes root")
    return resolved

def reference_graph_identity(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> str:
    payload = {"nodes": sorted(nodes, key=lambda x: json.dumps(x, sort_keys=True)),
               "edges": sorted(edges, key=lambda x: json.dumps(x, sort_keys=True))}
    return sha256_json(payload)

def reference_score(correct: int, total: int) -> float:
    if total < 0 or correct < 0 or correct > total: raise ValueError("invalid score inputs")
    return 0.0 if total == 0 else correct / total

def environment_report(root: Path) -> dict[str, Any]:
    return {"python": platform.python_version(), "implementation": platform.python_implementation(),
            "os": platform.system(), "release": platform.release(), "machine": platform.machine(),
            "benchmark_root": str(root.resolve()), "package_mode": "source"}

def certify(results: dict[str, dict[str, Any]], identity: dict[str, Any]) -> dict[str, Any]:
    required = {"implementation","independent_verification","reproducibility","security","release"}
    missing = sorted(required - set(results))
    failed = sorted(k for k,v in results.items() if v.get("status") not in {"PASS","GREEN"})
    status = "CERTIFIED" if not missing and not failed else "NOT_CERTIFIED"
    return {"certification_policy": CERTIFICATION_POLICY, "status": status,
            "release_identity": identity, "checks": results,
            "missing_checks": missing, "failed_checks": failed}

def run_clean_install_smoke(root: Path) -> dict[str, Any]:
    env = os.environ.copy()
    for key in list(env):
        if key.startswith("FAS_BENCH_") or key in {"PYTHONPATH","PYTHONHOME"}: env.pop(key, None)
    proc = subprocess.run([sys.executable,"-c","import fas_bench; print(fas_bench.__version__)"],
        cwd=root, env=env, capture_output=True, text=True, timeout=30, check=False)
    return {"status":"PASS" if proc.returncode == 0 else "FAIL",
            "stdout":proc.stdout.strip(), "stderr":proc.stderr[-1000:]}
