import json,os,urllib.request
from pathlib import Path
s=json.loads((Path(__file__).parents[1]/"repository/state.json").read_text()); s.update(json.loads(os.getenv("FAS_BENCH_MUTATION_JSON","{}")))
# Synthetic local target: reachability is the security property, not process success.
observed="EXPLOITABLE" if s.get("path_viable") and not s.get("allowlist",False) else "NOT_EXPLOITABLE"
print(json.dumps({"observed_verdict":observed,"observed_security_state":s,"oracle_version":"0.2.0","validation":"HYBRID","target_reached":observed=="EXPLOITABLE"},sort_keys=True))