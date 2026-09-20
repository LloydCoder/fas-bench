import pytest

from fas_bench.secure_eval.archive import safe_relative_path, write_inputs
from fas_bench.secure_eval.artifacts import ArtifactSecurityError, collect_artifacts
from fas_bench.secure_eval.cache import EvaluationCache
from fas_bench.secure_eval.identity import run_identity
from fas_bench.secure_eval.lifecycle import LifecycleError, LifecycleState, RunLifecycle
from fas_bench.secure_eval.models import (
    Artifact,
    ExecutionPolicy,
    ExecutionRequest,
    ExecutionResult,
    FailureCode,
)
from fas_bench.secure_eval.network import NetworkPolicy, NetworkRule
from fas_bench.secure_eval.resources import CaseResourceRequest, ResourceLimits, effective_resources
from fas_bench.secure_eval.runner import SecureRunner
from fas_bench.secure_eval.scheduler import ResourceScheduler
from fas_bench.secure_eval.verification import IntegrityError, verify_result

PINNED = "ghcr.io/example/fas-bench@sha256:" + "a" * 64


def test_policy_is_fail_closed():
    with pytest.raises(ValueError):
        ExecutionPolicy("python:3.13").validate()
    with pytest.raises(ValueError):
        ExecutionPolicy(PINNED, no_network=False).validate()
    with pytest.raises(ValueError):
        ExecutionPolicy(PINNED, run_as_uid=0).validate()


def test_archive_traversal():
    for path in ("../x", "/etc/passwd", "a/../../x", "C:/x", r"\\server\\share\\x"):
        with pytest.raises(ValueError):
            safe_relative_path(path)
    assert safe_relative_path("src/main.py") == "src/main.py"


def test_input_digest_deterministic(tmp_path):
    digest = write_inputs(tmp_path, {"b": b"2", "a": b"1"}, 100)
    assert len(digest) == 64


def test_runner_never_falls_back_to_host():
    runner = SecureRunner(ExecutionPolicy(PINNED), docker_binary="fas-bench-no-such-docker")
    result = runner.execute(ExecutionRequest("FAS-001", "SUB-1", ("/bin/true",)))
    assert result.failure_code == FailureCode.ISOLATION_UNAVAILABLE.value


def test_secret_like_environment_rejected():
    runner = SecureRunner(ExecutionPolicy(PINNED), docker_binary="fas-bench-no-such-docker")
    result = runner.execute(
        ExecutionRequest(
            "FAS-001",
            "SUB-1",
            ("/bin/true",),
            environment={"AWS_SECRET_ACCESS_KEY": "x"},
        )
    )
    assert result.failure_code == FailureCode.INVALID_REQUEST.value


def test_artifact_symlink_is_rejected(tmp_path):
    (tmp_path / "safe.txt").write_text("ok", encoding="utf-8")
    (tmp_path / "escape").symlink_to("/etc/passwd")
    with pytest.raises(ArtifactSecurityError):
        collect_artifacts(tmp_path, max_files=10, max_bytes=10000)


def test_cache_identity_changes_with_submission(tmp_path):
    cache = EvaluationCache(tmp_path)
    first = cache.key(
        benchmark_digest="a",
        case_digest="b",
        submission_digest="c",
        evaluator_digest="d",
        scoring_digest="e",
        environment_digest="f",
        execution_policy_digest="g",
    )
    changed = cache.key(
        benchmark_digest="a",
        case_digest="b",
        submission_digest="changed",
        evaluator_digest="d",
        scoring_digest="e",
        environment_digest="f",
        execution_policy_digest="g",
    )
    assert first != changed
    cache.put(first, {"status": "SUCCESS"})
    assert cache.get(first) == {"status": "SUCCESS"}
    assert cache.get(changed) is None


def test_run_identity_changes_with_policy_and_submission():
    base = dict(
        benchmark_digest="a",
        case_manifest_digest="b",
        submission_digest="c",
        evaluator_digest="d",
        scoring_digest="e",
        environment_digest="f",
        execution_policy_digest="g",
    )
    assert run_identity(**base) != run_identity(**{**base, "submission_digest": "changed"})
    assert run_identity(**base) != run_identity(**{**base, "execution_policy_digest": "changed"})


def test_lifecycle_rejects_illegal_transition():
    lifecycle = RunLifecycle()
    lifecycle.transition(LifecycleState.VALIDATING)
    with pytest.raises(LifecycleError):
        lifecycle.transition(LifecycleState.COMPLETED)


def test_result_verifier_rejects_bad_artifact_path():
    result = SecureRunner(
        ExecutionPolicy(PINNED),
        docker_binary="fas-bench-no-such-docker",
    ).execute(ExecutionRequest("FAS-001", "SUB-1", ("/bin/true",)))
    forged = ExecutionResult(
        **{
            **result.as_dict(),
            "artifacts": (Artifact("../secret", "a" * 64, 1),),
        }
    )
    with pytest.raises(IntegrityError):
        verify_result(forged)


def test_resource_request_is_bounded():
    request = CaseResourceRequest(cpus=2, memory_bytes=1024 * 1024 * 1024)
    assert effective_resources(request, ResourceLimits()).memory_bytes == request.memory_bytes
    with pytest.raises(ValueError):
        effective_resources(
            CaseResourceRequest(memory_bytes=3 * 1024**3),
            ResourceLimits(),
        )


def test_scheduler_admission_is_resource_aware():
    scheduler = ResourceScheduler(max_workers=2, total_cpus=2, total_memory_bytes=1024)
    assert scheduler.admit(1, 512)
    assert not scheduler.admit(1.5, 512)
    scheduler.release(1, 512)
    assert scheduler.admit(2, 1024)


def test_network_policy_is_deny_by_default():
    policy = NetworkPolicy()
    assert policy.docker_network_mode() == "none"
    with pytest.raises(ValueError):
        NetworkPolicy(
            mode="deny",
            allowlist=(NetworkRule("example.test", "tcp", 443, "test"),),
        ).validate()
