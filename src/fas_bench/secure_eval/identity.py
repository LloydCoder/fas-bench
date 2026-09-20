# fmt: off
# ruff: noqa: E701,E702,I001,UP035
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from typing import Any


def canonical_json(value: Any) -> bytes:
    if is_dataclass(value):
        value = asdict(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=_default).encode("utf-8")


def _default(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"__bytes_sha256__": hashlib.sha256(value).hexdigest(), "size": len(value)}
    if hasattr(value, "value"):
        return value.value
    raise TypeError(f"unsupported canonical value: {type(value)!r}")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_document(value: Any) -> str:
    return sha256_bytes(canonical_json(value))


def run_identity(*, benchmark_digest: str, case_manifest_digest: str, submission_digest: str,
                 evaluator_digest: str, scoring_digest: str, environment_digest: str,
                 execution_policy_digest: str, seed: int | None = None) -> str:
    return digest_document({
        "benchmark_digest": benchmark_digest,
        "case_manifest_digest": case_manifest_digest,
        "submission_digest": submission_digest,
        "evaluator_digest": evaluator_digest,
        "scoring_digest": scoring_digest,
        "environment_digest": environment_digest,
        "execution_policy_digest": execution_policy_digest,
        "seed": seed,
    })


def cache_identity(**inputs: str) -> str:
    return digest_document(inputs)
