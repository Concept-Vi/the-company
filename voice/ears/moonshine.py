"""voice/ears/moonshine.py — Moonshine ASR as an HTTP STT ear on :2034.

The compact realtime ear (Moonshine, useful-sensors). ONNX-runtime under the hood (no torch, no NeMo —
the leanest ear), built for low-latency live voice: it does NOT pad short clips to a fixed window the way
Whisper does, so a short conversational turn transcribes in a fraction of the time. English-focused.
Sub-1GB. HTTP twin of the other ears: POST /inference multipart file= → {"text": ...}; GET / → liveness.

MODEL: COMPANY_MOONSHINE_MODEL (default "moonshine/base"). The package ships moonshine/tiny (smallest,
~12% WER) and moonshine/base (the quality-leaning compact model). Newer v2 medium/streaming checkpoints
(≈Whisper-large accuracy) can be dropped in here via the env when packaged — model is a config knob, not
a code change (the whole point of the loadout-variant system).

Run (its OWN onnx venv — see voice/ears/REQUIREMENTS.md):  python voice/ears/moonshine.py 2034
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from voice.ears._stt_service import serve, wav_bytes_to_float32  # noqa: E402

PORT = 2034
MODEL = os.environ.get("COMPANY_MOONSHINE_MODEL", "moonshine/base")

_model = None
_tok = None


def _engine():
    """Lazy singleton Moonshine ONNX model + tokenizer. Guarded import → clear install message. ONNX-runtime
    only (CPU by default; an onnxruntime-gpu build picks the GPU provider automatically when present)."""
    global _model, _tok
    if _model is None:
        try:
            from moonshine_onnx import MoonshineOnnxModel, load_tokenizer
        except ImportError as e:
            raise RuntimeError(
                "moonshine_onnx not installed — `pip install useful-moonshine-onnx` (or moonshine-onnx) "
                "into the moonshine venv (see voice/ears/REQUIREMENTS.md).") from e
        _model = MoonshineOnnxModel(model_name=MODEL)
        _tok = load_tokenizer()
    return _model, _tok


def transcribe(audio: bytes) -> dict:
    import numpy as np
    model, tok = _engine()
    samples = wav_bytes_to_float32(audio)                     # mono float32 @ 16k
    arr = np.asarray(samples, dtype="float32")[np.newaxis, :]  # (1, T) — the model's expected shape
    tokens = model.generate(arr)
    text = tok.decode_batch(tokens)[0].strip()
    return {"text": text}


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    serve("moonshine", port, transcribe, warm=_engine)
