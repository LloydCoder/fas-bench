"""Public graph-domain result models."""

from __future__ import annotations

from dataclasses import dataclass, field

from .errors import GraphDiagnostic, GraphLimits


@dataclass(frozen=True)
class GraphValidationResult:
    valid: bool
    diagnostics: tuple[GraphDiagnostic, ...] = ()
    node_count: int = 0
    edge_count: int = 0
    path_count: int = 0
    graph_digest: str = ""

    def as_dict(self):
        return {
            "valid": self.valid,
            "diagnostics": [d.as_dict() for d in self.diagnostics],
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "path_count": self.path_count,
            "graph_digest": self.graph_digest,
        }


@dataclass(frozen=True)
class MetricSet:
    precision: float
    recall: float
    f1: float
    true_positive: int
    submitted: int
    expected: int

    def as_dict(self):
        return {
            "precision": self.precision,
            "recall": self.recall,
            "f1": self.f1,
            "true_positive": self.true_positive,
            "submitted": self.submitted,
            "expected": self.expected,
        }


@dataclass(frozen=True)
class GraphMetrics:
    node: MetricSet
    edge: MetricSet
    path_completeness: float
    boundary: MetricSet
    graph_score: float
    unsupported_edges: tuple[str, ...] = ()
    contradictory_edges: tuple[str, ...] = ()
    missing_transitions: tuple[str, ...] = ()
    matched_paths: tuple[str, ...] = ()
    alternate_paths: tuple[tuple[str, ...], ...] = ()

    def as_dict(self):
        return {
            "node_metrics": self.node.as_dict(),
            "edge_metrics": self.edge.as_dict(),
            "path_completeness": self.path_completeness,
            "boundary_crossing_metrics": self.boundary.as_dict(),
            "graph_score": self.graph_score,
            "unsupported_edges": list(self.unsupported_edges),
            "contradictory_edges": list(self.contradictory_edges),
            "missing_transitions": list(self.missing_transitions),
            "matched_paths": list(self.matched_paths),
            "alternate_paths": [list(p) for p in self.alternate_paths],
        }


@dataclass(frozen=True)
class GraphEvaluation:
    valid: bool
    validation: GraphValidationResult
    metrics: GraphMetrics
    graph_digest: str
    expected_graph_digest: str
    case_digest: str | None = None
    versions: dict[str, str] = field(default_factory=dict)

    def as_dict(self):
        return {
            "valid": self.valid,
            "validation": self.validation.as_dict(),
            **self.metrics.as_dict(),
            "graph_digest": self.graph_digest,
            "expected_graph_digest": self.expected_graph_digest,
            "case_digest": self.case_digest,
            "versions": dict(self.versions),
        }


DEFAULT_LIMITS = GraphLimits()
