import json,os,threading,urllib.request
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
s=json.loads((Path(__file__).parents[1]/"repository/state.json").read_text()); s.update(json.loads(os.getenv("FAS_BENCH_MUTATION_JSON","{}")))
class H(BaseHTTPRequestHandler):
 def do_GET(self):
  protected=s.get("primary_protected",False) if self.path.startswith("/primary") else s.get("alternate_protected",False)
  self.send_response(403 if protected else 200); self.end_headers()
srv=HTTPServer(("127.0.0.1",0),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
def code(path):
 try:return urllib.request.urlopen(f"http://127.0.0.1:{srv.server_port}{path}",timeout=2).status
 except urllib.error.HTTPError as e:return e.code
try: primary,alternate=code("/primary"),code("/alternate")
finally: srv.shutdown(); srv.server_close()
primary_blocked=primary==403; alternate_blocked=alternate==403
observed="REMEDIATED" if primary_blocked and alternate_blocked else ("REMEDIATION_FAILED" if primary_blocked else "EXPLOITABLE")
print(json.dumps({"observed_verdict":observed,"observed_security_state":s,"oracle_version":"0.3.0","validation":"DYNAMIC","primary_blocked":primary_blocked,"alternate_blocked":alternate_blocked},sort_keys=True))