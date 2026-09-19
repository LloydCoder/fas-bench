import json
from pathlib import Path

from jsonschema import Draft202012Validator

from fas_bench.contract import CASE_IDS
from fas_bench.validation import FAMILY_PATHS, load_schema, validate

ROOT = Path(__file__).parents[1]
VALID = ROOT / "tests/fixtures/valid"
INVALID = ROOT / "tests/fixtures/invalid"


def test_schema_meta_validation():
    for family in FAMILY_PATHS:
        schema = load_schema(family)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["$id"].startswith("https://fas-bench.dev/schemas/")
        Draft202012Validator.check_schema(schema)


def test_valid_fixtures_pass():
    for family in FAMILY_PATHS:
        path = VALID / f"{family}.json"
        assert path.exists(), path
        assert validate(
            json.loads(path.read_text()), family, True, set(CASE_IDS)
        ).status == "VALID"


def test_invalid_fixtures_fail():
    for path in INVALID.glob("*.json"):
        family = path.name.split("__", 1)[0]
        assert validate(
            json.loads(path.read_text()), family, True, set(CASE_IDS)
        ).status != "VALID"


def test_graph_semantics():
    document = json.loads((VALID / "attack-graph.json").read_text())
    document["paths"][0]["edge_ids"] = ["E-missing"]
    assert validate(document, "attack-graph").status == "SEMANTIC_INVALID"


def test_submission_semantics():
    document = json.loads((VALID / "submission.json").read_text())
    document["verdict"]["evidence_ids"] = ["EVD-missing"]
    assert validate(document, "submission").status == "SEMANTIC_INVALID"


def test_evaluation_integrity():
    document = json.loads((VALID / "evaluation-result.json").read_text())
    document["final_score"] = 0.5
    assert validate(document, "evaluation-result").status == "SEMANTIC_INVALID"
