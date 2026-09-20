# fmt: off
"""Phase 10 corpus integrity, contamination, mutation/release primitives, and governance."""

from __future__ import annotations

import ast
import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Iterable

from .cases import CASES_ROOT, validate_all, validate_case_package
from .contract import BENCHMARK_VERSION, CASE_IDS, SCHEMA_VERSION

PHASE10_VERSION = "0.1.0"
LIFECYCLE = (
    "DRAFT", "AUTHOR_VALIDATION", "PEER_REVIEW", "ORACLE_VALIDATED",
    "SECURITY_VALIDATED", "REPRODUCIBILITY_VALIDATED", "RELEASE_CANDIDATE",
    "RELEASED", "MAINTAINED", "DEPRECATED", "RETIRED",
)
TRANSITIONS = {
    "DRAFT": {"AUTHOR_VALIDATION"},
    "AUTHOR_VALIDATION": {"PEER_REVIEW"},
    "PEER_REVIEW": {"ORACLE_VALIDATED"},
    "ORACLE_VALIDATED": {"SECURITY_VALIDATED"},
    "SECURITY_VALIDATED": {"REPRODUCIBILITY_VALIDATED"},
    "REPRODUCIBILITY_VALIDATED": {"RELEASE_CANDIDATE"},
    "RELEASE_CANDIDATE": {"RELEASED"},
    "RELEASED": {"MAINTAINED", "DEPRECATED"},
    "MAINTAINED": {"DEPRECATED"},
    "DEPRECATED": {"RETIRED"},
    "RETIRED": set(),
}
CONTAMINATION = ("KNOWN", "SUSPECTED", "UNKNOWN", "NOT_ASSESSED")
ELIGIBILITY = (
    "ELIGIBLE", "INCOMPLETE", "INVALID", "POLICY_VIOLATION",
    "NON_REPRODUCIBLE", "INTEGRITY_FAILURE", "INFRASTRUCTURE_FAILURE",
)

FORBIDDEN_NAMES = (
    ".env", ".env.local", ".git", "hidden", "private", "secrets", "credentials",
    "expected-hidden", "oracle-private",
)
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)(?:api[_-]?key|secret|token|password)s*[:=]s*[A-Za-z0-9_./+=-]{20,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
)

@dataclass(frozen=True)
class LifecycleError(ValueError):
    message: str
    def __str__(self) -> str:
        return self.message

@dataclass(frozen=True)
class CaseLifecycle:
    case_id: str
    state: str
    def transition(self, target: str) -> "CaseLifecycle":
        if target not in LIFECYCLE:
            raise LifecycleError(f"unknown lifecycle state: {target}")
        if target not in TRANSITIONS.get(self.state, set()):
            raise LifecycleError(f"invalid lifecycle transition: {self.state} -> {target}")
        return CaseLifecycle(self.case_id, target)

def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value))

def digest_tree(root: Path, *, exclude: Iterable[str] = ()) -> str:
    root = root.resolve()
    excluded = set(exclude)
    entries = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel in excluded or any(part in excluded for part in Path(rel).parts):
            continue
        entries.append((rel, path.read_bytes()))
    h = hashlib.sha256()
    for rel, data in sorted(entries):
        h.update(rel.encode())
        h.update(b"\0")
        h.update(hashlib.sha256(data).digest())
        h.update(b"\0")
    return h.hexdigest()

def case_record(case_id: str) -> dict[str, Any]:
    case_dir = CASES_ROOT / case_id
    case = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
    metadata = json.loads((case_dir / "metadata.json").read_text(encoding="utf-8"))
    expected = json.loads((case_dir / "expected" / "verdict.json").read_text(encoding="utf-8"))
    legacy = metadata.get("lifecycle_status", "VALIDATED")
    # VALIDATED is the Phase 1-9 compatibility state; Phase 10 never treats it as RELEASED.
    phase10_state = metadata.get("phase10_lifecycle", "ORACLE_VALIDATED" if legacy == "VALIDATED" else legacy)
    return {
        "case_id": case_id,
        "title": case["title"],
        "case_version": metadata.get("case_version"),
        "schema_version": case.get("schema_version"),
        "benchmark_version": case.get("benchmark_version"),
        "category": case.get("category"),
        "categories": case.get("categories", []),
        "difficulty": case.get("difficulty"),
        "verdict": expected.get("verdict"),
        "legacy_lifecycle": legacy,
        "phase10_lifecycle": phase10_state,
        "provenance": metadata.get("provenance", "SYNTHETIC"),
        "contamination_status": metadata.get("contamination_status", "NOT_ASSESSED"),
        "case_digest": digest_tree(case_dir),
        "repository_digest": digest_tree(case_dir / "repository"),
    }

