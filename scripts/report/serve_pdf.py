#!/usr/bin/env python3
"""
Auto-refreshing viewer for latex/build/main.pdf — an Overleaf-preview
replacement. Serves a page that reloads the embedded PDF whenever the file
changes on disk (pair it with `./claw-spice report watch` for
rebuild-on-save).

Runs INSIDE the latex compose service (`./claw-spice report serve`), where
the report sources are mounted at /workspace. Stdlib only; Ctrl+C to stop.
"""

import http.server
import json
import os
import sys

PDF_PATH = os.environ.get("REPORT_PDF", "/workspace/reports/lab-01/build/main.pdf")

PAGE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Lab report preview</title>
<style>
  html, body { margin: 0; height: 100%; }
  #pdf { width: 100%; height: 100%; border: none; }
  #status { position: fixed; top: 8px; right: 12px; font: 12px sans-serif;
            background: #222; color: #eee; padding: 4px 10px; border-radius: 6px;
            opacity: 0.85; }
</style>
</head>
<body>
<div id="status">watching…</div>
<iframe id="pdf" src="/main.pdf"></iframe>
<script>
  let last = null;
  async function poll() {
    try {
      const r = await fetch('/mtime', {cache: 'no-store'});
      const {mtime} = await r.json();
      if (last !== null && mtime !== last && mtime > 0) {
        document.getElementById('pdf').src = '/main.pdf?ts=' + mtime;
        document.getElementById('status').textContent =
          'reloaded ' + new Date().toLocaleTimeString();
      } else if (mtime === 0) {
        document.getElementById('status').textContent =
          'no PDF yet — run: ./claw-spice report <slug>';
      }
      last = mtime;
    } catch (e) {
      document.getElementById('status').textContent = 'server stopped';
    }
    setTimeout(poll, 2000);
  }
  poll();
</script>
</body>
</html>
"""


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code, content_type, body):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/mtime"):
            mtime = os.path.getmtime(PDF_PATH) if os.path.exists(PDF_PATH) else 0
            self._send(200, "application/json", json.dumps({"mtime": mtime}).encode())
        elif self.path.startswith("/main.pdf"):
            if not os.path.exists(PDF_PATH):
                self.send_error(404, "PDF not built yet - run: ./claw-spice report <slug>")
                return
            with open(PDF_PATH, "rb") as f:
                self._send(200, "application/pdf", f.read())
        else:
            self._send(200, "text/html; charset=utf-8", PAGE.encode())

    def log_message(self, fmt, *args):  # keep the terminal quiet
        pass


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
    # 0.0.0.0: the server runs in the container; the compose port mapping
    # exposes it on the host as localhost:<port>.
    server = http.server.ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print("Report preview: http://localhost:{}  (Ctrl+C to stop)".format(port))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
