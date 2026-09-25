from fas_bench.canonical import canonical_json as production_canonical
from fas_bench.phase10 import digest_tree as production_tree
from fas_bench.verification import (
    canonical_json as reference_canonical,
    digest_tree as reference_tree,
)


def test_canonical_differential():
    fixtures = [
        {},
        {"a": 1, "b": [True, None, "✓"]},
        {"nested": {"z": -1, "a": 0}},
    ]
    for value in fixtures:
        assert production_canonical(value) == reference_canonical(value)


def test_tree_digest_differential(tmp_path):
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    assert production_tree(tmp_path) == reference_tree(tmp_path)
