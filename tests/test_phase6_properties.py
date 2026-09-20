from __future__ import annotations

import copy
import json
import random
from pathlib import Path

from fas_bench.graph import canonicalize_graph, compare_graphs, diff_graphs, graph_digest

ROOT = Path(__file__).parents[1]


def _graph():
    return json.loads((ROOT / "cases/FAS-004/expected/attack_graph.json").read_text(encoding="utf-8"))


def test_canonicalization_idempotence_property():
    graph = _graph()
    assert canonicalize_graph(canonicalize_graph(graph)) == canonicalize_graph(graph)


def test_digest_permutation_property():
    graph = _graph()
    baseline = graph_digest(graph)
    rng = random.Random(20260920)
    for _ in range(50):
        candidate = copy.deepcopy(graph)
        rng.shuffle(candidate["nodes"])
        rng.shuffle(candidate["edges"])
        rng.shuffle(candidate["paths"])
        assert graph_digest(candidate) == baseline


def test_identity_diff_property():
    graph = _graph()
    assert diff_graphs(graph, graph)["added_nodes"] == []
    assert diff_graphs(graph, graph)["removed_nodes"] == []
    assert diff_graphs(graph, graph)["added_edges"] == []
    assert diff_graphs(graph, graph)["removed_edges"] == []


def test_score_reflexivity_property():
    graph = _graph()
    result = compare_graphs(graph, graph, case_id="FAS-004")
    assert result.metrics.graph_score == 1.0
