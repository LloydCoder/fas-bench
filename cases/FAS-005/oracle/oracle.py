import json,os
from pathlib import Path
s=json.loads((Path(__file__).parents[1]/"repository/state.json").read_text())
if os.environ.get("FAS_BENCH_MUTATION_JSON"): s.update(json.loads(os.environ["FAS_BENCH_MUTATION_JSON"]))
if "FAS-005"=="FAS-008": v="CONDITIONALLY_EXPLOITABLE" if s.get("prerequisite_satisfied") else "NOT_EXPLOITABLE"
else: v="EXPLOITABLE" if s.get("path_viable") else "NOT_EXPLOITABLE"
print(json.dumps({"observed_verdict":v,"observed_security_state":s,"oracle_version":"0.1.0"},sort_keys=True))
