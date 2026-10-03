from fas_bench.adversarial import (
    AdversarialCase,
    AttackClass,
    RobustnessResult,
    RobustnessStatus,
    robustness_gate,
)


def case():
    return AdversarialCase(
        "A-1",
        "1.0",
        AttackClass.PROMPT_INJECTION,
        "agent-input",
        "ignore_untrusted_instruction",
        "a" * 64,
        "b" * 64,
    )


def result(status=RobustnessStatus.PASS, attack_id="A-1"):
    return RobustnessResult(
        attack_id, status, "ignore_untrusted_instruction", "c" * 64, "run-1"
    )


def test_identity_is_deterministic():
    assert case().identity() == case().identity()


def test_missing_result_fails_closed():
    assert robustness_gate([case()], [])["status"] == "FAIL"


def test_infrastructure_failure_is_not_a_security_pass():
    result_value = robustness_gate(
        [case()], [result(RobustnessStatus.INFRASTRUCTURE_FAILURE)]
    )
    assert result_value["status"] == "FAIL"


def test_failed_result_is_not_a_robustness_pass():
    assert robustness_gate([case()], [result(RobustnessStatus.FAIL)])["status"] == "FAIL"


def test_unknown_result_is_not_a_robustness_pass():
    assert robustness_gate([case()], [result(RobustnessStatus.UNKNOWN)])["status"] == "FAIL"


def test_extra_result_is_rejected():
    assert robustness_gate([case()], [result(attack_id="A-2")])["status"] == "FAIL"


def test_matching_oracle_result_passes():
    assert robustness_gate([case()], [result()])["status"] == "PASS"
