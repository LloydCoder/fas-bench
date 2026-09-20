# fmt: off
# ruff: noqa: E701,E702,I001,UP035
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .identity import cache_identity, canonical_json


class EvaluationCache:
    """Content-addressed cache. Candidate-controlled content is never a key by itself."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def key(self, *, benchmark_digest: str, case_digest: str, submission_digest: str,
            evaluator_digest: str, scoring_digest: str, environment_digest: str,
            execution_policy_digest: str) -> str:
        return cache_identity(
            benchmark_digest=benchmark_digest,
            case_digest=case_digest,
            submission_digest=submission_digest,
            evaluator_digest=evaluator_digest,
            scoring_digest=scoring_digest,
            environment_digest=environment_digest,
            execution_policy_digest=execution_policy_digest,
        )

    def _path(self, key: str) -> Path:
        if len(key) != 64 or any(c not in "0123456789abcdef" for c in key):
            raise ValueError("invalid cache key")
        return self.root / f"{key}.json"

    def get(self, key: str) -> dict[str, Any] | None:
        path = self._path(key)
        try:
            with path.open("rb") as handle:
                return json.loads(handle.read().decode("utf-8"))
        except (OSError, ValueError, json.JSONDecodeError):
            return None

    def put(self, key: str, value: dict[str, Any]) -> None:
        path = self._path(key)
        tmp = path.with_suffix(".tmp")
        data = canonical_json(value)
        with tmp.open("wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
