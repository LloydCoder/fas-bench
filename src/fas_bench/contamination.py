"""Phase 17 hidden-evaluation and contamination-defense contracts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum


_SHA256 = 64


class CorpusVisibility(StrEnum):
    PUBLIC_PRACTICE = "PUBLIC_PRACTICE"
    PUBLIC_CANARY = "PUBLIC_CANARY"
    PRIVATE_OFFICIAL = "PRIVATE_OFFICIAL"
    PRIVATE_HOLDOUT = "PRIVATE_HOLDOUT"


class ContaminationStatus(StrEnum):
    CLEAN = "CLEAN"
    SUSPECTED = "SUSPECTED"
    CONFIRMED = "CONFIRMED"
    UNKNOWN = "UNKNOWN"


def _valid_digest(value: str) -> bool:
    return (
        isinstance(value, str)
        and len(value) == _SHA256
        and value == value.lower()
        and all(character in "0123456789abcdef" for character in value)
    )


def _valid_temporal_cutoff(value: str | None) -> bool:
    if not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            date.fromisoformat(value)
        except ValueError:
            return False
    return True


@dataclass(frozen=True)
class CorpusSet:
    corpus_id: str
    version: str
    visibility: CorpusVisibility
    case_digests: tuple[str, ...]
    access_policy: str
    temporal_cutoff: str | None = None

    def identity(self) -> str:
        payload = {
            "corpus_id": self.corpus_id,
            "version": self.version,
            "visibility": self.visibility.value,
            "case_digests": sorted(self.case_digests),
            "access_policy": self.access_policy,
            "temporal_cutoff": self.temporal_cutoff,
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()


@dataclass(frozen=True)
class ContaminationFinding:
    corpus_id: str
    status: ContaminationStatus
    source: str
    evidence_digest: str
    temporal_scope: str | None = None


def validate_corpus(corpus: CorpusSet) -> list[str]:
    errors: list[str] = []
    if not isinstance(corpus.corpus_id, str) or not corpus.corpus_id.strip():
        errors.append("corpus_id must be a non-empty string")
    if not isinstance(corpus.version, str) or not corpus.version.strip():
        errors.append("corpus identity fields are required")
    if not corpus.case_digests:
        errors.append("case_digests must not be empty")
    if len(corpus.case_digests) != len(set(corpus.case_digests)):
        errors.append("case_digests must not contain duplicates")
    if any(not _valid_digest(digest) for digest in corpus.case_digests):
        errors.append("case_digests must contain lowercase SHA-256 digests")
    if not isinstance(corpus.access_policy, str) or not corpus.access_policy.strip():
        errors.append("access_policy is required")
    if corpus.visibility in {
        CorpusVisibility.PRIVATE_OFFICIAL,
        CorpusVisibility.PRIVATE_HOLDOUT,
    } and not _valid_temporal_cutoff(corpus.temporal_cutoff):
        errors.append("private corpora require an ISO-8601 temporal cutoff")
    return sorted(set(errors))


def _validate_finding(finding: ContaminationFinding) -> list[str]:
    errors: list[str] = []
    if not isinstance(finding.corpus_id, str) or not finding.corpus_id.strip():
        errors.append("finding corpus_id is required")
    if not isinstance(finding.source, str) or not finding.source.strip():
        errors.append("finding source is required")
    if not _valid_digest(finding.evidence_digest):
        errors.append("finding evidence_digest must be a lowercase SHA-256 digest")
    if finding.temporal_scope and not _valid_temporal_cutoff(finding.temporal_scope):
        errors.append("finding temporal_scope must be ISO-8601")
    return errors


def contamination_gate(corpus: CorpusSet, findings: list[ContaminationFinding]) -> dict:
    errors = validate_corpus(corpus)
    errors.extend(
        f"finding: {error}" for finding in findings for error in _validate_finding(finding)
    )
    relevant = [f for f in findings if f.corpus_id == corpus.corpus_id]
    if len(relevant) != len({(f.source, f.evidence_digest) for f in relevant}):
        errors.append("duplicate contamination finding")

    if corpus.visibility in {
        CorpusVisibility.PRIVATE_OFFICIAL,
        CorpusVisibility.PRIVATE_HOLDOUT,
    }:
        if not relevant:
            errors.append("private corpus requires an explicit contamination assessment")
        if any(f.status != ContaminationStatus.CLEAN for f in relevant):
            errors.append("private corpus is not contamination-clean")

    return {
        "phase": "17",
        "status": "PASS" if not errors else "FAIL",
        "corpus_id": corpus.corpus_id,
        "visibility": corpus.visibility.value,
        "contamination_status": (
            "BLOCKED"
            if any(f.status == ContaminationStatus.CONFIRMED for f in relevant)
            else "REVIEW"
            if any(f.status != ContaminationStatus.CLEAN for f in relevant)
            else "ASSESSED"
        ),
        "errors": sorted(set(errors)),
        "hidden_answers_in_public_repo": False,
    }
