from fas_bench.phase11_1 import dynamic_oracle_gate, validate_observation


def _observation(**overrides):
    value = {
        "oracle_id": "oracle-v1",
        "case_id": "FAS-001",
        "observation_type": "REACHABILITY",
        "status": "PASS",
        "run_id": "run-1",
        "input_digest": "a" * 64,
        "artifact_manifest_digest": "b" * 64,
        "policy_digest": "c" * 64,
        "environment_digest": "d" * 64,
        "observed_at": "2026-10-01T00:00:00Z",
        "evidence": [{"path": "stdout.txt", "sha256": "e" * 64}],
    }
    value.update(overrides)
    return value


def test_dynamic_oracle_requires_inspectable_evidence():
    errors = validate_observation(_observation(evidence=[]))
    assert "PASS/FAIL observations require independently inspectable evidence" in errors


def test_dynamic_oracle_rejects_invalid_status():
    errors = validate_observation(_observation(status="VERDICT"))
    assert "invalid oracle status" in errors


def test_dynamic_oracle_gate_is_not_ground_truth_authority():
    result = dynamic_oracle_gate([_observation()])
    assert result["status"] == "PASS"
    assert result["oracle_self_certifies_ground_truth"] is False
    assert result["requires_secure_execution_provider"] is True
