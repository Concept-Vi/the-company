"""voice/engines/xtts.py — XTTS-v2 (Coqui) as an HTTP service on :4127 (mirrors tts_service.py).

XTTS-v2 — the realism ceiling for the trial (most alive read; suits Wren). Zero-shot cross-lingual
cloning from a 3–6 s clip.

LICENSE GATE (important): XTTS-v2 weights are Coqui Public Model License — NON-COMMERCIAL only. This
is a TRIAL voice (judged by ear), NOT a shippable production voice. Keep it out of any commercial path;
it is here so Tim can compare its realism. The maintained fork is `coqui-tts` (idiap/coqui-ai-TTS).
Running it requires accepting the Coqui TOS: set COQUI_TOS_AGREED=1 (it prompts otherwise).

API (verified against the catalog + idiap/coqui-ai-TTS, 2026-06-03):
  pip install coqui-tts ; export COQUI_TOS_AGREED=1
  from TTS.api import TTS
  tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")
  wav = tts.tts(text=text, speaker_wav="ref.wav", language="en")   # list[float] @ 24000
  (or tts.tts_to_file(... file_path=...))

Run (its OWN venv — see REQUIREMENTS.md):  COQUI_TOS_AGREED=1 python voice/engines/xtts.py 4127
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from voice.engines._service import serve, wav_bytes_from_array  # noqa: E402

PORT = 4127
DEVICE = os.environ.get("COMPANY_TTS_DEVICE", "cuda")
MODEL = os.environ.get("COMPANY_XTTS_MODEL", "tts_models/multilingual/multi-dataset/xtts_v2")
VOICE_REF = os.environ.get("COMPANY_VOICE_REF", "")          # the refined-Australian clip (not fabricated)
LANG = os.environ.get("COMPANY_XTTS_LANG", "en")
RATE = 24000

_tts = None


def _engine():
    global _tts
    if _tts is None:
        os.environ.setdefault("COQUI_TOS_AGREED", "1")      # accept the non-commercial TOS non-interactively
        try:
            from TTS.api import TTS
        except ImportError as e:
            raise RuntimeError("coqui-tts not installed — `pip install coqui-tts` into the xtts venv "
                               "(NON-COMMERCIAL weights; see voice/engines/REQUIREMENTS.md)") from e
        _tts = TTS(MODEL).to(DEVICE)
    return _tts


def synth(text: str, voice: str | None, speed: float) -> bytes:
    ref = (voice or VOICE_REF or "").strip()
    if not ref:
        raise RuntimeError("XTTS needs a speaker clip — set COMPANY_VOICE_REF to a real wav (the "
                           "refined-Australian clip), or pass {'voice': '<clip path>'}. No clip "
                           "was fabricated; fail loud.")
    if not os.path.exists(ref):
        raise RuntimeError(f"speaker clip not found: {ref!r}")
    # XTTS's tts() accepts `speed` — wire the contract's speed through (1.0 = natural).
    wav = _engine().tts(text=text, speaker_wav=ref, language=LANG, speed=speed)   # list[float] @ 24k
    return wav_bytes_from_array(wav, RATE)


def voices() -> tuple[list, str]:
    ref = VOICE_REF or "(set COMPANY_VOICE_REF)"
    return ([ref], ref)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    serve("xtts", port, synth, voices, warm=_engine)
