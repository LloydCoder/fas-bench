from fas_bench.phase13 import phase13_gate, validate_release_security_policy


def _controls():
    return {
        "content_addressed_release": True,
        "independent_verification": True,
        "reproducible_build": True,
        "artifact_provenance_attestation": True,
        "sbom_attestation": True,
        "secret_scan": True,
        "dependency_audit": True,
    }


def test_phase13_requires_all_release_controls():
    errors = validate_release_security_policy({})
    assert "missing or failed enterprise release control: sbom_attestation" in errors


def test_phase13_gate_accepts_complete_control_set():
    result = phase13_gate(_controls(), artifacts=["dist/fas_bench.whl"])
    assert result["status"] == "PASS"
    assert result["requires_signed_provenance"] is True
    assert result["requires_sbom"] is True


def test_phase13_gate_does_not_self_claim_enterprise_security():
    result = phase13_gate(_controls(), artifacts=["dist/fas_bench.whl"])
    assert result["enterprise_security_claim"] is False
