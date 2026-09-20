from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from fas_bench.graph import (
    GraphLimits,
    canonicalize_graph,
    compare_graphs,
    diff_graphs,
    extract_paths,
    graph_digest,
    minimal_security_paths,
    validate_graph,
)

ROOT = Path(__file__).parents[1]
CASES = ROOT / "cases"


def load_graph(case_id: str) -> dict:
    return json.loads(
        (CASES / case_id / "expected" / "attack_graph.json").read_text(encoding="utf-8")
    )


@pytest.mark.parametrize("number", range(1, 21))
def test_all_public_gold_graphs_validate(number: int):
    graph = load_graph(f"FAS-{number:03d}")
    result = validate_graph(graph, case_id=f"FAS-{number:03d}")
    assert result.valid, result.as_dict()


@pytest.mark.parametrize("number", range(1, 21))
def test_gold_graph_compares_to_itself_at_maximum(number: int):
    graph = load_graph(f"FAS-{number:03d}")
    result = compare_graphs(graph, copy.deepcopy(graph), case_id=f"FAS-{number:03d}")
    assert result.valid
    assert result.metrics.graph_score == pytest.approx(1.0)
    assert result.metrics.node.f1 == pytest.approx(1.0)
    assert result.metrics.edge.f1 == pytest.approx(1.0)
    assert result.metrics.path_completeness == pytest.approx(1.0)


def test_serialization_and_ordering_invariance():
    graph = load_graph("FAS-002")
    reordered = copy.deepcopy(graph)
    reordered["nodes"] = list(reversed(reordered["nodes"]))
    reordered["edges"] = list(reversed(reordered["edges"]))
    reordered["paths"] = list(reversed(reordered["paths"]))
    assert graph_digest(graph) == graph_digest(reordered)
    assert canonicalize_graph(canonicalize_graph(graph)) == canonicalize_graph(graph)


def test_empty_graph_is_valid_input_but_scores_zero():
    expected = load_graph("FAS-002")
    empty = {
        "graph_id": "G-EMPTY",
        "benchmark_version": "0.1.0",
        "schema_version": "0.1",
        "nodes": [],
        "edges": [],
        "paths": [],
        "metadata": {"case_id": "FAS-002"},
    }
    assert validate_graph(empty, case_id="FAS-002").valid
    result = compare_graphs(expected, empty, case_id="FAS-002")
    assert result.metrics.graph_score == pytest.approx(0.0)


def test_fabricated_edge_does_not_improve_score():
    expected = load_graph("FAS-002")
    submission = copy.deepcopy(expected)
    extra = copy.deepcopy(submission["edges"][0])
    extra["edge_id"] = "E-002-FABRICATED"
    extra["target"] = submission["nodes"][-1]["node_id"]
    submission["edges"].append(extra)
    result = compare_graphs(expected, submission, case_id="FAS-002")
    assert "E-002-FABRICATED" in result.metrics.unsupported_edges
    assert result.metrics.graph_score < 1.0


def test_fabricated_privileged_identity_is_detected_as_unsupported():
    expected = load_graph("FAS-002")
    submission = copy.deepcopy(expected)
    submission["nodes"].append({"node_id": "N-002-admin", "type": "IDENTITY", "name": "admin"})
    submission["edges"].append(
        {
            "edge_id": "E-002-admin",
            "type": "AUTHENTICATES_AS",
            "source": "N-002-input",
            "target": "N-002-admin",
        }
    )
    result = compare_graphs(expected, submission, case_id="FAS-002")
    assert "E-002-admin" in result.metrics.unsupported_edges


def test_reversed_edge_is_not_semantically_equivalent():
    expected = load_graph("FAS-002")
    submission = copy.deepcopy(expected)
    submission["edges"][1]["source"], submission["edges"][1]["target"] = (
        submission["edges"][1]["target"],
        submission["edges"][1]["source"],
    )
    result = compare_graphs(expected, submission, case_id="FAS-002")
    assert result.metrics.edge.f1 < 1.0


def test_duplicate_and_dangling_edges_are_rejected():
    graph = load_graph("FAS-002")
    graph["edges"].append(copy.deepcopy(graph["edges"][0]))
    graph["edges"][-1]["edge_id"] = graph["edges"][0]["edge_id"]
    graph["edges"].append(
        {
            "edge_id": "E-002-DANGLING",
            "type": "CALLS",
            "source": "N-002-input",
            "target": "N-NOT-REAL",
        }
    )
    result = validate_graph(graph, case_id="FAS-002")
    codes = {d.code for d in result.diagnostics}
    assert "DUPLICATE_EDGE" in codes
    assert "DANGLING_REFERENCE" in codes


def test_disconnected_path_is_rejected():
    graph = load_graph("FAS-002")
    graph["paths"][0]["node_ids"] = [graph["nodes"][0]["node_id"], graph["nodes"][2]["node_id"]]
    result = validate_graph(graph, case_id="FAS-002")
    assert any(d.code == "DISCONNECTED_PATH" for d in result.diagnostics)


