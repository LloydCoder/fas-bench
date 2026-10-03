import math

from fas_bench.ecosystem import (
    Lifecycle,
    ProvenanceEdge,
    ResultRecord,
    ResultStatus,
    SubmissionManifest,
    governance_transition,
    provenance_gate,
)


def manifest():
    return SubmissionManifest(
        "system",
        "1",
        "model",
        "a" * 64,
        "b" * 64,
        "c" * 64,
        "d" * 64,
        "1",
    )


def test_submission_identity_is_deterministic():
    assert manifest().identity() == manifest().identity()


def test_submission_requires_identity_fields():
    invalid = SubmissionManifest("", "1", "model", "a", "b", "c", "d", "1")
    assert invalid.validate()


def test_result_rejects_invalid_score():
    result = ResultRecord(
        "r",
        "a" * 64,
        "s",
        "b" * 64,
        "e",
        1.1,
        (0, 1),
        ResultStatus.VALID,
        "p",
    )
    assert result.validate()


def test_result_rejects_non_finite_values():
    result = ResultRecord(
        "r",
        "a" * 64,
        "s" * 64,
        "b" * 64,
        "e" * 64,
        math.nan,
        (0, 1),
        ResultStatus.VALID,
        "p" * 64,
    )
    assert result.validate()


def test_provenance_requires_complete_edges():
    edge = ProvenanceEdge("source", "build", "PRODUCED", "a" * 64, "actor")
    assert provenance_gate([edge])["status"] == "PASS"


def test_provenance_rejects_self_edges():
    edge = ProvenanceEdge("source", "source", "PRODUCED", "a" * 64, "actor")
    assert provenance_gate([edge])["status"] == "FAIL"


def test_release_requires_human_approval():
    assert not governance_transition(Lifecycle.CERTIFIED, Lifecycle.RELEASED)["allowed"]
    assert governance_transition(Lifecycle.CERTIFIED, Lifecycle.RELEASED, True)["allowed"]

def test_provenance_rejects_cycles():
    edges = [
        ProvenanceEdge("source", "build", "PRODUCED", "a" * 64, "actor"),
        ProvenanceEdge("build", "source", "DERIVED_FROM", "b" * 64, "actor"),
    ]
    assert provenance_gate(edges)["status"] == "FAIL"

def test_retirement_requires_human_approval():
    assert not governance_transition(
        Lifecycle.DEPRECATED, Lifecycle.RETIRED
    )["allowed"]
    assert governance_transition(
        Lifecycle.DEPRECATED, Lifecycle.RETIRED, True
    )["allowed"]
