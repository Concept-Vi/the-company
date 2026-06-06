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
import asyncio
import io
import os
import queue
import sys
import threading
import uuid
import wave

# TRITON_ATTN (the attention backend, see ATTN_BACKEND) JIT-compiles its kernels with `ninja`, which
# must be on PATH. The systemd unit runs the venv's python DIRECTLY (not an activated venv), so the
# venv's bin/ — where `ninja` lives — is NOT on PATH and Triton's compile fails with
# FileNotFoundError: 'ninja'. Prepend the venv bin (dir of THIS interpreter) so ninja is found. This
# propagates to the spawned EngineCore (inherits env). (Researched + hit by use 2026-06-06.)
os.environ["PATH"] = os.path.dirname(sys.executable) + os.pathsep + os.environ.get("PATH", "")
# DISABLE the FlashInfer SAMPLER — THE layer-③ fix (verified by capture 2026-06-06). TRITON_ATTN moves
# ATTENTION off FlashInfer, but vLLM still used FlashInfer for top-k/top-p SAMPLING, which nvcc-JIT-
# compiles on first real use → "Could not find nvcc" → EngineCore DIES after the first synth. Forcing
# the native (torch) sampler removes FlashInfer from sampling too — no JIT, no nvcc dependency. Set
# BEFORE any vLLM import. (This was in the original orpheus.py; lost in the TRITON rewrite — restored.)
os.environ.setdefault("VLLM_USE_FLASHINFER_SAMPLER", "0")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from voice.engines._service import serve  # noqa: E402

PORT = 4125
# the model that's actually CACHED (canopylabs/orpheus-3b-0.1-ft) — NOT orpheus-speech's stock default
# "orpheus-tts-0.1-finetune-prod", which isn't on disk and triggers a ~6GB DOWNLOAD at load.
MODEL_NAME = os.environ.get("COMPANY_ORPHEUS_MODEL", "canopylabs/orpheus-3b-0.1-ft")
# context window (tokens): MUST hold a real spoken reply — text + the MANY SNAC audio tokens a reply
# generates (audio is token-dense). NOT minimised (a starved window can't carry a real reply). 8192
# comfortably holds a multi-sentence turn at modest KV cost on a 3B. (The CONVERSATION history is held
# by the BRAIN's 32K window — this per-utterance window only needs to fit one spoken reply.)
MAX_LEN = int(os.environ.get("COMPANY_ORPHEUS_MAXLEN", "8192"))
GPU_UTIL = float(os.environ.get("COMPANY_ORPHEUS_GPU_UTIL", "0.6"))    # ~9.8GB budget; weights ~6GB + 8192 KV fits
# graphs ON by default (enforce_eager=False) — Tim's priority is REAL-TIME inference after a one-time
# pinned load. (Earlier theory that graphs caused the gen crash was WRONG — see ATTN_BACKEND: the crash
# was FlashInfer on CUDA-13, not the graphs. COMPANY_ORPHEUS_EAGER=1 still available as a diagnostic.)
EAGER = os.environ.get("COMPANY_ORPHEUS_EAGER", "0") == "1"
# THE attention backend (root-caused over 4 layers, 2026-06-06): vLLM's priority on sm_89 is
# [FLASH_ATTN, FLASHINFER, TRITON_ATTN]. With flash-attn ABSENT it fell to FlashInfer (decode crash on
# CUDA-13, #26381); forcing TRITON_ATTN got past that but JIT-compiles a kernel PER sequence-shape
# during decode → the 2nd (new-shape) synth silently killed the EngineCore. FIX: install the matching
# prebuilt flash-attn (torch2.11/cu13 wheel) so vLLM uses FLASH_ATTN — PRECOMPILED, no per-shape JIT, no
# FlashInfer. The whole onion traces to flash-attn having been missing; it's how orpheus is built to run.
# Keeps graphs ON + context 8192. COMPANY_ORPHEUS_ATTN overrides (TRITON_ATTN/FLASHINFER to reproduce).
ATTN_BACKEND = os.environ.get("COMPANY_ORPHEUS_ATTN", "FLASH_ATTN")
DEFAULT_VOICE = os.environ.get("COMPANY_ORPHEUS_VOICE", "tara")
RATE = 24000
VOICE_BANK = ["tara", "leah", "jess", "leo", "dan", "mia", "zac", "zoe"]

_model = None


