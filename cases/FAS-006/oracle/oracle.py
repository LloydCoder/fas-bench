import json,os,threading,urllib.request
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
s=json.loads((Path(__file__).parents[1]/"repository/state.json").read_text()); s.update(json.loads(os.getenv("FAS_BENCH_MUTATION_JSON","{}")))
class H(BaseHTTPRequestHandler):
 def do_GET(self): self.send_response(403 if s.get("authorization",False) else 200); self.end_headers()
 def log_message(self,*a): pass
srv=HTTPServer(("127.0.0.1",0),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
try: code=urllib.request.urlopen(f"http://127.0.0.1:{srv.server_port}/admin",timeout=2).status
except urllib.error.HTTPError as e: code=e.code
finally: srv.shutdown(); srv.server_close()
blocked=code==403; observed="NOT_EXPLOITABLE" if blocked else "EXPLOITABLE"
print(json.dumps({"observed_verdict":observed,"observed_security_state":s,"oracle_version":"0.3.0","validation":"DYNAMIC","unauthorized_admin_blocked":blocked},sort_keys=True))