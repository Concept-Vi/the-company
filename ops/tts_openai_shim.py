#!/usr/bin/env python3
"""ops/tts_openai_shim.py — OpenAI-compatible /v1/audio/speech in front of the COMPANY voice circuit.

OpenWebUI's native TTS (engine='openai', base=this shim) speaks through the company's bridge `/api/tts`,
which resolves the engine + voice FROM THE LOADOUT (rhm_config.tts_engine → persona → fallback) and applies
the speakable layer. So switching voice/engine in the company makes OpenWebUI follow BY CONSTRUCTION — this
shim holds NO engine/voice choice of its own (the earlier version hardcoded kokoro + a voice map; that
duplication is removed). Thin adapter only: translate the OpenAI shape → the bridge, return the audio.
"""
from __future__ import annotations
import json, os, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BRIDGE = os.environ.get("COMPANY_BRIDGE", "http://127.0.0.1:8770")
PORT = int(os.environ.get("TTS_SHIM_PORT", "4200"))


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        # OWUI may probe /models or /voices — answer minimally; the real voice lives in the loadout.
        body = json.dumps({"data": [{"id": "company-voice"}]}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(n) or b"{}")
            text = req.get("input") or req.get("text") or ""
            # Forward ONLY the text — NO engine/voice. The bridge resolves both from the live loadout, so
            # OWUI speaks in whatever voice the company currently has selected. (Following, not choosing.)
            r = urllib.request.Request(f"{BRIDGE}/api/tts", data=json.dumps({"text": text}).encode(),
                                       headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(r, timeout=90) as resp:
                audio = resp.read()
            self.send_response(200); self.send_header("Content-Type", "audio/wav")
            self.send_header("Content-Length", str(len(audio))); self.end_headers(); self.wfile.write(audio)
        except Exception as e:
            b = json.dumps({"error": str(e)}).encode()
            self.send_response(502); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)


if __name__ == "__main__":
    print(f"tts-openai-shim → company bridge {BRIDGE}/api/tts (loadout-resolved) on :{PORT}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
