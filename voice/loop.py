"""voice/loop.py — the conversation loop: STT → brain → TTS, with barge-in + turn-detection hooks.

The trial's pipeline (cast doc: "a pipeline wrapping the Qwen brain", NOT speech-to-speech). A clean
module the bridge/UI drives — this does NOT wire the UI and does NOT capture the mic/speaker (browser
hardware; that's lane G). It is the headless circuit underneath.

WHY HTTP for the brain (not `import Suite.chat`): this module runs in .voice-venv (Python 3.12, where
faster-whisper + the engines live); the runtime/Suite is Python 3.14. A 3.12 process cannot import the
3.14 Suite. Instantiating a *second* Suite here would FORK the brain + event log + store — breaking
reuse-don't-parallel (AGENTS rule). So the brain is reached the same way the UI reaches it: POST the
bridge `/api/chat` {message, graph_id, focus} -> {reply, action, mode, history} (bridge.py:216-219,
which calls Suite.chat at suite.py:847). One brain, one event log, one store.

The three steps, each an injectable endpoint/callable so the bridge can repoint them:
  • ear:   voice.stt.transcribe(audio, provider="local")  -> {"text", "provider"}   (in-process, 3.12)
  • brain: POST <bridge>/api/chat                          -> {"reply", ...}          (HTTP, the one Suite)
  • mouth: POST <engine>/tts {text, voice?, speed?}        -> wav bytes              (HTTP, lane B engine)

Barge-in + semantic turn-detection are exposed as HOOKS (callables you pass in), not hardcoded, because
the actual audio stream lives in the browser (lane G) — the loop provides the SHAPE and the VAD glue;
the UI feeds it frames and honours `stop_playback`.
"""
from __future__ import annotations
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from voice import stt as voice_stt                          # noqa: E402  (in-process STT, same venv)
from voice import personas as voice_personas                # noqa: E402

BRIDGE_URL = os.environ.get("COMPANY_BRIDGE_URL", "http://127.0.0.1:8770")
# The engine port map — the SHARED contract the runtime-backend builder relies on. Names → base URLs.
ENGINE_PORTS = {"kokoro": 4123, "chatterbox": 4124, "orpheus": 4125,
                "cosyvoice": 4126, "xtts": 4127, "qwen3tts": 4128}


def engine_url(engine: str) -> str:
    """Base URL for an engine by name. Fail loud on an unknown engine — never silently default."""
    if engine not in ENGINE_PORTS:
        raise ValueError(f"unknown engine {engine!r} — one of {sorted(ENGINE_PORTS)}")
    return os.environ.get(f"COMPANY_{engine.upper()}_URL", f"http://127.0.0.1:{ENGINE_PORTS[engine]}")


