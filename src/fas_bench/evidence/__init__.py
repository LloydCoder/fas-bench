"""Deterministic evidence verification engine for FAS-Bench Phase 4."""

from .engine import evaluate_submission, load_case, load_submission, verify_evidence
from .coverage import calculate_coverage
from .integrity import calculate_integrity
from .normalization import canonical_evidence, evidence_identity, normalize_evidence
from .relationships import relationship_errors

__all__ = [
    "calculate_coverage",
    "calculate_integrity",
    "canonical_evidence",
    "evidence_identity",
    "evaluate_submission",
    "load_case",
    "load_submission",
    "normalize_evidence",
    "relationship_errors",
    "verify_evidence",
]
