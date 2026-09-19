import json
from pathlib import Path

state = json.loads((Path(__file__).parents[1] / "repository/state.json").read_text())
if not state.get("reachability_evidence"):
    observed = "UNKNOWN"
else:
    observed = "EXPLOITABLE" if state.get("path_viable") else "NOT_EXPLOITABLE"
print(json.dumps({"observed_verdict": observed, "observed_security_state": state, "oracle_version": "0.1.0"}, sort_keys=True))
