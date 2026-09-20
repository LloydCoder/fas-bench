"""fas-bench validation CLI."""

import argparse
import json
import sys
from pathlib import Path

from .cases import reproduce_all, validate_all
from .evaluator import evaluate_submission as evaluate_finding_submission
from .evaluator.errors import EvaluatorCaseError, EvaluatorInternalError, EvaluatorSubmissionError
from .evidence import evaluate_submission as evaluate_evidence_submission
from .graph import canonicalize_graph, compare_graphs, diff_graphs, extract_paths, graph_digest, validate_graph
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

    evaluate_parser = subparsers.add_parser("evaluate")
    evaluate_subparsers = evaluate_parser.add_subparsers(dest="evaluate_command", required=True)
    finding_parser = evaluate_subparsers.add_parser("finding")
    finding_parser.add_argument("--case", dest="case_id", required=True)
    finding_parser.add_argument("--submission", type=Path, required=True)
    finding_parser.add_argument("--cases-root", type=Path)
    finding_parser.add_argument("--output", type=Path)
    finding_parser.add_argument("--json", action="store_true")
    finding_parser.add_argument("--strict", action="store_true")

    graph_parser = subparsers.add_parser("graph")
    graph_subparsers = graph_parser.add_subparsers(dest="graph_command", required=True)
    graph_validate = graph_subparsers.add_parser("validate")
    graph_validate.add_argument("graph", type=Path)
    graph_validate.add_argument("--case")
    graph_validate.add_argument("--json", action="store_true")
    graph_normalize = graph_subparsers.add_parser("normalize")
    graph_normalize.add_argument("graph", type=Path)
    graph_normalize.add_argument("--output", type=Path)
    graph_digest_parser = graph_subparsers.add_parser("digest")
    graph_digest_parser.add_argument("graph", type=Path)
    graph_paths = graph_subparsers.add_parser("paths")
    graph_paths.add_argument("graph", type=Path)
    graph_paths.add_argument("--json", action="store_true")
    graph_diff = graph_subparsers.add_parser("diff")
    graph_diff.add_argument("before", type=Path)
    graph_diff.add_argument("after", type=Path)
    graph_diff.add_argument("--json", action="store_true")
    graph_compare = graph_subparsers.add_parser("compare")
    graph_compare.add_argument("--expected", type=Path, required=True)
    graph_compare.add_argument("--submission", type=Path, required=True)
    graph_compare.add_argument("--case")
    graph_compare.add_argument("--json", action="store_true")

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
            result = evaluate_evidence_submission(args.submission, args.cases_root)
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

    if args.command == "evaluate" and args.evaluate_command == "finding":
        try:
            result = evaluate_finding_submission(args.submission, args.cases_root)
            payload = result.as_dict()
            if args.case_id != payload["case_id"]:
                raise EvaluatorSubmissionError(
                    "SUBMISSION_ERROR: submission case_id does not match --case"
                )
            rendered = json.dumps(payload, indent=2, sort_keys=True)
            if args.output:
                args.output.write_text(rendered + "\\n", encoding="utf-8")
            if args.json or not args.output:
                print(rendered)
            else:
                verdict = payload["verdict_evaluation"]
                print(
                    f"Finding evaluation: case={payload['case_id']} "
                    f"verdict={verdict['submitted']} "
                    f"correct={verdict['verdict_correct']} "
                    f"supported={verdict['verdict_supported']}"
                )
            if args.strict and not (
                payload["verdict_evaluation"]["verdict_correct"]
                and payload["verdict_evaluation"]["verdict_supported"]
                and payload["finding_evaluation"]["matched"]
            ):
                return 3
            return 0
        except (EvaluatorCaseError, EvaluatorSubmissionError) as exc:
            print(json.dumps({"status": "ERROR", "error": str(exc)}, indent=2))
            return 2
        except EvaluatorInternalError as exc:
            print(json.dumps({"status": "EVALUATOR_ERROR", "error": str(exc)}, indent=2))
            return 4

    if args.command == "graph":
        try:
            if args.graph_command in {"validate", "normalize", "digest", "paths"}:
                document = json.loads(args.graph.read_text(encoding="utf-8"))
            if args.graph_command == "validate":
                payload = validate_graph(document, case_id=args.case).as_dict()
            elif args.graph_command == "normalize":
                payload = canonicalize_graph(document)
                if args.output:
                    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                    return 0
            elif args.graph_command == "digest":
                payload = {"graph_digest": graph_digest(document)}
            elif args.graph_command == "paths":
                payload = {"paths": [list(path) for path in extract_paths(document)]}
            elif args.graph_command == "diff":
                before = json.loads(args.before.read_text(encoding="utf-8"))
                after = json.loads(args.after.read_text(encoding="utf-8"))
                payload = diff_graphs(before, after)
            else:
                expected = json.loads(args.expected.read_text(encoding="utf-8"))
                submission = json.loads(args.submission.read_text(encoding="utf-8"))
                payload = compare_graphs(expected, submission, case_id=args.case).as_dict()
            print(json.dumps(payload, indent=2, sort_keys=True))
            if args.graph_command in {"validate", "compare"} and payload.get("valid") is False:
                return 2
            return 0
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(json.dumps({"status": "ERROR", "error": str(exc)}, indent=2))
            return 2

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
