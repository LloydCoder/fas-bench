import json,os
from pathlib import Path
s=json.loads((Path(__file__).parents[1]/"repository/state.json").read_text())
if os.environ.get("FAS_BENCH_MUTATION_JSON"): s.update(json.loads(os.environ["FAS_BENCH_MUTATION_JSON"]))
v="EXPLOITABLE" if s.get("path_viable") and not s.get("tool_authorization") else "NOT_EXPLOITABLE"
print(json.dumps({"observed_verdict":v,"observed_security_state":s,"oracle_version":"0.1.0"},sort_keys=True))