def test_cycle_safe_path_extraction():
    graph = {
        "graph_id": "G-CYCLE",
        "benchmark_version": "0.1.0",
        "schema_version": "0.1",
        "nodes": [
            {"node_id": "N-a", "type": "ACTOR", "name": "a"},
            {"node_id": "N-b", "type": "SERVICE", "name": "b"},
            {"node_id": "N-c", "type": "IMPACT", "name": "c"},
        ],
        "edges": [
            {"edge_id": "E-ab", "type": "CALLS", "source": "N-a", "target": "N-b"},
            {"edge_id": "E-ba", "type": "CALLS", "source": "N-b", "target": "N-a"},
            {"edge_id": "E-bc", "type": "REACHES", "source": "N-b", "target": "N-c"},
        ],
        "paths": [],
        "entry_points": ["N-a"],
    }
    paths = extract_paths(graph, limits=GraphLimits(max_path_length=10))
    assert ("N-a", "N-b", "N-c") in paths


def test_path_explosion_is_bounded():
    nodes = [{"node_id": "N-0", "type": "ACTOR", "name": "entry"}]
    edges = []
    for i in range(1, 30):
        nodes.append({"node_id": f"N-{i}", "type": "SERVICE", "name": f"s{i}"})
        edges.append({"edge_id": f"E-{i}", "type": "CALLS", "source": "N-0", "target": f"N-{i}"})
    nodes.append({"node_id": "N-impact", "type": "IMPACT", "name": "impact"})
    for i in range(1, 30):
        edges.append(
            {"edge_id": f"E-i-{i}", "type": "REACHES", "source": f"N-{i}", "target": "N-impact"}
        )
    graph = {
        "graph_id": "G-WIDE",
        "benchmark_version": "0.1.0",
        "schema_version": "0.1",
        "nodes": nodes,
        "edges": edges,
        "paths": [],
        "entry_points": ["N-0"],
    }
    paths = extract_paths(graph, limits=GraphLimits(max_paths=5))
    assert len(paths) <= 5


def test_limits_reject_oversized_submission():
    graph = load_graph("FAS-002")
    result = validate_graph(graph, limits=GraphLimits(max_nodes=2))
    assert not result.valid
    assert any(d.code == "GRAPH_LIMIT_EXCEEDED" for d in result.diagnostics)


def test_diff_is_empty_for_identical_graphs():
    graph = load_graph("FAS-020")
    assert diff_graphs(graph, graph) == {
        "added_nodes": [],
        "removed_nodes": [],
        "added_edges": [],
        "removed_edges": [],
        "changed_nodes": [],
        "changed_edges": [],
        "node_identity_changes": [],
    }


def test_diff_ignores_ordering_but_reports_security_edge_change():
    before = load_graph("FAS-020")
    after = copy.deepcopy(before)
    after["nodes"] = list(reversed(after["nodes"]))
    after["edges"] = list(reversed(after["edges"]))
    assert diff_graphs(before, after)["added_edges"] == []
    after["edges"][0]["type"] = "CONTROLS"
    assert after["edges"][0]["edge_id"] in diff_graphs(before, after)["changed_edges"]


def test_missing_security_transition_reduces_completeness():
    expected = load_graph("FAS-002")
    submission = copy.deepcopy(expected)
    submission["paths"][0]["node_ids"] = [
        expected["nodes"][0]["node_id"],
        expected["nodes"][2]["node_id"],
    ]
    submission["paths"][0]["edge_ids"] = [expected["edges"][1]["edge_id"]]
    result = compare_graphs(expected, submission, case_id="FAS-002")
    assert result.metrics.path_completeness < 1.0


def test_semantic_alias_can_match_without_id_equality():
    expected = load_graph("FAS-002")
    submission = copy.deepcopy(expected)
    for node in submission["nodes"]:
        node["node_id"] = node["node_id"].replace("002", "999")
    for edge in submission["edges"]:
        edge["edge_id"] = edge["edge_id"].replace("002", "999")
        edge["source"] = edge["source"].replace("002", "999")
        edge["target"] = edge["target"].replace("002", "999")
    for path in submission["paths"]:
        path["path_id"] = path["path_id"].replace("002", "999")
        path["node_ids"] = [n.replace("002", "999") for n in path["node_ids"]]
        path["edge_ids"] = [e.replace("002", "999") for e in path["edge_ids"]]
        path["entry_node"] = path["entry_node"].replace("002", "999")
        path["impact_node"] = path["impact_node"].replace("002", "999")
    result = compare_graphs(expected, submission, case_id="FAS-002")
    assert result.metrics.node.f1 == pytest.approx(1.0)


def test_graph_saturation_is_not_maximum():
    expected = load_graph("FAS-002")
    submission = copy.deepcopy(expected)
    for i in range(20):
        submission["nodes"].append(
            {"node_id": f"N-extra-{i}", "type": "SERVICE", "name": f"extra-{i}"}
        )
    result = compare_graphs(expected, submission, case_id="FAS-002")
    assert result.metrics.graph_score < 1.0


def test_minimal_security_path_is_cycle_safe():
    graph = load_graph("FAS-002")
    assert minimal_security_paths(graph)
