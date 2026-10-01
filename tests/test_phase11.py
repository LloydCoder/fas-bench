from fas_bench.phase11 import phase11_gate, validate_mutation_semantics


def test_security_changing_mutation_requires_oracle():
    ok, reason = validate_mutation_semantics(
        semantic_class="SECURITY_WEAKENED",
        source_before=b"before",
        source_after=b"after",
        oracle=None,
    )
    assert not ok and "oracle" in reason


def test_security_changing_mutation_requires_positive_oracle():
    ok, reason = validate_mutation_semantics(
        semantic_class="CONTROL_REMOVED",
        source_before=b"before",
        source_after=b"after",
        oracle=lambda before, after: True,
    )
    assert ok and reason == "validated"


def test_invalid_mutation_is_rejected():
    ok, _ = validate_mutation_semantics(
        semantic_class="INVALID",
        source_before=b"before",
        source_after=b"after",
        oracle=lambda before, after: True,
    )
    assert not ok


def test_phase11_gate_accepts_canonical_shape():
    result = phase11_gate(
        [
            {
                "case_id": "FAS-001",
                "category": "C1_REACHABILITY",
                "difficulty": "L2_MULTI_FUNCTION",
                "provenance": "SYNTHETIC",
                "validation_type": "DYNAMIC",
                "phase10_lifecycle": "ORACLE_VALIDATED",
            }
        ]
    )
    assert result["status"] == "PASS" and result["case_count"] == 1
