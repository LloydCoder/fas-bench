"""Offline JSON Schema and semantic validation."""
from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator,FormatChecker
from referencing import Registry,Resource
from .contract import BENCHMARK_VERSION,SCHEMA_VERSION,CASE_IDS
PACKAGE_ROOT=Path(__file__).resolve().parent
ROOT=PACKAGE_ROOT.parents[1]
SCHEMA_ROOT=PACKAGE_ROOT/"schemas" if (PACKAGE_ROOT/"schemas").exists() else ROOT/"schemas"
FAMILY_PATHS={k:SCHEMA_ROOT/f"{k}/v0.1/{k}.schema.json" for k in ("case","claim","evidence","attack-graph","verdict","remediation","submission","evaluation-result")}
@dataclass(frozen=True)
class ValidationErrorDetail:
 code:str; path:str; message:str; schema_location:str|None=None; instance_location:str|None=None
@dataclass(frozen=True)
class ValidationResult:
 status:str; errors:tuple[ValidationErrorDetail,...]=()
def load_schema(family:str)->dict[str,Any]:
 if family not in FAMILY_PATHS: raise ValueError(f"Unsupported schema family: {family}")
 return json.loads(FAMILY_PATHS[family].read_text(encoding="utf-8"))
def _registry():
 r=Registry()
 for p in [SCHEMA_ROOT/"common/v0.1/common.schema.json",*FAMILY_PATHS.values()]:
  d=json.loads(p.read_text(encoding="utf-8")); r=r.with_resource(d["$id"],Resource.from_contents(d))
 return r
def validate_instance(doc,family):
 s=load_schema(family)
 try: Draft202012Validator.check_schema(s)
 except Exception as e: return ValidationResult("SCHEMA_INVALID",(ValidationErrorDetail("SCHEMA_INVALID","$",str(e)),))
 v=Draft202012Validator(s,registry=_registry(),format_checker=FormatChecker())
 es=tuple(sorted(v.iter_errors(doc),key=lambda e:list(e.absolute_path)))
 return ValidationResult("SCHEMA_INVALID",tuple(ValidationErrorDetail("SCHEMA_INVALID",".".join(map(str,e.absolute_path)) or "$",e.message) for e in es)) if es else ValidationResult("VALID")
def _e(c,p,m): return ValidationErrorDetail(c,p,m)
def _index(items,key):
 out={}; es=[]
 for i,x in enumerate(items):
  k=x.get(key)
  if k in out: es.append(_e("DUPLICATE_ID",f"{key}s[{i}]",f"duplicate identifier {k!r}"))
  elif k is not None: out[k]=x
 return out,es
