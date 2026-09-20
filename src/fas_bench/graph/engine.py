"""Deterministic attack-path and security-graph evaluation engine."""

from __future__ import annotations
import hashlib
import json
from collections import defaultdict, deque
from dataclasses import replace
from typing import Any, Iterable
from .errors import GraphDiagnostic, GraphLimits
from .models import GraphEvaluation, GraphMetrics, GraphValidationResult, MetricSet
from .normalization import canonical_json, canonicalize_graph, node_key, normalize_identity

GRAPH_SCHEMA_VERSION = "0.1"
GRAPH_ENGINE_VERSION = "0.1.0"
NORMALIZATION_VERSION = "0.1.0"
SCORING_VERSION = "0.1.0"
NODE_TYPES = {
    "ACTOR",
    "INPUT",
    "FUNCTION",
    "PROCESS",
    "SERVICE",
    "DATA",
    "RESOURCE",
    "TOOL",
    "AGENT",
    "MCP_SERVER",
    "IDENTITY",
    "PERMISSION",
    "POLICY",
    "NETWORK_ZONE",
    "TRUST_BOUNDARY",
    "SINK",
    "IMPACT",
}
EDGE_TYPES = {
    "CONTROLS",
    "FLOWS_TO",
    "CALLS",
    "READS",
    "WRITES",
    "INVOKES",
    "AUTHENTICATES_AS",
    "AUTHORIZED_BY",
    "CROSSES",
    "TRANSFORMS",
    "REACHES",
    "DEPENDS_ON",
    "DEPLOYS_TO",
    "TRIGGERS",
}
SECURITY_CRITICAL_NODE_TYPES = {
    "IDENTITY",
    "PERMISSION",
    "POLICY",
    "TRUST_BOUNDARY",
    "NETWORK_ZONE",
    "SINK",
    "IMPACT",
}


def graph_digest(graph: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(graph)).hexdigest()


def _metric(tp: int, submitted: int, expected: int) -> MetricSet:
    p = tp / submitted if submitted else 0.0
    r = tp / expected if expected else (1.0 if submitted == 0 else 0.0)
    f = 2 * p * r / (p + r) if p + r else 0.0
    return MetricSet(p, r, f, tp, submitted, expected)


def _limit_diagnostics(graph: dict[str, Any], limits: GraphLimits) -> list[GraphDiagnostic]:
    raw = json.dumps(graph, separators=(",", ":"), ensure_ascii=False).encode()
    d = []
    if len(raw) > limits.max_serialized_bytes:
        d.append(
            GraphDiagnostic(
                "GRAPH_LIMIT_EXCEEDED",
                "$",
                f"serialized graph exceeds {limits.max_serialized_bytes} bytes",
            )
        )
    if len(graph.get("nodes", [])) > limits.max_nodes:
        d.append(
            GraphDiagnostic(
                "GRAPH_LIMIT_EXCEEDED", "nodes", f"node limit {limits.max_nodes} exceeded"
            )
        )
    if len(graph.get("edges", [])) > limits.max_edges:
        d.append(
            GraphDiagnostic(
                "GRAPH_LIMIT_EXCEEDED", "edges", f"edge limit {limits.max_edges} exceeded"
            )
        )
    if len(graph.get("paths", [])) > limits.max_paths:
        d.append(
            GraphDiagnostic(
                "GRAPH_LIMIT_EXCEEDED", "paths", f"path limit {limits.max_paths} exceeded"
            )
        )
    return d