def _post(url: str, payload, timeout: int = 120, raw_bytes: bool = False):
    """POST JSON; return parsed JSON (or raw bytes for the wav). Fail loud on any HTTP/parse error."""
    data = payload if isinstance(payload, (bytes, bytearray)) else json.dumps(payload).encode()
    headers = {"Content-Type": "application/octet-stream" if isinstance(payload, (bytes, bytearray))
               else "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
    return body if raw_bytes else json.loads(body or b"{}")


# --- the three steps ---

def default_ear(bridge_url: str | None = None) -> str:
    """The SELECTED ear, read from the bridge's GET /api/rhm-config .stt (the ONE source of which ear
    is active — the config slot the suite lane added). The loop runs in .voice-venv (3.12) and cannot
    import the 3.14 Suite, so it asks the bridge (same as it reaches the brain). Fail-soft to the stt
    module's STT_DEFAULT only if the bridge can't be reached / has no slot yet (NOT a hardcoded 'local'
    — that was bug 2, selection split bridge-vs-loop)."""
    base = bridge_url or BRIDGE_URL
    try:
        req = urllib.request.Request(base + "/api/rhm-config")
        with urllib.request.urlopen(req, timeout=5) as r:
            cfg = json.loads(r.read() or b"{}")
        ear = cfg.get("stt")
        if ear:
            return ear
    except Exception:
        pass
    return getattr(voice_stt, "STT_DEFAULT", None) or voice_stt.active_ear()


def listen(audio: bytes, provider: str | None = None, bridge_url: str | None = None) -> dict:
    """STT step. In-process (same venv) so no extra hop. The ear defaults to the SELECTED provider
    (bridge /api/rhm-config .stt via default_ear), not a literal 'local' — one source of selection.
    Returns voice.stt.transcribe's shape: {"text":..., "provider":...}. Fails loud if the chosen ear
    is down / not installed (the RuntimeError from transcribe), per fail-loud (no silent fallback)."""
    ear = provider or default_ear(bridge_url)
    return voice_stt.transcribe(audio, provider=ear)


def think(message: str, graph_id: str = "codebase", focus: dict | None = None,
          bridge_url: str | None = None) -> dict:
    """Brain step — the ONE Company brain via the bridge (never a forked Suite). Returns {"reply", ...}.
    graph_id defaults to the demo graph the bridge seeds; focus is the optional context hint Suite.chat
    accepts. Fail loud if the bridge is down (no silent 'brain unavailable')."""
    base = bridge_url or BRIDGE_URL
    return _post(base + "/api/chat", {"message": message, "graph_id": graph_id, "focus": focus})


def speak(text: str, engine: str, voice: str | None = None, speed: float = 1.0) -> bytes:
    """TTS step — POST the selected engine's /tts, return wav bytes. `voice` semantics are per-engine:
    Orpheus = a voice name (tara…); Qwen3-TTS/CosyVoice = a voice DESCRIPTION/instruction; XTTS/Chatterbox
    = a reference-clip path (or None → the engine's COMPANY_VOICE_REF). loop_turn fills this from the
    persona automatically."""
    payload = {"text": text, "speed": speed}
    if voice is not None:
        payload["voice"] = voice
    base = engine_url(engine)
    try:
        return _post(base + "/tts", payload, raw_bytes=True)
    except (urllib.error.URLError, ConnectionError, OSError) as e:   # legible fail-loud (name engine+port)
        raise RuntimeError(
            f"TTS engine {engine!r} at {base} unreachable: {type(e).__name__}: {e} — "
            f"start/load the engine's service. Refusing a silent failure (no garbage audio).") from e


# Sensible bank defaults for the named-voice engines when a persona carries no explicit assignment.
_DEFAULT_NAMED_VOICE = {"orpheus": "tara", "kokoro": "bf_emma"}


def _voice_arg_for(persona: dict, engine: str | None = None) -> str | None:
    """Map a persona record → the right `voice` arg for the SELECTED engine (engines differ in what
    `voice` means — see speak()). Keying off the SELECTED engine, NOT the persona's default engine, is
    what lets ANY persona be voiced by ANY engine (Tim 2026-06-07: 'all personas work for all engines').
      • qwen3tts / cosyvoice — the natural-language voice_description (the character's SOUND, designed).
      • orpheus / kokoro     — a NAMED bank voice from the persona's `voices` map (fallback to a default).
      • xtts / chatterbox    — None → the engine's COMPANY_VOICE_REF reference clip.
    Centralised so the picker/loop/bridge don't each re-derive it."""
    eng = engine or persona.get("engine")
    if eng in ("qwen3tts", "cosyvoice"):
        return persona.get("voice_description")             # description-driven engines
    if eng in ("orpheus", "kokoro"):
        return (persona.get("voices") or {}).get(eng) or persona.get("voice") or _DEFAULT_NAMED_VOICE.get(eng)
    return None                                             # xtts/chatterbox: None → engine's COMPANY_VOICE_REF


def select_persona(persona_id: str, bridge_url: str | None = None) -> dict:
    """Set the brain's persona for this character via the bridge (POST /api/rhm-config {persona}), so the
    ONE brain holds the sketch (suite.py:866). Returns {persona record, rhm_config}. This is how a
    character's CHARACTER is loaded — the loop then voices it with that character's engine."""
    p = voice_personas.get_persona(persona_id)              # fail loud on unknown id
    base = bridge_url or BRIDGE_URL
    cfg = _post(base + "/api/rhm-config", {"persona": p["brain"]})
    return {"persona": p, "rhm_config": cfg}


# --- one turn, and the hooks ---

def loop_turn(audio: bytes, persona_id: str, *, graph_id: str = "codebase",
              stt_provider: str | None = None, bridge_url: str | None = None,
              think_fn=None, speak_reply: bool = True, engine_override: str | None = None,
              voice_override: str | None = None, on_transcript=None, on_reply=None) -> dict:
    """ONE full turn of the circuit for a given character:
        audio (a finished utterance) → transcript → brain reply → wav in that character's voice.
    Returns {"transcript", "reply", "engine", "voice", "wav": <bytes>, "action", "mode"}.
    `speak_reply` is the per-mode VOICE GATE (G4.4): when False (the mode's voice_enabled is off — a
    text-only presence), the SPEAK step is skipped — hear→think still run, wav is b"" and engine/voice
    are None. The bridge passes Suite.voice_enabled() here so a text-only mode never synthesises audio
    (and never boots an engine for nothing), honouring the per-mode toggle in the circuit itself.
    `on_transcript`/`on_reply` are optional callbacks (the UI shows them as they arrive — streaming feel).
    `think_fn` is the INJECTABLE brain step (the module docstring's "each step an injectable callable so
    the bridge can repoint them"): a callable `(transcript) -> {"reply", "action"?, "mode"?}`. When the
    loop runs INSIDE the 3.14 bridge, the bridge injects the IN-PROCESS Suite.chat here — so the brain is
    the ONE in-process Suite (one event log, one store), NOT an HTTP self-call back to /api/chat. When
    omitted (the loop running standalone in .voice-venv), it falls to the HTTP think() — same brain, the
    way the UI reaches it. Either way: one brain, never a forked Suite (reuse-don't-parallel).
    Endpointing (knowing the utterance finished) is the CALLER's job via the turn-detection hooks below;
    by the time loop_turn is called, `audio` is a complete thought."""
    p = voice_personas.get_persona(persona_id)              # fail loud on unknown character
    heard = listen(audio, provider=stt_provider, bridge_url=bridge_url)
    transcript = heard.get("text", "")
    if on_transcript:
        on_transcript(transcript)
    if not transcript.strip():
        raise RuntimeError("empty transcript — STT heard nothing (fail loud, not a silent skip)")
    thought = think_fn(transcript) if think_fn else think(transcript, graph_id=graph_id, bridge_url=bridge_url)
    reply = thought.get("reply", "")
    if on_reply:
        on_reply(reply)
    if not speak_reply:                                     # G4.4: voice off for this mode → text-only turn
        return {"transcript": transcript, "reply": reply, "engine": None, "voice": None,
                "wav": b"", "spoke": False, "action": thought.get("action"), "mode": thought.get("mode")}
    # G4.2: an explicit engine/voice override (the tts_engine/tts_voice config slots) wins over the
    # persona's default engine — so the operator can voice ANY persona through ANY engine live; unset
    # → the persona's own engine (qwen3tts for Sable, etc.) unchanged.
    engine = engine_override or p["engine"]
    voice_arg = voice_override or _voice_arg_for(p, engine)   # voice for the SELECTED engine (any persona × any engine)
    wav = speak(reply, engine, voice=voice_arg)
    return {"transcript": transcript, "reply": reply, "engine": engine,
            "voice": voice_arg, "wav": wav, "spoke": True, "action": thought.get("action"),
            "mode": thought.get("mode")}


# --- turn-detection + barge-in (the naturalness levers) — VAD glue the UI's audio stream drives ---

# The trailing-silence endpoint window (ms). Lowered 700→500 default for snappier turn-taking (Tim:
# "shorter silence window") — the SEMANTIC judge (semantic_complete) catches false stops, so we can be
# aggressive without cutting him off mid-ramble. Configurable: COMPANY_VAD_SILENCE_MS, and the caller
# (the browser VAD) may pass `silence_ms` per-call. This is a per-request naturalness knob.
SILENCE_MS = int(os.environ.get("COMPANY_VAD_SILENCE_MS", "500"))


def utterance_ended(audio_buffer, *, silence_ms: int = SILENCE_MS, sampling_rate: int = 16000,
                    semantic_complete=None) -> bool:
    """Endpoint detector for the live stream: True when the operator's CURRENT utterance is finished, so
    the loop should fire a turn. Two signals (the cast doc's 'reply on a finished thought, not a silence
    timer'):
      1. trailing silence — VAD finds speech, then `silence_ms` of quiet after the last speech region;
      2. semantic completeness — an OPTIONAL caller hook `semantic_complete(text)->bool` (e.g. the brain
         judging 'is this a finished thought?'). When given, BOTH the pause AND semantic-complete must
         hold — that's the big naturalness lever (don't cut him off mid-ramble).
    `audio_buffer` is float32 mono @ 16k. Fails loud if VAD isn't installed (via vad_speech_timestamps)."""
    ts = voice_stt.vad_speech_timestamps(audio_buffer, sampling_rate=sampling_rate)
    if not ts:
        return False                                        # no speech yet — nothing to end
    try:
        total = len(audio_buffer)
    except TypeError:
        total = int(getattr(audio_buffer, "shape", [0])[-1])
    trailing_samples = total - ts[-1]["end"]
    paused = trailing_samples >= int(silence_ms / 1000.0 * sampling_rate)
    if not paused:
        return False
    if semantic_complete is not None:                       # require a finished THOUGHT, not just a pause
        return bool(semantic_complete())
    return True


def barge_in(mic_buffer, *, sampling_rate: int = 16000, threshold: float = 0.5) -> bool:
    """Barge-in detector: True if the operator started speaking (any VAD speech in the mic buffer) WHILE a
    character is talking — the UI then STOPS playback immediately and starts a new listen. A property the
    cast doc requires ('barge-in' / 'two-way'). Fails loud if VAD isn't installed."""
    return voice_stt.vad_has_speech(mic_buffer, sampling_rate=sampling_rate, threshold=threshold)
