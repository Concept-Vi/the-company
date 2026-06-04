"""voice/ears/canary.py — NVIDIA Canary-Qwen 2.5B as an HTTP STT ear on :2032.

English-max + understanding: an LLM-based ASR (best English WER ~5.63%) that can also *understand* the
audio (summarize/answer) in a second mode. NeMo toolkit (a SALM / speech-augmented LM). HTTP twin of the
TTS engines: POST /inference multipart file= → {"text": ...}; GET / → liveness.

API (verified against the model card / NeMo, 2026-06-05):
  pip install -U nemo_toolkit['asr']
  from nemo.collections.speechlm2.models import SALM
  m = SALM.from_pretrained("nvidia/canary-qwen-2.5b")
  out = m.generate(prompts=[[{"role":"user","content":f"Transcribe: {m.audio_locator_tag}",
                              "audio":[wav_path]}]], max_new_tokens=128)
  text = m.tokenizer.ids_to_text(out[0].cpu())
(NeMo API across versions varies — the wrapper tries the SALM path, then a generic ASRModel fallback, and
fails loud if neither is importable. The heaviest of the three — ~6-7 GB fp16 — mind co-residency with
the chat brain on the 16 GB card.)

CUDA-13 HAZARD: GPU path won't load → FAIL LOUD at warm(); registry shows it down (needs_tim). NO silent
fallback. Run (its OWN NeMo venv — see voice/ears/REQUIREMENTS.md):  python voice/ears/canary.py 2032
"""
from __future__ import annotations
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from voice.ears._stt_service import serve  # noqa: E402

PORT = 2032
MODEL = os.environ.get("COMPANY_CANARY_MODEL", "nvidia/canary-qwen-2.5b")

_model = None
_kind = None


def _engine():
    """Lazy singleton. Prefer the SALM (speech-LM) path Canary-Qwen ships as; fall back to a generic
    NeMo ASRModel if this NeMo build exposes it that way. Guarded import → clear install message."""
    global _model, _kind
    if _model is None:
        try:
            from nemo.collections.speechlm2.models import SALM
            _model = SALM.from_pretrained(MODEL)
            _kind = "salm"
        except ImportError as e:
            # SALM not in this NeMo build → try the generic ASR loader (older/newer layout).
            try:
                import nemo.collections.asr as nemo_asr
                _model = nemo_asr.models.ASRModel.from_pretrained(model_name=MODEL)
                _kind = "asr"
            except ImportError:
                raise RuntimeError(
                    "NeMo (with Canary-Qwen support) not installed — `pip install -U "
                    "nemo_toolkit['asr']` into the canary venv (see voice/ears/REQUIREMENTS.md). "
                    "CUDA-13 hazard: verify the GPU path loads.") from e
    return _model, _kind


def transcribe(audio: bytes) -> dict:
    model, kind = _engine()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
        f.write(audio)
        f.flush()
        if kind == "salm":                                    # the LLM-ASR generate path
            out = model.generate(
                prompts=[[{"role": "user",
                           "content": f"Transcribe the following: {model.audio_locator_tag}",
                           "audio": [f.name]}]],
                max_new_tokens=256)
            text = model.tokenizer.ids_to_text(out[0].cpu()).strip()
        else:                                                 # generic NeMo ASR
            hyps = model.transcribe([f.name])
            h = hyps[0] if hyps else ""
            text = (getattr(h, "text", None) or (h if isinstance(h, str) else str(h))).strip()
    return {"text": text}


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    serve("canary", port, transcribe, warm=_engine)
