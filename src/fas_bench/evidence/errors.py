"""Stable Phase 4 evidence-engine errors."""

from __future__ import annotations


class EvidenceEngineError(Exception):
    """Base class for deterministic evaluator failures."""


class CaseIntegrityError(EvidenceEngineError):
    """Raised when benchmark case integrity cannot be established."""


class CaseLoadError(EvidenceEngineError):
    """Raised when a case cannot be safely loaded."""


class SubmissionError(EvidenceEngineError):
    """Raised when a submission cannot be parsed or validated."""


class EvidenceVerificationError(EvidenceEngineError):
    """Raised for evaluator-internal evidence verification failures."""
