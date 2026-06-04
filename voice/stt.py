"""voice/stt.py — speech-to-text, a SWAPPABLE provider (see voice/AGENTS.md).

Default: AssemblyAI (cloud, top accuracy + low latency, key from ~/company/.secrets). Audio leaves
the machine — that trades the fully-local path; it's a config flag so you can flip to local Whisper.
Stdlib only (HTTP), so it runs in the 3.14 runtime venv — no heavy install for the cloud provider.
"""
from __future__ import annotations
import io
import json
import os
import time
import urllib.error
import urllib.request
import uuid

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AAI_BASE = "https://api.assemblyai.com/v2"

# --- the EAR REGISTRY (registry-is-truth, AGENTS.md rule 8) ---------------------------------------
# STT_PROVIDERS is the SINGLE source of what ears exist. The UI/RHM reads available_stt() (a status
# projection of this) — it NEVER guesses which providers exist. Adding an ear = adding a row here +
# (for local_http) running its service; no dispatch edit (transcribe() routes by `kind`).
#
# `kind` decides how transcribe() reaches the ear:
#   • cloud      — an off-machine API (needs a secret); audio LEAVES the machine (deliberate, configurable)
#   • local_lib  — an in-process library in THIS interpreter (the .voice-venv); reported available only
#                  when the lib is importable here (never guess)
#   • local_http — a small HTTP service on its own port (whisper.cpp now; the 3 GPU ears on 2031-2033),
#                  reached stdlib-only (multipart POST → {text}); liveness via GET / (200). This is how
#                  stt.py stays 3.14-IMPORTABLE — no heavy import for the HTTP ears.
#
# whisper.cpp ROUTE NOTE (verified 2026-06-05): the live voicemode whisper-server build on :2022 serves
# the OpenAI-compatible route /v1/audio/transcriptions and returns 404 for /inference (the classic
# whisper.cpp example route this build does NOT mount). A POST of a kokoro clip to
# /v1/audio/transcriptions returned {"text":" The quick brown fox..."}. So `route` is the one that
# ACTUALLY works on this box (evidence over the assumed /inference). `route`+`field` are per-provider
# config so a build that uses /inference is a one-line catalog edit, not a code change.
STT_PROVIDERS: dict[str, dict] = {
    "assemblyai": {
        "kind": "cloud", "label": "AssemblyAI (cloud)",
        "needs_secret": "ASSEMBLYAI_API_KEY",
        "note": "top accuracy/latency; audio leaves the machine (configurable trade)."},
    "whispercpp": {
        "kind": "local_http", "label": "whisper.cpp (local, CPU)",
        "url": os.environ.get("COMPANY_WHISPERCPP_URL", "http://127.0.0.1:2022"),
        "route": os.environ.get("COMPANY_WHISPERCPP_ROUTE", "/v1/audio/transcriptions"),
        "field": "file",
        "note": "zero-install on-machine ear; the boot default. OpenAI-compat route on this build."},
    "whisper_local": {
        "kind": "local_lib", "label": "faster-whisper (local lib)",
        "lib": "faster_whisper",
        "note": "fully on-machine; runs in .voice-venv (3.12). CPU int8 by default (CUDA-13 box)."},
    # The three GPU ears (lane 4) — registered DECLARATIVELY so available_stt() probes them and the UI
    # lists them, even when their service isn't up. A down ear = available:false + legible detail (NOT
    # a crash). Each is an HTTP twin of the TTS engine service (voice/ears/_stt_service.py).
    "parakeet": {
        "kind": "local_http", "label": "NVIDIA Parakeet-TDT 0.6B v3 (GPU, NeMo)",
        "url": os.environ.get("COMPANY_PARAKEET_URL", "http://127.0.0.1:2031"),
        "route": "/inference", "field": "file",
        "note": "live multilingual workhorse; ~2000x; needs NeMo venv (CUDA-13 hazard)."},
    "canary": {
        "kind": "local_http", "label": "NVIDIA Canary-Qwen 2.5B (GPU, NeMo)",
        "url": os.environ.get("COMPANY_CANARY_URL", "http://127.0.0.1:2032"),
        "route": "/inference", "field": "file",
        "note": "English-max + understanding (LLM-based); needs NeMo venv."},
    "granite": {
        "kind": "local_http", "label": "IBM Granite Speech 4.0 1B (GPU, transformers)",
        "url": os.environ.get("COMPANY_GRANITE_URL", "http://127.0.0.1:2033"),
        "route": "/inference", "field": "file",
        "note": "compact top-accuracy cross-check; transformers venv (lands clean)."},
}

