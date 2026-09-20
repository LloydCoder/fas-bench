"""Evidence coverage calculations."""

from __future__ import annotations

from typing import Any

def calculate_coverage(expected: list[dict[str, Any]], submitted: list[dict[str, Any]], verified_ids: set[str]) -> float:
    required = {item["evidence_id"] for item in expected if item.get("role") in {"DIRECT", "SUPPORTING"}}
    if not required:
        return 1.0 if not expected else 0.0
    matched = sum(1 for item in required if item in verified_ids)
    return matched / len(required)
