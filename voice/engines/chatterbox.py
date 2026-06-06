"""voice/engines/chatterbox.py — Chatterbox-TTS as an HTTP service on :4124 (mirrors tts_service.py).

Resemble AI's Chatterbox (MIT, commercial-OK). Warm-realness benchmark for the trial. Clones from a
reference clip and has an EMOTION-EXAGGERATION knob (monotone → dramatic) — the one open model with it.

API (verified against github.com/resemble-ai/chatterbox, 2026-06-03):
  pip install chatterbox-tts
  from chatterbox.tts import ChatterboxTTS
  model = ChatterboxTTS.from_pretrained(device="cuda")
  wav = model.generate(text, audio_prompt_path="ref.wav", cfg_weight=0.5, exaggeration=0.5)  # torch tensor
  sample rate: model.sr ; save via torchaudio / soundfile.

Run (in its own venv — see REQUIREMENTS.md):  python voice/engines/chatterbox.py 4124
"""
from __future__ import annotations
import os
import sys

# THIS file is voice/engines/chatterbox.py and the pip package is ALSO named `chatterbox` — so when the
# script is launched as a FILE (its own dir lands on sys.path[0], ahead of site-packages), the import
# `from chatterbox.tts import ChatterboxTTS` resolves to THIS file (no .tts submodule) → ImportError →
# the misleading "not installed". Remove this script's own dir from sys.path so the installed pip
# `chatterbox` package wins. (Verified 2026-06-06 — the shadow is why company up tts-chatterbox failed
# while a bare-venv import worked. Robust for BOTH the systemd-unit and lifecycle Popen launch paths.)
_self_dir = os.path.dirname(os.path.abspath(__file__))
sys.path[:] = [p for p in sys.path if os.path.abspath(p or ".") != _self_dir]
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from voice.engines._service import serve, wav_bytes_from_array  # noqa: E402

PORT = 4124
DEVICE = os.environ.get("COMPANY_TTS_DEVICE", "cuda")
# The refined-Australian reference clip. It does NOT exist yet (no clip was fabricated) — set this to a
# real wav before running. Fail loud if absent rather than silently use the model's default speaker.
VOICE_REF = os.environ.get("COMPANY_VOICE_REF", "")
EXAGGERATION = float(os.environ.get("COMPANY_CHATTERBOX_EXAGGERATION", "0.5"))
CFG_WEIGHT = float(os.environ.get("COMPANY_CHATTERBOX_CFG", "0.5"))

_model = None


def _engine():
    global _model
    if _model is None:
        try:
            from chatterbox.tts import ChatterboxTTS
        except ImportError as e:
            # Surface the REAL import error — don't assume "not installed" (it was a path-shadow, not a
            # missing package; a misleading message cost real debug time). Name the actual cause.
            raise RuntimeError(f"chatterbox import failed ({type(e).__name__}: {e}) — if it's a missing "
                               f"module, `pip install chatterbox-tts` into the chatterbox venv; if it's a "
                               f"shadow/path issue, check sys.path (see voice/engines/REQUIREMENTS.md)") from e
        _model = ChatterboxTTS.from_pretrained(device=DEVICE)
    return _model


def synth(text: str, voice: str | None, speed: float) -> bytes:
    # `voice` here is OPTIONAL override of the reference-clip path: a request may pass a clip path.
    ref = (voice or VOICE_REF or "").strip()
    if not ref:
        raise RuntimeError("Chatterbox needs a reference clip — set COMPANY_VOICE_REF to a real wav "
                           "(the refined-Australian clip), or pass {'voice': '<clip path>'}. No clip "
                           "was fabricated; fail loud rather than use a wrong speaker.")
    if not os.path.exists(ref):
        raise RuntimeError(f"reference clip not found: {ref!r}")
    # speed accepted per the shared contract but NOT applied — Chatterbox has no speed arg (pace comes
    # from the reference clip + exaggeration). Documented in REQUIREMENTS.md.
    m = _engine()
    wav = m.generate(text, audio_prompt_path=ref, cfg_weight=CFG_WEIGHT, exaggeration=EXAGGERATION)
    return wav_bytes_from_array(wav, m.sr)                 # Chatterbox returns a torch tensor; m.sr is its rate


def voices() -> tuple[list, str]:
    # Chatterbox is reference-clip-driven, not a fixed voice bank — the "voice" is whatever clip is set.
    ref = VOICE_REF or "(set COMPANY_VOICE_REF)"
    return ([ref], ref)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    serve("chatterbox", port, synth, voices, warm=_engine)
