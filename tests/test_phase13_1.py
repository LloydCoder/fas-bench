from fas_bench.phase13_1 import governance_gate, validate_change_record


def _record():
    return {
        "change_class": "RELEASE",
        "rationale": "Release a verified benchmark revision.",
        "impact_assessment": "Updates release metadata only.",
        "validation_evidence": "CI, security, release and independent checks passed.",
        "changelog_entry": "Documented in CHANGELOG.md.",
        "reviews": {
            "security_objective": True,
            "oracle_ground_truth": True,
            "security": True,
            "reproducibility_integrity": True,
        },
        "approval": True,
    }


def test_governance_requires_all_review_dimensions():
    errors = validate_change_record(_record() | {"reviews": {}})
    assert "required review missing: security" in errors


def test_governance_gate_accepts_complete_record():
    result = governance_gate([_record()])
    assert result["status"] == "PASS"
    assert result["requires_human_approval"] is True


def test_governance_never_self_claims_governance():
    result = governance_gate([_record()])
    assert result["governance_claim"] is False
