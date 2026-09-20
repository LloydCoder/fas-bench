from http.server import BaseHTTPRequestHandler, HTTPServer

PRIMARY_PROTECTED = True
ALTERNATE_PROTECTED = False


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/primary"):
            protected = PRIMARY_PROTECTED
        elif self.path.startswith("/alternate"):
            protected = ALTERNATE_PROTECTED
        else:
            protected = True
        self.send_response(403 if protected else 200)
        self.end_headers()

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 0), Handler).serve_forever()
