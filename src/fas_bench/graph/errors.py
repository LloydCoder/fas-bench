"""Structured graph-engine diagnostics and limits."""

from __future__ import annotations

from dataclasses import dataclass

GRAPH_ERROR_CODES = frozenset(
    {
        "INVALID_SUBMISSION",
        "INVALID_SCHEMA",
        "INVALID_GRAPH",
        "DANGLING_REFERENCE",
        "DUPLICATE_NODE",
        "DUPLICATE_EDGE",
        "UNSUPPORTED_VERSION",
        "UNSUPPORTED_NODE",
        "UNSUPPORTED_EDGE",
        "INVALID_PATH",
        "DISCONNECTED_PATH",
        "UNSUPPORTED_EVIDENCE",
        "CONTRADICTORY_EVIDENCE",
        "CROSS_CASE_REFERENCE",
        "GRAPH_LIMIT_EXCEEDED",
        "PATH_LIMIT_EXCEEDED",
        "EVALUATOR_ERROR",
        "DUPLICATE_PATH",
        "CASE_MISMATCH",
    }
)


@dataclass(frozen=True)
class GraphDiagnostic:
    code: str
    path: str
    message: str
    severity: str = "ERROR"

    def as_dict(self):
        return {
            "code": self.code,
            "path": self.path,
            "message": self.message,
            "severity": self.severity,
        }


@dataclass(frozen=True)
class GraphLimits:
    max_nodes: int = 20000
    max_edges: int = 50000
    max_paths: int = 1000
    max_path_length: int = 256
    max_serialized_bytes: int = 5_000_000
    max_traversal_states: int = 250_000


class GraphValidationError(ValueError):
    def __init__(self, diagnostics: tuple[GraphDiagnostic, ...]):
        self.diagnostics = diagnostics
        super().__init__(
            "graph validation failed: " + "; ".join(d.message for d in diagnostics[:5])
        )
