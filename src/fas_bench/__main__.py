"""fas-bench validation CLI."""
import argparse,json,sys
from pathlib import Path
from .validation import validate_file
def main(argv=None):
 p=argparse.ArgumentParser(prog="fas-bench"); s=p.add_subparsers(dest="command",required=True); v=s.add_parser("validate"); v.add_argument("path",type=Path); v.add_argument("--schema",required=True); v.add_argument("--semantic",action=argparse.BooleanOptionalAction,default=True); a=p.parse_args(argv)
 r=validate_file(a.path,a.schema,a.semantic); print(json.dumps({"status":r.status,"errors":[e.__dict__ for e in r.errors]},indent=2)); return 0 if r.status=="VALID" else 2
if __name__=="__main__": sys.exit(main())
