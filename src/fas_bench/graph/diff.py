"""Deterministic graph snapshot diffing."""
from __future__ import annotations
from typing import Any
from .normalization import canonicalize_graph, node_key


def _index(items, key):
    return {item[key]: item for item in items}


def diff_graphs(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    a, b = canonicalize_graph(before), canonicalize_graph(after)
    an, bn = _index(a.get("nodes", []), "node_id"), _index(b.get("nodes", []), "node_id")
    ae, be = _index(a.get("edges", []), "edge_id"), _index(b.get("edges", []), "edge_id")
    added_nodes = sorted(set(bn) - set(an)); removed_nodes = sorted(set(an) - set(bn))
    added_edges = sorted(set(be) - set(ae)); removed_edges = sorted(set(ae) - set(be))
    changed_nodes = sorted(k for k in set(an) & set(bn) if an[k] != bn[k])
    changed_edges = sorted(k for k in set(ae) & set(be) if ae[k] != be[k])
    return {"added_nodes": added_nodes, "removed_nodes": removed_nodes, "added_edges": added_edges, "removed_edges": removed_edges, "changed_nodes": changed_nodes, "changed_edges": changed_edges, "node_identity_changes": sorted([{"before": k, "after": node_key(bn[k])} for k in set(an)&set(bn) if node_key(an[k]) != node_key(bn[k])], key=lambda x: x["before"])}
