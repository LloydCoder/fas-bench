from fas_bench.verification import certify


def test_certification_requires_all_mandatory_checks():
    good = {
        key: {"status": "PASS"}
        for key in (
            "implementation",
            "independent_verification",
            "reproducibility",
            "security",
            "release",
        )
    }
    assert certify(good, {"version": "0.1.0"})["status"] == "CERTIFIED"


def test_not_assessed_blocks_certification():
    checks = {
        "implementation": {"status": "PASS"},
        "independent_verification": {"status": "NOT_ASSESSED"},
        "reproducibility": {"status": "PASS"},
        "security": {"status": "PASS"},
        "release": {"status": "PASS"},
    }
    assert certify(checks, {"version": "0.1.0"})["status"] == "NOT_CERTIFIED"
