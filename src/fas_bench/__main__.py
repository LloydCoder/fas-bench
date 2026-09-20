"""fas-bench validation CLI."""

import argparse
import json
import sys
from pathlib import Path

from .cases import reproduce_all, validate_all
from .evidence import evaluate_submission
from .validation import validate_file


def main(argv=None):
    parser = argparse.ArgumentParser(prog="fas-bench")
    subparsers = parser.add_subparsers(dest="command", required=True)

    evidence_parser = subparsers.add_parser("evidence")
    evidence_subparsers = evidence_parser.add_subparsers(dest="evidence_command", required=True)
    evidence_validate = evidence_subparsers.add_parser("validate")
    evidence_validate.add_argument("submission", type=Path)
    evidence_validate.add_argument("--case", dest="case_id")
    evidence_validate.add_argument("--cases-root", type=Path)
    evidence_validate.add_argument("--output", type=Path)
    evidence_validate.add_argument("--json", action="store_true")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("path", type=Path)
    validate_parser.add_argument("--schema", required=True)
    validate_parser.add_argument("--semantic", action=argparse.BooleanOptionalAction, default=True)

    cases_parser = subparsers.add_parser("cases")
    cases_subparsers = cases_parser.add_subparsers(dest="cases_command", required=True)
    validate_all_parser = cases_subparsers.add_parser("validate-all")
    validate_all_parser.add_argument("--reproduce", action="store_true")
    validate_gold_parser = cases_subparsers.add_parser("validate-gold")
    validate_gold_parser.add_argument("--reproduce", action="store_true")
    reproduce_parser = cases_subparsers.add_parser("reproduce")
    reproduce_parser.add_argument("case_id")

    args = parser.parse_args(argv)

    if args.command == "evidence" and args.evidence_command == "validate":
        try:
            result = evaluate_submission(args.submission, args.cases_root)
            if args.case_id and result["case_id"] != args.case_id:
                raise ValueError("submission case_id does not match --case")
        except Exception as exc:
            print(json.dumps({"status": "ERROR", "error": str(exc)}, indent=2))
            return 2
        payload = json.dumps(result, indent=2, sort_keys=True)
        if args.output:
            args.output.write_text(payload + "\\n", encoding="utf-8")
        if args.json or not args.output:
            print(payload)
        else:
            print(
                f"Evidence verification: case={result['case_id']} "
                f"coverage={result['coverage']:.3f} "
                f"integrity={result['evidence_hallucination_rate']:.3f}"
            )
        return 0

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
        if args.reproduce:
            ok = ok and result["reproduction"]["status"] == "PASS"
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
            "status": (
                "PASS"
                if result["status"] == "PASS" and (gold is None or gold["status"] == "PASS")
                else "FAIL"
            ),
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
