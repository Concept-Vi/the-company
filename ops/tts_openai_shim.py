#!/usr/bin/env python3
"""ops/tts_openai_shim.py — an OpenAI-compatible /v1/audio/speech shim in front of the Company's kokoro TTS.

So OpenWebUI's OWN native TTS (engine="openai", base=this shim) speaks with the Company's local kokoro
voice — connecting OWUI's built-in voice to our engine instead of a bolt-on page. OWUI POSTs the OpenAI
shape {model, input, voice, response_format}; we translate to kokoro {text, voice, speed} and return audio.
"""
from __future__ import annotations
import json, os, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

KOKORO = f"http://127.0.0.1:{os.environ.get('COMPANY_TTS_PORT','4123')}/"
PORT = int(os.environ.get("TTS_SHIM_PORT", "4200"))
DEFAULT_VOICE = os.environ.get("COMPANY_TTS_VOICE", "af_heart")
# OpenAI voice names → kokoro voices (so OWUI's voice picker maps to real kokoro voices)
VOICE_MAP = {"alloy": "af_heart", "nova": "af_bella", "echo": "am_adam", "fable": "af_sky",
             "onyx": "am_michael", "shimmer": "af_nicole"}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        # OWUI may probe /audio/voices and /models — answer minimally.
        if self.path.endswith("/voices"):
            self._send(200, json.dumps({"voices": [{"id": k, "name": k} for k in VOICE_MAP]}).encode(), "application/json")
        elif self.path.endswith("/models"):
            self._send(200, json.dumps({"data": [{"id": "kokoro"}]}).encode(), "application/json")
        else:
            self._send(200, b'{"ok":true}', "application/json")

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(n) or b"{}")
            text = req.get("input") or req.get("text") or ""
            voice = VOICE_MAP.get(req.get("voice", ""), req.get("voice") or DEFAULT_VOICE)
            if voice not in VOICE_MAP.values() and not voice.startswith(("af_", "am_", "bf_", "bm_")):
                voice = DEFAULT_VOICE
            body = json.dumps({"text": text, "voice": voice, "speed": req.get("speed", 1.0)}).encode()
            r = urllib.request.Request(KOKORO, data=body, headers={"Content-Type": "application/json"}, method="POST")
            audio = urllib.request.urlopen(r, timeout=60).read()
            self._send(200, audio, "audio/wav")
        except Exception as e:
            self._send(500, json.dumps({"error": str(e)}).encode(), "application/json")

    def _send(self, code, body, ctype):
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)


if __name__ == "__main__":
    print(f"tts-openai-shim → kokoro {KOKORO} on :{PORT}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
