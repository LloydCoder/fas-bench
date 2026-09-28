from fas_bench.verification import certify


def _good_checks():
    names = (
        "implementation",
        "independent_verification",
        "reproducibility",
        "security",
        "release",
        "corpus",
        "scoring",
    )
    return {key: {"status": "PASS", "source": "derived"} for key in names}


def test_certification_requires_all_mandatory_checks():
    assert certify(_good_checks(), {"version": "0.1.0"})["status"] == "CERTIFIED"


def test_not_assessed_blocks_certification():
    checks = _good_checks()
    checks["independent_verification"] = {"status": "NOT_ASSESSED", "source": "derived"}
    assert certify(checks, {"version": "0.1.0"})["status"] == "NOT_CERTIFIED"


def test_self_declared_checks_block_certification():
    checks = _good_checks()
    checks["security"] = {"status": "PASS"}
    assert certify(checks, {"version": "0.1.0"})["status"] == "NOT_CERTIFIED"


def test_missing_full_contract_checks_block_certification():
    checks = _good_checks()
    del checks["corpus"]
    assert certify(checks, {"version": "0.1.0"})["status"] == "NOT_CERTIFIED"
