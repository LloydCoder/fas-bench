from __future__ import annotations

from jsonschema import Draft202012Validator

from fas_bench.validation import load_schema, validate



def test_phase7_schema_is_valid():
    document = load_schema("remediation-evaluation")
    Draft202012Validator.check_schema(document)


def test_phase7_result_shape_validates():
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
    assert validate(payload, "remediation-evaluation").status == "VALID"
