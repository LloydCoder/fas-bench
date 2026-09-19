import json,os
from pathlib import Path
s=json.loads((Path(__file__).parents[1]/"repository/state.json").read_text())
if os.environ.get("FAS_BENCH_MUTATION_JSON"): s.update(json.loads(os.environ["FAS_BENCH_MUTATION_JSON"]))
v="REMEDIATION_FAILED" if s.get("alternate_path_viable") else ("REMEDIATED" if s.get("primary_protected") else "EXPLOITABLE")
print(json.dumps({"observed_verdict":v,"observed_security_state":s,"oracle_version":"0.1.0"}))