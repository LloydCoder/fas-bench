from http.server import BaseHTTPRequestHandler, HTTPServer


EXPLICIT_DENY = True


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(403 if EXPLICIT_DENY else 200)
        self.end_headers()

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 0), Handler).serve_forever()
