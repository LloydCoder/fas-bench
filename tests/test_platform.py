from fas_bench.platform import EvaluationJob, platform_gate


def _job(seed=0):
    return EvaluationJob(
        benchmark_digest="a" * 64,
        corpus_digest="b" * 64,
        evaluator_digest="c" * 64,
        scoring_digest="d" * 64,
        submission_digest="e" * 64,
        environment_digest="f" * 64,
        policy_digest="g" * 64,
        seed=seed,
    )


def test_job_identity_is_deterministic():
    assert _job().identity() == _job().identity()


def test_distinct_seed_changes_identity():
    assert _job(0).identity() != _job(1).identity()


def test_platform_gate_rejects_duplicate_jobs():
    result = platform_gate([_job(), _job()])
    assert result["status"] == "FAIL"


def test_platform_gate_keeps_execution_outside_platform_layer():
    result = platform_gate([_job()])
    assert result["status"] == "PASS"
    assert result["execution_provider"] == "PHASE9_SECURE_EVAL"
    assert result["host_execution"] is False
