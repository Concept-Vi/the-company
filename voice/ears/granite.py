"""voice/ears/granite.py — IBM Granite Speech 4.0 1B as an HTTP STT ear on :2033.

Compact top-accuracy cross-check (leaderboard-topping ~5.52% WER, English + translate). HuggingFace
TRANSFORMERS (not NeMo — "lands clean", the standard path), so this is the ear most likely to load
without the NeMo/CUDA-13 hazard. HTTP twin of the TTS engines: POST /inference multipart file= →
{"text": ...}; GET / → liveness.

API (verified against the model card, 2026-06-05):
  pip install transformers peft soundfile torchaudio
  from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq  # or the granite-speech class
  proc = AutoProcessor.from_pretrained("ibm-granite/granite-4.0-1b-speech")
  model = AutoModelForSpeechSeq2Seq.from_pretrained("ibm-granite/granite-4.0-1b-speech")
  # granite-speech is an LLM+speech adapter — uses a chat template with an <|audio|> turn:
  chat = [{"role":"user","content":"<|audio|>can you transcribe the speech into text?"}]
  prompt = proc.tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
  inputs = proc(prompt, wav_tensor, device=device, return_tensors="pt")
  out = model.generate(**inputs, max_new_tokens=200)
  text = proc.tokenizer.batch_decode(out[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True)[0]

(The transformers granite-speech API has shifted across releases; the wrapper uses the
processor+chat-template+generate path the model card documents, and fails loud with the exact error if
this build's class layout differs — never a silent wrong transcript.)

CUDA-13 NOTE: transformers honours COMPANY_GRANITE_DEVICE (default cuda; set cpu to dodge the GPU
hazard, slower). GPU won't load → FAIL LOUD at warm(); registry shows it down (needs_tim). NO fallback.
Run (its OWN transformers venv — see voice/ears/REQUIREMENTS.md):  python voice/ears/granite.py 2033
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from voice.ears._stt_service import serve, wav_bytes_to_float32  # noqa: E402

PORT = 2033
MODEL = os.environ.get("COMPANY_GRANITE_MODEL", "ibm-granite/granite-4.0-1b-speech")
DEVICE = os.environ.get("COMPANY_GRANITE_DEVICE", "cuda")

_proc = None
_model = None


def _engine():
    """Lazy singleton processor+model via transformers. Guarded import → clear install message. Honours
    COMPANY_GRANITE_DEVICE (cpu dodges the CUDA-13 GPU hazard)."""
    global _proc, _model
    if _model is None:
        try:
            import torch  # noqa: F401
            from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
        except ImportError as e:
            raise RuntimeError(
                "transformers/torch not installed — `pip install transformers peft soundfile "
                "torchaudio torch` into the granite venv (see voice/ears/REQUIREMENTS.md).") from e
        _proc = AutoProcessor.from_pretrained(MODEL)
        # bf16 on CUDA (the model card's dtype — fp32 would be ~4x the VRAM); fp32 on CPU.
        dtype = torch.bfloat16 if DEVICE.startswith("cuda") else torch.float32
        _model = AutoModelForSpeechSeq2Seq.from_pretrained(
            MODEL, torch_dtype=dtype, device_map=DEVICE)
        _model.eval()
    return _proc, _model


def transcribe(audio: bytes) -> dict:
    import torch
    proc, model = _engine()
    samples = wav_bytes_to_float32(audio)                     # mono float32 @ 16k
    wav = torch.tensor(samples).unsqueeze(0)                  # (1, T)
    chat = [{"role": "user", "content": "<|audio|>can you transcribe the speech into text?"}]
    prompt = proc.tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)
    inputs = proc(prompt, wav, device=DEVICE, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        out = model.generate(**inputs, max_new_tokens=200, do_sample=False)
    gen = out[:, inputs["input_ids"].shape[1]:]
    text = proc.tokenizer.batch_decode(gen, skip_special_tokens=True)[0].strip()
    return {"text": text}


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    serve("granite", port, transcribe, warm=_engine)
