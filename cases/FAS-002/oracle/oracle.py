import json
import os
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

state = json.loads((Path(__file__).parents[1] / "repository/state.json").read_text())
state.update(json.loads(os.getenv("FAS_BENCH_MUTATION_JSON", "{}")))


class Target(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"TARGET_REACHED")

    def log_message(self, *args):
        pass


server = HTTPServer(("127.0.0.1", 0), Target)
threading.Thread(target=server.serve_forever, daemon=True).start()
target = f"http://127.0.0.1:{server.server_port}/secret"
reached = False
try:
    if not state.get("allowlist", False) and state.get("path_viable"):
        urllib.request.urlopen(target, timeout=2).read()
        reached = True
finally:
    server.shutdown()
    server.server_close()

observed = "EXPLOITABLE" if reached else "NOT_EXPLOITABLE"
print(
    json.dumps(
        {
            "observed_verdict": observed,
            "observed_security_state": state,
            "oracle_version": "0.3.0",
            "validation": "DYNAMIC",
            "target_reached": reached,
        },
        sort_keys=True,
    )
)
