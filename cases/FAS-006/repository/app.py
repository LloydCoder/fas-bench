from http.server import BaseHTTPRequestHandler, HTTPServer


AUTHORIZED = True


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/admin") and not AUTHORIZED:
            self.send_response(200)
        elif self.path.startswith("/admin"):
            self.send_response(403)
        else:
            self.send_response(404)
        self.end_headers()

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 0), Handler).serve_forever()
