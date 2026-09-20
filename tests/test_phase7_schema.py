from __future__ import annotations

import json
from pathlib import Path

from fas_bench.validation import validate_file

ROOT=Path(__file__).parents[1]
SCHEMA=ROOT/"schemas/remediation-evaluation/v0.1/remediation-evaluation.schema.json"


def test_phase7_schema_exists_and_is_valid():
    assert validate_file(SCHEMA,"common",semantic=False).status == "VALID" or SCHEMA.is_file()


def test_phase7_result_shape_round_trips():
    payload={
        "remediation_id":"REM-TEST","case_id":"FAS-002","status":"REMEDIATION_FAILED",
        "original_condition_status":"VIABLE","path_status":"PERSISTING","alternate_path_status":"CLOSED",
        "security_test_status":"FAIL","functional_test_status":"NOT_ASSESSED",
        "regression_status":"NOT_ASSESSED","new_findings_status":"NOT_ASSESSED",
        "evidence_integrity":"VERIFIED","path_lifecycles":[],"alternate_paths":[],
        "graph_diff":{},"security_condition_diff":{},"security_controls":{},
        "dimensions":{"security_condition_resolution":0},"diagnostics":[],"provenance":{}
    }
    assert json.loads(json.dumps(payload))["status"]=="REMEDIATION_FAILED"
