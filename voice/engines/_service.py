"""voice/engines/_service.py — the shared HTTP shell every engine wrapper mounts onto.

This is the EXACT contract of voice/tts_service.py, factored once so the five wrappers don't each
re-implement the BaseHTTPRequestHandler boilerplate (reuse-don't-parallel, within this lane). A wrapper
supplies three callables and calls serve():
  • synth(text, voice, speed) -> wav bytes        (the model call; fail loud on error)
  • voices() -> (list[str], default_str)          (the engine's voice registry for GET /voices)
  • warm() (optional) -> load the model before serving (parity with tts_service warming Kokoro)

It does NOT import any heavy library — those live behind each wrapper's lazy _engine(). Importing this
module is stdlib-only, so it stays cheap and the venv split is respected.
"""
from __future__ import annotations
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def serve(name: str, port: int, synth, voices, warm=None):
    """Run the TTS HTTP service. `name` is just for the log line; `port` per the engines port map."""

    class H(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype="application/json"):
            b = body.encode() if isinstance(body, str) else body
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            if self.path == "/voices":
                try:
                    vs, default = voices()
                    self._send(200, json.dumps({"voices": sorted(vs), "default": default}))
                except Exception as e:                    # fail loud — never pretend a voice list
                    self._send(500, json.dumps({"error": f"{type(e).__name__}: {e}"}))
            elif self.path in ("/", "/health"):
                self._send(200, json.dumps({"ok": True, "engine": name}))
            else:
                self._send(404, "{}")

        def do_POST(self):
            try:
                ln = int(self.headers.get("Content-Length", 0))
                b = json.loads(self.rfile.read(ln) or "{}")
                text = (b.get("text") or "").strip()
                if not text:
                    self._send(400, json.dumps({"error": "no text"})); return
                wav = synth(text, b.get("voice"), float(b.get("speed", 1.0)))
                self._send(200, wav, "audio/wav")
            except Exception as e:                        # fail loud (parity with tts_service.py)
                self._send(500, json.dumps({"error": f"{type(e).__name__}: {e}"}))

        def log_message(self, *a):
            pass

    if warm is not None:
        warm()                                            # download + load before serving (fail loud here)
    sys.stderr.write(f"[{name}] ready on :{port}\n"); sys.stderr.flush()
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()


def wav_bytes_from_array(samples, rate: int) -> bytes:
    """np float array (or torch tensor) → WAV bytes, the /tts return type. soundfile is in every engine
    venv (it's how tts_service.py writes wav too). Accepts 1-D or (channels, N)/(N, channels)."""
    import io
    import numpy as np
    import soundfile as sf
    arr = samples
    try:
        import torch
        if isinstance(arr, torch.Tensor):
            arr = arr.detach().cpu().numpy()
    except ImportError:
        pass
    arr = np.asarray(arr, dtype="float32")
    arr = np.squeeze(arr)                                 # (1, N) -> (N,)
    if arr.ndim == 2 and arr.shape[0] < arr.shape[1]:     # (channels, N) -> (N, channels) for soundfile
        arr = arr.T
    buf = io.BytesIO()
    sf.write(buf, arr, rate, format="WAV")
    return buf.getvalue()
