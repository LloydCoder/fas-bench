"""Deterministic evidence verification engine."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ..cases import _digest_case, validate_case_package
from ..contract import BENCHMARK_VERSION, EVALUATOR_VERSION, SCHEMA_VERSION
from ..validation import validate
from .errors import CaseIntegrityError, CaseLoadError, SubmissionError
from .models import EvidenceItemResult, EvidenceVerificationResult
from .normalization import canonical_evidence, evidence_identity, normalize_evidence
from .resolver import read_fact, resolve_artifact_path, safe_resolve, verify_location
from .coverage import calculate_coverage
from .integrity import calculate_integrity

def _cases_root(cases_root: Path | None) -> Path:
    if cases_root is not None:
        return cases_root.resolve()
    for candidate in (Path.cwd(), *Path.cwd().parents, Path(__file__).resolve().parents[3]):
        if (candidate / "cases").is_dir():
            return (candidate / "cases").resolve()
    raise CaseLoadError("cases root not found")

def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CaseLoadError(f"cannot load JSON: {path}") from exc
    if not isinstance(value, dict):
        raise CaseLoadError(f"expected object: {path}")
    return value

def load_case(case_id: str, cases_root: Path | None = None) -> dict[str, Any]:
    root = _cases_root(cases_root)
    case_root = safe_resolve(root, case_id)
    result = validate_case_package(case_id)
    if result["status"] != "PASS":
        raise CaseIntegrityError(f"case integrity failed for {case_id}: {result['errors']}")
    case = _load_json(case_root / "case.json")
    expected = _load_json(case_root / "expected/evidence.json")
    if case.get("benchmark_version") != BENCHMARK_VERSION or case.get("schema_version") != SCHEMA_VERSION:
        raise CaseIntegrityError("case version is incompatible")
    if not expected.get("evidence_id"):
        raise CaseIntegrityError("expected evidence is malformed")
    return {"case_id": case_id, "root": case_root, "case": case, "expected_evidence": [expected]}

def load_submission(path: Path) -> dict[str, Any]:
    try:
        document = _load_json(path)
    except CaseLoadError as exc:
        raise SubmissionError(str(exc)) from exc
    result = validate(document, "submission", True)
    if result.status != "VALID":
        raise SubmissionError(f"submission validation failed: {[e.message for e in result.errors]}")
    return document

def _fact_matches(case_root: Path, evidence: dict[str, Any], expected: dict[str, Any]) -> tuple[bool, str]:
    fact = evidence.get("fact")
    expected_fact = expected.get("fact")
    if not isinstance(fact, dict) or not isinstance(expected_fact, dict):
        return False, "EVIDENCE_UNRESOLVED"
    if fact.get("artifact_path") != expected_fact.get("artifact_path") or fact.get("key") != expected_fact.get("key"):
        return False, "EVIDENCE_VALUE_MISMATCH"
    found, actual, detail = read_fact(case_root, evidence)
    if not found:
        return False, "EVIDENCE_UNRESOLVED"
    if expected_fact.get("operator", "EQUALS") != "EQUALS":
        return False, "EVIDENCE_UNRESOLVED"
    if actual != expected_fact.get("value"):
        return False, "EVIDENCE_VALUE_MISMATCH"
    if actual != expected_fact.get("value"):
        return False, "EVIDENCE_VALUE_MISMATCH"
    return True, "EVIDENCE_VERIFIED"

def _item_match(case_root: Path, evidence: dict[str, Any], expected: dict[str, Any]) -> tuple[str, str]:
    if evidence.get("case_id") and evidence["case_id"] != expected.get("case_id"):
        return "INVALID", "EVIDENCE_CASE_MISMATCH"
    if evidence.get("benchmark_version") != expected.get("benchmark_version"):
        return "INVALID", "EVIDENCE_CASE_MISMATCH"
    if evidence.get("schema_version") != expected.get("schema_version"):
        return "INVALID", "EVIDENCE_CASE_MISMATCH"
    if evidence.get("type") != expected.get("type"):
        return "INVALID", "EVIDENCE_VALUE_MISMATCH"
    if evidence.get("fact") is not None or expected.get("fact") is not None:
        matched, reason = _fact_matches(case_root, evidence, expected)
        if not matched:
            return "INVALID" if reason != "EVIDENCE_UNRESOLVED" else "UNRESOLVED", reason
    location = evidence.get("location")
    expected_location = expected.get("location")
    if location:
        status, reason = verify_location(case_root, location)
        if status != "VERIFIED":
            return status, reason
        if expected_location:
            if normalize_evidence(location) != normalize_evidence(expected_location):
                return "INVALID", "EVIDENCE_VALUE_MISMATCH"
    elif expected_location:
        return "INVALID", "EVIDENCE_VALUE_MISMATCH"
    return "VERIFIED", "EVIDENCE_VERIFIED"

def verify_evidence(case: dict[str, Any], submitted: list[dict[str, Any]]) -> EvidenceVerificationResult:
    expected = case["expected_evidence"]
    expected_by_id = {item["evidence_id"]: item for item in expected}
    items: list[EvidenceItemResult] = []
    identities: dict[str, str] = {}
    verified_expected: set[str] = set()
    duplicate_count = 0
    for evidence in sorted((normalize_evidence(item) for item in submitted), key=lambda item: item["evidence_id"]):
        evidence_id = evidence["evidence_id"]
        identity = evidence_identity(evidence)
        if identity in identities:
            duplicate_count += 1
            items.append(EvidenceItemResult(evidence_id, "INVALID", "EVIDENCE_DUPLICATE", duplicate_of=identities[identity]))
            continue
        identities[identity] = evidence_id
        expected_item = expected_by_id.get(evidence_id)
        if expected_item is None:
            items.append(EvidenceItemResult(evidence_id, "INVALID", "EVIDENCE_VALUE_MISMATCH", details="unknown evidence id"))
            continue
        status, reason = _item_match(case["root"], evidence, expected_item)
        matched = (evidence_id,) if status == "VERIFIED" else ()
        if status == "VERIFIED":
            verified_expected.add(evidence_id)
        items.append(EvidenceItemResult(evidence_id, status, reason, matched_ground_truth=matched))
    missing = len(set(expected_by_id) - verified_expected)
    counts = {state.lower(): 0 for state in ("VERIFIED", "INVALID", "UNRESOLVED", "CONTRADICTED")}
    for item in items:
        counts[item.status.lower()] += 1
    integrity = calculate_integrity(len(submitted), counts["invalid"])
    coverage = calculate_coverage(expected, submitted, verified_expected)
    canonical = {
        "case_id": case["case_id"],
        "submission_ids": [item.evidence_id for item in items],
        "items": [item.as_dict() for item in items],
        "missing_expected": missing,
        "coverage": coverage,
    }
    result_hash = hashlib.sha256(
        json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return EvidenceVerificationResult(
        case_id=case["case_id"],
        submission_id="",
        benchmark_version=BENCHMARK_VERSION,
        evaluator_version=EVALUATOR_VERSION,
        items=tuple(items),
        submitted=len(submitted),
        verified=counts["verified"],
        invalid=counts["invalid"],
        unresolved=counts["unresolved"],
        contradicted=counts["contradicted"],
        missing_expected=missing,
        duplicate=duplicate_count,
        coverage=coverage,
        evidence_hallucination_rate=float(integrity["evidence_hallucination_rate"]),
        result_hash=result_hash,
    )

def evaluate_submission(submission_path: Path, cases_root: Path | None = None) -> dict[str, Any]:
    submission = load_submission(submission_path)
    case = load_case(submission["case_id"], cases_root)
    result = verify_evidence(case, submission["evidence"])
    result = EvidenceVerificationResult(
        **{**result.__dict__, "submission_id": submission["submission_id"]}
    )
    return result.as_dict()
