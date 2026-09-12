#!/usr/bin/env python3
"""
Tiny local server for the Friend Group Soundboard.

Why this exists: a plain double-clicked index.html can't look inside the
sounds/ folder (browsers block that for security) and can't accept a real
file upload (nowhere to write it to). Running this script gives the page
a real backend, on your own machine, that can do both:

  GET  /api/sounds  -> scans sounds/ and returns what's actually in there
  POST /api/upload  -> saves an uploaded mp3 + display name into sounds/

No third-party packages required -- just Python 3's standard library.

Usage:
    python3 serve.py
(or double-click start.command / start.bat / start.sh next to this file)
"""

import http.server
import io
import json
import mimetypes
import os
import re
import socketserver
import sys
import threading
import webbrowser
from functools import partial

ROOT = os.path.dirname(os.path.abspath(__file__))
SOUNDS_DIR = os.path.join(ROOT, "sounds")
ALLOWED_EXTS = {".mp3", ".wav", ".ogg", ".m4a", ".flac"}
DEFAULT_PORT = 8000
MAX_PORT_ATTEMPTS = 15

mimetypes.add_type("audio/mpeg", ".mp3")


def humanize(filename):
    """Turn 'air-horn_2.mp3' into 'Air Horn 2' for a display name."""
    stem = os.path.splitext(filename)[0]
    words = re.split(r"[-_]+", stem)
    words = [w.capitalize() if w.islower() else w for w in words]
    return " ".join(w for w in words if w) or filename


def slugify(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "sound"


def unique_path(directory, filename):
    base, ext = os.path.splitext(filename)
    candidate = filename
    n = 2
    while os.path.exists(os.path.join(directory, candidate)):
        candidate = f"{base}-{n}{ext}"
        n += 1
    return candidate


def list_sounds():
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    files = sorted(
        f for f in os.listdir(SOUNDS_DIR)
        if os.path.splitext(f)[1].lower() in ALLOWED_EXTS
    )
    return [{"file": f, "name": humanize(f)} for f in files]


def parse_multipart(body, boundary):
    """Minimal multipart/form-data parser (no cgi module dependency)."""
    fields = {}
    marker = b"--" + boundary
    for part in body.split(marker):
        part = part.strip(b"\r\n")
        if not part or part == b"--":
            continue
        if b"\r\n\r\n" not in part:
            continue
        header_blob, content = part.split(b"\r\n\r\n", 1)
        content = content[:-2] if content.endswith(b"\r\n") else content
        headers = header_blob.decode("utf-8", errors="replace")

        name_match = re.search(r'name="([^"]*)"', headers)
        if not name_match:
            continue
        field_name = name_match.group(1)

        filename_match = re.search(r'filename="([^"]*)"', headers)
        if filename_match:
            fields[field_name] = {"filename": filename_match.group(1), "content": content}
        else:
            fields[field_name] = {"value": content.decode("utf-8", errors="replace")}
    return fields


class Handler(http.server.SimpleHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        payload = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path.split("?")[0] == "/api/sounds":
            self._send_json(list_sounds())
            return
        super().do_GET()

    def do_POST(self):
        if self.path.split("?")[0] != "/api/upload":
            self.send_error(404, "Not found")
            return

        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self._send_json({"ok": False, "error": "Expected multipart/form-data"}, 400)
            return

        boundary_match = re.search(r'boundary="?([^";]+)"?', content_type)
        if not boundary_match:
            self._send_json({"ok": False, "error": "Missing multipart boundary"}, 400)
            return
        boundary = boundary_match.group(1).encode()

        try:
            length = int(self.headers.get("Content-Length", 0))
        except ValueError:
            length = 0
        if length <= 0:
            self._send_json({"ok": False, "error": "Empty upload"}, 400)
            return

        body = self.rfile.read(length)
        fields = parse_multipart(body, boundary)

        file_field = fields.get("file")
        if not file_field or "content" not in file_field:
            self._send_json({"ok": False, "error": "No file provided"}, 400)
            return

        display_name = ""
        if "name" in fields and "value" in fields["name"]:
            display_name = fields["name"]["value"].strip()
        if not display_name:
            display_name = os.path.splitext(file_field.get("filename", "sound"))[0]

        orig_ext = os.path.splitext(file_field.get("filename", ""))[1].lower()
        if orig_ext not in ALLOWED_EXTS:
            orig_ext = ".mp3"

        os.makedirs(SOUNDS_DIR, exist_ok=True)
        filename = unique_path(SOUNDS_DIR, slugify(display_name) + orig_ext)
        with open(os.path.join(SOUNDS_DIR, filename), "wb") as f:
            f.write(file_field["content"])

        self._send_json({"ok": True, "file": filename, "name": display_name})

    def log_message(self, fmt, *args):
        sys.stderr.write("  " + (fmt % args) + "\n")


def main():
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    handler = partial(Handler, directory=ROOT)

    port = DEFAULT_PORT
    httpd = None
    for attempt in range(MAX_PORT_ATTEMPTS):
        try:
            httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
            break
        except OSError:
            port += 1
    if httpd is None:
        print(f"Couldn't find a free port between {DEFAULT_PORT} and {port}.")
        sys.exit(1)

    url = f"http://localhost:{port}"
    print(f"Soundboard running at {url}")
    print(f"Sounds folder: {SOUNDS_DIR}")
    print("Press Ctrl+C to stop.\n")

    threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
        httpd.server_close()


if __name__ == "__main__":
    main()
