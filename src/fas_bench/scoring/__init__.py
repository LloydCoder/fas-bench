"""Deterministic Phase 8 measurement and scoring API."""

from .engine import build_perfect_submission, load_config, score_case, score_submission
from .metrics import (
    binary_metrics,
    brier_score,
    confusion_matrix,
    evidence_score,
    expected_calibration_error,
    multiclass_brier,
    normalize_score,
)
from .models import CaseScore, ScoreComponent, ScoringConfig

__all__ = [
    "CaseScore",
    "ScoreComponent",
    "ScoringConfig",
    "score_case",
    "score_submission",
    "build_perfect_submission",
    "load_config",
    "binary_metrics",
    "evidence_score",
    "brier_score",
    "expected_calibration_error",
    "confusion_matrix",
    "normalize_score",
    "multiclass_brier",
]