def _engine():
    """Load Orpheus's vLLM engine, configured for this box. Three fixes vs stock OrpheusModel (which
    cold-loaded ~17min + crashed on generation): (1) CACHED model (above) — stock pointed at an
    un-cached repo → a ~6GB download; (2) the installed OrpheusModel.__init__ is (model_name, dtype)
    ONLY (a version drift — passing max_model_len TypeErrors), so the engine args ride via this
    _setup_engine patch, not the constructor; (3) attention_backend=TRITON_ATTN — the real fix for the
    generation crash (vLLM fell through to FlashInfer, which crashes on decode on CUDA-13/Ada, #26381).
    Graphs stay ON (fast inference) + context at 8192 (adequate) — both preserved, not traded away."""
    global _model
    if _model is None:
        try:
            from orpheus_tts import OrpheusModel
            from vllm import AsyncLLMEngine, AsyncEngineArgs
        except ImportError as e:
            raise RuntimeError("orpheus not installed — `pip install orpheus-speech` (vLLM-based) "
                               "into the orpheus venv (see voice/engines/REQUIREMENTS.md)") from e

        def _fast_setup(self):                                  # replaces OrpheusModel._setup_engine
            args = AsyncEngineArgs(model=self.model_name, dtype=self.dtype, enforce_eager=EAGER,
                                   gpu_memory_utilization=GPU_UTIL, max_model_len=MAX_LEN,
                                   attention_backend=ATTN_BACKEND)   # TRITON_ATTN — avoid the FlashInfer cu13 crash
            return AsyncLLMEngine.from_engine_args(args)
        OrpheusModel._setup_engine = _fast_setup
        _model = OrpheusModel(model_name=MODEL_NAME)            # __init__ takes (model_name, dtype) only
    return _model


# --- ONE PERSISTENT event loop for the engine's lifetime (THE sequential-hang fix, 2026-06-06) ---
# orpheus_tts's generate_tokens_sync runs `asyncio.run(...)` in a NEW thread+loop PER CALL. AsyncLLMEngine
# binds its background output-processing loop to the FIRST call's event loop; asyncio.run() CLOSES that
# loop when the first synth returns, so the 2nd+ call's fresh loop can't drive the engine → the request
# HANGS (engine stays alive, request never completes — exactly the symptom: synth#1 OK, synth#2+ hang,
# even with unique request_ids). Fix: run ONE event loop in a daemon thread for the whole process and
# submit every request to it via run_coroutine_threadsafe — the engine's bg loop stays alive across
# requests. We drive m.engine.generate directly (the wrapper's prompt-format + sampling + SNAC decoder
# reused verbatim) so only the loop lifecycle changes.
_loop = None
_loop_lock = threading.Lock()


def _persistent_loop():
    global _loop
    with _loop_lock:
        if _loop is None:
            _loop = asyncio.new_event_loop()
            threading.Thread(target=_loop.run_forever, daemon=True, name="orpheus-engine-loop").start()
    return _loop


def _generate_token_texts(text: str, voice: str):
    """Yield the engine's token-text stream for one request, driven on the PERSISTENT loop (not a
    per-call asyncio.run). Matches orpheus_tts.generate_tokens_sync's params + per-result token handling
    exactly; only the loop lifecycle differs."""
    from vllm import SamplingParams
    m = _engine()
    prompt_string = m._format_prompt(text, voice)
    sp = SamplingParams(temperature=0.6, top_p=0.8, max_tokens=1200,
                        stop_token_ids=[49158], repetition_penalty=1.3)
    rid = "orph-" + uuid.uuid4().hex
    q: queue.Queue = queue.Queue()

    async def _producer():
        try:
            async for result in m.engine.generate(prompt=prompt_string, sampling_params=sp, request_id=rid):
                q.put(result.outputs[0].text)
        except Exception as e:                                # surface engine errors to the consumer
            q.put(e)
        q.put(None)                                           # completion sentinel

    asyncio.run_coroutine_threadsafe(_producer(), _persistent_loop())
    while True:
        item = q.get()
        if item is None:
            break
        if isinstance(item, Exception):
            raise item
        yield item


def synth(text: str, voice: str | None, speed: float) -> bytes:
    v = (voice or DEFAULT_VOICE).strip()
    if v not in VOICE_BANK:
        raise RuntimeError(f"unknown Orpheus voice {v!r} — one of {VOICE_BANK}")
    # speed accepted per the shared contract but NOT applied — Orpheus has no speed arg (it's an LLM
    # token stream; pace via inline cues / prompt). Documented in REQUIREMENTS.md.
    from orpheus_tts.decoder import tokens_decoder_sync     # SNAC: token-texts → 16-bit mono PCM chunks
    _engine()                                                # ensure loaded
    chunks = tokens_decoder_sync(_generate_token_texts(text, v))
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
    # PREVENT-AT-LAUNCH (the orphan fix, researched 2026-06-06): vLLM's EngineCore is a spawn Process
    # with NO OS death-link; its cleanup is finalizer-driven and runs ONLY on graceful Python exit. A
    # bare SIGTERM (or kill -9) bypasses it → EngineCore orphans + squats VRAM. Translating SIGTERM into
    # sys.exit() makes THIS launcher exit gracefully → Python finalizers fire → vLLM's own
    # terminate→join→kill_process_tree runs → EngineCore dies + VRAM frees. (systemd-unit stop also
    # reaps the whole cgroup; this protects the non-unit / direct path too.)
    import signal
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    serve("orpheus", port, synth, voices, warm=_engine)
