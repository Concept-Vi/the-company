"""voice/ears/parakeet.py — NVIDIA Parakeet-TDT 0.6B v3 as an HTTP STT ear on :2031.

The live multilingual workhorse (~6% WER, ~2000x RT, 25 languages). NeMo toolkit (NOT transformers).
HTTP twin of the TTS engines (mounts voice/ears/_stt_service.serve): POST /inference multipart file=
→ {"text": ...}; GET / → liveness.

API (verified against the model card / NeMo ASR, 2026-06-05):
  pip install -U nemo_toolkit['asr']      (heavy; CUDA-sensitive — this box is CUDA-13, the same class
                                           of hazard that forced faster-whisper to CPU; NeMo's torch
                                           wheel usually bundles its own CUDA — VERIFY, don't assume)
  import nemo.collections.asr as nemo_asr
  m = nemo_asr.models.ASRModel.from_pretrained("nvidia/parakeet-tdt-0.6b-v3")
  hyps = m.transcribe([wav_path_or_array])   # → list of Hypothesis (or str depending on version)

CUDA-13 HAZARD (lane note): if the GPU path won't load/verify, this FAILS LOUD at warm() — the ear is
then marked unavailable in the registry (available_stt() probes :2031, gets nothing). NO silent fallback
to whisper.cpp; the registry just shows it down (needs_tim).

Run (its OWN NeMo venv — see voice/ears/REQUIREMENTS.md):  python voice/ears/parakeet.py 2031
"""
from __future__ import annotations
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from voice.ears._stt_service import serve  # noqa: E402

PORT = 2031
MODEL = os.environ.get("COMPANY_PARAKEET_MODEL", "nvidia/parakeet-tdt-0.6b-v3")

_model = None


def _engine():
    """Lazy singleton NeMo ASR model. Heavy import guarded → a clear install message, never a crash on
    import of this module (so the stdlib _stt_service shell stays cheap)."""
    global _model
    if _model is None:
        try:
            import nemo.collections.asr as nemo_asr
        except ImportError as e:
            raise RuntimeError(
                "NeMo not installed — `pip install -U nemo_toolkit['asr']` into the parakeet venv "
                "(see voice/ears/REQUIREMENTS.md). CUDA-13 hazard: verify the GPU path loads.") from e
        _model = nemo_asr.models.ASRModel.from_pretrained(model_name=MODEL)
    return _model


def _hyp_text(hyps) -> str:
    """NeMo .transcribe returns a list whose items are either str or a Hypothesis with .text — normalise."""
    if not hyps:
        return ""
    h = hyps[0]
    return (getattr(h, "text", None) or (h if isinstance(h, str) else str(h))).strip()


def transcribe(audio: bytes) -> dict:
    """Bytes (a wav) → {"text"}. NeMo's transcribe takes file paths most reliably across versions, so we
    write the upload to a temp wav (it's already a wav from the loop/bridge)."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
        f.write(audio)
        f.flush()
        hyps = _engine().transcribe([f.name])
    return {"text": _hyp_text(hyps)}


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    serve("parakeet", port, transcribe, warm=_engine)
