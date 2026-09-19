from http.server import BaseHTTPRequestHandler,HTTPServer
PRIMARY_PROTECTED=True; ALTERNATE_PROTECTED=False
class H(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path.startswith('/primary'): self.send_response(403 if PRIMARY_PROTECTED else 200)
  elif self.path.startswith('/alternate'): self.send_response(403 if ALTERNATE_PROTECTED else 200)
  else: self.send_response(404)
  self.end_headers()
 def log_message(self,*a): pass
if __name__=="__main__": HTTPServer(("127.0.0.1",0),H).serve_forever()
