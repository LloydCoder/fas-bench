import pytest
from fas_bench.secure_eval.archive import safe_relative_path,write_inputs
from fas_bench.secure_eval.models import ExecutionPolicy,ExecutionRequest,FailureCode
from fas_bench.secure_eval.runner import SecureRunner
PINNED="ghcr.io/example/fas-bench@sha256:"+"a"*64
def test_policy_is_fail_closed():
 with pytest.raises(ValueError): ExecutionPolicy("python:3.13").validate()
 with pytest.raises(ValueError): ExecutionPolicy(PINNED,no_network=False).validate()
 with pytest.raises(ValueError): ExecutionPolicy(PINNED,run_as_uid=0).validate()
def test_archive_traversal():
 for p in ("../x","/etc/passwd","a/../../x","C:/x"):
  with pytest.raises(ValueError): safe_relative_path(p)
 assert safe_relative_path("src/main.py")=="src/main.py"
def test_input_digest_deterministic(tmp_path):
 a=write_inputs(tmp_path,{"b":b"2","a":b"1"},100); assert len(a)==64
def test_runner_never_falls_back_to_host():
 r=SecureRunner(ExecutionPolicy(PINNED),docker_binary="fas-bench-no-such-docker")
 x=r.execute(ExecutionRequest("FAS-001","SUB-1",("/bin/true",)))
 assert x.failure_code==FailureCode.ISOLATION_UNAVAILABLE.value
def test_secret_like_environment_rejected():
 r=SecureRunner(ExecutionPolicy(PINNED),docker_binary="fas-bench-no-such-docker")
 x=r.execute(ExecutionRequest("FAS-001","SUB-1",("/bin/true",),environment={"AWS_SECRET_ACCESS_KEY":"x"}))
 assert x.failure_code==FailureCode.INVALID_REQUEST.value
