# fmt: off
# ruff: noqa: E701,E702,I001,UP035
from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable


@dataclass(frozen=True)
class ArtifactRecord:
    path: str
    type: str
    size: int
    sha256: str
    producer: str
    trust_level: str


class ArtifactSecurityError(ValueError):
    pass


def _safe_rel(path: Path, root: Path) -> str:
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError as exc:
        raise ArtifactSecurityError("artifact escaped output root") from exc
    p = PurePosixPath(rel)
    if not rel or p.is_absolute() or ".." in p.parts or any(part == "" for part in p.parts):
        raise ArtifactSecurityError("unsafe artifact path")
    return rel


def collect_artifacts(root: Path, *, max_files: int, max_bytes: int,
                      producer: str = "candidate", trust_level: str = "UNTRUSTED") -> tuple[ArtifactRecord, ...]:
    root = root.resolve()
    if not root.is_dir():
        raise ArtifactSecurityError("output root is missing")
    rows: list[ArtifactRecord] = []
    total = 0
    for path in sorted(root.rglob("*"), key=lambda p: p.as_posix()):
        rel = _safe_rel(path, root)
        info = path.lstat()
        mode = info.st_mode
        if stat.S_ISLNK(mode) or stat.S_ISSOCK(mode) or stat.S_ISFIFO(mode) or stat.S_ISCHR(mode) or stat.S_ISBLK(mode):
            raise ArtifactSecurityError(f"unsupported artifact type: {rel}")
        if not stat.S_ISREG(mode):
            continue
        size = info.st_size
        total += size
        if len(rows) >= max_files or total > max_bytes:
            raise ArtifactSecurityError("artifact limits exceeded")
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
        rows.append(ArtifactRecord(rel, "file", size, digest.hexdigest(), producer, trust_level))
    return tuple(rows)


def manifest_digest(records: Iterable[ArtifactRecord]) -> str:
    payload = [
        asdict(item)
        for item in sorted(records, key=lambda x: x.path)
    ]
    return hashlib.sha256(
        __import__("json").dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
