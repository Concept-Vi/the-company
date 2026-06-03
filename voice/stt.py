"""voice/stt.py — speech-to-text, a SWAPPABLE provider (see voice/AGENTS.md).

Default: AssemblyAI (cloud, top accuracy + low latency, key from ~/company/.secrets). Audio leaves
the machine — that trades the fully-local path; it's a config flag so you can flip to local Whisper.
Stdlib only (HTTP), so it runs in the 3.14 runtime venv — no heavy install for the cloud provider.
"""
from __future__ import annotations
import json
import os
import time
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PROVIDER = os.environ.get("COMPANY_STT", "assemblyai")
AAI_BASE = "https://api.assemblyai.com/v2"


def secret(key: str, default: str = "") -> str:
    """env first, then ~/company/.secrets (KEY=VALUE, gitignored) — so a key never lives in code or git."""
    if os.environ.get(key):
        return os.environ[key]
    p = os.path.join(REPO, ".secrets")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                if k.strip() == key:
                    return v.strip().strip('"').strip("'")
    return default


def _whisper_importable() -> bool:
    """True only if faster-whisper is actually importable in THIS interpreter (the .voice-venv).
    available() reports the registry the UI/RHM reads — it must reflect reality, never guess."""
    import importlib.util
    return importlib.util.find_spec("faster_whisper") is not None


def available() -> dict:
    """Which providers are usable right now (the registry the RHM/UI should read — never guess)."""
    return {"assemblyai": bool(secret("ASSEMBLYAI_API_KEY")),
            "whisper_local": _whisper_importable()}


def transcribe(audio: bytes, provider: str | None = None) -> dict:
    provider = provider or DEFAULT_PROVIDER
    if provider == "assemblyai":
        return _assemblyai(audio)
    if provider in ("whisper", "local"):
        return _whisper_local(audio)
    raise ValueError(f"unknown STT provider {provider!r}")


def _post(url: str, data: bytes, headers: dict, timeout: int = 90) -> dict:
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def _assemblyai(audio: bytes) -> dict:
    key = secret("ASSEMBLYAI_API_KEY")
    if not key:
        raise RuntimeError("ASSEMBLYAI_API_KEY not set — add it to ~/company/.secrets (gitignored) or the env")
    upload = _post(AAI_BASE + "/upload", audio,
                   {"authorization": key, "content-type": "application/octet-stream"})
    tid = _post(AAI_BASE + "/transcript", json.dumps({"audio_url": upload["upload_url"]}).encode(),
                {"authorization": key, "content-type": "application/json"})["id"]
    for _ in range(90):                                   # poll until done (fail loud on error/timeout)
        req = urllib.request.Request(AAI_BASE + f"/transcript/{tid}", headers={"authorization": key})
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read())
        if d["status"] == "completed":
            return {"text": d.get("text") or "", "provider": "assemblyai"}
        if d["status"] == "error":
            raise RuntimeError("AssemblyAI error: " + str(d.get("error")))
        time.sleep(1)
    raise RuntimeError("AssemblyAI transcription timed out")


# --- local faster-whisper (one-shot transcribe; the fully-on-machine ear) ---
# Tunables (env so the loop/operator can repoint without code): the model is large-v3-turbo (fast +
# accurate), int8_float16 on CUDA (pure int8 is the CPU path; on this RTX 4080 int8_float16 is the one
# that actually loads on GPU), beam_size 1 for low latency in a live loop.
WHISPER_MODEL = os.environ.get("COMPANY_WHISPER_MODEL", "large-v3-turbo")
WHISPER_DEVICE = os.environ.get("COMPANY_WHISPER_DEVICE", "cuda")
WHISPER_COMPUTE = os.environ.get("COMPANY_WHISPER_COMPUTE", "int8_float16")
WHISPER_LANG = os.environ.get("COMPANY_WHISPER_LANG", "en")

_whisper = None


