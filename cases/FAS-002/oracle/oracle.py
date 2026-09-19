import json,os,threading,urllib.request
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
s=json.loads((Path(__file__).parents[1]/"repository/state.json").read_text()); s.update(json.loads(os.getenv("FAS_BENCH_MUTATION_JSON","{}")))
class T(BaseHTTPRequestHandler):
 def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"TARGET_REACHED")
 def log_message(self,*a): pass
srv=HTTPServer(("127.0.0.1",0),T); threading.Thread(target=srv.serve_forever,daemon=True).start(); target=f"http://127.0.0.1:{srv.server_port}/secret"
reached=False
try:
 if not s.get("allowlist",False) and s.get("path_viable"): urllib.request.urlopen(target,timeout=2).read(); reached=True
finally: srv.shutdown(); srv.server_close()
observed="EXPLOITABLE" if reached else "NOT_EXPLOITABLE"
print(json.dumps({"observed_verdict":observed,"observed_security_state":s,"oracle_version":"0.3.0","validation":"DYNAMIC","target_reached":reached},sort_keys=True))