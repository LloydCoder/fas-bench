"""Independent Phase 10.2 verification primitives."""

# ruff: noqa: E501

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

CERTIFICATION_POLICY = "FAS-BENCH-CERTIFICATION-V1"


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def digest_tree(root: Path) -> str:
    root = root.resolve()
    entries: list[tuple[str, bytes]] = []
    for path in root.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if any(part in {".git", "__pycache__", ".pytest_cache"} for part in Path(rel).parts):
            continue
        entries.append((rel, path.read_bytes()))
    digest = hashlib.sha256()
    for rel, data in sorted(entries):
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(data).digest())
        digest.update(b"\0")
    return digest.hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _component_digest(root: Path, name: str) -> str | None:
    path = root / name
    if path.is_dir():
        return digest_tree(path)
    if path.is_file():
        return _sha256_file(path)
    return None


def verify_manifest_independently(
    root: Path,
    manifest: dict[str, Any],
    *,
    expected_benchmark_version: str,
    expected_case_ids: tuple[str, ...],
    required_components: tuple[str, ...],
) -> dict[str, Any]:
    errors: list[str] = []
    if manifest.get("benchmark_version") != expected_benchmark_version:
        errors.append("benchmark version mismatch")
    if tuple(manifest.get("case_ids", ())) != expected_case_ids:
        errors.append("case population mismatch")
    for component in required_components:
        declared = manifest.get("component_digests", {}).get(component)
        actual = _component_digest(root, component)
        if actual is None:
            errors.append(f"missing component: {component}")
        elif declared != actual:
            errors.append(f"component digest mismatch: {component}")
    unsigned = {key: value for key, value in manifest.items() if key != "release_digest"}
    if manifest.get("release_digest") != sha256_json(unsigned):
        errors.append("release digest mismatch")
    if manifest.get("channel") == "official":
        errors.append("official channel requires externally controlled held-out corpus")
    if manifest.get("hidden_ground_truth") is True:
        errors.append("public verifier rejects self-declared hidden ground truth")
    return {"status": "PASS" if not errors else "FAIL", "errors": sorted(set(errors))}


def reference_line_range(text: str, start: int, end: int) -> str:
    if start < 1 or end < start:
        raise ValueError("invalid line range")
    lines = text.splitlines()
    if end > len(lines):
        raise ValueError("line range exceeds artifact")
    return "\n".join(lines[start - 1 : end])


def reference_path(root: Path, candidate: str) -> Path:
    if not isinstance(candidate, str) or not candidate or "\x00" in candidate:
        raise ValueError("invalid path")
    raw = Path(candidate)
    if raw.is_absolute():
        raise ValueError("absolute path rejected")
    resolved = (root / raw).resolve()
    base = root.resolve()
    if resolved != base and base not in resolved.parents:
        raise ValueError("path escapes root")
    return resolved


def reference_graph_identity(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> str:
    payload = {
        "nodes": sorted(nodes, key=lambda item: json.dumps(item, sort_keys=True)),
        "edges": sorted(edges, key=lambda item: json.dumps(item, sort_keys=True)),
    }
    return sha256_json(payload)


def reference_score(correct: int, total: int) -> float:
    if total < 0 or correct < 0 or correct > total:
        raise ValueError("invalid score inputs")
    return 0.0 if total == 0 else correct / total


def environment_report(root: Path) -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "os": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "benchmark_root": str(root.resolve()),
        "package_mode": "source",
    }


def independent_security_check(root: Path) -> dict[str, Any]:
    """Run security checks without importing the production phase-10 implementation."""
    findings: list[str] = []
    forbidden = {"fas", "threatfade", "tinlance"}
    surface = root / "src" / "fas_bench"
    for path in surface.rglob("*.py"):
        try:
            tree = __import__("ast").parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError) as exc:
            findings.append(f"parse failure: {path}: {exc}")
            continue
        for node in __import__("ast").walk(tree):
            if isinstance(node, __import__("ast").Import):
                names = [a.name for a in node.names]
            elif isinstance(node, __import__("ast").ImportFrom) and node.module:
                names = [node.module]
            else:
                names = []
            for name in names:
                if name.split(".", 1)[0].lower() in forbidden:
                    findings.append(f"forbidden dependency: {path}: {name}")
    for path in (root / "cases").rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        rel = path.relative_to(root / "cases").as_posix()
        if any(part.lower() in {".git", "hidden", "private", "secrets", "credentials", "oracle-private"} for part in Path(rel).parts):
            findings.append(f"forbidden release path: cases/{rel}")
        try:
            data = path.read_bytes()
        except OSError as exc:
            findings.append(f"unreadable case artifact: cases/{rel}: {exc}")
            continue
        if len(data) > 5_000_000:
            findings.append(f"oversized case artifact: cases/{rel}")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in (
            r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----",
            r"(?i)\\b(?:api[_-]?key|secret|token|password)s*\\s*[:=]\\s*['\\\"]?[A-Za-z0-9_./+=-]{12,}",
            r"\\bAKIA[0-9A-Z]{16}\\b",
            r"\\bgh[pousr]_[A-Za-z0-9_]{20,}\\b",
        ):
            import re
            if re.search(pattern, text):
                findings.append(f"secret pattern in cases/{rel}")
                break
    return {"status": "PASS" if not findings else "FAIL", "errors": sorted(set(findings)), "source": "independent"}

