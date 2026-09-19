import json, os
from pathlib import Path
STATE=json.loads((Path(__file__).parents[1]/"repository"/"state.json").read_text())
def decide(s):
    if "FAS-002"=="FAS-008": return "CONDITIONALLY_EXPLOITABLE" if s.get("prerequisite_satisfied") else "NOT_EXPLOITABLE"
    if "FAS-002"=="FAS-020":
        if s.get("alternate_path_viable"): return "REMEDIATION_FAILED"
        return "REMEDIATED" if s.get("primary_protected") else "EXPLOITABLE"
    if "FAS-002" in ("FAS-013","FAS-019"): return "REMEDIATED" if not s.get("path_viable") else "EXPLOITABLE"
    if "FAS-002"=="FAS-012" and not s.get("reachability_evidence"): return "UNKNOWN"
    if s.get("path_viable"): return "EXPLOITABLE"
    return "EXPLOITABLE"
state=dict(STATE)
if os.environ.get("FAS_BENCH_MUTATION_JSON"): state.update(json.loads(os.environ["FAS_BENCH_MUTATION_JSON"]))
print(json.dumps({"observed_verdict":decide(state),"observed_security_state":state,"oracle_version":"0.1.0"},sort_keys=True))