# back-compat aliases — selecting one of these resolves to a canonical catalog id (the id-mismatch
# bug fix: `whisper_local` was advertised but transcribe() only took whisper/local). transcribe()
# normalises through this map BEFORE dispatch, so a flip assemblyai↔whispercpp↔whisper_local is a
# config change, never a code change.
STT_ALIASES = {
    "whisper": "whisper_local",
    "local": "whisper_local",
    "whisper.cpp": "whispercpp",
    "whisper_cpp": "whispercpp",
}

# The boot-default ear. whisper.cpp NOW (live, zero-install, on-machine) — flip to parakeet once it's
# verified up. COMPANY_STT overrides. (Old name DEFAULT_PROVIDER kept as an alias below.)
STT_DEFAULT = os.environ.get("COMPANY_STT", "whispercpp")
DEFAULT_PROVIDER = STT_DEFAULT                                # back-compat alias (bridge/loop may read it)


def active_ear() -> str:
    """The currently-selected default ear id (one source). The Suite's rhm_config().stt records WHICH
    ear is selected; this is the FALLBACK default when nothing is configured (= STT_DEFAULT). Always a
    real catalog id (never a guess)."""
    d = STT_DEFAULT
    return d if d in STT_PROVIDERS else "whispercpp"


def stt_default() -> str:
    """Alias of active_ear() for the bridge's /api/voice payload (mirrors the TTS stt_default field)."""
    return active_ear()


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


def _resolve_id(provider: str | None) -> str:
    """Normalise a selected provider id to a CANONICAL catalog id (applying back-compat aliases).
    None → the active default ear. Raises ValueError('unknown provider') only for a genuinely
    unregistered id — that's the registry-is-truth guard (the path-of-least-resistance law)."""
    pid = provider or active_ear()
    pid = STT_ALIASES.get(pid, pid)
    if pid not in STT_PROVIDERS:
        raise ValueError(
            f"unknown STT provider {provider!r} — registered ears: {sorted(STT_PROVIDERS)} "
            f"(aliases: {sorted(STT_ALIASES)}). Author from the registry, never invent.")
    return pid


def _probe_provider(pid: str, spec: dict) -> dict:
    """STATUS read for ONE ear — is it usable right now? NEVER raises (every branch is wrapped); a down
    ear returns available:false + a LEGIBLE detail (the UI greys it out, the RHM says why). This is the
    projection the registry-is-truth surfaces read. Returns {id,label,kind,available:bool,detail:str}."""
    base = {"id": pid, "label": spec.get("label", pid), "kind": spec.get("kind", "?")}
    try:
        kind = spec.get("kind")
        if kind == "cloud":
            key = secret(spec.get("needs_secret", ""))
            return {**base, "available": bool(key),
                    "detail": "key present" if key
                    else f"{spec.get('needs_secret')} not set (add to ~/company/.secrets)"}
        if kind == "local_lib":
            import importlib.util
            ok = importlib.util.find_spec(spec.get("lib", "")) is not None
            return {**base, "available": ok,
                    "detail": f"{spec.get('lib')} importable here" if ok
                    else f"{spec.get('lib')} not installed in this interpreter (.voice-venv)"}
        if kind == "local_http":
            url = spec.get("url", "")
            try:                                              # liveness via GET / (200) — in the contract
                with urllib.request.urlopen(url + "/", timeout=3) as r:
                    up = 200 <= r.status < 500                # 200 home OR 404 home both = the server answers
            except urllib.error.HTTPError as he:
                up = he.code < 500                            # a 4xx home still means the server is ALIVE
            except Exception as e:
                return {**base, "available": False, "url": url,
                        "detail": f"unreachable at {url} ({type(e).__name__}: {e}) — start its service"}
            return {**base, "available": up, "url": url,
                    "detail": f"up at {url}" if up else f"answered but unhealthy at {url}"}
        return {**base, "available": False, "detail": f"unknown kind {kind!r}"}
    except Exception as e:                                    # the no-raise guarantee — one bad row can't blow up the read
        return {**base, "available": False, "detail": f"probe error: {type(e).__name__}: {e}"}