def independent_corpus_contract_check(root: Path) -> dict[str, Any]:
    """Validate corpus semantics directly from JSON artifacts, never via production validators."""
    errors: list[str] = []
    cases_root = root / "cases"
    registry_path = cases_root / "registry.json"
    if not registry_path.is_file():
        return {"status": "FAIL", "errors": ["missing cases/registry.json"], "source": "independent"}
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [f"invalid registry: {exc}"], "source": "independent"}
    ids = [x.get("case_id") for x in registry.get("cases", [])]
    if len(ids) != len(set(ids)) or not ids:
        errors.append("registry case ids must be unique and non-empty")
    for case_id in ids:
        case_dir = cases_root / str(case_id)
        try:
            case = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
            meta = json.loads((case_dir / "metadata.json").read_text(encoding="utf-8"))
            finding = json.loads((case_dir / "expected" / "findings.json").read_text(encoding="utf-8"))
            verdict = json.loads((case_dir / "expected" / "verdict.json").read_text(encoding="utf-8"))
            graph = json.loads((case_dir / "expected" / "attack_graph.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{case_id}: unreadable contract artifact: {exc}")
            continue
        if case.get("case_id") != case_id or meta.get("case_id") != case_id:
            errors.append(f"{case_id}: identity mismatch")
        if finding.get("finding_id") is None or not finding.get("evidence_ids"):
            errors.append(f"{case_id}: finding must bind to evidence")
        if finding.get("verdict") != verdict.get("verdict"):
            errors.append(f"{case_id}: finding/verdict mismatch")
        allowed = {"EXPLOITABLE","NOT_EXPLOITABLE","CONDITIONALLY_EXPLOITABLE","REMEDIATED","REMEDIATION_FAILED","REGRESSED","UNKNOWN"}
        if verdict.get("verdict") not in allowed:
            errors.append(f"{case_id}: unsupported verdict")
        path_ids = {p.get("path_id") for p in graph.get("paths", [])}
        attack_paths = case_dir / "expected" / "attack_paths.json"
        if attack_paths.is_file():
            try:
                ap = json.loads(attack_paths.read_text(encoding="utf-8"))
                if ap.get("path_id") not in path_ids:
                    errors.append(f"{case_id}: attack path not represented in graph")
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{case_id}: invalid attack_paths.json: {exc}")
        if not meta.get("provenance"):
            errors.append(f"{case_id}: missing provenance")
    return {"status": "PASS" if not errors else "FAIL", "errors": sorted(set(errors)), "source": "independent"}

def independent_scoring_contract_check(root: Path) -> dict[str, Any]:
    """Check scoring configuration without importing the scoring engine."""
    config = root / "src" / "fas_bench" / "scoring" / "config" / "v0.1.json"
    if not config.is_file():
        return {"status": "FAIL", "errors": ["missing scoring configuration"], "source": "independent"}
    try:
        value = json.loads(config.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [f"invalid scoring config: {exc}"], "source": "independent"}
    errors: list[str] = []
    weights = value.get("weights")
    if isinstance(weights, dict):
        numeric = [float(v) for v in weights.values()]
        if any(v < 0 for v in numeric):
            errors.append("negative scoring weight")
        if numeric and abs(sum(numeric) - 1.0) > 1e-9:
            errors.append("scoring weights must sum to 1")
    else:
        errors.append("missing scoring weights")
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "source": "independent"}

def independent_full_contract_check(root: Path) -> dict[str, Any]:
    checks = {
        "security": independent_security_check(root),
        "corpus": independent_corpus_contract_check(root),
        "scoring": independent_scoring_contract_check(root),
    }
    errors = [f"{name}: {error}" for name, result in checks.items() for error in result["errors"]]
    return {"status": "PASS" if not errors else "FAIL", "checks": checks, "errors": sorted(set(errors)), "source": "independent"}


def certify(results: dict[str, dict[str, Any]], identity: dict[str, Any]) -> dict[str, Any]:
    required = {
        "implementation",
        "independent_verification",
        "reproducibility",
        "security",
        "release",
    }
    missing = sorted(required - set(results))
    failed = sorted(
        key for key, value in results.items() if value.get("status") not in {"PASS", "GREEN"}
    )
    derived_only = all(
        isinstance(value, dict) and value.get("source") == "derived"
        for value in results.values()
    )
    if not derived_only:
        missing.append("derived-check-provenance")
    status = "CERTIFIED" if not missing and not failed else "NOT_CERTIFIED"
    return {
        "certification_policy": CERTIFICATION_POLICY,
        "status": status,
        "release_identity": identity,
        "checks": results,
        "missing_checks": missing,
        "failed_checks": failed,
    }


def run_clean_install_smoke(root: Path) -> dict[str, Any]:
    env = os.environ.copy()
    for key in list(env):
        if key.startswith("FAS_BENCH_") or key in {"PYTHONPATH", "PYTHONHOME"}:
            env.pop(key, None)
    process = subprocess.run(
        [sys.executable, "-c", "import fas_bench; print(fas_bench.__version__)"],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return {
        "status": "PASS" if process.returncode == 0 else "FAIL",
        "stdout": process.stdout.strip(),
        "stderr": process.stderr[-1000:],
    }
