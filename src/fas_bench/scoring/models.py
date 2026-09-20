"""Typed Phase 8 measurement models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ScoreComponent:
    name: str
    normalized: float
    weight: float
    available: bool = True
    contribution: float = 0.0
    direction: str = "higher_is_better"
    formula: str = ""
    raw: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not 0 <= self.normalized <= 1 or self.weight < 0 or not 0 <= self.contribution <= 1:
            raise ValueError("invalid score component")
        if self.direction not in {"higher_is_better", "lower_is_better"}:
            raise ValueError("invalid score direction")

    def as_dict(self):
        return {
            "name": self.name,
            "normalized": self.normalized,
            "weight": self.weight,
            "available": self.available,
            "contribution": self.contribution,
            "direction": self.direction,
            "formula": self.formula,
            "raw": self.raw,
        }


@dataclass(frozen=True)
class ScoringConfig:
    scoring_version: str
    evidence_weights: dict[str, float]
    integrity_policy: dict[str, float]
    graph_weights: dict[str, float]
    composite_weights: dict[str, float]
    calibration: dict[str, Any]
    bootstrap: dict[str, Any]

    @classmethod
    def from_dict(cls, value):
        obj = cls(**value)
        for name, weights in (
            ("evidence_weights", obj.evidence_weights),
            ("graph_weights", obj.graph_weights),
            ("composite_weights", obj.composite_weights),
        ):
            if any(v < 0 for v in weights.values()) or sum(weights.values()) <= 0:
                raise ValueError("invalid " + name)
        if set(obj.evidence_weights) != {"validity", "relevance", "coverage", "specificity"}:
            raise ValueError("invalid evidence weight keys")
        if set(obj.graph_weights) != {
            "node_f1",
            "edge_f1",
            "path_completeness",
            "boundary_crossing_f1",
        }:
            raise ValueError("invalid graph weight keys")
        if set(obj.composite_weights) != {
            "evidence",
            "verdict",
            "reachability",
            "attack_path",
            "false_positive_resistance",
            "remediation",
            "calibration",
            "efficiency",
        }:
            raise ValueError("invalid composite weight keys")
        if (
            not isinstance(obj.calibration.get("bins"), int)
            or not 1 <= obj.calibration["bins"] <= 1000
        ):
            raise ValueError("invalid calibration bins")
        if not 0 < float(obj.calibration.get("confidence_level", 0)) < 1:
            raise ValueError("invalid confidence level")
        return obj


@dataclass(frozen=True)
class CaseScore:
    case_id: str
    benchmark_version: str
    evaluator_version: str
    scoring_version: str
    submission_id: str
    gold_verdict: str
    candidate_verdict: str
    verdict_correct: bool
    finding_metrics: dict[str, Any]
    evidence_metrics: dict[str, Any]
    reachability_metrics: dict[str, Any]
    graph_metrics: dict[str, Any]
    impact_metrics: dict[str, Any]
    remediation_metrics: dict[str, Any]
    calibration_metrics: dict[str, Any]
    efficiency_metrics: dict[str, Any]
    integrity_metrics: dict[str, Any]
    score_components: dict[str, ScoreComponent]
    case_score: float
    evaluation_status: str = "SUCCESS"
    errors: tuple[dict[str, str], ...] = ()
    warnings: tuple[str, ...] = ()

    def as_dict(self):
        return {
            "case_id": self.case_id,
            "benchmark_version": self.benchmark_version,
            "evaluator_version": self.evaluator_version,
            "scoring_version": self.scoring_version,
            "submission_id": self.submission_id,
            "gold_verdict": self.gold_verdict,
            "candidate_verdict": self.candidate_verdict,
            "verdict_correct": self.verdict_correct,
            "finding_metrics": self.finding_metrics,
            "evidence_metrics": self.evidence_metrics,
            "reachability_metrics": self.reachability_metrics,
            "graph_metrics": self.graph_metrics,
            "impact_metrics": self.impact_metrics,
            "remediation_metrics": self.remediation_metrics,
            "calibration_metrics": self.calibration_metrics,
            "efficiency_metrics": self.efficiency_metrics,
            "integrity_metrics": self.integrity_metrics,
            "score_components": {k: v.as_dict() for k, v in self.score_components.items()},
            "case_score": self.case_score,
            "evaluation_status": self.evaluation_status,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
        }