def validate_graph(
    graph: dict[str, Any],
    *,
    case_id: str | None = None,
    evidence_ids: set[str] | None = None,
    limits: GraphLimits | None = None,
) -> GraphValidationResult:
    limits = limits or GraphLimits()
    diagnostics = _limit_diagnostics(graph, limits)
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    paths = graph.get("paths", [])
    ni = {}
    ei = {}
    pi = {}
    for i, n in enumerate(nodes):
        nid = n.get("node_id")
        if nid in ni:
            diagnostics.append(
                GraphDiagnostic("DUPLICATE_NODE", f"nodes[{i}]", f"duplicate node {nid!r}")
            )
        else:
            ni[nid] = n
        if n.get("type") not in NODE_TYPES:
            diagnostics.append(
                GraphDiagnostic(
                    "UNSUPPORTED_NODE",
                    f"nodes[{i}].type",
                    f"unsupported node type {n.get('type')!r}",
                )
            )
    for i, e in enumerate(edges):
        eid = e.get("edge_id")
        if eid in ei:
            diagnostics.append(
                GraphDiagnostic("DUPLICATE_EDGE", f"edges[{i}]", f"duplicate edge {eid!r}")
            )
        else:
            ei[eid] = e
        if e.get("type") not in EDGE_TYPES:
            diagnostics.append(
                GraphDiagnostic(
                    "UNSUPPORTED_EDGE",
                    f"edges[{i}].type",
                    f"unsupported edge type {e.get('type')!r}",
                )
            )
        if e.get("source") not in ni:
            diagnostics.append(
                GraphDiagnostic(
                    "DANGLING_REFERENCE",
                    f"edges[{i}].source",
                    f"unknown source {e.get('source')!r}",
                )
            )
        if e.get("target") not in ni:
            diagnostics.append(
                GraphDiagnostic(
                    "DANGLING_REFERENCE",
                    f"edges[{i}].target",
                    f"unknown target {e.get('target')!r}",
                )
            )
        if evidence_ids is not None:
            for ev in e.get("evidence_ids", []):
                if ev not in evidence_ids:
                    diagnostics.append(
                        GraphDiagnostic(
                            "UNSUPPORTED_EVIDENCE",
                            f"edges[{i}].evidence_ids",
                            f"unknown evidence {ev!r}",
                        )
                    )
    for i, p in enumerate(paths):
        pid = p.get("path_id")
        if pid in pi:
            diagnostics.append(
                GraphDiagnostic("DUPLICATE_PATH", f"paths[{i}]", f"duplicate path {pid!r}")
            )
        else:
            pi[pid] = p
        ns = p.get("node_ids", [])
        es = p.get("edge_ids", [])
        if len(ns) > limits.max_path_length:
            diagnostics.append(
                GraphDiagnostic(
                    "GRAPH_LIMIT_EXCEEDED",
                    f"paths[{i}]",
                    f"path length limit {limits.max_path_length} exceeded",
                )
            )
        if len(es) != max(0, len(ns) - 1):
            diagnostics.append(
                GraphDiagnostic(
                    "INVALID_PATH",
                    pid or f"paths[{i}]",
                    "path must contain one edge per node transition",
                )
            )
        for nid in ns:
            if nid not in ni:
                diagnostics.append(
                    GraphDiagnostic("DANGLING_REFERENCE", pid or "path", f"unknown node {nid!r}")
                )
        for j, eid in enumerate(es):
            if eid not in ei:
                diagnostics.append(
                    GraphDiagnostic("DANGLING_REFERENCE", pid or "path", f"unknown edge {eid!r}")
                )
                continue
            if j + 1 < len(ns):
                e = ei[eid]
                if e.get("source") != ns[j] or e.get("target") != ns[j + 1]:
                    diagnostics.append(
                        GraphDiagnostic(
                            "DISCONNECTED_PATH",
                            pid or "path",
                            f"edge {eid!r} contradicts node sequence",
                        )
                    )
        if p.get("entry_node") not in ni or p.get("impact_node") not in ni:
            diagnostics.append(
                GraphDiagnostic("INVALID_PATH", pid or "path", "invalid entry or impact node")
            )
        if evidence_ids is not None:
            for ev in p.get("evidence_ids", []):
                if ev not in evidence_ids:
                    diagnostics.append(
                        GraphDiagnostic(
                            "UNSUPPORTED_EVIDENCE", pid or "path", f"unknown evidence {ev!r}"
                        )
                    )
    if case_id is not None and graph.get("metadata", {}).get("case_id") not in (None, case_id):
        diagnostics.append(
            GraphDiagnostic(
                "CASE_MISMATCH", "metadata.case_id", "graph case does not match evaluation case"
            )
        )
    digest = graph_digest(graph)
    return GraphValidationResult(
        not diagnostics, tuple(diagnostics), len(nodes), len(edges), len(paths), digest
    )


def _semantic_node_matches(expected: dict[str, Any], submitted: dict[str, Any]) -> bool:
    if expected.get("type") != submitted.get("type"):
        return False
    if node_key(expected) == node_key(submitted):
        return True
    ea = expected.get("attributes") or {}
    sa = submitted.get("attributes") or {}
    aliases = set(map(str, ea.get("aliases", []))) | {str(expected.get("node_id"))}
    return normalize_identity(submitted) in {
        normalize_identity(expected),
        *aliases,
    } or normalize_identity(expected) in {
        normalize_identity(submitted),
        *set(map(str, sa.get("aliases", []))),
    }


