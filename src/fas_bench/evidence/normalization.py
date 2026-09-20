"""Canonical evidence normalization and identity."""

from __future__ import annotations

import hashlib
import json
import posixpath
from copy import deepcopy
from typing import Any


def normalize_path(value: str) -> str:
    if not isinstance(value, str) or not value:
        return value
    value = value.replace("\\", "/")
    normalized = posixpath.normpath(value)
    if normalized == ".":
        return ""
    if normalized.startswith("./"):
        return normalized[2:]
    return normalized


def _normalize(value: Any, key: str | None = None) -> Any:
    if isinstance(value, dict):
        return {k: _normalize(value[k], k) for k in sorted(value)}
    if isinstance(value, list):
        normalized = [_normalize(item, key) for item in value]
        if key in {
            "related_claims",
            "related_findings",
            "related_nodes",
            "related_edges",
            "related_paths",
            "related_remediations",
        }:
            return sorted(normalized)
        return normalized
    if isinstance(value, str):
        if key in {"file", "path", "artifact_path"}:
            return normalize_path(value)
        return value.replace("\r\n", "\n").replace("\r", "\n")
    return value


def normalize_evidence(evidence: dict[str, Any]) -> dict[str, Any]:
    """Return a copy normalized only for semantically irrelevant representation."""
    return _normalize(deepcopy(evidence))


def canonical_evidence(evidence: dict[str, Any]) -> bytes:
    normalized = normalize_evidence(evidence)
    return json.dumps(
        normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def evidence_identity(evidence: dict[str, Any]) -> str:
    """Stable SHA-256 identity over canonical evidence semantics, excluding presentation IDs."""
    normalized = normalize_evidence(evidence)
    for field in ("evidence_id", "description", "verification", "observed_at"):
        normalized.pop(field, None)
    return hashlib.sha256(
        json.dumps(
            normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    ).hexdigest()
