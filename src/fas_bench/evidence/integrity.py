"""Evidence integrity statistics."""

from __future__ import annotations


def calculate_integrity(submitted: int, invalid: int) -> dict[str, float | int]:
    rate = (invalid / submitted) if submitted else 0.0
    return {
        "submitted": submitted,
        "invalid": invalid,
        "evidence_hallucination_rate": rate,
    }
