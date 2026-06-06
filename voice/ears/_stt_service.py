"""voice/ears/_stt_service.py — the shared HTTP shell every STT ear wrapper mounts onto.

The STT twin of voice/engines/_service.py (reuse-don't-parallel, same shape on the other side of the
seam). A wrapper supplies one callable + an optional warm, and calls serve():
  • transcribe(audio_bytes) -> {"text": "..."}      (the model call; fail loud on error)
  • warm() (optional) -> load the model before serving (parity with the engine services' warm)

The CONTRACT (so voice/stt.py's local_http kind reaches every ear uniformly — the SAME route/shape
whisper.cpp's catalog row uses):
  • POST /inference   multipart/form-data, field `file=@clip.wav`  →  {"text": "..."}
  • GET  /            → {"ok": true, "ear": <name>}   (liveness, NOT raising)
  • GET  /health      → same (convenience)
  • fail-loud 500 {"error":"<Type>: <msg>"} on any error.

It does NOT import any heavy library — those live behind each wrapper's lazy _engine(). Importing this
module is stdlib-only, so it stays cheap and the per-ear venv split is respected (NeMo / transformers
never touch this file, only the wrappers).

WHY a multipart `file=` POST (not raw bytes): it mirrors whisper.cpp's own /inference form contract, so
voice/stt.py's _http_transcribe (which builds exactly that multipart) reaches whisper.cpp AND these
three ears with ONE code path — adding an ear is a STT_PROVIDERS row, never a transport edit.
"""
from __future__ import annotations
import io
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def _parse_multipart_file(handler) -> bytes:
    """Pull the uploaded file field's bytes out of a multipart/form-data POST. Dependency-free (stdlib
    `cgi` was removed in Python 3.13, so we parse the boundary ourselves — this keeps the shell
    importable on ANY interpreter, 3.12 or 3.14). Fail loud if there's no file part (parity with
    whisper.cpp's 'no file field' error)."""
    ctype = handler.headers.get("Content-Type", "")
    ln = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(ln)
    if "multipart/form-data" not in ctype or "boundary=" not in ctype:
        return body                                           # tolerate a raw-bytes POST — the body IS the audio
    boundary = ctype.split("boundary=", 1)[1].strip().strip('"')
    delim = b"--" + boundary.encode()
    # Split into parts; each part = headers \r\n\r\n payload. We want the FILE part (has a filename) —
    # fall back to any part with a name we recognise (file/audio/data).
    fallback = None
    for part in body.split(delim):
        part = part.strip(b"\r\n")
        if not part or part == b"--":
            continue
        if b"\r\n\r\n" not in part:
            continue
        head, _, payload = part.partition(b"\r\n\r\n")
        head_l = head.lower()
        payload = payload.rstrip(b"\r\n")                     # trim the trailing CRLF before the next boundary
        if b"filename=" in head_l:                            # the file upload part — prefer this
            return payload
        if fallback is None and any(f'name="{n}"'.encode() in head for n in ("file", "audio", "data")):
            fallback = payload
    if fallback is not None:
        return fallback
    raise RuntimeError("no 'file' field in the request (multipart `file=@clip.wav` expected)")


def serve(name: str, port: int, transcribe, warm=None):
    """Run the STT HTTP service. `name` is for the log line + the liveness payload; `port` per the ears
    port map (parakeet 2031 · canary 2032 · granite 2033)."""

    class H(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype="application/json"):
            b = body.encode() if isinstance(body, str) else body
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

        def do_GET(self):
            if self.path in ("/", "/health"):
                self._send(200, json.dumps({"ok": True, "ear": name}))
            else:
                self._send(404, "{}")

        def do_POST(self):
            try:
                if self.path != "/inference":
                    self._send(404, json.dumps({"error": "POST /inference (multipart file=) expected"}))
                    return
                audio = _parse_multipart_file(self)
                if not audio:
                    self._send(400, json.dumps({"error": "empty audio"})); return
                out = transcribe(audio)
                text = out.get("text", "") if isinstance(out, dict) else str(out)
                self._send(200, json.dumps({"text": text}))
            except Exception as e:                            # fail loud (parity with the engine service)
                self._send(500, json.dumps({"error": f"{type(e).__name__}: {e}"}))

        def log_message(self, *a):
            pass

    if warm is not None:
        warm()                                                # load before serving (fail loud HERE — the
        # CUDA-13 / VRAM hazard surfaces at startup, not on the first request)
    sys.stderr.write(f"[ear:{name}] ready on :{port}\n"); sys.stderr.flush()
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()


def wav_bytes_to_float32(audio: bytes):
    """WAV/audio bytes → mono float32 numpy @ 16 kHz (what NeMo/transformers ASR want). soundfile is in
    each ear's venv. Linear-resamples to 16k if needed (dependency-free; STT is robust to it)."""
    import math
    import numpy as np
    import soundfile as sf
    data, sr = sf.read(io.BytesIO(audio), dtype="float32")
    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != 16000:
        n = int(math.floor(len(data) * 16000 / sr))
        idx = np.linspace(0, len(data) - 1, n)
        data = np.interp(idx, np.arange(len(data)), data).astype("float32")
    return data
