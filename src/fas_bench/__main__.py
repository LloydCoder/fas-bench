"""fas-bench validation CLI."""
import argparse, json, sys
from pathlib import Path
from .cases import reproduce_all, validate_all
from .validation import validate_file

def main(argv=None):
    parser=argparse.ArgumentParser(prog="fas-bench")
    subs=parser.add_subparsers(dest="command",required=True)
    p=subs.add_parser("validate"); p.add_argument("path",type=Path); p.add_argument("--schema",required=True); p.add_argument("--semantic",action=argparse.BooleanOptionalAction,default=True)
    cases=subs.add_parser("cases"); csub=cases.add_subparsers(dest="cases_command",required=True)
    va=csub.add_parser("validate-all"); va.add_argument("--reproduce",action="store_true")
    vg=csub.add_parser("validate-gold"); vg.add_argument("--reproduce",action="store_true")
    rp=csub.add_parser("reproduce"); rp.add_argument("case_id")
    args=parser.parse_args(argv)
    if args.command=="validate":
        r=validate_file(args.path,args.schema,args.semantic); print(json.dumps({"status":r.status,"errors":[e.__dict__ for e in r.errors]},indent=2)); return 0 if r.status=="VALID" else 2
    if args.cases_command=="validate-all":
        r=validate_all(); 
        if args.reproduce: r["reproduction"]=reproduce_all()
        print(json.dumps(r,indent=2)); return 0 if r["status"]=="PASS" and (not args.reproduce or r["reproduction"]["status"]=="PASS") else 2
    if args.cases_command=="validate-gold":
        r=validate_all(); gold=reproduce_all(["FAS-001","FAS-002","FAS-006","FAS-016","FAS-020"]) if args.reproduce else None
        out={"status":"PASS" if r["status"]=="PASS" and (gold is None or gold["status"]=="PASS") else "FAIL","corpus":r,"gold":gold}
        print(json.dumps(out,indent=2)); return 0 if out["status"]=="PASS" else 2
    r=reproduce_all([args.case_id]); print(json.dumps(r,indent=2)); return 0 if r["status"]=="PASS" else 2
if __name__=="__main__": sys.exit(main())
