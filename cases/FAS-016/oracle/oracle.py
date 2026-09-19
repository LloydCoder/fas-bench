import json,os
from pathlib import Path
s=json.loads((Path(__file__).parents[1]/"repository/state.json").read_text()); s.update(json.loads(os.getenv("FAS_BENCH_MUTATION_JSON","{}")))
# Effective permission is the result after explicit deny, not the raw allow.
observed="NOT_EXPLOITABLE" if s.get("explicit_deny",False) else "EXPLOITABLE"
print(json.dumps({"observed_verdict":observed,"observed_security_state":s,"oracle_version":"0.2.0","validation":"HYBRID","privilege_escalation_denied":observed=="NOT_EXPLOITABLE"},sort_keys=True))