def available_stt() -> dict:
    """The ear REGISTRY as a STATUS read — id → {label,kind,available,detail,...}. NEVER raises (each
    entry is probed under _probe_provider's guard). The UI/RHM reads THIS to know which ears exist and
    which are usable right now — it never guesses (AGENTS.md rule 8). A down ear is available:false with
    a legible detail, never an omission and never a crash (fail-loud-but-legible)."""
    return {pid: _probe_provider(pid, spec) for pid, spec in STT_PROVIDERS.items()}


def available() -> dict:
    """Back-compat thin wrapper (the old shape the bridge/UI may still read): id → bool. Built FROM
    available_stt() so it can never drift from the registry."""
    return {pid: e["available"] for pid, e in available_stt().items()}


def transcribe(audio: bytes, provider: str | None = None) -> dict:
    """Turn a finished utterance (wav/audio bytes) into {text, provider}. Routes BY KIND from
    STT_PROVIDERS (so every registered id is dispatchable — the id IS the catalog key; that structurally
    kills the old id-mismatch where `whisper_local` was advertised but unrouted). A selected-but-DOWN
    local_http ear raises LOUD naming the provider + endpoint — NO silent fallback to another ear
    (AGENTS.md rule 4)."""
    pid = _resolve_id(provider)
    spec = STT_PROVIDERS[pid]
    kind = spec["kind"]
    if kind == "cloud":
        if pid == "assemblyai":
            return _assemblyai(audio)
        raise ValueError(f"no cloud handler for {pid!r}")     # only assemblyai cloud today
    if kind == "local_lib":
        return _whisper_local(audio)                          # the in-process faster-whisper ear
    if kind == "local_http":
        return _http_transcribe(audio, pid, spec)
    raise ValueError(f"unknown STT kind {kind!r} for provider {pid!r}")


# --- local_http transport (stdlib only — keeps stt.py 3.14-importable, no heavy deps) -------------

def _multipart_wav(audio: bytes, field: str, filename: str = "audio.wav",
                   extra: dict | None = None) -> tuple[bytes, str]:
    """Build a multipart/form-data body uploading `audio` under form field `field` (whisper.cpp /
    the ear services want `file=@clip`). Returns (body_bytes, content_type). Pure stdlib (no `requests`)
    so the cloud + HTTP ears run in the 3.14 runtime venv. `extra` adds plain string fields (e.g.
    response_format=json)."""
    boundary = "----company-stt-" + uuid.uuid4().hex
    out = io.BytesIO()
    crlf = b"\r\n"
    for k, v in (extra or {}).items():                        # plain string fields first
        out.write(b"--" + boundary.encode() + crlf)
        out.write(f'Content-Disposition: form-data; name="{k}"'.encode() + crlf + crlf)
        out.write(str(v).encode() + crlf)
    out.write(b"--" + boundary.encode() + crlf)
    out.write(f'Content-Disposition: form-data; name="{field}"; filename="{filename}"'.encode() + crlf)
    out.write(b"Content-Type: audio/wav" + crlf + crlf)
    out.write(audio + crlf)
    out.write(b"--" + boundary.encode() + b"--" + crlf)
    return out.getvalue(), f"multipart/form-data; boundary={boundary}"


def _http_transcribe(audio: bytes, pid: str, spec: dict) -> dict:
    """POST the audio as multipart to a local_http ear's route → {text}. A DOWN ear raises LOUD naming
    the provider + the full endpoint — NEVER a silent fallback to another ear (AGENTS.md rule 4). The
    ear's response is {"text": "..."} (whisper.cpp + the _stt_service.py twin both return that shape)."""
    url = spec["url"].rstrip("/") + spec.get("route", "/v1/audio/transcriptions")
    field = spec.get("field", "file")
    body, ctype = _multipart_wav(audio, field, extra={"response_format": "json"})
    req = urllib.request.Request(url, data=body, headers={"Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.loads(r.read() or b"{}")
    except (urllib.error.URLError, ConnectionError, OSError) as e:
        raise RuntimeError(
            f"STT ear {pid!r} ({spec.get('label', pid)}) unreachable at {url}: "
            f"{type(e).__name__}: {e} — start its service. Refusing to fall back to another ear "
            f"(fail loud, AGENTS.md rule 4).") from e
    return {"text": (d.get("text") or "").strip(), "provider": pid}


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