def validate_semantics(doc,family,case_ids=None):
 es=[]
 if doc.get("benchmark_version")!=BENCHMARK_VERSION: es.append(_e("VERSION_MISMATCH","benchmark_version","unsupported benchmark version"))
 if doc.get("schema_version")!=SCHEMA_VERSION: es.append(_e("VERSION_MISMATCH","schema_version","unsupported schema version"))
 if family=="case": return ValidationResult("SEMANTIC_INVALID",tuple(es)) if es else ValidationResult("VALID")
 if family=="evidence":
  l=doc.get("location",{})
  if l.get("line_start") is not None and l.get("line_end") is not None and l["line_end"]<l["line_start"]: es.append(_e("SEMANTIC_INVALID","location","line_end must be >= line_start"))
 if family=="attack-graph":
  nodes,ne=_index(doc.get("nodes",[]),"node_id"); edges,ee=_index(doc.get("edges",[]),"edge_id"); es+=ne+ee
  for e in doc.get("edges",[]):
   if e["source"] not in nodes: es.append(_e("REFERENCE_INVALID","edges",f"unknown source node {e['source']!r}"))
   if e["target"] not in nodes: es.append(_e("REFERENCE_INVALID","edges",f"unknown target node {e['target']!r}"))
  paths,pe=_index(doc.get("paths",[]),"path_id"); es+=pe
  for p in doc.get("paths",[]):
   if any(n not in nodes for n in p["node_ids"]): es.append(_e("PATH_INVALID",p["path_id"],"unknown path node"))
   if any(e not in edges for e in p["edge_ids"]): es.append(_e("PATH_INVALID",p["path_id"],"unknown path edge"))
   if p["entry_node"] not in nodes or p["impact_node"] not in nodes: es.append(_e("PATH_INVALID",p["path_id"],"invalid entry/impact node"))
   if len(p["edge_ids"])!=max(0,len(p["node_ids"])-1): es.append(_e("PATH_INVALID",p["path_id"],"ordered path requires one edge per node transition"))
   for i,eid in enumerate(p["edge_ids"]):
    if eid in edges and i+1<len(p["node_ids"]) and (edges[eid]["source"]!=p["node_ids"][i] or edges[eid]["target"]!=p["node_ids"][i+1]): es.append(_e("PATH_INVALID",p["path_id"],f"edge {eid!r} contradicts node sequence"))
 if family=="verdict":
  if doc["verdict"]=="CONDITIONALLY_EXPLOITABLE" and not doc.get("conditions"): es.append(_e("MISSING_REQUIRED_DATA","conditions","conditional verdict requires explicit conditions"))
  if doc["verdict"]!="CONDITIONALLY_EXPLOITABLE" and doc.get("conditions"): es.append(_e("SEMANTIC_INVALID","conditions","conditions only apply to conditional exploitability"))
 if family=="remediation":
  if doc["verification_status"]=="VERIFIED" and doc["final_verdict"]!="REMEDIATED": es.append(_e("SEMANTIC_INVALID","final_verdict","VERIFIED remediation must end REMEDIATED"))
  if doc["verification_status"]=="FAILED" and doc["final_verdict"]!="REMEDIATION_FAILED": es.append(_e("SEMANTIC_INVALID","final_verdict","FAILED remediation must end REMEDIATION_FAILED"))
  if doc.get("alternate_path_ids") and doc["final_verdict"]=="REMEDIATED": es.append(_e("SEMANTIC_INVALID","alternate_path_ids","alternate paths conflict with REMEDIATED"))
 if family=="submission":
  if case_ids is not None and doc["case_id"] not in case_ids: es.append(_e("CASE_MISMATCH","case_id","case is not in benchmark registry"))
  claims,ce=_index(doc["claims"],"claim_id"); evidence,ee=_index(doc["evidence"],"evidence_id"); paths,pe=_index(doc["attack_paths"],"path_id"); es+=ce+ee+pe
  for c in doc["claims"]:
   for eid in c.get("related_evidence",[]):
    if eid not in evidence: es.append(_e("REFERENCE_INVALID",f"claims.{c['claim_id']}.related_evidence",f"unknown evidence {eid!r}"))
  for e in doc["evidence"]:
   for cid in e.get("related_claims",[]):
    if cid not in claims: es.append(_e("REFERENCE_INVALID",f"evidence.{e['evidence_id']}.related_claims",f"unknown claim {cid!r}"))
  v=doc["verdict"]
  for cid in v["claim_ids"]:
   if cid not in claims: es.append(_e("REFERENCE_INVALID","verdict.claim_ids",f"unknown claim {cid!r}"))
  for eid in v["evidence_ids"]:
   if eid not in evidence: es.append(_e("REFERENCE_INVALID","verdict.evidence_ids",f"unknown evidence {eid!r}"))
  for pid in v["attack_path_ids"]:
   if pid not in paths: es.append(_e("REFERENCE_INVALID","verdict.attack_path_ids",f"unknown path {pid!r}"))
  for p in doc["attack_paths"]:
   if len(p["edge_ids"])!=max(0,len(p["node_ids"])-1): es.append(_e("PATH_INVALID",p["path_id"],"edge/node sequence mismatch"))
  if doc.get("remediation"):
   r=doc["remediation"]
   for cid in r["target_claim_ids"]:
    if cid not in claims: es.append(_e("REFERENCE_INVALID","remediation.target_claim_ids",f"unknown claim {cid!r}"))
   for pid in r["original_path_ids"]+r["revalidated_path_ids"]+r["alternate_path_ids"]:
    if pid not in paths: es.append(_e("REFERENCE_INVALID","remediation.path_ids",f"unknown path {pid!r}"))
 if family=="evaluation-result":
  comps=("finding_score","verdict_score","evidence_score","reachability_score","attack_path_score","impact_score","remediation_score","calibration_score","efficiency_score")
  total=sum(doc.get(k,{}).get("contribution",0) for k in comps); expected=max(0,min(doc["cap"],total-doc["penalty"]))
  if abs(expected-doc["final_score"])>1e-9: es.append(_e("INTEGRITY_VIOLATION","final_score","final score is not coherent with contributions, cap, and penalty"))
  if doc["validity"]!="VALID" and not doc["errors"]: es.append(_e("MISSING_REQUIRED_DATA","errors","non-valid result requires structured errors"))
 return ValidationResult("SEMANTIC_INVALID",tuple(es)) if es else ValidationResult("VALID")
def validate(doc,family,semantic=True,case_ids=None):
 r=validate_instance(doc,family)
 if r.status!="VALID" or not semantic:return r
 return validate_semantics(doc,family,case_ids or set(CASE_IDS))
def validate_file(path:Path,family:str,semantic=True,case_ids=None):
 try: d=json.loads(path.read_text(encoding="utf-8"))
 except Exception as e:return ValidationResult("SCHEMA_INVALID",(_e("SCHEMA_INVALID","$",f"invalid JSON: {e}"),))
 return validate(d,family,semantic,case_ids)
