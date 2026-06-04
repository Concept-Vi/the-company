"""voice/engines/orpheus.py — Orpheus-TTS as an HTTP service on :4125 (mirrors tts_service.py).

Canopy Labs' Orpheus (Apache-2.0). LLM-backbone (Llama-3.2) → SNAC audio codec, served via vLLM.
Cued emotion via inline tags (<laugh>, <chuckle>, <sigh>, …) and a small bank of NAMED voices —
suits Pip's well-timed bit. NOT a reference-clip model in this path; you pick a voice name.

API (verified against github.com/canopyai/Orpheus-TTS, 2026-06-03):
  pip install orpheus-speech    (built on vLLM; pin vllm==0.7.3 if the bundled build is buggy)
  from orpheus_tts import OrpheusModel
  model = OrpheusModel(model_name="canopylabs/orpheus-tts-0.1-finetune-prod", max_model_len=2048)
  syn_tokens = model.generate_speech(prompt=text, voice="tara")   # iterable of PCM byte chunks
  voices: tara leah jess leo dan mia zac zoe ; sample rate 24000 ; 16-bit mono PCM frames.

Run (its OWN venv with vLLM — see REQUIREMENTS.md):  python voice/engines/orpheus.py 4125
"""
from __future__ import annotations
import io
import os
import sys
import wave

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from voice.engines._service import serve  # noqa: E402

PORT = 4125
MODEL_NAME = os.environ.get("COMPANY_ORPHEUS_MODEL", "canopylabs/orpheus-tts-0.1-finetune-prod")
MAX_LEN = int(os.environ.get("COMPANY_ORPHEUS_MAXLEN", "2048"))
DEFAULT_VOICE = os.environ.get("COMPANY_ORPHEUS_VOICE", "tara")
RATE = 24000
VOICE_BANK = ["tara", "leah", "jess", "leo", "dan", "mia", "zac", "zoe"]

_model = None


def _engine():
    global _model
    if _model is None:
        try:
            from orpheus_tts import OrpheusModel
        except ImportError as e:
            raise RuntimeError("orpheus not installed — `pip install orpheus-speech` (vLLM-based) "
                               "into the orpheus venv (see voice/engines/REQUIREMENTS.md)") from e
        _model = OrpheusModel(model_name=MODEL_NAME, max_model_len=MAX_LEN)
    return _model


def synth(text: str, voice: str | None, speed: float) -> bytes:
    v = (voice or DEFAULT_VOICE).strip()
    if v not in VOICE_BANK:
        raise RuntimeError(f"unknown Orpheus voice {v!r} — one of {VOICE_BANK}")
    # speed accepted per the shared contract but NOT applied — Orpheus has no speed arg (it's an LLM
    # token stream; pace via inline cues / prompt). Documented in REQUIREMENTS.md.
    # generate_speech yields raw 16-bit mono PCM byte chunks; assemble them into one WAV container.
    chunks = _engine().generate_speech(prompt=text, voice=v)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)                                # 16-bit
        wf.setframerate(RATE)
        wrote = False
        for chunk in chunks:
            wf.writeframes(chunk)
            wrote = True
        if not wrote:                                     # fail loud — never return a 44-byte empty wav
            raise RuntimeError("Orpheus produced no audio (empty token stream)")
    return buf.getvalue()


def voices() -> tuple[list, str]:
    return (list(VOICE_BANK), DEFAULT_VOICE)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    serve("orpheus", port, synth, voices, warm=_engine)
