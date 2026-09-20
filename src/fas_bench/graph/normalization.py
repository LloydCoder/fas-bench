"""Conservative, deterministic graph normalization and canonical serialization."""
from __future__ import annotations
import json
import re
import unicodedata
from typing import Any

_WS = re.compile(r"\\s+")


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).strip()
    return _WS.sub(" ", value)


def normalize_path(value: str) -> str:
    value = normalize_text(value).replace("\\\\", "/")
    return value


def normalize_name(value: str) -> str:
    value = normalize_text(value)
    return value.casefold()


def normalize_identity(node: dict[str, Any]) -> str:
    attrs = node.get("attributes") or {}
    explicit = attrs.get("canonical_identity")
    if isinstance(explicit, str) and explicit.strip():
        return normalize_text(explicit)
    reference = node.get("reference")
    if isinstance(reference, str) and reference.strip():
        return normalize_path(reference)
    location = node.get("location") or {}
    file_name = location.get("file")
    symbol = location.get("symbol")
    if file_name or symbol:
        parts = [normalize_path(str(file_name)) if file_name else "", normalize_text(str(symbol)) if symbol else ""]
        return "::".join(parts).strip(":")
    return normalize_name(str(node.get("name", "")))


def node_key(node: dict[str, Any]) -> tuple[str, str]:
    return (str(node.get("type", "")), normalize_identity(node))


def _normalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _normalize_value(value[k]) for k in sorted(value)}
    if isinstance(value, list):
        normalized = [_normalize_value(v) for v in value]
        return sorted(normalized, key=lambda v: json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
    if isinstance(value, str):
        return normalize_text(value)
    return value


def canonicalize_graph(graph: dict[str, Any]) -> dict[str, Any]:
    result = _normalize_value(graph)
    result["nodes"] = sorted(result.get("nodes", []), key=lambda n: (node_key(n), n.get("node_id", "")))
    result["edges"] = sorted(result.get("edges", []), key=lambda e: (e.get("type", ""), e.get("source", ""), e.get("target", ""), e.get("edge_id", "")))
    result["paths"] = sorted(result.get("paths", []), key=lambda p: p.get("path_id", ""))
    result["trust_boundaries"] = sorted(result.get("trust_boundaries", []), key=lambda b: b.get("boundary_id", ""))
    return result


def canonical_json(graph: dict[str, Any]) -> bytes:
    return json.dumps(canonicalize_graph(graph), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
