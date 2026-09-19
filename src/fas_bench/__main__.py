"""fas-bench validation CLI."""

import argparse
import json
import sys
from pathlib import Path

from .validation import validate_file


def main(argv=None):
    parser = argparse.ArgumentParser(prog="fas-bench")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("path", type=Path)
    validate_parser.add_argument("--schema", required=True)
    validate_parser.add_argument(
        "--semantic", action=argparse.BooleanOptionalAction, default=True
    )
    args = parser.parse_args(argv)

    result = validate_file(args.path, args.schema, args.semantic)
    print(
        json.dumps(
            {"status": result.status, "errors": [error.__dict__ for error in result.errors]},
            indent=2,
        )
    )
    return 0 if result.status == "VALID" else 2


if __name__ == "__main__":
    sys.exit(main())
