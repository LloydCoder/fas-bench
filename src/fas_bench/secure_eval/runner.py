# fmt: off
# ruff: noqa: E501,UP035,UP037,I001,E701,E702,F541
"""Fail-closed Docker execution runner with bounded runtime resources."""
from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
import tempfile
import threading
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from .archive import write_inputs
from .artifacts import ArtifactSecurityError,collect_artifacts,manifest_digest
from .identity import canonical_json,digest_document,run_identity
from .models import Artifact,ExecutionPolicy,ExecutionRequest,ExecutionResult,FailureCode

_SENSITIVE=("SECRET","TOKEN","PASSWORD","PRIVATE_KEY","CREDENTIAL","API_KEY")
_PROTECTED_PREFIXES=("FAS_BENCH_",)
_PROVIDER_PREFIXES=("GITHUB_","AWS_","AZURE_","GOOGLE_","KUBERNETES_")

class SecureRunner:
 def __init__(self,policy:ExecutionPolicy,docker_binary="docker"):
  policy.validate();self.policy=policy;self.docker_binary=docker_binary
 def _docker(self,args,timeout=10):
  try:return subprocess.run([self.docker_binary,*args],stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=timeout,check=False)
  except (OSError,subprocess.SubprocessError):return None
 def _image_digest(self):
  r=self._docker(["image","inspect","--format","{{json .RepoDigests}}",self.policy.image],5)
  if r is None or r.returncode!=0:return None
  try:ds=json.loads(r.stdout)
  except json.JSONDecodeError:return None
  req=self.policy.image.split("@",1)[-1]
  return req if isinstance(ds,list) and any(req in str(x) for x in ds) else None
 def _reader(self,stream,limit,sink,flag):
  total=0
  while True:
   chunk=stream.read(65536)
   if not chunk:break
   remaining=max(0,limit-total)
   if remaining: sink.append(chunk[:remaining]);total+=min(len(chunk),remaining)
   if len(chunk)>remaining:flag[0]=True
 def _run(self,cmd,timeout,container_name):
  p=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  out=[];err=[];of=[False];ef=[False]
  threads=[threading.Thread(target=self._reader,args=(p.stdout,self.policy.output_bytes,out,of),daemon=True),threading.Thread(target=self._reader,args=(p.stderr,self.policy.output_bytes,err,ef),daemon=True)]
  for t in threads:t.start()
  timed=False
  try:p.wait(timeout=timeout)
  except subprocess.TimeoutExpired:
   timed=True;self._docker(["rm","-f",container_name],10)
   try:p.wait(timeout=10)
   except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
  for t in threads:t.join(timeout=10)
  return p.returncode,b"".join(out),b"".join(err),of[0],ef[0],timed
 def _validate_environment(self,environment):
  if len(environment)>self.policy.max_env_entries:return False
  for key,value in environment.items():
   if not isinstance(key,str) or not isinstance(value,str) or not key:return False
   upper=key.upper()
   if len(value.encode("utf-8"))>self.policy.max_env_value_bytes:return False
   if upper.startswith(_PROTECTED_PREFIXES) or upper.startswith(_PROVIDER_PREFIXES):return False
   if any(token in upper for token in _SENSITIVE):return False
  return True
 def execute(self,request:ExecutionRequest):
  started=datetime.now(UTC);t0=time.monotonic();root=Path(tempfile.mkdtemp(prefix="fas-bench-run-"));name=None
  cleanup_ok=True
  try:
   if not request.case_id or not request.submission_id or not request.command or any(not isinstance(x,str) or not x or "\\x00" in x for x in request.command):
    return self._fail(started,t0,FailureCode.INVALID_REQUEST,request)
   if not self._validate_environment(request.environment):return self._fail(started,t0,FailureCode.INVALID_REQUEST,request)
   d=self._docker(["version","--format","{{.Server.Version}}"],5)
   if d is None or d.returncode!=0:return self._fail(started,t0,FailureCode.ISOLATION_UNAVAILABLE,request)
   d=self._docker(["image","inspect",self.policy.image],5)
   if d is None or d.returncode!=0:return self._fail(started,t0,FailureCode.IMAGE_UNAVAILABLE,request)
   container_digest=self._image_digest()
   if container_digest is None:return self._fail(started,t0,FailureCode.IMAGE_DIGEST_MISMATCH,request)
   inp=root/"input";out=root/"output";inp.mkdir();out.mkdir()
   try:input_digest=write_inputs(inp,request.input_files,self.policy.workspace_bytes)
   except (ValueError,TypeError,OSError):return self._fail(started,t0,FailureCode.INPUT_INVALID,request)
   policy_digest=digest_document(self.policy)
   rid=run_identity(benchmark_digest=request.benchmark_digest or "UNSPECIFIED",case_manifest_digest=request.case_manifest_digest or request.case_id,submission_digest=request.submission_digest or request.submission_id,evaluator_digest=request.evaluator_digest or "UNSPECIFIED",scoring_digest=request.scoring_digest or "UNSPECIFIED",environment_digest=request.environment_digest or container_digest,execution_policy_digest=policy_digest,seed=request.seed)
   name=f"fas-bench-{rid[:24]}-{uuid.uuid4().hex[:12]}"
   cmd=[self.docker_binary,"run","--init","--network","none","--ipc","private","--cgroupns","private","--name",name,"--read-only","--cap-drop","ALL","--security-opt","no-new-privileges=true","--security-opt","seccomp=builtin","--pids-limit",str(self.policy.pids_limit),"--memory",str(self.policy.memory_bytes),"--memory-swap",str(self.policy.memory_bytes),"--cpus",str(self.policy.cpus),"--ulimit","nofile=1024:1024","--user",f"{self.policy.run_as_uid}:{self.policy.run_as_gid}","--tmpfs",f"/tmp:rw,nosuid,nodev,noexec,size=67108864","--tmpfs",f"/workspace:rw,nosuid,nodev,noexec,size={self.policy.workspace_bytes}","--tmpfs",f"/output:rw,nosuid,nodev,noexec,size={self.policy.output_bytes}","--mount",f"type=bind,src={inp},dst=/input,readonly","--workdir","/workspace"]
   env={"PATH":"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin","HOME":"/tmp","LANG":"C.UTF-8","LC_ALL":"C.UTF-8","TZ":"UTC","FAS_BENCH_RUN_ID":rid,"FAS_BENCH_CASE_ID":request.case_id}
   env.update(request.environment)
   for k,v in sorted(env.items()):cmd += ["--env",f"{k}={v}"]
   cmd += ["--entrypoint",request.command[0],self.policy.image,*request.command[1:]]
   rc,stdout,stderr,ot,et,timed=self._run(cmd,self.policy.timeout_seconds,name)
   status,failure=("TIMEOUT",FailureCode.TIMEOUT.value) if timed else ("OUTPUT_LIMIT",FailureCode.OUTPUT_LIMIT.value) if ot or et else ("SUCCESS",None) if rc==0 else ("FAILED",FailureCode.EXECUTION_FAILED.value)
   events=[]
   if not timed:
    cp=self._docker(["cp",f"{name}:/output/.",str(out)],10)
    if cp is None or cp.returncode!=0:
     status,failure="SECURITY_VIOLATION",FailureCode.SECURITY_VIOLATION.value
     events.append({"type":"ARTIFACT_COLLECTION_FAILED","message":"bounded output could not be collected"})
   records=()
   artifacts=()
   try:
    records=collect_artifacts(out,max_files=self.policy.max_artifacts,max_bytes=self.policy.max_artifact_bytes)
    artifacts=tuple(Artifact(r.path,r.sha256,r.size,r.type,r.producer,r.trust_level) for r in records)
   except ArtifactSecurityError as exc:
    status,failure="SECURITY_VIOLATION",FailureCode.SECURITY_VIOLATION.value;events.append({"type":"ARTIFACT_POLICY_VIOLATION","message":str(exc)})
   manifest={"run_id":rid,"case_id":request.case_id,"submission_id":request.submission_id,"benchmark_digest":request.benchmark_digest,"case_manifest_digest":request.case_manifest_digest,"submission_digest":request.submission_digest,"evaluator_digest":request.evaluator_digest,"scoring_digest":request.scoring_digest,"environment_digest":request.environment_digest or container_digest,"execution_policy_digest":policy_digest,"container_digest":container_digest,"input_digest":input_digest,"artifact_manifest_digest":manifest_digest(records),"status":status,"failure_code":failure}
   mh=hashlib.sha256(canonical_json(manifest)).hexdigest()
   if name:
    rr=self._docker(["rm","-f",name],10);cleanup_ok=rr is not None and rr.returncode in (0,1)
   return ExecutionResult(status,failure,rc,started.isoformat(),datetime.now(UTC).isoformat(),time.monotonic()-t0,stdout.decode("utf-8","replace"),stderr.decode("utf-8","replace"),ot,et,artifacts,mh,rid,self.policy.__dict__,input_digest,cleanup_ok,container_digest,tuple(events))
  finally:
   if name:
    rr=self._docker(["rm","-f",name],10);cleanup_ok=cleanup_ok and rr is not None and rr.returncode in (0,1)
   try:shutil.rmtree(root)
   except OSError:pass
 def _fail(self,started,t0,code,request):
  d=digest_document(request);rid=hashlib.sha256((request.case_id+request.submission_id+d).encode()).hexdigest()
  return ExecutionResult("FAILED",code.value,None,started.isoformat(),datetime.now(UTC).isoformat(),time.monotonic()-t0,"","",False,False,(),hashlib.sha256(b"").hexdigest(),rid,self.policy.__dict__,d,True)