def validate_case_phase10(case_id: str) -> dict[str, Any]:
    base = validate_case_package(case_id)
    errors = list(base.get("errors", []))
    record = case_record(case_id) if (CASES_ROOT / case_id).is_dir() else {"case_id": case_id}
    if record.get("phase10_lifecycle") not in LIFECYCLE:
        errors.append("invalid phase10_lifecycle")
    if record.get("contamination_status") not in CONTAMINATION:
        errors.append("invalid contamination_status")
    if not record.get("provenance"):
        errors.append("missing provenance")
    if record.get("case_id") not in CASE_IDS:
        errors.append("case is outside canonical initial corpus")
    return {**record, "status": "PASS" if not errors and base.get("status") == "PASS" else "FAIL", "errors": errors}

def validate_corpus() -> dict[str, Any]:
    base = validate_all()
    results = [validate_case_phase10(case_id) for case_id in CASE_IDS]
    errors = list(base.get("errors", []))
    errors.extend(f"{r['case_id']}: {e}" for r in results for e in r["errors"])
    return {
        "status": "PASS" if not errors else "FAIL",
        "benchmark_version": BENCHMARK_VERSION,
        "schema_version": SCHEMA_VERSION,
        "phase10_version": PHASE10_VERSION,
        "case_count": len(results),
        "valid_count": sum(r["status"] == "PASS" for r in results),
        "errors": sorted(set(errors)),
        "cases": results,
    }

