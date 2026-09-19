"""Phase 3 corpus validation and reproducibility helpers."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from .contract import BENCHMARK_VERSION, CASE_IDS, GOLD_CASE_IDS, SCHEMA_VERSION
from .validation import validate, validate_file

ROOT = Path(__file__).resolve().parents[2]
CASES_ROOT = ROOT / "cases"
REGISTRY_PATH = CASES_ROOT / "registry.json"
MANIFEST_PATH = CASES_ROOT / "manifest.json"

EXPECTED_FILES = (
    ("claims.json", "claim"),
    ("evidence.json", "evidence"),
    ("verdict.json", "verdict"),
    ("remediation.json", "remediation"),
    ("attack_graph.json", "attack-graph"),
)

STATUS_ORDER = {"DRAFT": 0, "IN_REVIEW": 1, "VALIDATED": 2, "RELEASED": 3}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _digest_case(case_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in case_dir.rglob("*") if p.is_file() and p.name != "manifest.json"):
        digest.update(path.relative_to(case_dir).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def load_registry() -> dict[str, Any]:
    return _load(REGISTRY_PATH)


def validate_case_package(case_id: str) -> dict[str, Any]:
    case_dir = CASES_ROOT / case_id
    if not case_dir.is_dir():
        return {"case_id": case_id, "status": "FAIL", "errors": ["missing case directory"]}

    errors: list[str] = []
    case_path = case_dir / "case.json"
    if not case_path.is_file():
        return {"case_id": case_id, "status": "FAIL", "errors": ["missing case.json"]}

    case = _load(case_path)
    metadata_path = case_dir / "metadata.json"
    metadata = _load(metadata_path) if metadata_path.is_file() else case.get("metadata", {})
    if case.get("case_id") != case_id or metadata.get("case_id") != case_id:
        errors.append("case_id does not match directory")
    if case.get("benchmark_version") != BENCHMARK_VERSION or case.get("schema_version") != SCHEMA_VERSION:
        errors.append("version mismatch")

    structural = validate(case, "case")
    if structural.status != "VALID":
        errors.extend(f"schema: {e.message}" for e in structural.errors)

    for name, family in EXPECTED_FILES:
        path = case_dir / "expected" / name
        if not path.is_file():
            errors.append(f"missing expected/{name}")
            continue
        result = validate_file(path, family)
        if result.status != "VALID":
            errors.extend(f"{name}: {e.message}" for e in result.errors)

    findings = case_dir / "expected" / "findings.json"
    if not findings.is_file():
        errors.append("missing expected/findings.json")
    else:
        finding = _load(findings)
        required = {"finding_id", "title", "category", "severity", "description", "claim_ids", "evidence_ids", "verdict", "confidence"}
        if not required <= finding.keys():
            errors.append("finding schema contract incomplete")

    paths = _load(case_dir / "expected" / "attack_paths.json") if (case_dir / "expected" / "attack_paths.json").is_file() else {}
    graph_path = case_dir / "expected" / "attack_graph.json"
    graph = _load(graph_path) if graph_path.is_file() else {}
    if not graph_path.is_file():
        errors.append("missing expected/attack_graph.json")
    elif paths.get("path_id") and not any(p.get("path_id") == paths["path_id"] for p in graph.get("paths", [])):
        errors.append("attack_paths.json is not represented in attack_graph.json")

    expected_verdict = _load(case_dir / "expected" / "verdict.json").get("verdict")
    if expected_verdict != finding.get("verdict"):
        errors.append("finding/verdict mismatch")

    digest = _digest_case(case_dir)
    recorded = metadata.get("artifact_digest")
    if recorded and recorded != "PLACEHOLDER" and recorded != digest:
        errors.append("metadata artifact_digest mismatch")

    return {
        "case_id": case_id,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "verdict": expected_verdict,
        "validation_type": metadata.get("validation_type"),
        "gold": case_id in GOLD_CASE_IDS,
        "artifact_digest": digest,
    }


def validate_all() -> dict[str, Any]:
    registry = load_registry()
    registry_ids = [item["case_id"] for item in registry["cases"]]
    errors: list[str] = []
    if registry_ids != list(CASE_IDS):
        errors.append("registry does not contain exactly FAS-001..FAS-020 in order")

    results = [validate_case_package(case_id) for case_id in registry_ids]
    errors.extend(f"{r['case_id']}: {e}" for r in results for e in r["errors"])

    manifest = _load(MANIFEST_PATH) if MANIFEST_PATH.is_file() else {}
    if manifest.get("case_ids") != registry_ids:
        errors.append("manifest case_ids do not match registry")

    return {
        "status": "PASS" if not errors else "FAIL",
        "case_count": len(results),
        "validated_count": sum(r["status"] == "PASS" for r in results),
        "errors": errors,
        "results": results,
    }


def run_oracle(case_id: str, timeout: int = 30, mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    case_dir = CASES_ROOT / case_id
    oracle = case_dir / "oracle" / "oracle.py"
    if not oracle.is_file():
        return {"case_id": case_id, "status": "ERROR", "message": "oracle missing"}

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    if mutation is not None:
        env["FAS_BENCH_MUTATION_JSON"] = json.dumps(mutation, sort_keys=True)
    try:
        completed = subprocess.run(
            [sys.executable, str(oracle)],
            cwd=case_dir,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"case_id": case_id, "status": "INCONCLUSIVE", "message": "oracle timeout"}

    if completed.returncode != 0:
        return {"case_id": case_id, "status": "ERROR", "message": completed.stderr.strip()}

    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"case_id": case_id, "status": "ERROR", "message": "oracle emitted non-JSON output"}

    expected = _load(case_dir / "expected" / "verdict.json")["verdict"]
    if result.get("observed_verdict") != expected:
        result["status"] = "FAIL"
        result["message"] = "oracle result disagrees with ground truth"
    else:
        result["status"] = "PASS"
    result["case_id"] = case_id
    return result


def reproduce_all(case_ids: list[str] | None = None) -> dict[str, Any]:
    ids = case_ids or list(CASE_IDS)
    results = [run_oracle(case_id) for case_id in ids]
    return {
        "status": "PASS" if all(r.get("status") == "PASS" for r in results) else "FAIL",
        "results": results,
    }
