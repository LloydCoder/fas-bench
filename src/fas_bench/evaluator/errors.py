"""Stable Phase 5 evaluator errors."""

class EvaluatorError(Exception):
    """Base class for deterministic finding/verdict evaluation failures."""


class EvaluatorCaseError(EvaluatorError):
    """Raised when authoritative case data cannot be trusted or resolved."""


class EvaluatorSubmissionError(EvaluatorError):
    """Raised when a submission cannot be evaluated."""


class EvaluatorInternalError(EvaluatorError):
    """Raised for evaluator implementation failures; never converted to a verdict."""
