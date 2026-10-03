from dataclasses import replace

from fas_bench import test_registry


def spec(
    test_id="FAS-REG-001",
    version="1.0.0",
    lifecycle=test_registry.TestLifecycle.DRAFT,
    source_digest="",
):
    return test_registry.TestSpec(
        test_id=test_id,
        version=version,
        title="registry test",
        objective="verify a security condition",
        primary_category="C1",
        difficulty="L2",
        oracle_type="STATIC",
        evidence_requirements=("source", "sink"),
        lifecycle=lifecycle,
        source_digest=source_digest,
    )


def test_identity_is_stable_and_order_independent():
    a = spec()
    b = replace(a, evidence_requirements=("sink", "source"))
    assert a.identity() == b.identity()


def test_identity_is_stable_across_lifecycle_transitions():
    assert spec().identity() == spec(lifecycle=test_registry.TestLifecycle.REVIEW).identity()


def test_registry_rejects_duplicate_versions_but_allows_history():
    assert registry_validate([spec(), spec(version="2.0.0")])["status"] == "PASS"
    assert registry_validate([spec(), spec()])["status"] == "FAIL"


def test_released_test_requires_source_digest():
    assert (
        registry_validate([spec(lifecycle=test_registry.TestLifecycle.RELEASED)])["status"]
        == "FAIL"
    )
    assert (
        registry_validate([spec(lifecycle=test_registry.TestLifecycle.RELEASED, source_digest="a" * 64)])[
            "status"
        ]
        == "PASS"
    )


def test_duplicate_requirements_are_rejected():
    invalid = replace(spec(), evidence_requirements=("source", "source"))
    assert registry_validate([invalid])["status"] == "FAIL"


def test_lifecycle_transitions_are_monotonic():
    assert lifecycle_transition_allowed(
        test_registry.TestLifecycle.DRAFT, test_registry.TestLifecycle.REVIEW
    )
    assert not lifecycle_transition_allowed(
        test_registry.TestLifecycle.RETIRED, test_registry.TestLifecycle.DRAFT
    )


def test_coverage_matrix_is_deterministic():
    assert coverage_matrix([spec(), spec("FAS-REG-002")]) == {"C1": 2}
