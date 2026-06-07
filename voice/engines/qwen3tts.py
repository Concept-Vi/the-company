"""voice/engines/qwen3tts.py — Qwen3-TTS VoiceDesign as an HTTP service on :4128 (mirrors tts_service.py).

Alibaba Qwen3-TTS-12Hz-1.7B-VoiceDesign (Apache-2.0). The DESIGN-a-voice engine: you hand it a TEXT
DESCRIPTION (the `instruct`) and it creates a voice from it — exactly the "tweakable incl. accent"
requirement, and the only one the persona voice_description feeds directly. Suits Sable (describe +
lock + re-tune the cool register). Already in the HF cache (the 13-file snapshot downloaded).

API (verified against github.com/QwenLM/Qwen3-TTS README, 2026-06-03):
  pip install -U qwen-tts
  from qwen_tts import Qwen3TTSModel
  model = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
                                        device_map="cuda:0", dtype=torch.bfloat16,
                                        attn_implementation="flash_attention_2")
  wavs, sr = model.generate_voice_design(text=..., language="English", instruct=<description>)
  sf.write("out.wav", wavs[0], sr)   # config.json: output_sample_rate 24000
  NOTE: VoiceDesign uses generate_voice_design(text, language, instruct) — NO `speaker` arg. That's the
  CustomVoice model's method (generate_custom_voice with a fixed speaker bank). This checkpoint is
  tts_model_type=voice_design — it BUILDS a voice from the `instruct` description, so no speaker slot.

Run (its OWN venv — see REQUIREMENTS.md):  python voice/engines/qwen3tts.py 4128
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from voice.engines._service import serve, wav_bytes_from_array  # noqa: E402

PORT = 4128

# ONE SOURCE (2026-06-07): settings live in the registry config block (ops/services.json → tts-qwen3tts.
# config); the COMPANY_QWEN3TTS_* env vars (voice.env) are the fallback. Mirrors orpheus.py — the engine
# reads the same record the resource manager budgets/sees, so settings stay in one place. (qwen3tts is
# NOT vLLM — transformers VoiceDesign, a fixed footprint — so it carries vram_mb, not a gpu_util knob.)
def _reg_config():
    import json
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        return json.load(open(os.path.join(root, "ops", "services.json")))["services"]["tts-qwen3tts"].get("config") or {}
    except Exception:
        return {}


_C = _reg_config()
MODEL_ID = _C.get("model") or os.environ.get("COMPANY_QWEN3TTS_MODEL", "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign")
DEVICE_MAP = _C.get("device") or os.environ.get("COMPANY_QWEN3TTS_DEVICE", "cuda:0")
# flash_attention_2 needs the flash-attn package built; default to "sdpa" which always works on CUDA.
# Set config.attn (or COMPANY_QWEN3TTS_ATTN) = flash_attention_2 once flash-attn is installed.
ATTN = _C.get("attn") or os.environ.get("COMPANY_QWEN3TTS_ATTN", "sdpa")
LANGUAGE = _C.get("lang") or os.environ.get("COMPANY_QWEN3TTS_LANG", "English")
# The default voice DESCRIPTION (instruct). loop.py passes the persona's voice_description as `voice`.
DEFAULT_DESC = os.environ.get(
    "COMPANY_QWEN3TTS_DESC",
    "A refined, educated Australian woman in her early forties — warm, mid-low pitch, unhurried, "
    "composed, with a dry, understated wit. Clear and articulate, not broad or ocker.")

_model = None


def _engine():
    global _model
    if _model is None:
        try:
            import torch
            from qwen_tts import Qwen3TTSModel
        except ImportError as e:
            raise RuntimeError("qwen-tts not installed — `pip install -U qwen-tts` into the qwen3tts "
                               "venv (see voice/engines/REQUIREMENTS.md)") from e
        _model = Qwen3TTSModel.from_pretrained(
            MODEL_ID, device_map=DEVICE_MAP, dtype=torch.bfloat16, attn_implementation=ATTN)
    return _model


def synth(text: str, voice: str | None, speed: float) -> bytes:
    description = (voice or DEFAULT_DESC).strip()           # `voice` carries the persona voice_description
    # speed is accepted per the shared contract but NOT applied — VoiceDesign has no speed arg
    # (encode pace into the `instruct` description instead, e.g. "unhurried, composed pace").
    wavs, sr = _engine().generate_voice_design(
        text=text, language=LANGUAGE, instruct=description)
    if wavs is None or len(wavs) == 0:
        raise RuntimeError("Qwen3-TTS produced no audio")
    return wav_bytes_from_array(wavs[0], sr)


def voices() -> tuple[list, str]:
    # VoiceDesign is description-driven; the "voice" is the description string (default = base sketch).
    return ([DEFAULT_DESC], DEFAULT_DESC)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    serve("qwen3tts", port, synth, voices, warm=_engine)
