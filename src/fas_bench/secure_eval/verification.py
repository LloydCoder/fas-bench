# fmt: off
# ruff: noqa: E701,E702,I001,UP035
from __future__ import annotations
import hashlib
from pathlib import Path
from .identity import canonical_json
from .models import ExecutionResult

class IntegrityError(ValueError): pass

def result_digest(result:ExecutionResult)->str:
    data=result.as_dict()
    data.pop("started_at",None);data.pop("finished_at",None);data.pop("duration_seconds",None)
    return hashlib.sha256(canonical_json(data)).hexdigest()

def verify_result(result:ExecutionResult)->None:
    if len(result.run_id)!=64 or len(result.manifest_sha256)!=64 or len(result.input_digest)!=64: raise IntegrityError("invalid result digest fields")
    if result.status=="SUCCESS" and result.failure_code is not None: raise IntegrityError("successful result has failure code")
    if result.status in {"TIMEOUT","OUTPUT_LIMIT","SECURITY_VIOLATION"} and result.failure_code is None: raise IntegrityError("terminal failure lacks failure code")
    seen=set()
    for artifact in result.artifacts:
        if artifact.path in seen: raise IntegrityError("duplicate artifact path")
        seen.add(artifact.path)
        if not artifact.path or artifact.path.startswith("/") or ".." in Path(artifact.path).parts: raise IntegrityError("unsafe artifact path")
        if len(artifact.sha256)!=64: raise IntegrityError("invalid artifact digest")

def write_result_bundle(root:Path,result:ExecutionResult)->Path:
    verify_result(result)
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    payload=result.as_dict()
    payload["result_digest"]=result_digest(result)
    data=canonical_json(payload)
    tmp=root/"result.json.tmp";final=root/"result.json"
    tmp.write_bytes(data);tmp.replace(final)
    digest=hashlib.sha256(data).hexdigest()
    (root/"result.sha256").write_text(digest+"\n",encoding="ascii")
    return final
