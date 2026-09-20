"""Deterministic Phase 5 finding, claim, security-condition, and verdict evaluation."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from ..contract import BENCHMARK_VERSION, SCHEMA_VERSION
from ..evidence import load_case, load_submission, verify_evidence
from ..graph import compare_graphs
from ..evidence.errors import CaseIntegrityError, CaseLoadError
from .errors import EvaluatorCaseError, EvaluatorInternalError, EvaluatorSubmissionError
from .models import (
    ClaimEvaluation,
    FindingEvaluation,
    FindingEvaluationResult,
    SecurityCondition,
    VerdictEvaluation,
)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvaluatorCaseError(f"cannot load authoritative case artifact: {path}") from exc


def _as_list(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        return value
    raise EvaluatorCaseError("authoritative artifact must be an object or array of objects")


def _load_ground_truth(case: dict[str, Any]) -> dict[str, Any]:
    root = case["root"]
    expected_root = root / "expected"
    claims = _as_list(_load_json(expected_root / "claims.json"))
    findings = _as_list(_load_json(expected_root / "findings.json"))
    verdict = _load_json(expected_root / "verdict.json")
    graph = _load_json(expected_root / "attack_graph.json")
    remediation = _load_json(expected_root / "remediation.json")
    if len(findings) != 1 or len(verdict) == 0 or len(graph.get("paths", [])) != 1:
        raise EvaluatorCaseError(
            "initial case contract requires one expected finding, verdict, and path"
        )
    return {
        "claims": claims,
        "finding": findings[0],
        "verdict": verdict,
        "graph": graph,
        "remediation": remediation,
    }


def _claim_key(claim: dict[str, Any]) -> tuple[Any, ...]:
    return (
        claim.get("claim_type"),
        claim.get("subject"),
        claim.get("predicate"),
    )


def _claim_exact_key(claim: dict[str, Any]) -> tuple[Any, ...]:
    return _claim_key(claim) + (claim.get("object"),)


def _evidence_status_map(evidence_result: Any) -> dict[str, str]:
    return {item.evidence_id: item.status for item in evidence_result.items}


def _finite_confidence(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and 0 <= float(value) <= 1
    )


def _expected_claims_for_submission(
    submission_claims: list[dict[str, Any]], expected_claims: list[dict[str, Any]]
) -> tuple[list[ClaimEvaluation], dict[str, str]]:
    expected_by_exact = {_claim_exact_key(claim): claim for claim in expected_claims}
    expected_by_base: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for claim in expected_claims:
        expected_by_base.setdefault(_claim_key(claim), []).append(claim)

    evaluations: list[ClaimEvaluation] = []
    mapping: dict[str, str] = {}
    for claim in sorted(submission_claims, key=lambda item: item["claim_id"]):
        exact = expected_by_exact.get(_claim_exact_key(claim))
        if exact is not None:
            evidence_ids = tuple(claim.get("related_evidence", ()))
            evaluations.append(
                ClaimEvaluation(
                    claim_id=claim["claim_id"],
                    status="UNRESOLVED",
                    expected_claim_id=exact["claim_id"],
                    reason_code="CLAIM_UNRESOLVED",
                    evidence_ids=evidence_ids,
                )
            )
            mapping[claim["claim_id"]] = exact["claim_id"]
            continue
        if expected_by_base.get(_claim_key(claim)):
            evaluations.append(
                ClaimEvaluation(
                    claim_id=claim["claim_id"],
                    status="CONTRADICTED",
                    reason_code="CLAIM_CONTRADICTED",
                    details=(
                        "claim structure matches an expected predicate but "
                        "asserts a different object"
                    ),
                )
            )
        else:
            evaluations.append(
                ClaimEvaluation(
                    claim_id=claim["claim_id"],
                    status="INVALID",
                    reason_code="CLAIM_INVALID",
                    details="no authoritative structured claim match",
                )
            )

    # A submission may contain contradictory assertions with the same structured subject/predicate.
    grouped: dict[tuple[Any, ...], list[ClaimEvaluation]] = {}
    for evaluation, claim in zip(
        evaluations, sorted(submission_claims, key=lambda item: item["claim_id"]), strict=True
    ):
        grouped.setdefault(_claim_key(claim), []).append(evaluation)
    for group in grouped.values():
        if len(group) > 1:
            objects = {
                next(
                    claim["object"]
                    for claim in submission_claims
                    if claim["claim_id"] == evaluation.claim_id
                )
                for evaluation in group
            }
            if len(objects) > 1:
                for evaluation in group:
                    idx = evaluations.index(evaluation)
                    evaluations[idx] = ClaimEvaluation(
                        claim_id=evaluation.claim_id,
                        status="CONTRADICTED",
                        expected_claim_id=evaluation.expected_claim_id,
                        reason_code="CLAIM_CONTRADICTED",
                        evidence_ids=evaluation.evidence_ids,
                        details="submission contains contradictory assertions",
                    )
    return evaluations, mapping


def evaluate_claims(
    submission: dict[str, Any],
    expected_claims: list[dict[str, Any]],
    evidence_result: Any,
) -> tuple[ClaimEvaluation, ...]:
    evaluations, _ = _expected_claims_for_submission(submission["claims"], expected_claims)
    evidence_states = _evidence_status_map(evidence_result)
    updated: list[ClaimEvaluation] = []
    for evaluation in evaluations:
        if evaluation.status not in {"UNRESOLVED", "VERIFIED"}:
            updated.append(evaluation)
            continue
        evidence_ids = evaluation.evidence_ids
        if not evidence_ids:
            updated.append(
                ClaimEvaluation(
                    claim_id=evaluation.claim_id,
                    status="MISSING",
                    expected_claim_id=evaluation.expected_claim_id,
                    reason_code="CLAIM_MISSING",
                    details="matched claim has no supporting evidence references",
                )
            )
            continue
        states = [evidence_states.get(evidence_id, "MISSING") for evidence_id in evidence_ids]
        if any(state == "CONTRADICTED" for state in states):
            status, reason = "CONTRADICTED", "CLAIM_CONTRADICTED"
        elif any(state == "INVALID" for state in states):
            status, reason = "INVALID", "CLAIM_INVALID"
        elif any(state == "UNRESOLVED" for state in states):
            status, reason = "UNRESOLVED", "CLAIM_UNRESOLVED"
        elif any(state == "MISSING" for state in states):
            status, reason = "MISSING", "CLAIM_MISSING"
        elif all(state == "VERIFIED" for state in states):
            status, reason = "VERIFIED", "CLAIM_VERIFIED"
        else:
            status, reason = "UNRESOLVED", "CLAIM_UNRESOLVED"
        updated.append(
            ClaimEvaluation(
                claim_id=evaluation.claim_id,
                status=status,
                expected_claim_id=evaluation.expected_claim_id,
                reason_code=reason,
                evidence_ids=evidence_ids,
                details=evaluation.details,
            )
        )
    return tuple(updated)


def resolve_security_condition(
    case: dict[str, Any], ground_truth: dict[str, Any]
) -> SecurityCondition:
    graph = ground_truth["graph"]
    path = graph["paths"][0]
    remediation = ground_truth["remediation"]
    verdict = ground_truth["verdict"]

    conditions = tuple(condition["prerequisite"] for condition in verdict.get("conditions", []))
    satisfied = tuple(
        condition["prerequisite"]
        for condition in verdict.get("conditions", [])
        if condition.get("satisfied") is True
    )
    unsatisfied = tuple(
        condition["prerequisite"]
        for condition in verdict.get("conditions", [])
        if condition.get("satisfied") is False
    )
    unknown = tuple(
        condition["prerequisite"]
        for condition in verdict.get("conditions", [])
        if condition.get("satisfied") is None
    )

    remediation_status = remediation.get("verification_status")
    if remediation_status == "VERIFIED":
        control_state = "EFFECTIVE"
    elif remediation_status == "FAILED":
        control_state = "INEFFECTIVE_OR_BYPASSED"
    elif path["status"] == "BLOCKED":
        control_state = "EFFECTIVE"
    elif path["status"] in {"VIABLE", "COMPLETE"}:
        control_state = "INEFFECTIVE_OR_BYPASSED"
    else:
        control_state = "UNKNOWN"

    claim_type = ground_truth["claims"][0].get("claim_type", "SECURITY_CONDITION")
    return SecurityCondition(
        path_id=path["path_id"],
        path_status=path["status"],
        security_property=claim_type,
        effective_control_state=control_state,
        required_conditions=conditions,
        satisfied_conditions=satisfied,
        unsatisfied_conditions=unsatisfied,
        unknown_conditions=unknown,
    )


def _derive_authoritative_verdict(
    ground_truth: dict[str, Any], condition: SecurityCondition
) -> str:
    remediation = ground_truth["remediation"]
    previous = remediation.get("previous_verdict")
    current = remediation.get("current_verdict")
    if previous == "REMEDIATED" and current == "EXPLOITABLE":
        return "REGRESSED"
    if remediation.get("verification_status") == "VERIFIED":
        return "REMEDIATED"
    if remediation.get("verification_status") == "FAILED":
        return "REMEDIATION_FAILED"
    if any(claim.get("status") == "UNKNOWN" for claim in ground_truth["claims"]):
        return "UNKNOWN"
    if condition.required_conditions:
        return "CONDITIONALLY_EXPLOITABLE"
    if condition.path_status in {"VIABLE", "COMPLETE"}:
        return "EXPLOITABLE"
    if condition.path_status == "BLOCKED":
        return "NOT_EXPLOITABLE"
    return "UNKNOWN"


def _reason_for_verdict(condition: SecurityCondition, verdict: str) -> str:
    if verdict == "EXPLOITABLE":
        return "EXPLOITABLE_VERIFIED_PATH"
    if verdict == "NOT_EXPLOITABLE":
        if "AUTHORIZATION" in condition.security_property:
            return "NOT_EXPLOITABLE_AUTHORIZATION_BOUNDARY"
        return "NOT_EXPLOITABLE_EFFECTIVE_CONTROL"
    if verdict == "CONDITIONALLY_EXPLOITABLE":
        return "CONDITIONAL_REQUIRED_PRECONDITION"
    if verdict == "REMEDIATED":
        return "REMEDIATED_ORIGINAL_PATH_BLOCKED"
    if verdict == "REMEDIATION_FAILED":
        return "REMEDIATION_FAILED_ALTERNATE_PATH"
    if verdict == "REGRESSED":
        return "REGRESSED_PREVIOUSLY_FIXED_PATH"
    return "UNKNOWN_INSUFFICIENT_EVIDENCE"


def _evaluate_finding_impl(
    finding: dict[str, Any],
    expected_finding: dict[str, Any],
    claim_evaluations: tuple[ClaimEvaluation, ...],
    evidence_result: Any,
    expected_verdict: str,
) -> FindingEvaluation:
    verified = {item.evidence_id for item in evidence_result.items if item.status == "VERIFIED"}
    claim_map = {claim.claim_id: claim for claim in claim_evaluations}
    category_supported = finding.get("category") == expected_finding.get("category")
    claims_supported = bool(finding.get("claim_ids")) and all(
        claim_map.get(claim_id) is not None and claim_map[claim_id].status == "VERIFIED"
        for claim_id in finding.get("claim_ids", [])
    )
    evidence_supported = bool(finding.get("evidence_ids")) and all(
        evidence_id in verified for evidence_id in finding.get("evidence_ids", [])
    )
    matched = category_supported and claims_supported
    return FindingEvaluation(
        finding_id=finding["finding_id"],
        matched=matched,
        category_supported=category_supported,
        claims_supported=claims_supported,
        evidence_supported=evidence_supported,
        verdict_claimed=finding["verdict"],
        expected_verdict=expected_verdict,
        reason_code="FINDING_MATCHED" if matched else "FINDING_MISMATCH",
        details=None if matched else "structured category/claim matching failed",
    )


def _expected_support(
    submission: dict[str, Any],
    ground_truth: dict[str, Any],
    claim_evaluations: tuple[ClaimEvaluation, ...],
    evidence_result: Any,
    condition: SecurityCondition,
    expected_verdict: str,
) -> tuple[bool, tuple[str, ...], tuple[str, ...]]:
    verified_evidence = {
        item.evidence_id for item in evidence_result.items if item.status == "VERIFIED"
    }
    verified_claims = {
        claim.expected_claim_id for claim in claim_evaluations if claim.status == "VERIFIED"
    }
    expected_claim_ids = {claim["claim_id"] for claim in ground_truth["claims"]}
    expected_evidence_ids = set(ground_truth["verdict"].get("evidence_ids", []))
    required_conditions = set(condition.required_conditions)

    supporting_claims = tuple(sorted(expected_claim_ids & verified_claims))
    blocking_claims = tuple(sorted(expected_claim_ids - set(supporting_claims)))
    submission_verdict_claim_ids = set(submission["verdict"].get("claim_ids", []))
    submission_verdict_evidence_ids = set(submission["verdict"].get("evidence_ids", []))

    claims_ok = expected_claim_ids <= verified_claims
    evidence_ok = expected_evidence_ids <= verified_evidence
    references_ok = (
        bool(submission_verdict_claim_ids)
        and submission_verdict_claim_ids
        <= {claim.claim_id for claim in claim_evaluations if claim.status == "VERIFIED"}
        and bool(submission_verdict_evidence_ids)
        and submission_verdict_evidence_ids <= verified_evidence
    )
    conditions_ok = not required_conditions or (
        set(condition.satisfied_conditions) == required_conditions
        and not condition.unknown_conditions
    )

    if expected_verdict == "UNKNOWN":
        # UNKNOWN is supported when the authoritative case itself remains inconclusive and
        # the submission demonstrates the case's known evidence rather than inventing certainty.
        support = claims_ok and evidence_ok and references_ok
    else:
        support = claims_ok and evidence_ok and references_ok and conditions_ok
    return support, supporting_claims, blocking_claims


def evaluate_verdict(
    submission: dict[str, Any],
    ground_truth: dict[str, Any],
    condition: SecurityCondition,
    claim_evaluations: tuple[ClaimEvaluation, ...],
    evidence_result: Any,
    finding_evaluation: FindingEvaluation,
    expected_verdict: str,
) -> VerdictEvaluation:
    submitted_verdict = submission["verdict"]["verdict"]
    supported, supporting_claims, blocking_claims = _expected_support(
        submission,
        ground_truth,
        claim_evaluations,
        evidence_result,
        condition,
        expected_verdict,
    )
    verdict_correct = submitted_verdict == expected_verdict
    if not finding_evaluation.matched:
        supported = False
    if not verdict_correct:
        reason = "VERDICT_INCORRECT"
    elif not supported:
        reason = "VERDICT_UNSUPPORTED_EVIDENCE"
    else:
        reason = _reason_for_verdict(condition, expected_verdict)
    return VerdictEvaluation(
        submitted=submitted_verdict,
        expected=expected_verdict,
        verdict_correct=verdict_correct,
        verdict_supported=supported,
        reason_code=reason,
        supporting_claims=supporting_claims,
        blocking_claims=blocking_claims,
        required_conditions=condition.required_conditions,
        satisfied_conditions=condition.satisfied_conditions,
        unsatisfied_conditions=condition.unsatisfied_conditions,
        evidence_ids=tuple(
            item.evidence_id for item in evidence_result.items if item.status == "VERIFIED"
        ),
    )


def _fingerprint_payload(
    case_id: str,
    finding: FindingEvaluation,
    claims: tuple[ClaimEvaluation, ...],
    condition: SecurityCondition,
    verdict: VerdictEvaluation,
    evidence: dict[str, Any],
    graph: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "finding": finding.as_dict(),
        "claims": [claim.as_dict() for claim in claims],
        "security_condition": condition.as_dict(),
        "verdict": verdict.as_dict(),
        "evidence": {
            key: evidence[key]
            for key in (
                "submitted_evidence_count",
                "verified_evidence_count",
                "invalid_evidence_count",
                "unresolved_evidence_count",
                "contradicted_evidence_count",
                "missing_expected_evidence_count",
                "duplicate_evidence_count",
                "coverage",
                "result_hash",
            )
        },
    }


def evaluate_submission_document(
    submission: dict[str, Any], cases_root: Path | None = None
) -> FindingEvaluationResult:
    if not _finite_confidence(submission["verdict"].get("confidence")):
        raise EvaluatorSubmissionError(
            "SUBMISSION_ERROR: verdict confidence must be finite and within [0,1]"
        )
    for finding in submission.get("findings", []):
        if not _finite_confidence(finding.get("confidence")):
            raise EvaluatorSubmissionError(
                "SUBMISSION_ERROR: finding confidence must be finite and within [0,1]"
            )
    for claim in submission.get("claims", []):
        if not _finite_confidence(claim.get("confidence")):
            raise EvaluatorSubmissionError(
                "SUBMISSION_ERROR: claim confidence must be finite and within [0,1]"
            )

    try:
        case = load_case(submission["case_id"], cases_root)
    except (CaseIntegrityError, CaseLoadError) as exc:
        raise EvaluatorCaseError(str(exc)) from exc
    ground_truth = _load_ground_truth(case)
    expected_verdict = ground_truth["verdict"]["verdict"]
    condition = resolve_security_condition(case, ground_truth)
    derived_verdict = _derive_authoritative_verdict(ground_truth, condition)
    if derived_verdict != expected_verdict:
        raise EvaluatorCaseError(
            f"authoritative verdict is inconsistent with declarative security condition: "
            f"stored={expected_verdict}, derived={derived_verdict}"
        )

    evidence_result = verify_evidence(case, submission["evidence"], submission)
    claims = evaluate_claims(submission, ground_truth["claims"], evidence_result)

    expected_finding = ground_truth["finding"]
    findings = sorted(submission.get("findings", []), key=lambda item: item["finding_id"])
    if not findings:
        raise EvaluatorSubmissionError("SUBMISSION_ERROR: at least one finding is required")
    selected = findings[0]
    finding_evaluation = evaluate_finding(
        selected, expected_finding, claims, evidence_result, expected_verdict
    )
    verdict_evaluation = evaluate_verdict(
        submission,
        ground_truth,
        condition,
        claims,
        evidence_result,
        finding_evaluation,
        expected_verdict,
    )
    evidence = {
        "submitted_evidence_count": evidence_result.submitted,
        "verified_evidence_count": evidence_result.verified,
        "invalid_evidence_count": evidence_result.invalid,
        "unresolved_evidence_count": evidence_result.unresolved,
        "contradicted_evidence_count": evidence_result.contradicted,
        "missing_expected_evidence_count": evidence_result.missing_expected,
        "duplicate_evidence_count": evidence_result.duplicate,
        "evidence_hallucination_rate": evidence_result.evidence_hallucination_rate,
        "coverage": evidence_result.coverage,
        "result_hash": evidence_result.result_hash,
    }
    graph_result = None
    if submission.get("attack_graph") is not None:
        graph_result = compare_graphs(
            ground_truth["graph"],
            submission["attack_graph"],
            case_id=submission["case_id"],
            evidence_ids={item.evidence_id for item in evidence_result.items},
        ).as_dict()
    payload = _fingerprint_payload(
        submission["case_id"], finding_evaluation, claims, condition, verdict_evaluation, evidence, graph_result
    )
    fingerprint = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    return FindingEvaluationResult(
        evaluation_id="EVAL-" + fingerprint[:16],
        case_id=submission["case_id"],
        submission_id=submission["submission_id"],
        benchmark_version=BENCHMARK_VERSION,
        schema_version=SCHEMA_VERSION,
        expected_verdict=expected_verdict,
        finding=finding_evaluation,
        claims=claims,
        security_condition=condition,
        verdict=verdict_evaluation,
        evidence=evidence,
        fingerprint=fingerprint,
        graph=graph_result,
    )


def evaluate_finding(
    finding: dict[str, Any],
    expected_finding: dict[str, Any],
    claim_evaluations: tuple[ClaimEvaluation, ...],
    evidence_result: Any,
    expected_verdict: str,
) -> FindingEvaluation:
    return _evaluate_finding_impl(
        finding, expected_finding, claim_evaluations, evidence_result, expected_verdict
    )


def evaluate_submission(
    submission_path: Path, cases_root: Path | None = None
) -> FindingEvaluationResult:
    try:
        submission = load_submission(submission_path)
        return evaluate_submission_document(submission, cases_root)
    except (EvaluatorCaseError, EvaluatorSubmissionError):
        raise
    except Exception as exc:
        raise EvaluatorInternalError("EVALUATOR_ERROR: unexpected evaluator failure") from exc
