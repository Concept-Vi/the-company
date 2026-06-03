"""voice/engines/cosyvoice.py — CosyVoice2 as an HTTP service on :4126 (mirrors tts_service.py).

Alibaba FunAudioLLM CosyVoice2-0.5B (Apache-2.0). Responsive + instruct-coachable: takes a
natural-language style instruction AND clones from a reference clip — suits Tess (warmth on demand).

Install is NOT pip — it's a git clone + a Matcha-TTS submodule on PYTHONPATH (see REQUIREMENTS.md):
  git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git
  export COMPANY_COSYVOICE_REPO=/path/to/CosyVoice           # added to sys.path here
  export PYTHONPATH=$COMPANY_COSYVOICE_REPO/third_party/Matcha-TTS
  model dir: pretrained_models/CosyVoice2-0.5B (snapshot_download FunAudioLLM/CosyVoice2-0.5B)

API (verified against example.py @ FunAudioLLM/CosyVoice main, 2026-06-03):
  from cosyvoice.cli.cosyvoice import AutoModel
  from cosyvoice.utils.file_utils import load_wav
  cosyvoice = AutoModel(model_dir='pretrained_models/CosyVoice2-0.5B')
  for j in cosyvoice.inference_instruct2(text, instruct, prompt_wav): j['tts_speech']   # torch tensor
  for j in cosyvoice.inference_zero_shot(text, prompt_text, prompt_wav): ...
  sample rate: cosyvoice.sample_rate

Run (its OWN conda/venv — see REQUIREMENTS.md):  python voice/engines/cosyvoice.py 4126
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from voice.engines._service import serve, wav_bytes_from_array  # noqa: E402

PORT = 4126
MODEL_DIR = os.environ.get("COMPANY_COSYVOICE_DIR", "pretrained_models/CosyVoice2-0.5B")
REPO = os.environ.get("COMPANY_COSYVOICE_REPO", "")            # the cloned CosyVoice repo (for imports)
VOICE_REF = os.environ.get("COMPANY_VOICE_REF", "")           # the refined-Australian prompt clip (not fabricated)
# The style instruction; CosyVoice2 wants it terminated with <|endofprompt|>. The persona's
# voice_description can be passed per-request as `voice` (loop.py does this) to steer warmth/tone.
DEFAULT_INSTRUCT = os.environ.get(
    "COMPANY_COSYVOICE_INSTRUCT",
    "Speak as a refined, mature Australian woman — warm, mid-low, unhurried, with an easy lightness.")

_model = None


def _engine():
    global _model
    if _model is None:
        if REPO and REPO not in sys.path:
            sys.path.insert(0, REPO)
            sys.path.insert(0, os.path.join(REPO, "third_party", "Matcha-TTS"))
        try:
            from cosyvoice.cli.cosyvoice import AutoModel
        except ImportError as e:
            raise RuntimeError(
                "cosyvoice not importable — clone github.com/FunAudioLLM/CosyVoice (--recursive), "
                "pip install its requirements, and set COMPANY_COSYVOICE_REPO to the clone "
                "(see voice/engines/REQUIREMENTS.md)") from e
        _model = AutoModel(model_dir=MODEL_DIR)
    return _model


def _prompt_wav():
    if not VOICE_REF:
        raise RuntimeError("CosyVoice needs a prompt clip — set COMPANY_VOICE_REF to a real wav "
                           "(the refined-Australian clip). No clip was fabricated; fail loud.")
    if not os.path.exists(VOICE_REF):
        raise RuntimeError(f"prompt clip not found: {VOICE_REF!r}")
    from cosyvoice.utils.file_utils import load_wav        # 16k load, the repo's canonical loader
    return load_wav(VOICE_REF, 16000)


def synth(text: str, voice: str | None, speed: float) -> bytes:
    m = _engine()
    prompt = _prompt_wav()
    instruct = (voice or DEFAULT_INSTRUCT).strip()         # `voice` carries the persona voice_description
    if "<|endofprompt|>" not in instruct:
        instruct = instruct + "<|endofprompt|>"
    # speed accepted per the shared contract but NOT applied as a numeric arg — CosyVoice2 steers pace
    # via the instruction text (e.g. "请用尽可能快地语速说"). Encode pace in the instruct/description.
    # inference_* are GENERATORS yielding {'tts_speech': tensor}; collect + concat the chunks into one wav.
    import torch
    parts = [j["tts_speech"] for j in m.inference_instruct2(text, instruct, prompt, stream=False)]
    if not parts:
        raise RuntimeError("CosyVoice produced no audio")
    audio = torch.cat(parts, dim=1) if len(parts) > 1 else parts[0]
    return wav_bytes_from_array(audio, m.sample_rate)


def voices() -> tuple[list, str]:
    # CosyVoice is instruction+clip driven; the "voice" is the instruction (its default is the base sketch).
    return ([DEFAULT_INSTRUCT], DEFAULT_INSTRUCT)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    serve("cosyvoice", port, synth, voices, warm=_engine)
