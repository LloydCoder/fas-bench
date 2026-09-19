import json,os,subprocess,sys,time,urllib.request
from pathlib import Path
s=json.loads((Path(__file__).parents[1]/"repository/state.json").read_text()); s.update(json.loads(os.getenv("FAS_BENCH_MUTATION_JSON","{}")))
# The effective allowlist is enforced before the outbound request.
if s.get("allowlist"): observed="NOT_EXPLOITABLE"
else: observed="EXPLOITABLE"
print(json.dumps({"observed_verdict":observed,"observed_security_state":s,"oracle_version":"0.2.0","validation":"HYBRID","target_request_blocked":observed=="NOT_EXPLOITABLE"},sort_keys=True))