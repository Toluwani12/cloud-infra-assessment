import json
from http.server import BaseHTTPRequestHandler, HTTPServer


def response_for(path):
    if path == "/":
        return 200, {"message": "Welcome to my cloud assessment"}

    if path == "/healthz":
        return 200, {"status": "ok"}

    return 404, {"error": "Not found"}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status, body = response_for(self.path)
        content = json.dumps(body).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print("Application listening on port 8080", flush=True)
    server.serve_forever()