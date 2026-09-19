import json
from pathlib import Path
s=json.loads((Path(__file__).parents[1]/"repository/state.json").read_text())
v="NOT_EXPLOITABLE" if s.get("sanitization") and not s.get("path_viable") else "EXPLOITABLE"
print(json.dumps({"observed_verdict":v,"observed_security_state":s,"oracle_version":"0.1.0"}))