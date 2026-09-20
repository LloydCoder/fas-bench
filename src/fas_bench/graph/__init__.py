"""Public Phase 6 security-graph API."""

from .diff import diff_graphs
from .engine import (
    GRAPH_ENGINE_VERSION,
    GRAPH_SCHEMA_VERSION,
    NORMALIZATION_VERSION,
    SCORING_VERSION,
    calculate_graph_metrics,
    compare_graphs,
    evaluate_attack_graph,
    extract_paths,
    find_alternate_paths,
    graph_digest,
    minimal_security_paths,
    validate_graph,
)
from .errors import GraphDiagnostic, GraphLimits, GraphValidationError
from .models import GraphEvaluation, GraphMetrics, GraphValidationResult, MetricSet
from .normalization import (
    canonical_json,
    canonicalize_graph,
    node_key,
    normalize_identity,
    normalize_name,
    normalize_path,
    normalize_text,
)

__all__ = [
    "GRAPH_ENGINE_VERSION",
    "GRAPH_SCHEMA_VERSION",
    "NORMALIZATION_VERSION",
    "SCORING_VERSION",
    "GraphDiagnostic",
    "GraphLimits",
    "GraphValidationError",
    "GraphEvaluation",
    "GraphMetrics",
    "GraphValidationResult",
    "MetricSet",
    "canonical_json",
    "canonicalize_graph",
    "calculate_graph_metrics",
    "compare_graphs",
    "diff_graphs",
    "evaluate_attack_graph",
    "extract_paths",
    "find_alternate_paths",
    "graph_digest",
    "minimal_security_paths",
    "node_key",
    "normalize_identity",
    "normalize_name",
    "normalize_path",
    "normalize_text",
    "validate_graph",
]
