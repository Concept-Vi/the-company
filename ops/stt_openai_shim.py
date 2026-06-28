#!/usr/bin/env python3
"""ops/stt_openai_shim.py — an OpenAI-compatible /v1/audio/transcriptions shim over the Company EARS.

So OpenWebUI's OWN native STT (engine='openai', base=this shim) transcribes with the Company's ear
dispatch (voice.stt → granite/whisper/…, with the browser-audio → wav16 conversion it already does)
instead of OWUI's built-in whisper. OWUI POSTs multipart {file=<audio>}; we hand the bytes to
voice.stt.transcribe and return the OpenAI shape {"text": ...}.
"""
from __future__ import annotations
import json, os, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
from voice import stt as _stt

PORT = int(os.environ.get("STT_SHIM_PORT", "4201"))
PROVIDER = os.environ.get("ROOM_STT", "granite")               # the Company ear to use


def _extract_file(body: bytes, ctype: str) -> bytes:
    """Minimal multipart/form-data parse: return the bytes of the part carrying a filename (the audio)."""
    if "boundary=" not in ctype:
        return body                                            # raw body fallback
    boundary = ("--" + ctype.split("boundary=", 1)[1].strip().strip('"')).encode()
    for part in body.split(boundary):
        head, _, data = part.partition(b"\r\n\r\n")
        if b"filename=" in head and data:
            return data.rsplit(b"\r\n", 1)[0]                  # strip trailing CRLF before next boundary
    return body


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        b = json.dumps({"data": [{"id": "company-ears"}]}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            audio = _extract_file(self.rfile.read(n), self.headers.get("Content-Type", ""))
            text = (_stt.transcribe(audio, provider=PROVIDER).get("text") or "").strip()
            b = json.dumps({"text": text}).encode()
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        except Exception as e:
            b = json.dumps({"error": str(e)}).encode()
            self.send_response(500); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)


if __name__ == "__main__":
    print(f"stt-openai-shim → company ear '{PROVIDER}' on :{PORT}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
