from fas_bench.contamination import (
    ContaminationFinding, ContaminationStatus, CorpusSet, CorpusVisibility,
    contamination_gate,
)


def corpus(visibility=CorpusVisibility.PUBLIC_PRACTICE):
    return CorpusSet("official-v1", "1.0.0", visibility, ("a" * 64,), "restricted", "2026-01-01" if visibility == CorpusVisibility.PRIVATE_OFFICIAL else None)


def test_identity_is_content_derived():
    assert corpus().identity() == corpus().identity()


def test_official_requires_assessment():
    assert contamination_gate(corpus(CorpusVisibility.PRIVATE_OFFICIAL), [])["status"] == "FAIL"


def test_confirmed_contamination_blocks_official():
    c = corpus(CorpusVisibility.PRIVATE_OFFICIAL)
    f = ContaminationFinding(c.corpus_id, ContaminationStatus.CONFIRMED, "training-corpus", "b" * 64)
    assert contamination_gate(c, [f])["status"] == "FAIL"


def test_clean_official_corpus_passes():
    c = corpus(CorpusVisibility.PRIVATE_OFFICIAL)
    f = ContaminationFinding(c.corpus_id, ContaminationStatus.CLEAN, "review", "b" * 64)
    assert contamination_gate(c, [f])["status"] == "PASS"
