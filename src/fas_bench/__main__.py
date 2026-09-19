"""fas-bench validation CLI."""
import argparse
import json
import sys
from pathlib import Path

from .cases import reproduce_all, validate_all
from .validation import validate_file


def main(argv=None):
    parser = argparse.ArgumentParser(prog="fas-bench")
    subs = parser.add_subparsers(dest="command", required=True)

    validate_parser = subs.add_parser("validate")
    validate_parser.add_argument("path", type=Path)
    validate_parser.add_argument("--schema", required=True)
    validate_parser.add_argument(
        "--semantic", action=argparse.BooleanOptionalAction, default=True
    )

    cases = subs.add_parser("cases")
    csub = cases.add_subparsers(dest="cases_command", required=True)
    va = csub.add_parser("validate-all")
    va.add_argument("--reproduce", action="store_true")
    vg = csub.add_parser("validate-gold")
    vg.add_argument("--reproduce")
    rp = csub.add_parser("reproduce")
    rp.add_argument("case_id")

    args = parser.parse_args(argv)

    if args.command == "validate":
        result = validate_file(args.path, args.schema, args.semantic)
        print(
            json.dumps(
                {
                    "status": result.status,
                    "errors": [error.__dict__ for error in result.errors],
                },
                indent=2,
            )
        )
        return 0 if result.status == "VALID" else 2

    if args.cases_command == "validate-all":
        result = validate_all()
        if args.reproduce:
            result["reproduction"] = reproduce_all()
        ok = result["status"] == "PASS"
        ok = ok and (
            not args.reproduce or result["reproduction"]["status"] == "PASS"
        )
        print(json.dumps(result, indent=2))
        return 0 if ok else 2

    if args.cases_command == "validate-gold":
        result = validate_all()
        gold = (
            reproduce_all(["FAS-001", "FAS-002", "FAS-006", "FAS-016", "FAS-020"])
            if args.reproduce
            else None
        )
        output = {
            "status": "PASS"
            if result["status"] == "PASS"
            and (gold is None or gold["status"] == "PASS")
            else "FAIL",
            "corpus": result,
            "gold": gold,
        }
        print(json.dumps(output, indent=2))
        return 0 if output["status"] == "PASS" else 2

    result = reproduce_all([args.case_id])
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
