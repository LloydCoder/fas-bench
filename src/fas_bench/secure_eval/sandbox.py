# fmt: off
# ruff: noqa: E701,E702,I001,UP035
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SandboxLayout:
    root: Path
    input: Path
    output: Path
    workspace: Path
    logs: Path
    metadata: Path

    @classmethod
    def create(cls, root: Path) -> SandboxLayout:
        root = Path(root)
        layout = cls(root, root / "input", root / "output", root / "workspace", root / "logs", root / "metadata")
        for path in (layout.input, layout.output, layout.workspace, layout.logs, layout.metadata):
            path.mkdir(parents=True, exist_ok=True)
        return layout

    def paths(self) -> tuple[Path, ...]:
        return (self.root, self.input, self.output, self.workspace, self.logs, self.metadata)


def assert_inside(path: Path, root: Path) -> Path:
    resolved_root = Path(root).resolve()
    resolved = Path(path).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("path escapes sandbox root") from exc
    return resolved
