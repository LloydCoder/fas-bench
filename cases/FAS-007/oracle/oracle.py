import json
import os
from pathlib import Path

state = json.loads((Path(__file__).parents[1] / "repository/state.json").read_text())
state.update(json.loads(os.getenv("FAS_BENCH_MUTATION_JSON", "{}")))
observed = (
    "EXPLOITABLE" if state.get("path_viable") and state.get("agent_capability") else "NOT_EXPLOITABLE"
)
print(
    json.dumps(
        {
            "observed_verdict": observed,
            "observed_security_state": state,
            "oracle_version": "0.1.0",
        },
        sort_keys=True,
    )
)
