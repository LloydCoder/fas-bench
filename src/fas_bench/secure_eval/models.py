from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum

class FailureCode(StrEnum):
    INVALID_REQUEST="INVALID_REQUEST"; UNSUPPORTED_PLATFORM="UNSUPPORTED_PLATFORM"; ISOLATION_UNAVAILABLE="ISOLATION_UNAVAILABLE"; IMAGE_NOT_PINNED="IMAGE_NOT_PINNED"; IMAGE_UNAVAILABLE="IMAGE_UNAVAILABLE"; IMAGE_DIGEST_MISMATCH="IMAGE_DIGEST_MISMATCH"; INPUT_INVALID="INPUT_INVALID"; ARCHIVE_UNSAFE="ARCHIVE_UNSAFE"; TIMEOUT="TIMEOUT"; RESOURCE_LIMIT="RESOURCE_LIMIT"; EXECUTION_FAILED="EXECUTION_FAILED"; OUTPUT_LIMIT="OUTPUT_LIMIT"; NETWORK_POLICY_VIOLATION="NETWORK_POLICY_VIOLATION"; FILESYSTEM_POLICY_VIOLATION="FILESYSTEM_POLICY_VIOLATION"; SECURITY_VIOLATION="SECURITY_VIOLATION"; CLEANUP_FAILED="CLEANUP_FAILED"; EVALUATOR_ERROR="EVALUATOR_ERROR"

class ExecutionStatus(StrEnum):
    SUCCESS="SUCCESS"; FAILED="FAILED"; TIMEOUT="TIMEOUT"; OUTPUT_LIMIT="OUTPUT_LIMIT"; RESOURCE_LIMIT="RESOURCE_LIMIT"; SECURITY_VIOLATION="SECURITY_VIOLATION"; EVALUATOR_ERROR="EVALUATOR_ERROR"

@dataclass(frozen=True)
class ExecutionPolicy:
    image:str
    timeout_seconds:int=30; memory_bytes:int=536870912; cpus:float=1.0; pids_limit:int=128
    workspace_bytes:int=268435456; output_bytes:int=4194304; max_artifacts:int=4096; max_artifact_bytes:int=268435456
    max_env_entries:int=64; max_env_value_bytes:int=8192
    no_network:bool=True; read_only_root:bool=True; drop_all_capabilities:bool=True; no_new_privileges:bool=True
    private_pid:bool=True; private_ipc:bool=True; private_cgroup:bool=True; default_seccomp:bool=True
    run_as_uid:int=65532; run_as_gid:int=65532; require_pinned_image:bool=True
    def validate(self):
        if self.require_pinned_image and "@sha256:" not in self.image: raise ValueError("execution image must be pinned by immutable digest")
        if not 1<=self.timeout_seconds<=3600 or not 16777216<=self.memory_bytes<=8*1024**3 or not .1<=self.cpus<=64 or not 16<=self.pids_limit<=10000: raise ValueError("invalid resource policy")
        if not 4096<=self.workspace_bytes<=8*1024**3 or not 1024<=self.output_bytes<=256*1024**2: raise ValueError("invalid size limits")
        if not 1<=self.max_artifacts<=100000 or not 1024<=self.max_artifact_bytes<=8*1024**3: raise ValueError("invalid artifact limits")
        if not 1<=self.max_env_entries<=256 or not 64<=self.max_env_value_bytes<=65536: raise ValueError("invalid environment policy")
        if not all((self.no_network,self.read_only_root,self.drop_all_capabilities,self.no_new_privileges,self.private_pid,self.private_ipc,self.private_cgroup,self.default_seccomp)): raise ValueError("mandatory isolation control disabled")
        if self.run_as_uid==0 or self.run_as_gid==0: raise ValueError("root execution is forbidden")

@dataclass(frozen=True)
class ExecutionRequest:
    case_id:str; submission_id:str; command:tuple[str,...]
    input_files:dict[str,bytes]=field(default_factory=dict); environment:dict[str,str]=field(default_factory=dict)
    benchmark_digest:str=""; case_manifest_digest:str=""; submission_digest:str=""; evaluator_digest:str=""; scoring_digest:str=""; environment_digest:str=""; seed:int|None=None

@dataclass(frozen=True)
class Artifact:
    path:str; sha256:str; size:int; type:str="file"; producer:str="candidate"; trust_level:str="UNTRUSTED"

@dataclass(frozen=True)
class ExecutionResult:
    status:str; failure_code:str|None; exit_code:int|None; started_at:str; finished_at:str; duration_seconds:float
    stdout:str; stderr:str; stdout_truncated:bool; stderr_truncated:bool; artifacts:tuple[Artifact,...]; manifest_sha256:str
    run_id:str; policy:dict[str,object]; input_digest:str; cleanup_ok:bool; container_digest:str|None=None
    security_events:tuple[dict[str,object],...]=(); attempt_id:str="attempt-001"
    def as_dict(self): return {**self.__dict__,"artifacts":[a.__dict__ for a in self.artifacts]}
