from dataclasses import replace

from fas_bench.test_registry import (
    TestLifecycle,
    TestSpec,
    coverage_matrix,
    registry_validate,
)


def spec(test_id="FAS-REG-001", lifecycle=TestLifecycle.DRAFT):
    return TestSpec(
        test_id=test_id,
        version="1.0.0",
        title="registry test",
        objective="verify a security condition",
        primary_category="C1",
        difficulty="L2",
        oracle_type="STATIC",
        evidence_requirements=("source", "sink"),
        lifecycle=lifecycle,
    )


def test_identity_is_stable_and_order_independent():
    a = spec()
    b = replace(a, evidence_requirements=("sink", "source"))
    assert a.identity() == b.identity()


def test_registry_rejects_duplicate_ids():
    result = registry_validate([spec(), spec()])
    assert result["status"] == "FAIL"


def test_released_test_requires_source_digest():
    result = registry_validate([spec(lifecycle=TestLifecycle.RELEASED)])
    assert result["status"] == "FAIL"


def test_coverage_matrix_is_deterministic():
    assert coverage_matrix([spec(), spec("FAS-REG-002")]) == {"C1": 2}
