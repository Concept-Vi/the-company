"""runtime/cc_voice.py — give text a VOICE through the Company's resident TTS engine (the building
block for voiced cross-session conversation). SURFACES the existing voice services (voice/tts_service.py
on a tts-* port) — does NOT reinvent TTS. Discovers whichever tts-* engine is currently UP from the
registry, POSTs text to it, saves a WAV. Playback is device-side (the operator/UI); this renders.

Part of the Claude Code Extended Interconnection (Tim 2026-06-14: "adding in the voice"). The voice
engine rides in the @xsession loadout (tts-qwen3tts); this is the fabric's wire to it.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, ".data", "voice")


class VoiceError(RuntimeError):
    """No usable TTS engine / synth failed — raised TEACHING-loud (never silent)."""


def _tts_services() -> list:
    """The tts-* services from the registry: [(key, port, title)]."""
    d = json.load(open(os.path.join(REPO, "ops", "services.json")))["services"]
    return [(k, v.get("port"), v.get("title") or "") for k, v in d.items()
            if k.startswith("tts-") and v.get("port")]


def _is_up(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def engines() -> dict:
    """Which TTS engines exist (registry) and which is currently UP (health-checked)."""
    out = []
    up = None
    for key, port, title in _tts_services():
        alive = _is_up(port)
        out.append({"engine": key, "port": port, "title": title, "up": alive})
        if alive and up is None:
            up = key
    return {"engines": out, "up": up}


def running_engine() -> tuple:
    """(engine_key, port) of the first UP tts-* service. Raises if none up."""
    for key, port, _ in _tts_services():
        if _is_up(port):
            return key, port
    raise VoiceError("no TTS engine is up — bring one online (e.g. `company up @xsession` for "
                     "tts-qwen3tts, or `company up tts-kokoro`). cc_voice surfaces a RUNNING engine; "
                     "it does not start one.")


def speak(text: str, *, out_path: str | None = None, voice: str | None = None, timeout: float = 60) -> dict:
    """Render `text` to a WAV via the running TTS engine. Returns {engine, path, bytes, sample_hint}.
    Playback is device-side (the operator/UI plays the file)."""
    text = (text or "").strip()
    if not text:
        raise VoiceError("speak: empty text — nothing to synthesise (never synth silence).")
    engine, port = running_engine()
    os.makedirs(OUT_DIR, exist_ok=True)
    if out_path is None:
        # deterministic-ish name without Date.now/random (stamp from monotonic-ish file count)
        n = len([f for f in os.listdir(OUT_DIR) if f.endswith(".wav")]) if os.path.isdir(OUT_DIR) else 0
        out_path = os.path.join(OUT_DIR, f"speak-{engine}-{n:04d}.wav")
    body = {"text": text}
    if voice:
        body["voice"] = voice
    req = urllib.request.Request(f"http://127.0.0.1:{port}/", data=json.dumps(body).encode(),
                                 method="POST", headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
    except (urllib.error.URLError, OSError) as e:
        raise VoiceError(f"synth via {engine} (:{port}) failed: {e}")
    if not data or data[:4] != b"RIFF":
        # the service returned JSON (an error) instead of audio
        snippet = data[:200].decode("utf-8", "replace")
        raise VoiceError(f"{engine} did not return audio: {snippet}")
    with open(out_path, "wb") as f:
        f.write(data)
    return {"engine": engine, "path": out_path, "bytes": len(data), "sample_hint": "24kHz mono PCM WAV"}


if __name__ == "__main__":
    import sys
    print(json.dumps(speak(sys.argv[1] if len(sys.argv) > 1 else "Voice fabric online."), indent=2))
