# fmt: off
"""Deterministic identities shared by the secure evaluator."""
from __future__ import annotations
from typing import Any
from ..canonical import canonical_json, digest_json

def sha256_bytes(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()

def digest_document(value: Any) -> str:
    return digest_json(value)

def run_identity(*, benchmark_digest: str, case_manifest_digest: str, submission_digest: str,
                 evaluator_digest: str, scoring_digest: str, environment_digest: str,
                 execution_policy_digest: str, seed: int | None = None) -> str:
    return digest_document({
        "benchmark_digest": benchmark_digest, "case_manifest_digest": case_manifest_digest,
        "submission_digest": submission_digest, "evaluator_digest": evaluator_digest,
        "scoring_digest": scoring_digest, "environment_digest": environment_digest,
        "execution_policy_digest": execution_policy_digest, "seed": seed,
    })

def cache_identity(**inputs: str) -> str:
    return digest_document(inputs)
