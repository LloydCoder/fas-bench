from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

from .archive import hash_tree, write_inputs
from .models import Artifact, ExecutionPolicy, ExecutionRequest, ExecutionResult, FailureCode


class SecureRunner:
    def __init__(self, policy: ExecutionPolicy, docker_binary="docker"):
        policy.validate()
        self.policy = policy
        self.docker_binary = docker_binary

    def _docker(self, args, timeout=10):
        try:
            return subprocess.run(
                [self.docker_binary, *args],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.SubprocessError):
            return None

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        started = datetime.now(UTC)
        t0 = time.monotonic()
        root = Path(tempfile.mkdtemp(prefix="fas-bench-run-"))
        cleanup = True
        try:
            if (
                not request.case_id
                or not request.submission_id
                or not request.command
                or any(not isinstance(x, str) or not x for x in request.command)
            ):
                return self._fail(started, t0, FailureCode.INVALID_REQUEST, request)
            for key in request.environment:
                if (
                    not key
                    or key.startswith("GITHUB_")
                    or any(
                        marker in key.upper()
                        for marker in ("SECRET", "TOKEN", "PASSWORD", "PRIVATE_KEY")
                    )
                ):
                    return self._fail(started, t0, FailureCode.INVALID_REQUEST, request)
            version = self._docker(["version", "--format", "{{.Server.Version}}"], 5)
            if version is None or version.returncode != 0:
                return self._fail(started, t0, FailureCode.ISOLATION_UNAVAILABLE, request)
            inspect = self._docker(["image", "inspect", self.policy.image], 5)
            if inspect is None or inspect.returncode != 0:
                return self._fail(started, t0, FailureCode.IMAGE_UNAVAILABLE, request)
            inp = root / "input"
            out = root / "output"
            inp.mkdir()
            out.mkdir()
            os.chmod(out, 0o777)
            try:
                input_digest = write_inputs(inp, request.input_files, self.policy.workspace_bytes)
            except (ValueError, TypeError):
                return self._fail(started, t0, FailureCode.INPUT_INVALID, request)
            seed = json.dumps(
                {
                    "case": request.case_id,
                    "submission": request.submission_id,
                    "input": input_digest,
                    "policy": self.policy.__dict__,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
            run_id = hashlib.sha256(seed).hexdigest()
            name = "fas-bench-" + run_id[:24]
            cmd = [
                self.docker_binary,
                "run",
                "--init",
                "--network",
                "none",
                "--name",
                name,
                "--read-only",
                "--cap-drop",
                "ALL",
                "--security-opt",
                "no-new-privileges",
                "--pids-limit",
                str(self.policy.pids_limit),
                "--memory",
                str(self.policy.memory_bytes),
                "--cpus",
                str(self.policy.cpus),
                "--user",
                f"{self.policy.run_as_uid}:{self.policy.run_as_gid}",
                "--tmpfs",
                "/tmp:rw,nosuid,nodev,noexec,size=67108864",
                "--tmpfs",
                f"/workspace:rw,nosuid,nodev,noexec,size={self.policy.workspace_bytes}",
                "--mount",
                f"type=bind,src={out},dst=/output",
                "--mount",
                f"type=bind,src={inp},dst=/input,readonly",
                "--workdir",
                "/workspace",
            ]
            env = {
                "PATH": "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "HOME": "/tmp",
                "LANG": "C.UTF-8",
                "LC_ALL": "C.UTF-8",
                "TZ": "UTC",
                "FAS_BENCH_RUN_ID": run_id,
                "FAS_BENCH_CASE_ID": request.case_id,
            }
            for k, v in request.environment.items():
                if (
                    not k
                    or k.startswith("GITHUB_")
                    or any(x in k.upper() for x in ("SECRET", "TOKEN", "PASSWORD", "PRIVATE_KEY"))
                ):
                    return self._fail(started, t0, FailureCode.INVALID_REQUEST, request)
                env[k] = v
            for k, v in sorted(env.items()):
                cmd += ["--env", f"{k}={v}"]
            cmd += ["--entrypoint", request.command[0], self.policy.image, *request.command[1:]]
            try:
                proc = subprocess.run(
                    cmd,
                    stdin=subprocess.DEVNULL,
                    capture_output=True,
                    text=True,
                    timeout=self.policy.timeout_seconds,
                    check=False,
                )
                stdout = self._cap(proc.stdout or "")
                stderr = self._cap(proc.stderr or "")
                truncated = len(stdout) < len(proc.stdout or "") or len(stderr) < len(
                    proc.stderr or ""
                )
                status = (
                    "SUCCESS"
                    if proc.returncode == 0 and not truncated
                    else ("OUTPUT_LIMIT" if truncated else "FAILED")
                )
                code = (
                    None
                    if status == "SUCCESS"
                    else (
                        FailureCode.OUTPUT_LIMIT.value
                        if truncated
                        else FailureCode.EXECUTION_FAILED.value
                    )
                )
            except subprocess.TimeoutExpired as e:
                self._docker(["rm", "-f", name], 10)
                stdout = self._cap(e.stdout or "")
                stderr = self._cap(e.stderr or "")
                status = "TIMEOUT"
                code = FailureCode.TIMEOUT.value
                proc = None
                truncated = False
            finally:
                rm = self._docker(["rm", "-f", name], 10)
                if rm is None or rm.returncode not in (0, 1):
                    cleanup = False
            artifacts = tuple(Artifact(p, h, s) for p, h, s in hash_tree(out))
            manifest = {
                "run_id": run_id,
                "case_id": request.case_id,
                "submission_id": request.submission_id,
                "input_digest": input_digest,
                "artifacts": [a.__dict__ for a in artifacts],
                "policy": self.policy.__dict__,
                "status": status,
            }
            mb = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
            mh = hashlib.sha256(mb).hexdigest()
            (out / "manifest.json").write_bytes(mb)
            return ExecutionResult(
                status,
                code,
                proc.returncode if proc else None,
                started.isoformat(),
                datetime.now(UTC).isoformat(),
                time.monotonic() - t0,
                stdout,
                stderr,
                truncated,
                truncated,
                artifacts,
                mh,
                run_id,
                self.policy.__dict__,
                input_digest,
                cleanup,
            )
        finally:
            try:
                shutil.rmtree(root)
            except OSError:
                pass

    def _cap(self, s, limit=None):
        return (
            (s or "")
            .encode("utf-8", "replace")[: limit or self.policy.output_bytes]
            .decode("utf-8", "replace")
        )

    def _fail(self, started, t0, code, request):
        d = hashlib.sha256(
            json.dumps(
                request.__dict__,
                sort_keys=True,
                default=lambda x: x.hex() if isinstance(x, bytes) else x,
            ).encode()
        ).hexdigest()
        rid = hashlib.sha256((request.case_id + request.submission_id + d).encode()).hexdigest()
        return ExecutionResult(
            "FAILED",
            code.value,
            None,
            started.isoformat(),
            datetime.now(UTC).isoformat(),
            time.monotonic() - t0,
            "",
            "",
            False,
            False,
            (),
            hashlib.sha256(b"").hexdigest(),
            rid,
            self.policy.__dict__,
            d,
            True,
        )
