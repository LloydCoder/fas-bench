"""One-time migration helper for stale Phase 3 content digests."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from fas_bench.cases import CASE_IDS,_digest_case,_digest_repository

def repair(root:Path)->int:
 changed=0
 for case_id in CASE_IDS:
  d=root/"cases"/case_id
  meta_path=d/"metadata.json"; case_path=d/"case.json"
  meta=json.loads(meta_path.read_text(encoding="utf-8"))
  case=json.loads(case_path.read_text(encoding="utf-8"))
  artifact=_digest_case(d); repo_digest=_digest_repository(d)
  if meta.get("artifact_digest")!=artifact:
   meta["artifact_digest"]=artifact;changed+=1
  recorded=case.get("repository",{}).get("artifact_digest")
  if isinstance(recorded,dict) and recorded.get("sha256")!=repo_digest:
   recorded["sha256"]=repo_digest;changed+=1
  meta_path.write_text(json.dumps(meta,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
  case_path.write_text(json.dumps(case,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 return changed

if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--root",type=Path,default=Path("."))
 args=p.parse_args();print(f"updated digest fields: {repair(args.root.resolve())}")
