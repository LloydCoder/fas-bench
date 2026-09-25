from pathlib import Path

import pytest

from fas_bench.verification import (
    canonical_json,
    digest_tree,
    reference_graph_identity,
    reference_line_range,
    reference_path,
    reference_score,
)


def test_reference_canonical_and_tree(tmp_path):
    assert canonical_json({"b": 2, "a": [1, "✓"]}) == canonical_json({"a": [1, "✓"], "b": 2})
    with pytest.raises(ValueError):
        canonical_json({"x": float("nan")})
    (tmp_path / "b").write_text("b", encoding="utf-8")
    (tmp_path / "a").write_text("a", encoding="utf-8")
    (tmp_path / "link").symlink_to(tmp_path / "a")
    first = digest_tree(tmp_path)
    (tmp_path / "link").unlink()
    assert first == digest_tree(tmp_path)


def test_reference_location_graph_score():
    assert reference_line_range("a\nb\nc\n", 2, 3) == "b\nc"
    with pytest.raises(ValueError):
        reference_line_range("a\n", 0, 1)
    root = Path.cwd()
    assert reference_path(root, "README.md").is_file()
    with pytest.raises(ValueError):
        reference_path(root, "/etc/passwd")
    with pytest.raises(ValueError):
        reference_path(root, "../outside")
    nodes = [{"id": "b"}, {"id": "a"}]
    edges = [{"source": "a", "target": "b"}]
    assert reference_graph_identity(nodes, edges) == reference_graph_identity(
        list(reversed(nodes)), edges
    )
    assert reference_score(3, 4) == 0.75
    with pytest.raises(ValueError):
        reference_score(5, 4)
