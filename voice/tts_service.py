"""voice/tts_service.py — local text-to-speech (Kokoro, CPU, no VRAM). See voice/AGENTS.md.

Runs in .voice-venv (3.12; kokoro-onnx needs onnxruntime, not in the 3.14 runtime). A tiny stdlib
HTTP service: POST /tts {text, voice?, speed?} -> audio/wav bytes; GET /voices -> the voice registry.
The bridge proxies /api/tts here. Downloads the model on first run (gitignored under voice/models/).

Run: ./.voice-venv/bin/python voice/tts_service.py 4123
"""
import io
import json
import os
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "models")
MODEL = os.path.join(MODELS, "kokoro-v1.0.onnx")
VOICES = os.path.join(MODELS, "voices-v1.0.bin")
REL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
DEFAULT_VOICE = os.environ.get("COMPANY_TTS_VOICE", "af_heart")


def _ensure_models():
    os.makedirs(MODELS, exist_ok=True)
    for path, name in ((MODEL, "kokoro-v1.0.onnx"), (VOICES, "voices-v1.0.bin")):
        if not os.path.exists(path):
            sys.stderr.write(f"[tts] downloading {name} …\n"); sys.stderr.flush()
            urllib.request.urlretrieve(REL + name, path)


_kokoro = None


def _engine():
    global _kokoro
    if _kokoro is None:
        _ensure_models()
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(MODEL, VOICES)
    return _kokoro


def _wav(text: str, voice: str, speed: float) -> bytes:
    import soundfile as sf
    samples, rate = _engine().create(text, voice=voice, speed=speed, lang="en-us")
    buf = io.BytesIO()
    sf.write(buf, samples, rate, format="WAV")
    return buf.getvalue()


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        if self.path == "/voices":
            try:
                voices = sorted(_engine().get_voices())
            except Exception:
                voices = [DEFAULT_VOICE]
            self._send(200, json.dumps({"voices": voices, "default": DEFAULT_VOICE}))
        elif self.path in ("/", "/health"):
            self._send(200, json.dumps({"ok": True}))
        else:
            self._send(404, "{}")

    def do_POST(self):
        try:
            ln = int(self.headers.get("Content-Length", 0))
            b = json.loads(self.rfile.read(ln) or "{}")
            text = (b.get("text") or "").strip()
            if not text:
                self._send(400, json.dumps({"error": "no text"})); return
            wav = _wav(text, b.get("voice") or DEFAULT_VOICE, float(b.get("speed", 1.0)))
            self._send(200, wav, "audio/wav")
        except Exception as e:                            # fail loud
            self._send(500, json.dumps({"error": f"{type(e).__name__}: {e}"}))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 4123
    _engine()                                             # warm (download + load) before serving
    sys.stderr.write(f"[tts] kokoro ready on :{port}\n"); sys.stderr.flush()
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
