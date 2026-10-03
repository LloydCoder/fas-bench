"""Phase 17 hidden-evaluation and contamination-defense contracts."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import StrEnum


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
    if not corpus.corpus_id.strip() or not corpus.version.strip():
        errors.append("corpus identity fields are required")
    if not corpus.case_digests:
        errors.append("case_digests must not be empty")
    if not corpus.access_policy.strip():
        errors.append("access_policy is required")
    if corpus.visibility == CorpusVisibility.PRIVATE_OFFICIAL:
        if not corpus.temporal_cutoff:
            errors.append("private official corpora require a temporal cutoff")
    return sorted(set(errors))


def contamination_gate(
    corpus: CorpusSet, findings: list[ContaminationFinding]
) -> dict:
    errors = validate_corpus(corpus)
    relevant = [f for f in findings if f.corpus_id == corpus.corpus_id]
    if corpus.visibility == CorpusVisibility.PRIVATE_OFFICIAL:
        if not relevant:
            errors.append("official corpus requires an explicit contamination assessment")
        if any(
            f.status != ContaminationStatus.CLEAN for f in relevant
        ):
            errors.append("official corpus is not contamination-clean")
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
