"""Unified console entrypoint preserving the pre-Phase-10 CLI."""

from __future__ import annotations

import sys

PHASE10_COMMANDS = {
    "cases",
    "corpus",
    "benchmark",
    "release",
    "contamination",
    "health",
    "report-release",
}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in PHASE10_COMMANDS:
        from .phase10_cli import main as phase10_main
        return phase10_main(argv)
    from .__main__ import main as legacy_main
    return legacy_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
