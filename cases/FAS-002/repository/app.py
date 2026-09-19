from http.server import BaseHTTPRequestHandler,HTTPServer
class H(BaseHTTPRequestHandler):
 def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b"TARGET_REACHED")
 def log_message(self,*a): pass
if __name__=="__main__": HTTPServer(("127.0.0.1",0),H).serve_forever()
