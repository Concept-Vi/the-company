#!/usr/bin/env python3
"""ops/stt_openai_shim.py — OpenAI-compatible /v1/audio/transcriptions in front of the COMPANY ears.

OpenWebUI's native STT (engine='openai', base=this shim) transcribes through the company's bridge
`/api/stt`, which resolves the EAR FROM THE LOADOUT (rhm_config.stt → active_ear). So switching the ear in
the company makes OpenWebUI follow BY CONSTRUCTION — this shim holds NO ear choice of its own (the earlier
version pinned a provider and had a NameError; both removed). Thin adapter: pull the audio out of OWUI's
multipart upload, forward the bytes to the bridge, return {"text": ...}.
"""
from __future__ import annotations
import json, os, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BRIDGE = os.environ.get("COMPANY_BRIDGE", "http://127.0.0.1:8770")
PORT = int(os.environ.get("STT_SHIM_PORT", "4201"))


def _extract_file(body: bytes, ctype: str) -> bytes:
    """Minimal multipart/form-data parse: return the bytes of the part carrying a filename (the audio)."""
    if "boundary=" not in ctype:
        return body
    boundary = ("--" + ctype.split("boundary=", 1)[1].strip().strip('"')).encode()
    for part in body.split(boundary):
        head, _, data = part.partition(b"\r\n\r\n")
        if b"filename=" in head and data:
            return data.rsplit(b"\r\n", 1)[0]
    return body


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        body = json.dumps({"data": [{"id": "company-ears"}]}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            audio = _extract_file(self.rfile.read(n), self.headers.get("Content-Type", ""))
            # Forward the raw audio to the bridge; it picks the ear from the live loadout.
            r = urllib.request.Request(f"{BRIDGE}/api/stt", data=audio,
                                       headers={"Content-Type": "application/octet-stream"}, method="POST")
            with urllib.request.urlopen(r, timeout=90) as resp:
                d = json.loads(resp.read() or b"{}")
            text = (d.get("text") or "").strip()
            b = json.dumps({"text": text}).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        except Exception as e:
            b = json.dumps({"error": str(e)}).encode()
            self.send_response(502); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)


if __name__ == "__main__":
    print(f"stt-openai-shim → company bridge {BRIDGE}/api/stt (loadout-resolved ear) on :{PORT}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
