import json
from pathlib import Path
from jsonschema import Draft202012Validator
def test_execution_schema_is_valid():
 s=json.loads(Path("schemas/execution-result.schema.json").read_text())
 Draft202012Validator.check_schema(s)
