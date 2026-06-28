"""voice/ears/parakeet_onnx.py — Parakeet-TDT 0.6B v3, int8 ONNX, as an HTTP STT ear on :2035.

The QUANTIZED, lean form of NVIDIA Parakeet: the same model exported to ONNX and quantized to int8, run
on the lightweight sherpa-onnx runtime instead of the heavy NeMo framework. So it keeps Parakeet's quality
(~6.3% WER) and 25-language coverage, but at a fraction of the footprint — ~1-1.5 GB, CPU by default (int8's
sweet spot), no VRAM. The accurate-multilingual sibling of the Moonshine ear; a drop-in swap in the
interaction loadout (the loadout-variant trial).

Customization (the STA payoff): sherpa-onnx supports CONTEXT BIASING / hotwords — a list of phrases to
boost (UI terms, filter names, command words) — wire via COMPANY_PARAKEET_ONNX_HOTWORDS later. Decode is
greedy by default. HTTP twin of the other ears: POST /inference multipart file= -> {"text": ...}.

MODEL: voice/models/parakeet-tdt-v3-int8/{encoder,decoder,joiner}.int8.onnx + tokens.txt (sherpa-onnx
export csukuangfj/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8). DEVICE: COMPANY_PARAKEET_ONNX_DEVICE
(default cpu; set cuda for the onnxruntime-gpu provider).

Run (its OWN onnx venv — see voice/ears/REQUIREMENTS.md):  python voice/ears/parakeet_onnx.py 2035
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from voice.ears._stt_service import serve, wav_bytes_to_float32  # noqa: E402

PORT = 2035
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # voice/ears/x.py -> repo root
MODEL_DIR = os.environ.get("COMPANY_PARAKEET_ONNX_DIR",
                           os.path.join(_REPO, "voice", "models", "parakeet-tdt-v3-int8"))
DEVICE = os.environ.get("COMPANY_PARAKEET_ONNX_DEVICE", "cpu")
THREADS = int(os.environ.get("COMPANY_PARAKEET_ONNX_THREADS", "4"))

_rec = None


def _engine():
    """Lazy singleton sherpa-onnx offline recognizer over the int8 TDT transducer. Guarded import →
    clear install message. Fail-loud if the model files are missing (registry-is-truth)."""
    global _rec
    if _rec is None:
        try:
            import sherpa_onnx
        except ImportError as e:
            raise RuntimeError(
                "sherpa_onnx not installed — `pip install sherpa-onnx soundfile` into the parakeet-onnx "
                "venv (see voice/ears/REQUIREMENTS.md).") from e
        enc = os.path.join(MODEL_DIR, "encoder.int8.onnx")
        dec = os.path.join(MODEL_DIR, "decoder.int8.onnx")
        join = os.path.join(MODEL_DIR, "joiner.int8.onnx")
        tok = os.path.join(MODEL_DIR, "tokens.txt")
        for p in (enc, dec, join, tok):
            if not os.path.exists(p):
                raise RuntimeError(f"parakeet-onnx model file missing: {p} — fetch the sherpa-onnx int8 export.")
        _rec = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=enc, decoder=dec, joiner=join, tokens=tok,
            num_threads=THREADS, model_type="nemo_transducer", provider=DEVICE,
            decoding_method="greedy_search")
    return _rec


def transcribe(audio: bytes) -> dict:
    rec = _engine()
    samples = wav_bytes_to_float32(audio)                     # mono float32 @ 16k
    stream = rec.create_stream()
    stream.accept_waveform(16000, samples)
    rec.decode_stream(stream)
    return {"text": (stream.result.text or "").strip()}


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    serve("parakeet-onnx", port, transcribe, warm=_engine)
