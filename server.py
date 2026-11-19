#!/usr/bin/env python3
"""Local admin server. Run: python server.py  ->  http://localhost:8000/admin.html
Serves the project folder, exposes /api/<collection> (GET/PUT) and image upload.
Binds to 127.0.0.1 only. Never deploy this file; only index.html, data/ and images/ go to GitHub Pages."""
import json, os, re, tempfile, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA, IMAGES = os.path.join(ROOT, "data"), os.path.join(ROOT, "images")
COLLECTIONS = {"units", "categories", "ingredients", "recipes"}
os.makedirs(DATA, exist_ok=True); os.makedirs(IMAGES, exist_ok=True)


class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def send_json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers(); self.wfile.write(b)

    def body(self):
        return self.rfile.read(int(self.headers.get("Content-Length", 0)))

    def do_GET(self):
        if self.path == "/api/images":
            return self.send_json(sorted(f for f in os.listdir(IMAGES) if not f.startswith(".")))
        m = re.fullmatch(r"/api/(\w+)", self.path)
        if m:
            if m[1] not in COLLECTIONS: return self.send_json({"error": "unknown"}, 404)
            p = os.path.join(DATA, m[1] + ".json")
            return self.send_json(json.load(open(p, encoding="utf-8")) if os.path.exists(p) else [])
        super().do_GET()

    def do_PUT(self):
        m = re.fullmatch(r"/api/(\w+)", self.path)
        if not m or m[1] not in COLLECTIONS: return self.send_json({"error": "unknown"}, 404)
        try:
            data = json.loads(self.body())
            assert isinstance(data, list)
        except Exception:
            return self.send_json({"error": "expected a JSON array"}, 400)
        fd, tmp = tempfile.mkstemp(dir=DATA)           # atomic write
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, os.path.join(DATA, m[1] + ".json"))
        self.send_json({"ok": True})

    def do_POST(self):
        m = re.fullmatch(r"/api/upload/([\w.\-]+\.(?:jpe?g|png|webp|gif))", self.path, re.I)
        if not m: return self.send_json({"error": "bad file name or type"}, 400)
        open(os.path.join(IMAGES, m[1]), "wb").write(self.body())
        self.send_json({"path": "images/" + m[1]})

    def log_message(self, *a): pass


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", 8000), H)
    print("Admin: http://localhost:8000/admin.html   Viewer: http://localhost:8000/index.html  (Ctrl+C to stop)")
    webbrowser.open("http://localhost:8000/admin.html")
    srv.serve_forever()
