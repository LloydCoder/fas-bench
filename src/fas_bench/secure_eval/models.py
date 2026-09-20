from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class FailureCode(str, Enum):
    INVALID_REQUEST = "INVALID_REQUEST"
    UNSUPPORTED_PLATFORM = "UNSUPPORTED_PLATFORM"
    ISOLATION_UNAVAILABLE = "ISOLATION_UNAVAILABLE"
    IMAGE_NOT_PINNED = "IMAGE_NOT_PINNED"
    IMAGE_UNAVAILABLE = "IMAGE_UNAVAILABLE"
    INPUT_INVALID = "INPUT_INVALID"
    ARCHIVE_UNSAFE = "ARCHIVE_UNSAFE"
    TIMEOUT = "TIMEOUT"
    RESOURCE_LIMIT = "RESOURCE_LIMIT"
    EXECUTION_FAILED = "EXECUTION_FAILED"
    OUTPUT_LIMIT = "OUTPUT_LIMIT"
    CLEANUP_FAILED = "CLEANUP_FAILED"


@dataclass(frozen=True)
class ExecutionPolicy:
    image: str
    timeout_seconds: int = 30
    memory_bytes: int = 536870912
    cpus: float = 1.0
    pids_limit: int = 128
    workspace_bytes: int = 268435456
    output_bytes: int = 4194304
    no_network: bool = True
    read_only_root: bool = True
    drop_all_capabilities: bool = True
    no_new_privileges: bool = True
    run_as_uid: int = 65532
    run_as_gid: int = 65532
    require_pinned_image: bool = True

    def validate(self):
        if self.require_pinned_image and "@sha256:" not in self.image:
            raise ValueError("execution image must be pinned by immutable digest")
        if (
            not 1 <= self.timeout_seconds <= 3600
            or self.memory_bytes < 16777216
            or self.cpus <= 0
            or self.cpus > 64
            or not 16 <= self.pids_limit <= 10000
        ):
            raise ValueError("invalid resource policy")
        if self.workspace_bytes < 4096 or self.output_bytes < 1024:
            raise ValueError("invalid size limits")
        if not (
            self.no_network
            and self.read_only_root
            and self.drop_all_capabilities
            and self.no_new_privileges
        ):
            raise ValueError("Phase 9 isolation controls are mandatory")
        if self.run_as_uid == 0 or self.run_as_gid == 0:
            raise ValueError("root execution is forbidden")


@dataclass(frozen=True)
class ExecutionRequest:
    case_id: str
    submission_id: str
    command: tuple[str, ...]
    input_files: dict[str, bytes] = field(default_factory=dict)
    environment: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Artifact:
    path: str
    sha256: str
    size: int


@dataclass(frozen=True)
class ExecutionResult:
    status: str
    failure_code: str | None
    exit_code: int | None
    started_at: str
    finished_at: str
    duration_seconds: float
    stdout: str
    stderr: str
    stdout_truncated: bool
    stderr_truncated: bool
    artifacts: tuple[Artifact, ...]
    manifest_sha256: str
    run_id: str
    policy: dict[str, object]
    input_digest: str
    cleanup_ok: bool

    def as_dict(self):
        return {**self.__dict__, "artifacts": [a.__dict__ for a in self.artifacts]}
