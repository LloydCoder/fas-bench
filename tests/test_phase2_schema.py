import json
from pathlib import Path
from jsonschema import Draft202012Validator
from fas_bench.contract import CASE_IDS
from fas_bench.validation import FAMILY_PATHS,load_schema,validate
ROOT=Path(__file__).parents[1]; VALID=ROOT/"tests/fixtures/valid"; INVALID=ROOT/"tests/fixtures/invalid"
def test_schema_meta_validation():
 for family in FAMILY_PATHS:
  s=load_schema(family); assert s["$schema"]=="https://json-schema.org/draft/2020-12/schema"; assert s["$id"].startswith("https://fas-bench.dev/schemas/"); Draft202012Validator.check_schema(s)
def test_valid_fixtures_pass():
 for family in FAMILY_PATHS:
  p=VALID/f"{family}.json"; assert p.exists(),p; assert validate(json.loads(p.read_text()),family,True,set(CASE_IDS)).status=="VALID"
def test_invalid_fixtures_fail():
 for p in INVALID.glob("*.json"):
  family=p.name.split("__",1)[0]; assert validate(json.loads(p.read_text()),family,True,set(CASE_IDS)).status!="VALID"
def test_graph_semantics():
 d=json.loads((VALID/"attack-graph.json").read_text()); d["paths"][0]["edge_ids"]=["E-missing"]; assert validate(d,"attack-graph").status=="SEMANTIC_INVALID"
def test_submission_semantics():
 d=json.loads((VALID/"submission.json").read_text()); d["verdict"]["evidence_ids"]=["EVD-missing"]; assert validate(d,"submission").status=="SEMANTIC_INVALID"
def test_evaluation_integrity():
 d=json.loads((VALID/"evaluation-result.json").read_text()); d["final_score"]=.5; assert validate(d,"evaluation-result").status=="SEMANTIC_INVALID"