def corpus_stats() -> dict[str, Any]:
    records = [case_record(case_id) for case_id in CASE_IDS]
    def count(key: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for record in records:
            value = record.get(key)
            out[value] = out.get(value, 0) + 1
        return dict(sorted(out.items()))
    return {
        "case_count": len(records),
        "categories": count("category"),
        "difficulty": count("difficulty"),
        "verdict": count("verdict"),
        "lifecycle": count("phase10_lifecycle"),
        "contamination": count("contamination_status"),
        "gold_cases": ["FAS-001", "FAS-002", "FAS-006", "FAS-016", "FAS-020"],
        "public_development": True,
        "statistical_representativeness_claim": False,
    }

def scan_leakage(root: Path) -> dict[str, Any]:
    root = root.resolve()
    findings: list[dict[str, str]] = []
    for path in root.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        parts = set(Path(rel).parts)
        if parts & set(FORBIDDEN_NAMES):
            findings.append({"type": "FORBIDDEN_PATH", "path": rel})
            continue
        if path.stat().st_size > 5_000_000:
            findings.append({"type": "OVERSIZED_RELEASE_FILE", "path": rel})
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append({"type": "SECRET_PATTERN", "path": rel})
                break
    return {"status": "PASS" if not findings else "FAIL", "findings": findings}

def independence_audit(root: Path) -> dict[str, Any]:
    findings = []
    forbidden_roots = {"fas", "threatfade", "tinlance"}
    for path in (root / "src" / "fas_bench").rglob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            findings.append({"path": path.relative_to(root).as_posix(), "match": f"syntax:{exc.msg}"})
            continue
        for node in ast.walk(tree):
            module = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name
                    if module.split(".", 1)[0].lower() in forbidden_roots:
                        findings.append({"path": path.relative_to(root).as_posix(), "match": module})
            elif isinstance(node, ast.ImportFrom) and node.module:
                module = node.module
                if module.split(".", 1)[0].lower() in forbidden_roots:
                    findings.append({"path": path.relative_to(root).as_posix(), "match": module})
    return {"status": "PASS" if not findings else "FAIL", "findings": findings}

def build_release_manifest(root: Path, version: str, *, channel: str = "development") -> dict[str, Any]:
    if channel not in {"development", "release-candidate", "public", "official"}:
        raise ValueError(f"unsupported release channel: {channel}")
    corpus = validate_corpus()
    if corpus["status"] != "PASS":
        raise ValueError("cannot build release manifest from invalid corpus")
    records = [case_record(case_id) for case_id in CASE_IDS]
    files = ["pyproject.toml", "src/fas_bench", "schemas", "cases", "docs", "README.md", "SECURITY.md"]
    component_digests = {}
    for item in files:
        path = root / item
        if path.is_dir():
            component_digests[item] = digest_tree(path)
        elif path.is_file():
            component_digests[item] = sha256_bytes(path.read_bytes())
    manifest = {
        "manifest_version": "0.1",
        "release_version": version,
        "benchmark_version": BENCHMARK_VERSION,
        "schema_versions": {"core": SCHEMA_VERSION, "phase10": PHASE10_VERSION},
        "channel": channel,
        "case_ids": [r["case_id"] for r in records],
        "case_versions": {r["case_id"]: r["case_version"] for r in records},
        "case_digests": {r["case_id"]: r["case_digest"] for r in records},
        "fixture_digests": {r["case_id"]: r["repository_digest"] for r in records},
        "oracle_digests": {
            r["case_id"]: digest_tree(CASES_ROOT / r["case_id"] / "oracle")
            for r in records
        },
        "component_digests": component_digests,
        "mutation_version": PHASE10_VERSION,
        "provenance": {"source": "repository", "public_surface": "development"},
        "validation_status": "VALIDATED",
        "hidden_ground_truth": channel in {"official"},
    }
    manifest["release_digest"] = sha256_json({k: v for k, v in manifest.items() if k != "release_digest"})
    return manifest

def validate_release_manifest(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    errors = []
    if manifest.get("benchmark_version") != BENCHMARK_VERSION:
        errors.append("benchmark version mismatch")
    if manifest.get("case_ids") != list(CASE_IDS):
        errors.append("release population differs from initial corpus")
    for case_id in manifest.get("case_ids", []):
        expected = validate_case_phase10(case_id)
        if expected["status"] != "PASS":
            errors.append(f"{case_id}: invalid case")
        if manifest.get("case_digests", {}).get(case_id) != expected.get("case_digest"):
            errors.append(f"{case_id}: case digest mismatch")
    leak = scan_leakage(root)
    if leak["status"] != "PASS":
        errors.append("release leakage scan failed")
    if manifest.get("validation_status") != "VALIDATED":
        errors.append("release manifest is not validated")
    expected_digest = sha256_json({k: v for k, v in manifest.items() if k != "release_digest"})
    if manifest.get("release_digest") != expected_digest:
        errors.append("release digest mismatch")
    return {"status": "PASS" if not errors else "FAIL", "errors": sorted(set(errors))}

def eligibility(
    *,
    integrity_ok: bool,
    infrastructure_ok: bool,
    reproducible: bool,
    policy_violation: bool = False,
    complete: bool = True,
) -> str:
    if policy_violation:
        return "POLICY_VIOLATION"
    if not integrity_ok:
        return "INTEGRITY_FAILURE"
    if not infrastructure_ok:
        return "INFRASTRUCTURE_FAILURE"
    if not reproducible:
        return "NON_REPRODUCIBLE"
    if not complete:
        return "INCOMPLETE"
    return "ELIGIBLE"

def benchmark_health(root: Path) -> dict[str, Any]:
    corpus = validate_corpus()
    leakage = scan_leakage(root / "cases")
    independence = independence_audit(root)
    stats = corpus_stats()
    return {
        "corpus_validity": corpus["status"],
        "oracle_validity": "NOT_ASSESSED",
        "mutation_validity": "NOT_ASSESSED",
        "release_integrity": "NOT_ASSESSED",
        "reproducibility": "NOT_ASSESSED",
        "contamination": "NOT_ASSESSED",
        "leakage_scan": leakage["status"],
        "independence": independence["status"],
        "coverage": stats,
        "statistical_representativeness_claim": False,
    }

def public_report(manifest: dict[str, Any], stats: dict[str, Any], health: dict[str, Any]) -> dict[str, Any]:
    return {
        "release_identity": {
            "release_version": manifest["release_version"],
            "release_digest": manifest["release_digest"],
            "benchmark_version": manifest["benchmark_version"],
        },
        "population": len(manifest["case_ids"]),
        "coverage": stats,
        "validation_status": manifest["validation_status"],
        "health": health,
        "known_limitations": [
            "The initial 20-case corpus is public development data.",
            "No claim of statistical representativeness is made.",
            "Hidden/official evaluation requires a separately controlled corpus.",
        ],
        "hidden_case_details": False,
    }
