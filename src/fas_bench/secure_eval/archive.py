from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath

MAX_FILES = 4096
MAX_PATH = 4096


def safe_relative_path(name: str) -> str:
    if not isinstance(name, str) or not name or len(name) > MAX_PATH:
        raise ValueError("invalid archive path")
    p = PurePosixPath(name.replace("\\", "/"))
    if p.is_absolute() or ".." in p.parts or any(x == "" for x in p.parts):
        raise ValueError("path traversal or empty archive component")
    if ":" in p.parts[0]:
        raise ValueError("drive-qualified path forbidden")
    return str(p)


def write_inputs(root: Path, files: dict[str, bytes], limit: int) -> str:
    if len(files) > MAX_FILES:
        raise ValueError("too many input files")
    total = 0
    d = hashlib.sha256()
    for name in sorted(files):
        rel = safe_relative_path(name)
        data = files[name]
        if not isinstance(data, bytes):
            raise TypeError("input content must be bytes")
        total += len(data)
        if total > limit:
            raise ValueError("input workspace exceeds limit")
        d.update(rel.encode() + b"\0" + hashlib.sha256(data).digest())
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        os.chmod(target, 0o444)
    return d.hexdigest()


def hash_tree(root: Path):
    rows = []
    for p in sorted(x for x in root.rglob("*") if x.is_file()):
        b = p.read_bytes()
        rows.append((p.relative_to(root).as_posix(), hashlib.sha256(b).hexdigest(), len(b)))
    return tuple(rows)
