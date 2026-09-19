import json
from pathlib import Path
s=json.loads((Path(__file__).parents[1]/"repository/state.json").read_text())
v="EXPLOITABLE" if s.get("path_viable") and not s.get("sanitization") else "NOT_EXPLOITABLE"
print(json.dumps({"observed_verdict":v,"observed_security_state":s,"oracle_version":"0.1.0"}))