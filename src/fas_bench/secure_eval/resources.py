# fmt: off
# ruff: noqa: E701,E702,I001,UP035
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class ResourceLimits:
    max_cpus: float = 4.0
    max_memory_bytes: int = 2 * 1024**3
    max_pids: int = 512
    max_timeout_seconds: int = 300
    max_workspace_bytes: int = 1024**3
    max_output_bytes: int = 64 * 1024**2
    max_artifacts: int = 10000
    max_artifact_bytes: int = 1024**3

@dataclass(frozen=True)
class CaseResourceRequest:
    cpus: float = 1.0
    memory_bytes: int = 512 * 1024**2
    pids: int = 128
    timeout_seconds: int = 30
    workspace_bytes: int = 256 * 1024**2
    output_bytes: int = 4 * 1024**2
    artifacts: int = 4096
    artifact_bytes: int = 256 * 1024**2

def effective_resources(request: CaseResourceRequest, limits: ResourceLimits) -> CaseResourceRequest:
    values = (
        request.cpus <= limits.max_cpus,
        request.memory_bytes <= limits.max_memory_bytes,
        request.pids <= limits.max_pids,
        request.timeout_seconds <= limits.max_timeout_seconds,
        request.workspace_bytes <= limits.max_workspace_bytes,
        request.output_bytes <= limits.max_output_bytes,
        request.artifacts <= limits.max_artifacts,
        request.artifact_bytes <= limits.max_artifact_bytes,
    )
    if not all(values):
        raise ValueError("case resource request exceeds benchmark maximum")
    if min(request.cpus, request.memory_bytes, request.pids, request.timeout_seconds,
           request.workspace_bytes, request.output_bytes, request.artifacts, request.artifact_bytes) <= 0:
        raise ValueError("resource values must be positive")
    return request