def _whisper_engine():
    """Lazy singleton WhisperModel. Heavy import guarded → a clear 'pip install' message, never a
    crash on import of this module (the cloud path must keep working in the 3.14 runtime)."""
    global _whisper
    if _whisper is None:
        try:
            from faster_whisper import WhisperModel
        except ImportError as e:
            raise RuntimeError(
                "local faster-whisper STT not installed — `pip install faster-whisper` into .voice-venv "
                "(see voice/engines/REQUIREMENTS.md), or set COMPANY_STT=assemblyai for the cloud ear."
            ) from e
        # CPU by default: this box is CUDA-13, but CTranslate2 (faster-whisper) wants CUDA-12 libs
        # (libcublas.so.12) which aren't present → GPU raises at inference. CPU int8 transcribed a
        # test utterance correctly (2026-06-04) and never contends with the LLM for VRAM — the
        # low-contention path the STT research recommends. Force GPU only via COMPANY_STT_FORCE_GPU.
        dev = WHISPER_DEVICE if os.environ.get("COMPANY_STT_FORCE_GPU") else "cpu"
        comp = WHISPER_COMPUTE if dev != "cpu" else "int8"
        _whisper = WhisperModel(WHISPER_MODEL, device=dev, compute_type=comp)
    return _whisper


def _decode_to_float32(audio: bytes):
    """Bytes (a wav container, or raw audio) → mono float32 numpy at 16 kHz, what faster-whisper wants.
    soundfile reads the wav the browser/loop sends; resample to 16k if needed. Fail loud on garbage."""
    import io
    import numpy as np
    import soundfile as sf
    data, sr = sf.read(io.BytesIO(audio), dtype="float32")
    if data.ndim > 1:                                     # stereo → mono (mean the channels)
        data = data.mean(axis=1)
    if sr != 16000:                                       # whisper expects 16 kHz
        import math
        n = int(math.floor(len(data) * 16000 / sr))
        # linear resample (dependency-free; good enough for STT, which is robust to it)
        idx = np.linspace(0, len(data) - 1, n)
        data = np.interp(idx, np.arange(len(data)), data).astype("float32")
    return data


def _whisper_local(audio: bytes) -> dict:
    """One-shot transcription of a complete utterance (the transcribe() contract). VAD/endpointing is a
    STREAM concern (loop.py calls vad_speech_timestamps below) — this just turns finished audio into text.
    Return shape mirrors _assemblyai: {"text":..., "provider":...}."""
    samples = _decode_to_float32(audio)
    segments, _info = _whisper_engine().transcribe(
        samples, language=WHISPER_LANG, beam_size=1, vad_filter=False)
    text = "".join(seg.text for seg in segments).strip()  # segments is a generator — consuming it runs inference
    return {"text": text, "provider": "whisper_local"}


# --- Silero VAD (endpoint detection / barge-in) — a STREAM helper the loop drives, not part of transcribe() ---
_silero = None


def _silero_vad():
    """Lazy singleton Silero VAD model + utils. Guarded import → clear install message. Used by loop.py
    for (a) endpointing — knowing an utterance finished — and (b) barge-in — detecting the operator
    started speaking while the character is talking, so playback can be cut."""
    global _silero
    if _silero is None:
        try:
            from silero_vad import load_silero_vad, get_speech_timestamps
        except ImportError as e:
            raise RuntimeError(
                "Silero VAD not installed — `pip install silero-vad` into .voice-venv "
                "(see voice/engines/REQUIREMENTS.md). Needed for endpointing + barge-in.") from e
        _silero = (load_silero_vad(), get_speech_timestamps)
    return _silero


def vad_speech_timestamps(audio, sampling_rate: int = 16000, threshold: float = 0.5) -> list:
    """Speech regions in `audio` (float32 mono numpy/list/tensor at 16 kHz) as [{'start':int,'end':int}, …]
    in SAMPLES. The loop uses this two ways:
      • endpointing — trailing silence after the last speech region marks a finished thought (combine with
        loop.py's semantic turn-detection — the naturalness lever);
      • barge-in — any speech region in the mic buffer WHILE the character speaks means cut playback.
    Fail loud if VAD isn't installed (no silent 'never detects speech' no-op)."""
    model, get_speech_timestamps = _silero_vad()
    return get_speech_timestamps(audio, model, sampling_rate=sampling_rate, threshold=threshold)


def vad_has_speech(audio, sampling_rate: int = 16000, threshold: float = 0.5) -> bool:
    """Convenience for barge-in: True if ANY speech is present in the buffer. Loud-fails like the above."""
    return len(vad_speech_timestamps(audio, sampling_rate=sampling_rate, threshold=threshold)) > 0
