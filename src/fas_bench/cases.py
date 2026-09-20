"""Phase 3 corpus validation, integrity, and isolated reproducibility helpers."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

from .contract import BENCHMARK_VERSION, CASE_IDS, GOLD_CASE_IDS, SCHEMA_VERSION
from .validation import validate, validate_file

ROOT = Path(__file__).resolve().parents[2]
CASES_ROOT = ROOT / "cases"
REGISTRY_PATH = CASES_ROOT / "registry.json"
MANIFEST_PATH = CASES_ROOT / "manifest.json"
DOCKER_IMAGE = (
    "python:3.12-slim@sha256:78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea"
)
EXPECTED_FILES = (
    ("claims.json", "claim"),
    ("evidence.json", "evidence"),
    ("findings.json", "finding"),
    ("verdict.json", "verdict"),
    ("remediation.json", "remediation"),
    ("attack_graph.json", "attack-graph"),
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical_bytes(path: Path, case_dir: Path) -> bytes:
    if path.name == "metadata.json":
        value = _load(path)
        value["artifact_digest"] = "CONTENT_DERIVED"
        return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    if path.name == "case.json":
        value = _load(path)
        repository = value.get("repository", {})
        if isinstance(repository, dict):
            digest = repository.get("artifact_digest")
            if isinstance(digest, dict):
                digest = dict(digest)
                digest["sha256"] = "CONTENT_DERIVED"
                repository["artifact_digest"] = digest
        return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    if path.suffix == ".json":
        return json.dumps(_load(path), sort_keys=True, separators=(",", ":")).encode()
    return path.read_bytes()


def _digest_paths(paths: list[Path], root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(_canonical_bytes(path, root))
        digest.update(b"\0")
    return digest.hexdigest()


def _digest_case(case_dir: Path) -> str:
    files = [
        path for path in case_dir.rglob("*") if path.is_file() and path.name != "manifest.json"
    ]
    return _digest_paths(files, case_dir)


def _digest_repository(case_dir: Path) -> str:
    repository = case_dir / "repository"
    files = [path for path in repository.rglob("*") if path.is_file()]
    return _digest_paths(files, case_dir)


def load_registry() -> dict[str, Any]:
    return _load(REGISTRY_PATH)


def validate_case_package(case_id: str) -> dict[str, Any]:
    case_dir = CASES_ROOT / case_id
    errors: list[str] = []
    if not case_dir.is_dir():
        return {
            "case_id": case_id,
            "status": "FAIL",
            "errors": ["missing case directory"],
        }
    case_path = case_dir / "case.json"
    metadata_path = case_dir / "metadata.json"
    if not case_path.is_file() or not metadata_path.is_file():
        missing = [
            name
            for name, present in (
                ("case.json", case_path.is_file()),
                ("metadata.json", metadata_path.is_file()),
            )
            if not present
        ]
        return {
            "case_id": case_id,
            "status": "FAIL",
            "errors": [f"missing {name}" for name in missing],
        }

    case = _load(case_path)
    metadata = _load(metadata_path)
    if case.get("case_id") != case_id or metadata.get("case_id") != case_id:
        errors.append("case_id does not match directory")
    if (
        case.get("benchmark_version") != BENCHMARK_VERSION
        or case.get("schema_version") != SCHEMA_VERSION
    ):
        errors.append("version mismatch")
    if metadata.get("case_version") != case.get("metadata", {}).get("case_version"):
        errors.append("case/metadata case_version mismatch")
    if metadata.get("lifecycle_status") != case.get("metadata", {}).get("lifecycle_status"):
        errors.append("case/metadata lifecycle mismatch")

    structural = validate(case, "case")
    if structural.status != "VALID":
        errors.extend(f"schema: {error.message}" for error in structural.errors)

    for name, family in EXPECTED_FILES:
        path = case_dir / "expected" / name
        if not path.is_file():
            errors.append(f"missing expected/{name}")
            continue
        result = validate_file(path, family)
        if result.status != "VALID":
            errors.extend(f"{name}: {error.message}" for error in result.errors)

    finding = (
        _load(case_dir / "expected" / "findings.json")
        if (case_dir / "expected" / "findings.json").is_file()
        else {}
    )
    verdict = (
        _load(case_dir / "expected" / "verdict.json")
        if (case_dir / "expected" / "verdict.json").is_file()
        else {}
    )
    if finding.get("verdict") != verdict.get("verdict"):
        errors.append("finding/verdict mismatch")

    graph = (
        _load(case_dir / "expected" / "attack_graph.json")
        if (case_dir / "expected" / "attack_graph.json").is_file()
        else {}
    )
    paths = (
        _load(case_dir / "expected" / "attack_paths.json")
        if (case_dir / "expected" / "attack_paths.json").is_file()
        else {}
    )
    graph_path_ids = {path.get("path_id") for path in graph.get("paths", [])}
    if paths.get("path_id") not in graph_path_ids:
        errors.append("attack_paths.json is not represented in attack_graph.json")

    digest = _digest_case(case_dir)
    repository_digest = _digest_repository(case_dir)
    recorded = metadata.get("artifact_digest")
    if recorded != digest:
        errors.append("metadata artifact_digest mismatch")
    repo_digest = case.get("repository", {}).get("artifact_digest", {}).get("sha256")
    if repo_digest != repository_digest:
        errors.append("case repository artifact digest mismatch")

    return {
        "case_id": case_id,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "verdict": verdict.get("verdict"),
        "validation_type": metadata.get("validation_type"),
        "gold": case_id in GOLD_CASE_IDS,
        "artifact_digest": digest,
        "repository_digest": repository_digest,
        "lifecycle_status": metadata.get("lifecycle_status"),
    }


def validate_all() -> dict[str, Any]:
    registry = load_registry()
    registry_ids = [item["case_id"] for item in registry.get("cases", [])]
    errors: list[str] = []
    if registry_ids != list(CASE_IDS):
        errors.append("registry does not contain exactly FAS-001..FAS-020 in order")

    actual_dirs = sorted(
        path.name for path in CASES_ROOT.iterdir() if path.is_dir() and path.name.startswith("FAS-")
    )
    if actual_dirs != sorted(CASE_IDS):
        errors.append("case directories do not exactly match the registry")

    manifest = _load(MANIFEST_PATH) if MANIFEST_PATH.is_file() else {}
    if manifest.get("case_ids") != registry_ids:
        errors.append("manifest case_ids do not match registry")

    results = [validate_case_package(case_id) for case_id in registry_ids]
    errors.extend(
        f"{result['case_id']}: {error}" for result in results for error in result["errors"]
    )
    manifest_by_id = {item.get("case_id"): item for item in manifest.get("cases", [])}
    registry_by_id = {item.get("case_id"): item for item in registry.get("cases", [])}
    for result in results:
        item = manifest_by_id.get(result["case_id"], {})
        reg = registry_by_id.get(result["case_id"], {})
        if item.get("artifact_digest") != result["artifact_digest"]:
            errors.append(f"{result['case_id']}: manifest artifact digest mismatch")
        for key in (
            "title",
            "primary_category",
            "difficulty",
            "case_version",
            "schema_version",
            "lifecycle_status",
        ):
            if item.get(key) != reg.get(key):
                errors.append(f"{result['case_id']}: manifest/registry {key} mismatch")

    return {
        "status": "PASS" if not errors else "FAIL",
        "case_count": len(results),
        "validated_count": sum(result["status"] == "PASS" for result in results),
        "errors": errors,
        "results": results,
    }


def _docker_command(case_dir: Path, mutation: dict[str, Any] | None) -> list[str]:
    command = [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges:true",
        "--pids-limit",
        "64",
        "--cpus",
        "1",
        "--memory",
        "256m",
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,size=16m",
        "-v",
        f"{case_dir.resolve()}:/case:ro",
        "-w",
        "/case",
    ]
    if mutation is not None:
        command.extend(
            [
                "-e",
                f"FAS_BENCH_MUTATION_JSON={json.dumps(mutation, sort_keys=True)}",
            ]
        )
    command.extend([DOCKER_IMAGE, "python", "oracle/oracle.py"])
    return command


def run_oracle(
    case_id: str, timeout: int = 30, mutation: dict[str, Any] | None = None
) -> dict[str, Any]:
    case_dir = CASES_ROOT / case_id
    oracle = case_dir / "oracle" / "oracle.py"
    if not oracle.is_file():
        return {"case_id": case_id, "status": "ERROR", "message": "oracle missing"}
    try:
        completed = subprocess.run(
            _docker_command(case_dir, mutation),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return {
            "case_id": case_id,
            "status": "ERROR",
            "message": "docker is required for isolated oracle execution",
        }
    except subprocess.TimeoutExpired:
        return {
            "case_id": case_id,
            "status": "INCONCLUSIVE",
            "message": "oracle timeout",
        }
    if completed.returncode != 0:
        return {
            "case_id": case_id,
            "status": "ERROR",
            "message": completed.stderr.strip() or "oracle container failed",
        }
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {
            "case_id": case_id,
            "status": "ERROR",
            "message": "oracle emitted non-JSON output",
            "stdout": completed.stdout,
        }
    expected = _load(case_dir / "expected" / "verdict.json")["verdict"]
    result["status"] = "PASS" if result.get("observed_verdict") == expected else "FAIL"
    if result["status"] == "FAIL":
        result["message"] = "oracle result disagrees with ground truth"
    result["case_id"] = case_id
    return result


def reproduce_all(case_ids: list[str] | None = None) -> dict[str, Any]:
    ids = case_ids or list(CASE_IDS)
    results = [run_oracle(case_id) for case_id in ids]
    return {
        "status": ("PASS" if all(result.get("status") == "PASS" for result in results) else "FAIL"),
        "results": results,
    }