def _match_nodes(expected_nodes: list[dict[str, Any]], submitted_nodes: list[dict[str, Any]]):
    matches = {}
    used = set()
    for en in sorted(expected_nodes, key=lambda n: n.get("node_id", "")):
        candidates = [
            sn
            for sn in submitted_nodes
            if sn.get("node_id") not in used and _semantic_node_matches(en, sn)
        ]
        if candidates:
            sn = min(candidates, key=lambda n: n.get("node_id", ""))
            matches[en["node_id"]] = sn["node_id"]
            used.add(sn["node_id"])
    return matches


def _edge_key(e, node_map=None):
    source = node_map.get(e.get("source"), e.get("source")) if node_map else e.get("source")
    target = node_map.get(e.get("target"), e.get("target")) if node_map else e.get("target")
    return (e.get("type"), source, target)


def _match_edges(expected, submitted, node_matches):
    inverse = {v: k for k, v in node_matches.items()}
    matched = {}
    used = set()
    for ee in sorted(expected, key=lambda e: e.get("edge_id", "")):
        target_key = (
            ee.get("type"),
            node_matches.get(ee.get("source"), ""),
            node_matches.get(ee.get("target"), ""),
        )
        candidates = [
            se for se in submitted if se.get("edge_id") not in used and _edge_key(se) == target_key
        ]
        if candidates:
            se = min(candidates, key=lambda e: e.get("edge_id", ""))
            matched[ee["edge_id"]] = se["edge_id"]
            used.add(se["edge_id"])
    return matched


def _path_signature(path, graph, node_map=None):
    nodes = graph.get("nodes", [])
    ni = {n["node_id"]: n for n in nodes}
    edges = {e["edge_id"]: e for e in graph.get("edges", [])}
    node_ids = path.get("node_ids", [])
    node_sig = tuple((ni[n].get("type"), normalize_identity(ni[n])) for n in node_ids if n in ni)
    edge_sig = tuple(edges[e].get("type") for e in path.get("edge_ids", []) if e in edges)
    return node_sig, edge_sig, path.get("status")


def compare_paths(expected_graph, submitted_graph, node_matches, edge_matches):
    expected = expected_graph.get("paths", [])
    submitted = submitted_graph.get("paths", [])
    matched = []
    used = set()
    for ep in sorted(expected, key=lambda p: p.get("path_id", "")):
        en = [node_matches.get(n) for n in ep.get("node_ids", [])]
        ee = [edge_matches.get(e) for e in ep.get("edge_ids", [])]
        for sp in submitted:
            if sp.get("path_id") in used:
                continue
            sn = sp.get("node_ids", [])
            se = sp.get("edge_ids", [])
            if en == sn and ee == se and ep.get("status") == sp.get("status"):
                matched.append(ep.get("path_id"))
                used.add(sp.get("path_id"))
                break
    completeness = len(matched) / len(expected) if expected else (1.0 if not submitted else 0.0)
    missing = []
    for ep in expected:
        if ep.get("path_id") not in matched:
            missing.append(ep.get("path_id"))
    return completeness, tuple(matched), tuple(missing)


def _boundary_metrics(expected, submitted):
    def keys(g):
        return {
            (b.get("from_zone"), b.get("to_zone"), b.get("control"))
            for b in g.get("trust_boundaries", [])
        }

    a, b = keys(expected), keys(submitted)
    tp = len(a & b)
    return _metric(tp, len(b), len(a))


def calculate_graph_metrics(
    expected: dict[str, Any], submitted: dict[str, Any], *, weights=(0.30, 0.35, 0.20, 0.15)
) -> GraphMetrics:
    nm = _match_nodes(expected.get("nodes", []), submitted.get("nodes", []))
    em = _match_edges(expected.get("edges", []), submitted.get("edges", []), nm)
    node_metric = _metric(len(nm), len(submitted.get("nodes", [])), len(expected.get("nodes", [])))
    edge_metric = _metric(len(em), len(submitted.get("edges", [])), len(expected.get("edges", [])))
    path_complete, matched_paths, missing = compare_paths(expected, submitted, nm, em)
    boundary = _boundary_metrics(expected, submitted)
    unsupported = []
    contradictory = []
    expected_edge_keys = {_edge_key(e) for e in expected.get("edges", [])}
    for e in submitted.get("edges", []):
        if _edge_key(e) not in expected_edge_keys:
            unsupported.append(e.get("edge_id", ""))
    for e in submitted.get("edges", []):
        if e.get("type") == "AUTHENTICATES_AS":
            for ee in expected.get("edges", []):
                if (
                    ee.get("source") == e.get("source")
                    and ee.get("type") == e.get("type")
                    and ee.get("target") != e.get("target")
                ):
                    contradictory.append(e.get("edge_id", ""))
    score = (
        weights[0] * node_metric.f1
        + weights[1] * edge_metric.f1
        + weights[2] * path_complete
        + weights[3] * boundary.f1
    )
    if unsupported:
        score = min(score, max(0.0, score - 0.05 * len(unsupported)))
    if contradictory:
        score = min(score, max(0.0, score - 0.10 * len(contradictory)))
    return GraphMetrics(
        node_metric,
        edge_metric,
        path_complete,
        boundary,
        max(0.0, min(1.0, score)),
        tuple(sorted(unsupported)),
        tuple(sorted(contradictory)),
        missing,
        matched_paths,
        (),
    )


