"""Controlled case digest reconciliation helper."""
from __future__ import annotations
import json
from pathlib import Path
from fas_bench.cases import CASE_IDS,_digest_case,_digest_repository
def repair(root:Path)->None:
 for case_id in CASE_IDS:
  d=root/"cases"/case_id
  mp=d/"metadata.json";cp=d/"case.json"
  meta=json.loads(mp.read_text(encoding="utf-8"));case=json.loads(cp.read_text(encoding="utf-8"))
  meta["artifact_digest"]=_digest_case(d)
  if isinstance(case.get("repository",{}).get("artifact_digest"),dict):
   case["repository"]["artifact_digest"]["sha256"]=_digest_repository(d)
  mp.write_text(json.dumps(meta,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
  cp.write_text(json.dumps(case,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
if __name__=="__main__": repair(Path(".").resolve())
