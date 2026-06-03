#!/usr/bin/env python3
"""voice/ops/test_ears.py — end-to-end EARS verification (STT round-trip + Silero VAD).

VERIFIED 2026-06-04 on CPU (int8) in both ~/.voice-venvs/ears and the loop's ~/company/.voice-venv:
synthesize a wav via the running Kokoro (:4123), feed it through the real local-STT lane
(voice.stt.transcribe(provider="local")), and confirm it transcribes back; then run Silero VAD on the
decoded samples and confirm it detects speech. This is the ears half of the trial — proven, not assumed.

Run (CPU now / GPU post-restart):
  COMPANY_WHISPER_DEVICE=cpu COMPANY_WHISPER_COMPUTE=int8 \
    ~/company/.voice-venv/bin/python voice/ops/test_ears.py
  # post-restart on GPU, just:  ~/company/.voice-venv/bin/python voice/ops/test_ears.py
"""
from __future__ import annotations
import json
import sys
import urllib.request

sys.path.insert(0, "/home/tim/company")  # so `from voice import stt` resolves
from voice import stt  # noqa: E402

KOKORO = "http://127.0.0.1:4123/tts"
TEXT = "Hello, this is a refined Australian voice test."


def _synth(text: str) -> bytes:
    """Make a test wav via the running Kokoro base TTS (no GPU, no extra model)."""
    req = urllib.request.Request(KOKORO, data=json.dumps({"text": text}).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def main() -> int:
    print(f"[available] {stt.available()}", flush=True)
    print(f"[config] model={stt.WHISPER_MODEL} device={stt.WHISPER_DEVICE} compute={stt.WHISPER_COMPUTE}",
          flush=True)
    wav = _synth(TEXT)
    print(f"[wav] {len(wav)} bytes from Kokoro for: {TEXT!r}", flush=True)

    res = stt.transcribe(wav, provider="local")               # the REAL local-STT lane
    got = (res.get("text") or "").strip()
    print(f"[stt] transcript: {got!r} (provider={res.get('provider')})", flush=True)

    samples = stt._decode_to_float32(wav)
    ts = stt.vad_speech_timestamps(samples)
    print(f"[vad] {len(samples)} samples @16k; speech regions: {ts}; has_speech={stt.vad_has_speech(samples)}",
          flush=True)

    # PASS if the transcript shares most words with the input and VAD found speech.
    want = set(TEXT.lower().strip(".").split())
    have = set(got.lower().strip(".").split())
    overlap = len(want & have) / max(1, len(want))
    ok = overlap >= 0.7 and bool(ts)
    print(f"\n=== {'PASS' if ok else 'FAIL'} — word overlap {overlap:.0%}, VAD speech={bool(ts)} ===")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
