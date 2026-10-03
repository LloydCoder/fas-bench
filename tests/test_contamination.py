from fas_bench.contamination import (
    ContaminationFinding,
    ContaminationStatus,
    CorpusSet,
    CorpusVisibility,
    contamination_gate,
)


def corpus(visibility=CorpusVisibility.PUBLIC_PRACTICE):
    cutoff = (
        "2026-01-01"
        if visibility in {CorpusVisibility.PRIVATE_OFFICIAL, CorpusVisibility.PRIVATE_HOLDOUT}
        else None
    )
    return CorpusSet("official-v1", "1.0.0", visibility, ("a" * 64,), "restricted", cutoff)


def test_identity_is_content_derived():
    assert corpus().identity() == corpus().identity()


def test_official_requires_assessment():
    result = contamination_gate(corpus(CorpusVisibility.PRIVATE_OFFICIAL), [])
    assert result["status"] == "FAIL"


def test_unknown_contamination_does_not_pass():
    c = corpus(CorpusVisibility.PRIVATE_OFFICIAL)
    finding = ContaminationFinding(c.corpus_id, ContaminationStatus.UNKNOWN, "review", "b" * 64)
    assert contamination_gate(c, [finding])["status"] == "FAIL"


def test_confirmed_contamination_blocks_official():
    c = corpus(CorpusVisibility.PRIVATE_OFFICIAL)
    finding = ContaminationFinding(
        c.corpus_id, ContaminationStatus.CONFIRMED, "training-corpus", "b" * 64
    )
    assert contamination_gate(c, [finding])["status"] == "FAIL"


def test_invalid_digest_and_temporal_scope_fail_closed():
    c = CorpusSet(
        "official-v1",
        "1.0.0",
        CorpusVisibility.PRIVATE_HOLDOUT,
        ("not-a-digest",),
        "restricted",
        "not-a-date",
    )
    assert contamination_gate(c, [])["status"] == "FAIL"


def test_clean_official_corpus_passes():
    c = corpus(CorpusVisibility.PRIVATE_OFFICIAL)
    finding = ContaminationFinding(c.corpus_id, ContaminationStatus.CLEAN, "review", "b" * 64)
    assert contamination_gate(c, [finding])["status"] == "PASS"


def test_private_public_access_policy_fails_closed():
    c = CorpusSet(
        "official-v1",
        "1.0.0",
        CorpusVisibility.PRIVATE_OFFICIAL,
        ("a" * 64,),
        "public",
        "2026-01-01",
    )
    assert contamination_gate(c, [])["status"] == "FAIL"
