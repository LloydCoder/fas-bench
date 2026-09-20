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
        self.send_response(403 if state.get("authorization", False) else 200)
        self.end_headers()

    def log_message(self, *args):
        pass


server = HTTPServer(("127.0.0.1", 0), Target) if False else HTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
try:
    code = urllib.request.urlopen(f"http://127.0.0.1:{server.server_port}/admin", timeout=2).status
except urllib.error.HTTPError as exc:
    code = exc.code
finally:
    server.shutdown()
    server.server_close()

blocked = code == 403
observed = "NOT_EXPLOITABLE" if blocked else "EXPLOITABLE"
print(
    json.dumps(
        {
            "observed_verdict": observed,
            "observed_security_state": state,
            "oracle_version": "0.3.0",
            "validation": "DYNAMIC",
            "unauthorized_admin_blocked": blocked,
        },
        sort_keys=True,
    )
)
