"""Single authoritative deterministic canonical JSON implementation."""
from __future__ import annotations
import dataclasses, json
from enum import Enum
from typing import Any

def _default(value: Any) -> Any:
    if isinstance(value, bytes):
        import hashlib
        return {"__bytes_sha256__": hashlib.sha256(value).hexdigest(), "size": len(value)}
    if isinstance(value, Enum):
        return value.value
    if dataclasses.is_dataclass(value):
        return dataclasses.asdict(value)
    raise TypeError(f"unsupported canonical value: {type(value)!r}")

def canonical_json(value: Any) -> bytes:
    """Canonical UTF-8 JSON; rejects NaN/Infinity and preserves array order."""
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                       allow_nan=False, default=_default) + "\n").encode("utf-8")

def digest_json(value: Any) -> str:
    import hashlib
    return hashlib.sha256(canonical_json(value)).hexdigest()
