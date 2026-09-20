from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).parents[1]
SCHEMA = ROOT / "schemas/remediation-evaluation/v0.1/remediation-evaluation.schema.json"


def test_phase7_schema_is_valid():
    document = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(document)


def test_phase7_result_shape_validates():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    payload = {
        "remediation_id": "REM-TEST",
        "case_id": "FAS-002",
        "status": "REMEDIATION_FAILED",
        "original_condition_status": "VIABLE",
        "path_status": "PERSISTING",
        "alternate_path_status": "CLOSED",
        "security_test_status": "FAIL",
        "functional_test_status": "NOT_ASSESSED",
        "regression_status": "NOT_ASSESSED",
        "new_findings_status": "NOT_ASSESSED",
        "evidence_integrity": "VERIFIED",
        "path_lifecycles": [],
        "alternate_paths": [],
        "graph_diff": {},
        "security_condition_diff": {},
        "security_controls": {},
        "dimensions": {"security_condition_resolution": 0},
        "diagnostics": [],
        "provenance": {},
    }
    Draft202012Validator(schema).validate(payload)
