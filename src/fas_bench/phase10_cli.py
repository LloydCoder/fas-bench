"""Phase 10 command surface. All outputs are deterministic JSON unless noted."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .cases import reproduce_all, validate_all
from .mutations import generate_identifier_mutation
from .phase10 import (
    benchmark_health,
    build_release_manifest,
    corpus_stats,
    independence_audit,
    public_report,
    scan_leakage,
    validate_case_phase10,
    validate_corpus,
    validate_release_manifest,
)


def _dump(value, path=None):
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if path:
        Path(path).write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="fas-bench")
    subs = parser.add_subparsers(dest="command", required=True)

    cases = subs.add_parser("cases")
    cs = cases.add_subparsers(dest="sub", required=True)
    validate = cs.add_parser("validate")
    validate.add_argument("case_id")
    verify = cs.add_parser("verify")
    verify.add_argument("case_id")
    validate_all_parser = cs.add_parser("validate-all")
    validate_all_parser.add_argument("--reproduce", action="store_true")
    validate_gold = cs.add_parser("validate-gold")
    validate_gold.add_argument("--reproduce", action="store_true")
    reproduce = cs.add_parser("reproduce")
    reproduce.add_argument("case_id")
    mutate = cs.add_parser("mutate")
    mutate.add_argument("case_id")
    mutate.add_argument("--file", type=Path, required=True)

    corpus = subs.add_parser("corpus")
    co = corpus.add_subparsers(dest="sub", required=True)
    co.add_parser("validate")
    co.add_parser("stats")

    benchmark = subs.add_parser("benchmark")
    bo = benchmark.add_subparsers(dest="sub", required=True)
    bo.add_parser("doctor")
    bo.add_parser("validate")
    release = bo.add_parser("release")
    release.add_argument("--version", required=True)
    release.add_argument("--channel", default="development")
    reproduce_release = bo.add_parser("reproduce")
    reproduce_release.add_argument("manifest", type=Path)

    rel = subs.add_parser("release")
    ro = rel.add_subparsers(dest="sub", required=True)
    rv = ro.add_parser("verify")
    rv.add_argument("manifest", type=Path)

    contam = subs.add_parser("contamination")
    co2 = contam.add_subparsers(dest="sub", required=True)
    co2.add_parser("scan")
    co2.add_parser("independence")

    subs.add_parser("health")
    report = subs.add_parser("report-release")
    report.add_argument("manifest", type=Path)

    args = parser.parse_args(argv)
    root = Path.cwd()

    if args.command == "cases":
        if args.sub in {"validate", "verify"}:
            result = validate_case_phase10(args.case_id)
            ok = result.get("status") == "PASS"
        elif args.sub == "validate-all":
            result = validate_corpus() if not args.reproduce else {
                "phase10": validate_corpus(),
                "legacy_reproduction": reproduce_all(),
            }
            ok = result.get("status") == "PASS" if not args.reproduce else (
                result["phase10"]["status"] == "PASS"
                and result["legacy_reproduction"]["status"] == "PASS"
            )
        elif args.sub == "validate-gold":
            result = validate_corpus()
            gold = ["FAS-001", "FAS-002", "FAS-006", "FAS-016", "FAS-020"]
            result["gold"] = [validate_case_phase10(case_id) for case_id in gold]
            if args.reproduce:
                result["gold_reproduction"] = reproduce_all(gold)
            ok = result["status"] == "PASS" and all(
                item["status"] == "PASS" for item in result["gold"]
            ) and (not args.reproduce or result["gold_reproduction"]["status"] == "PASS")
        elif args.sub == "reproduce":
            result = reproduce_all([args.case_id])
            ok = result["status"] == "PASS"
        else:
            result = generate_identifier_mutation(
                args.case_id, args.file.read_text(encoding="utf-8")
            ).__dict__
            ok = result.get("validation_status") == "VALIDATED"
        _dump(result)
        return 0 if ok else 1

    if args.command == "corpus":
        result = validate_corpus() if args.sub == "validate" else corpus_stats()
        _dump(result)
        return 0 if args.sub == "stats" or result.get("status") == "PASS" else 1

    if args.command == "benchmark":
        if args.sub == "doctor":
            result = benchmark_health(root)
        elif args.sub == "validate":
            result = validate_corpus()
        elif args.sub == "release":
            try:
                result = build_release_manifest(root, args.version, channel=args.channel)
            except Exception as exc:
                _dump({"status": "FAIL", "error": str(exc)})
                return 1
        else:
            manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
            result = validate_release_manifest(root, manifest)
        _dump(result)
        return 0 if result.get("status") in {"PASS", "VALIDATED"} or "release_digest" in result else 1

    if args.command == "release":
        result = validate_release_manifest(
            root, json.loads(args.manifest.read_text(encoding="utf-8"))
        )
        _dump(result)
        return 0 if result["status"] == "PASS" else 1

    if args.command == "contamination":
        result = scan_leakage(root / "cases") if args.sub == "scan" else independence_audit(root)
        _dump(result)
        return 0 if result["status"] == "PASS" else 1

    if args.command == "health":
        _dump(benchmark_health(root))
        return 0

    if args.command == "report-release":
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        _dump(public_report(manifest, corpus_stats(), benchmark_health(root)))
        return 0

    return 2
