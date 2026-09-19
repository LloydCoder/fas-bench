import json,os
from pathlib import Path
s=json.loads((Path(__file__).parents[1]/"repository/state.json").read_text()); s.update(json.loads(os.getenv("FAS_BENCH_MUTATION_JSON","{}")))
# Remediation is effective only when the original and alternate paths are both blocked.
if s.get("alternate_path_viable"): observed="REMEDIATION_FAILED"
elif s.get("primary_protected"): observed="REMEDIATED"
else: observed="EXPLOITABLE"
print(json.dumps({"observed_verdict":observed,"observed_security_state":s,"oracle_version":"0.2.0","validation":"HYBRID","primary_blocked":s.get("primary_protected",False),"alternate_blocked":not s.get("alternate_path_viable",False)},sort_keys=True))