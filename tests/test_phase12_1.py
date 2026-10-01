from fas_bench.phase12_1 import ReviewRecord, cohens_kappa, phase12_1_gate


def _reviewer(**overrides):
    value = {
        "evaluator_id": "reviewer-1",
        "independence": True,
        "blinded": True,
        "case_count": 20,
        "methodology_digest": "a" * 64,
        "environment_digest": "b" * 64,
        "status": "COMPLETE",
        "limitations": ("public corpus",),
    }
    value.update(overrides)
    return ReviewRecord(**value)


def test_cohens_kappa_perfect_agreement():
    assert cohens_kappa(["A", "B", "A"], ["A", "B", "A"]) == 1.0


def test_gate_requires_independent_review():
    result = phase12_1_gate([_reviewer(independence=False)])
    assert result["status"] == "FAIL"
    assert result["external_validation_claim"] is False


def test_gate_accepts_review_protocol_record():
    result = phase12_1_gate([_reviewer()])
    assert result["status"] == "PASS"
    assert result["requires_external_evidence"] is True
