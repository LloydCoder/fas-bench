"""Phase 10 command surface. All outputs are deterministic JSON unless noted."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .mutations import formatting_mutation, generate_identifier_mutation
from .phase10 import (
    CASES_ROOT, PHASE10_VERSION, build_release_manifest, benchmark_health,
    corpus_stats, independence_audit, public_report, scan_leakage,
    validate_case_phase10, validate_corpus, validate_release_manifest,
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
    v = cs.add_parser("validate"); v.add_argument("case_id")
    verify = cs.add_parser("verify"); verify.add_argument("case_id")
    mutate = cs.add_parser("mutate"); mutate.add_argument("case_id"); mutate.add_argument("--file", type=Path, required=True)
    corpus = subs.add_parser("corpus")
    co = corpus.add_subparsers(dest="sub", required=True)
    co.add_parser("validate")
    co.add_parser("stats")
    doctor = subs.add_parser("benchmark")
    bo = doctor.add_subparsers(dest="sub", required=True)
    bo.add_parser("doctor"); bo.add_parser("validate")
    release = bo.add_parser("release")
    release.add_argument("--version", required=True); release.add_argument("--channel", default="development")
    reproduce = bo.add_parser("reproduce")
    reproduce.add_argument("manifest", type=Path)
    rel = subs.add_parser("release")
    ro = rel.add_subparsers(dest="sub", required=True)
    rv = ro.add_parser("verify"); rv.add_argument("manifest", type=Path)
    contam = subs.add_parser("contamination")
    co2 = contam.add_subparsers(dest="sub", required=True)
    co2.add_parser("scan"); co2.add_parser("independence")
    health = subs.add_parser("health")
    report = subs.add_parser("report-release")
    report.add_argument("manifest", type=Path)
    args = parser.parse_args(argv)
    root = Path.cwd()
    if args.command == "cases":
        result = validate_case_phase10(args.case_id) if args.sub in {"validate", "verify"} else None
        if args.sub == "mutate":
            source = args.file.read_text(encoding="utf-8")
            result = generate_identifier_mutation(args.case_id, source).__dict__
        _dump(result); return 0 if result and result.get("status", "VALIDATED") in {"PASS", "VALIDATED"} else 1
    if args.command == "corpus":
        result = validate_corpus() if args.sub == "validate" else corpus_stats()
        _dump(result); return 0 if result.get("status", "PASS") == "PASS" else 1
    if args.command == "benchmark":
        if args.sub == "doctor":
            result = benchmark_health(root)
        elif args.sub == "validate":
            result = validate_corpus()
        elif args.sub == "release":
            try:
                result = build_release_manifest(root, args.version, channel=args.channel)
            except Exception as exc:
                _dump({"status": "FAIL", "error": str(exc)}); return 1
        else:
            manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
            result = validate_release_manifest(root, manifest)
        _dump(result); return 0 if result.get("status") in {"PASS", "VALIDATED"} or "release_digest" in result else 1
    if args.command == "release" and args.sub == "verify":
        result = validate_release_manifest(root, json.loads(args.manifest.read_text(encoding="utf-8")))
        _dump(result); return 0 if result["status"] == "PASS" else 1
    if args.command == "contamination":
        result = scan_leakage(root / "cases") if args.sub == "scan" else independence_audit(root)
        _dump(result); return 0 if result["status"] == "PASS" else 1
    if args.command == "health":
        result = benchmark_health(root); _dump(result); return 0
    if args.command == "report-release":
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        result = public_report(manifest, corpus_stats(), benchmark_health(root))
        _dump(result); return 0
    return 2
