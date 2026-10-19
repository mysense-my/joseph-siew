# Threaded static server with gzip for text and a 1-day cache header, so Lighthouse sees what a normal host serves.
# usage: python3 serve_gzip.py SITE_DIR PORT
import gzip, http.server, os, socketserver, sys

ROOT, PORT = sys.argv[1], int(sys.argv[2])
TEXT = (".html", ".css", ".js", ".svg", ".json", ".txt")


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            path = os.path.join(path, "index.html")
        if path.endswith(TEXT) and "gzip" in self.headers.get("Accept-Encoding", "") and os.path.isfile(path):
            data = gzip.compress(open(path, "rb").read(), 6)
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(path))
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "public, max-age=86400")
            self.end_headers()
            import io
            return io.BytesIO(data)
        return super().send_head()

    def end_headers(self):
        if not any(h.startswith(b"Cache-Control") for h in getattr(self, "_headers_buffer", [])):
            self.send_header("Cache-Control", "public, max-age=86400")
        super().end_headers()

    def log_message(self, *a):
        pass


class T(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


T(("127.0.0.1", PORT), H).serve_forever()
