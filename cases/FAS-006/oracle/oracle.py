import json,os
from pathlib import Path
s=json.loads((Path(__file__).parents[1]/"repository/state.json").read_text()); s.update(json.loads(os.getenv("FAS_BENCH_MUTATION_JSON","{}")))
# Effective authorization is evaluated at the request boundary, not by source presence alone.
observed="NOT_EXPLOITABLE" if s.get("authorization",False) and not s.get("path_viable",False) else "EXPLOITABLE"
print(json.dumps({"observed_verdict":observed,"observed_security_state":s,"oracle_version":"0.2.0","validation":"HYBRID","unauthorized_admin_blocked":observed=="NOT_EXPLOITABLE"},sort_keys=True))