def extract_paths(
    graph: dict[str, Any],
    *,
    limits: GraphLimits | None = None,
    entries: Iterable[str] | None = None,
    targets: Iterable[str] | None = None,
) -> tuple[tuple[str, ...], ...]:
    limits = limits or GraphLimits()
    v = validate_graph(graph, limits=limits)
    if not v.valid:
        return ()
    nodes = {n["node_id"]: n for n in graph.get("nodes", [])}
    adj = defaultdict(list)
    for e in graph.get("edges", []):
        adj[e["source"]].append(e)
    for k in adj:
        adj[k].sort(key=lambda e: (e["target"], e["type"], e["edge_id"]))
    starts = list(entries or graph.get("entry_points", [])) or sorted(
        n["node_id"] for n in nodes.values() if n.get("type") in {"ACTOR", "INPUT"}
    )
    goal = set(
        targets or [n["node_id"] for n in nodes.values() if n.get("type") in {"IMPACT", "SINK"}]
    )
    results = []
    states = 0
    for start in sorted(set(starts)):
        queue = deque([(start, (start,), frozenset({start}))])
        while queue and len(results) < limits.max_paths:
            current, path, seen = queue.popleft()
            states += 1
            if states > limits.max_traversal_states:
                return tuple(results)
            if current in goal and len(path) > 1:
                results.append(path)
                continue
            if len(path) >= limits.max_path_length:
                continue
            for edge in adj.get(current, []):
                target = edge["target"]
                if target in seen:
                    continue
                queue.append((target, path + (target,), seen | {target}))
    return tuple(results)


def minimal_security_paths(graph: dict[str, Any], *, limits: GraphLimits | None = None):
    paths = extract_paths(graph, limits=limits)
    nodes = {n["node_id"]: n for n in graph.get("nodes", [])}
    critical = {n for n, v in nodes.items() if v.get("type") in SECURITY_CRITICAL_NODE_TYPES}
    scored = []
    for p in paths:
        preserved = len(set(p) & critical)
        scored.append((-(preserved), len(p), p))
    scored.sort()
    return tuple(item[2] for item in scored[:1]) if scored else ()


def find_alternate_paths(
    graph: dict[str, Any], primary: Iterable[str], *, limits: GraphLimits | None = None
):
    primary = set(primary)
    all_paths = extract_paths(graph, limits=limits)
    return tuple(p for p in all_paths if p != tuple(primary) and not primary.intersection(p[1:-1]))


def compare_graphs(
    expected: dict[str, Any],
    submitted: dict[str, Any],
    *,
    case_id: str | None = None,
    evidence_ids: set[str] | None = None,
    limits: GraphLimits | None = None,
    case_digest: str | None = None,
) -> GraphEvaluation:
    limits = limits or GraphLimits()
    ev = validate_graph(expected, case_id=case_id, evidence_ids=evidence_ids, limits=limits)
    sv = validate_graph(submitted, case_id=case_id, evidence_ids=evidence_ids, limits=limits)
    metrics = (
        calculate_graph_metrics(expected, submitted)
        if sv.valid and ev.valid
        else GraphMetrics(
            _metric(0, 0, len(expected.get("nodes", []))),
            _metric(0, 0, len(expected.get("edges", []))),
            0.0,
            _metric(0, 0, len(expected.get("trust_boundaries", []))),
            0.0,
        )
    )
    return GraphEvaluation(
        sv.valid and ev.valid,
        sv,
        metrics,
        sv.graph_digest,
        ev.graph_digest,
        case_digest,
        {
            "graph_schema_version": GRAPH_SCHEMA_VERSION,
            "evaluator_version": GRAPH_ENGINE_VERSION,
            "normalization_version": NORMALIZATION_VERSION,
            "scoring_version": SCORING_VERSION,
        },
    )


def evaluate_attack_graph(expected: dict[str, Any], submitted: dict[str, Any], **kwargs):
    return compare_graphs(expected, submitted, **kwargs)
