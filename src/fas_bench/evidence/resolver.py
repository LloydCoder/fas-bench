# fmt: off
# ruff: noqa: E501,UP035,UP037,I001,E701,E702
"""Safe resolution and exact source-location verification."""
from __future__ import annotations
import ast
import json
from pathlib import Path
from typing import Any
from .errors import CaseLoadError

def safe_resolve(root:Path,relative:str)->Path:
 if not isinstance(relative,str) or not relative or "\x00" in relative: raise CaseLoadError("EVIDENCE_INVALID_PATH: empty or NUL-containing path")
 candidate=Path(relative)
 if candidate.is_absolute() or candidate.anchor: raise CaseLoadError("EVIDENCE_INVALID_PATH: absolute path is forbidden")
 resolved_root=root.resolve();resolved=(resolved_root/candidate).resolve()
 try: resolved.relative_to(resolved_root)
 except ValueError as exc: raise CaseLoadError("EVIDENCE_INVALID_PATH: path escapes case root") from exc
 return resolved

def resolve_artifact_path(case_root:Path,evidence:dict[str,Any])->Path|None:
 location=evidence.get("location") or {};file_name=location.get("file")
 if file_name:return safe_resolve(case_root,file_name)
 fact=evidence.get("fact") or {};artifact_path=fact.get("artifact_path")
 if artifact_path:return safe_resolve(case_root,artifact_path)
 return None

def _read_json_value(document:Any,key_path:str)->Any:
 current=document
 if not key_path:return current
 for part in key_path.split("."):
  if isinstance(current,dict) and part in current: current=current[part]
  else: raise KeyError(key_path)
 return current

def read_fact(case_root:Path,evidence:dict[str,Any])->tuple[bool,Any,str]:
 fact=evidence.get("fact")
 if not isinstance(fact,dict):return False,None,"no structured fact supplied"
 artifact_path,key=fact.get("artifact_path"),fact.get("key")
 if not isinstance(artifact_path,str) or not isinstance(key,str):return False,None,"fact requires artifact_path and key"
 try:path=safe_resolve(case_root,artifact_path)
 except CaseLoadError as exc:return False,None,str(exc)
 if not path.is_file():return False,None,f"artifact does not exist: {artifact_path}"
 try:
  if path.suffix.lower()==".json": return True,_read_json_value(json.loads(path.read_text(encoding="utf-8")),key),""
  text=path.read_text(encoding="utf-8")
 except (OSError,UnicodeError,json.JSONDecodeError,KeyError) as exc:return False,None,f"cannot read structured fact: {exc}"
 if key=="content":return True,text,""
 return False,None,"non-JSON facts require key=content"

def _symbol_intersects_range(path:Path,symbol:str,start:int,end:int)->bool:
 if path.suffix.lower()!=".py": return False
 try:tree=ast.parse(path.read_text(encoding="utf-8"))
 except (OSError,UnicodeError,SyntaxError): return False
 for node in ast.walk(tree):
  if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and node.name==symbol:
   node_start=getattr(node,"lineno",0);node_end=getattr(node,"end_lineno",node_start)
   return node_start>=start and node_end<=end
 return False

def verify_location(case_root:Path,location:dict[str,Any])->tuple[str,str]:
 if not isinstance(location,dict):return "INVALID","EVIDENCE_INVALID_LOCATION"
 file_name=location.get("file")
 if not isinstance(file_name,str) or not file_name:return "INVALID","EVIDENCE_INVALID_PATH"
 try:path=safe_resolve(case_root,file_name)
 except CaseLoadError:return "INVALID","EVIDENCE_INVALID_PATH"
 try:
  if not path.is_file():return "INVALID","EVIDENCE_INVALID_PATH"
  raw=path.read_bytes()
  text=raw.decode("utf-8")
 except (OSError,UnicodeDecodeError):return "UNRESOLVED","EVIDENCE_UNRESOLVED"
 lines=text.splitlines()
 start=location.get("line_start");end=location.get("line_end",start)
 if not isinstance(start,int) or start<1 or not isinstance(end,int) or end<start or end>len(lines):return "INVALID","EVIDENCE_INVALID_LINE"
 for key in ("column_start","column_end"):
  value=location.get(key)
  if value is not None and (not isinstance(value,int) or value<1):return "INVALID","EVIDENCE_INVALID_COLUMN"
 symbol=location.get("symbol")
 if symbol and not _symbol_intersects_range(path,symbol,start,end):return "INVALID","EVIDENCE_INVALID_SYMBOL"
 snippet=location.get("snippet")
 if snippet is not None:
  if not isinstance(snippet,str):return "INVALID","EVIDENCE_SNIPPET_MISMATCH"
  actual="\n".join(lines[start-1:end])
  expected=snippet.replace("\r\n","\n").replace("\r","\n")
  if actual!=expected:return "INVALID","EVIDENCE_SNIPPET_MISMATCH"
 return "VERIFIED","EVIDENCE_VERIFIED"
