import json
import os
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

state = json.loads((Path(__file__).parents[1] / "repository/state.json").read_text())
state.update(json.loads(os.getenv("FAS_BENCH_MUTATION_JSON", "{}")))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/primary"):
            protected = state.get("primary_protected", False)
        else:
            protected = state.get("alternate_protected", False)
        self.send_response(403 if protected else 200)
        self.end_headers()

    def log_message(self, *args):
        pass


server = HTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()


def status(path):
    try:
        return urllib.request.urlopen(
            f"http://127.0.0.1:{server.server_port}{path}", timeout=2
        ).status
    except urllib.error.HTTPError as exc:
        return exc.code


try:
    primary, alternate = status("/primary"), status("/alternate")
finally:
    server.shutdown()
    server.server_close()

primary_blocked = primary == 403
alternate_blocked = alternate == 403
if primary_blocked and alternate_blocked:
    observed = "REMEDIATED"
elif primary_blocked:
    observed = "REMEDIATION_FAILED"
else:
    observed = "EXPLOITABLE"

print(
    json.dumps(
        {
            "observed_verdict": observed,
            "observed_security_state": state,
            "oracle_version": "0.3.0",
            "validation": "DYNAMIC",
            "primary_blocked": primary_blocked,
            "alternate_blocked": alternate_blocked,
        },
        sort_keys=True,
    )
)
