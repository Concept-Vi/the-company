# Coverage — area://voice
> Sweep date: 2026-06-08 · Anchored to doc://grs/synthesis + doc://grs/criteria
> area://voice = /home/tim/company/voice/ (stt.py, loop.py, lifecycle.py, loop.py turn-detection hooks, ears/, engines/, personas.py, speakable.py, tts_service.py, AGENTS.md)
> Prior synthesis anchors: bridge.py:734-903 (`/api/voice/stream`), suite.py:5264 (`chat_parts`), suite.py:5223 (`chat`)

---

## Shape of the area

```
voice/
  stt.py          — the swappable ear registry + transcribe() + transcribe_partial() + VAD (silero) 
  loop.py         — one full turn (hear→think→speak) + turn-detection hooks (utterance_ended / barge_in)
  lifecycle.py    — service up/warm/down + VRAM for ears + TTS engines
  personas.py     — persona registry (engine × voice per character)
  speakable.py    — the SPEAKABLE cleaning layer (strips markdown/code/urls for TTS)
  tts_service.py  — TTS HTTP service wrapper
  ears/           — GPU ear services (parakeet, canary, granite via _stt_service.py)
  engines/        — TTS engine services (kokoro, xtts, chatterbox, orpheus, cosyvoice)
  ref/            — reference clips for voice cloning
```

66 files total. Seams targeted: stt.py (voice-in), loop.py (circuit + turn-detection), bridge.py:734-903 (stream route), suite.py:5264 (chat_parts generator = the reuse point).

---

## Relation 1 — USE: Voice-in (STT) for the live dialogue

**Kind: USE** — the guided-review-surface hear→think→speak loop depends on this path.

**Observed** (voice/stt.py:50–116 + bridge.py:815–822):
- `STT_PROVIDERS` is the single registry. Default ear: `whispercpp` (whisper.cpp on :2022, OpenAI-compatible `/v1/audio/transcriptions`).
- Three additional GPU ears (parakeet / canary / granite on :2031–2033) registered declaratively — available_stt() probes them.
- `transcribe(audio, provider=None)` routes by kind: `local_http` (whisper.cpp + GPU ears), `local_lib` (faster-whisper), `cloud` (assemblyai). Fails loud on down ear — no silent fallback (AGENTS.md rule 4).
- Audio normalisation to 16kHz mono WAV via `_to_wav16()` is handled transparently — browser webm/opus and iOS mp4/aac are both normalised before dispatch (verified 2026-06-06: raw webm → empty transcript; normalised → full transcript).
- At bridge.py:815–822: ear is read from `SUITE.rhm_config().get("stt")` → `voice_stt.active_ear()` fallback → `voice_stt.transcribe(audio, provider=ear)` → `transcript` string.

**Observed** (voice/stt.py:218–228 — `transcribe_partial`):
- Tier-2 streaming-STT primitive exists: posts the growing audio window as the operator speaks; on VAD pause the last partial = the finished utterance. The FE drives windowing (stateless). Documented as a scaffold for a later truly-streaming ASR swap.

**What it means for the guided-review-surface:**
The voice-in path is complete and stable. For the live dialogue surface to USE voice: the FE captures audio → sends to `/api/voice/stream` (POST body = raw audio bytes) → bridge normalises + transcribes → result is the operator's message. Zero new STT infrastructure needed. The `transcribe_partial` scaffold already provides a live-partial display path (show what the brain is "hearing" in real time) — this is a bonus capability the surface can expose with zero backend change.

---

## Relation 2 — USE: The voice stream generator (`chat_parts`) — the streaming path text-chat currently lacks

**Kind: USE + UNIFICATION** — the surface's "talks back live" requirement is satisfied by a generator that already exists and is proven on voice. Text chat does not yet use it.

**Observed** (suite.py:5264–5312):
- `chat_parts(message, graph_id, focus=None, *, turn_id=None, persist=True)` is a generator.
- Accepts `focus` as its 3rd positional param (same signature as `chat()`).
- Yields `{part, text, final, staged, …}` dicts. On the bypass path (trivial turn / focus/background/off mode): yields ONE part with `staged=False`. On the staged path: yields Part 1 instantly from base context, then Part 2 (final) after the cognition wave injects into `run://`. Epilogue (single append + single `_emit('chat')`) runs inside the generator — the caller gets this for free.
- `chat_parts` IS the voice stream's brain. `_stream_parts` in bridge.py:231 drives it with brain↔TTS overlap.

**Observed** (suite.py:5223–5242 — `chat()`):
- `/api/chat` (the text path) calls `chat()` which is prologue → ONE `_chat_part_core(is_final=True)` → epilogue. Full-wait. No streaming.
- There is NO text SSE/NDJSON endpoint wrapping `chat_parts`.

**Unification opportunity (named in synthesis, confirmed here):**
`chat_parts()` already exists and is proven. Wrapping it in a text SSE endpoint is straightforward: a new handler (`/api/chat/stream`) that drives `chat_parts` via `_stream_parts` with `speak_fn=lambda s: b""` (no TTS) and `emit_fn` writing NDJSON lines. The FE appends each `{type:part, text}` as it arrives. This is the same drain path used by the voice "voice off" branch (bridge.py:849–864) — that code already exists and demonstrates the exact pattern.

---

## Relation 3 — TOUCH: The focus-drop at bridge.py:848 — voice loses the studio locus

**Kind: TOUCH** — a seam that must be fixed for voice to be a first-class participant in the guided-review-surface.

**Observed** (bridge.py:848):
```python
parts_gen = SUITE.chat_parts(transcript, gid, turn_id=turn_id)
```
`focus` is **not passed**. `chat_parts` accepts `focus` as its 3rd parameter (suite.py:5264).

**Observed** (bridge.py:760 — `vq` parsing):
```python
vq = {k: v[0] for k, v in _pq(_up(self.path).query).items()}
```
The query string is parsed into `vq`. There is NO `focus` key extracted from `vq` at the voice/stream handler. Contrast with the text `/api/chat` handler, where `focus` arrives in the POST body JSON (suite.py:313–320 + bridge.py:216–219 approx.).

**Observed** (bridge.py via synthesis §D3):
The existing `sendChat` FE path carries `focus` (the synthesis notes "Auto-listen via `sendChat` already carries focus" — this is the typed text path through the chat endpoint). The voice route does NOT carry it.

**What it means:**
When the operator uses voice, `chat_parts` receives `focus=None`. The RHM's `_chat_context` (suite.py:1974) treats `focus=None` as no selection — no node detail, no co-presence, no widen-vocabulary (I1). The operator can be pointing at a node on the canvas and speaking about it, but the brain is blind to what they're looking at. The studio locus is dropped entirely for voice turns.

**The fix (Bucket B, small):**
Two parts:
1. FE: when posting audio to `/api/voice/stream`, include the current `focus.selected` in the query string (e.g., `?persona=…&focus_selected=ui://canvas/node/xyz`).
2. Bridge: extract `focus_selected` from `vq`, reconstruct `focus = {"selected": [focus_selected]}` (or as a comma-split list), and pass to `SUITE.chat_parts(transcript, gid, focus=focus, turn_id=turn_id)`.

That is 1 bridge line change + ~5 FE lines. The `chat_parts` internals need zero change — `focus` is already accepted and fully processed (suite.py:2073–2087).

---

## Relation 4 — USE: Finished-thought judge (VAD + semantic turn-detection)

**Kind: USE** — the live dialogue needs to know when the operator has finished speaking before firing the turn.

**Observed** (voice/loop.py:207–230 — `utterance_ended`):
- Two signals compose: trailing silence (VAD finds speech then `SILENCE_MS`=500ms of quiet after last speech region) + optional `semantic_complete` hook (a callable `()->bool`).
- When `semantic_complete` is given: BOTH pause AND semantic-complete must hold. This is the "reply on a finished thought, not a silence timer" design from the cast doc.
- `SILENCE_MS` is configurable: `COMPANY_VAD_SILENCE_MS` env var + per-call `silence_ms` kwarg.

**Observed** (voice/loop.py:233–237 — `barge_in`):
- `barge_in(mic_buffer)` → `vad_has_speech()` → True if operator started speaking while character is talking. Plugs into bridge.py:780–793 (`client_gone`) for the cancel-on-barge-in path.

**Observed** (voice/stt.py:403–416 — `vad_speech_timestamps` / `vad_has_speech`):
- Both backed by Silero VAD (lazy-loaded). Fail loud if not installed. Used by `utterance_ended` + `barge_in` respectively.

**What it means for the guided-review-surface:**
The finished-thought detection is built and composable. For the guided dialogue the relevant hook is `utterance_ended` — the FE drives the VAD loop on the client side (browser audio stream), accumulates audio, calls `/api/stt/partial` during capture (the `transcribe_partial` path), and fires the full `/api/voice/stream` POST when `utterance_ended` returns True. The `semantic_complete` hook is currently left empty in the live route (bridge.py does not pass one — the VAD silence alone is the trigger). A future improvement: pass a "is this a finished question/statement?" lightweight judge as the semantic hook to eliminate false cuts on mid-ramble pauses. The scaffold is already there; it's an open slot.

---

## Relation 5 — UNIFY: Voice barge-in cancel path → text streaming cancel path

**Kind: UNIFY** — the same disconnect-detection pattern that makes voice interruptible can be reused for text streaming.

**Observed** (bridge.py:772, 780–793 — `gone[0]` + `client_gone`):
```python
gone = [False]
def client_gone():
    if gone[0]: return True
    r, _, _ = _sel.select([self.connection], [], [], 0)
    if r and self.connection.recv(1, _sock.MSG_PEEK) == b"":
        gone[0] = True
    return gone[0]
```
- `gone[0]` is the shared cancellation flag. `client_gone()` proactively probes via `select+MSG_PEEK` — stops BEFORE the next expensive synth (not just on write failure).
- `_stream_parts` accepts `should_stop=client_gone` and polls it between each part (bridge.py:329–331).

**Observed** (synthesis §C-d):
The text streaming cancel path (client-disconnect detection for `/api/chat/stream`) does NOT exist yet. The synthesis identifies it as the net-new piece for barge-in on text (interruptible text streaming).

**Unification opportunity:**
`client_gone()` is defined inline in `_voice_stream`. It is generic — it only uses `self.connection` and `gone[0]`, which any HTTP handler has. Extracting it as a module-level helper `_client_gone_flag(connection)` → returns `(gone, probe_fn)` would let the new `/api/chat/stream` handler reuse the same cancellation primitive. Zero change to the voice path; the text path gets barge-in for free by composition.

---

## Relation 6 — RELATE: Voice + guided dialogue are the same hear→think→speak loop at a locus

**Kind: RELATE (conceptual)** — the two surfaces share a circuit shape; the guided-review-surface IS voice in typed form.

**Observed** (voice/loop.py:147–196 — `loop_turn`):
- The circuit is: `hear(audio)` → `think(transcript, graph_id, focus)` → `speak(reply)`.
- `loop_turn` accepts `focus` explicitly (line 89: `def think(message, graph_id, focus=None, …)`) and passes it through to the bridge `/api/chat` call.
- This is the standalone scripted/CLI form; bridge.py:`_voice_stream` is the live HTTP form of the same circuit.

**Observed** (GUIDED-REVIEW-SURFACE.md:67):
> "you CLICK + TALK → RHM TALKS BACK (live dialogue, follows this/here) ← locus BUILT; streaming + temporal net-new"

**What it means:**
The guided-review-surface's core interaction is structurally identical to the voice circuit — the only differences are: (a) the input channel (typed text vs. audio → STT), (b) the output channel (streamed text vs. text → TTS → wav), and (c) the cancellation trigger (stop button vs. barge-in). The `chat_parts` generator sits at the centre of both — it IS the think step for both paths. Designing the guided dialogue as "the voice circuit with typed input and text-stream output" is not a metaphor — it is literally the same code path. This means every improvement to the voice loop (focus passthrough, semantic turn-detection, cancellation) is simultaneously an improvement to the typed dialogue, and vice versa. The unification is structural, not aspirational.

---

## Summary table

| # | Relation kind | What | File:line evidence | Status |
|---|---------------|------|--------------------|--------|
| 1 | USE | Voice-in (STT): `transcribe()` + `transcribe_partial()` for live dialogue | voice/stt.py:231, :218; bridge.py:815–822 | Ready — no new infra needed |
| 2 | USE + UNIFY | `chat_parts()` streaming generator — text chat doesn't use it yet | suite.py:5264; bridge.py:848; vs suite.py:5223 | Proven on voice; wrap for text SSE is the top unification |
| 3 | TOUCH | Focus-drop at bridge.py:848 — voice is locus-blind | bridge.py:848 (no focus arg); suite.py:5264 (accepts it) | 1 bridge line + ~5 FE lines |
| 4 | USE | Finished-thought judge: VAD silence + semantic hook | voice/loop.py:207–230; voice/stt.py:403–416 | Built; semantic hook slot is open |
| 5 | UNIFY | `client_gone` barge-in cancel pattern → reusable for text streaming | bridge.py:772–793 | Extract as helper; text path gets interruptibility |
| 6 | RELATE | Voice circuit and guided dialogue are the same hear→think→speak at a locus | voice/loop.py:147–196; GUIDED-REVIEW-SURFACE.md:67 | Structural identity, not metaphor |

---

## What each means (concise)

**Relation 1 — Voice-in (STT):** The ear is production-ready (whisper.cpp + 3 GPU ears registered, audio normalisation proven, fail-loud on down ear). For the guided dialogue to accept voice, zero backend change is needed — the FE posts audio bytes, bridge transcribes. `transcribe_partial` gives live caption for free.

**Relation 2 — chat_parts generator:** This IS the streaming engine. It already stages multi-part replies with brain↔TTS overlap, yields parts incrementally, handles brevity bypass (trivial turns stay fast), and runs the epilogue inside the generator. Text chat (`/api/chat`) does a full-wait version of the same thing. Wrapping `chat_parts` in a text SSE endpoint is the single highest-value unification in this area — it makes the guided dialogue feel live and is reused from already-proven voice infrastructure.

**Relation 3 — Focus-drop (bridge.py:848):** Voice is locus-blind. When Tim speaks to the canvas the brain doesn't know what he's looking at. The fix is one line. It should land in the same Bucket B pass as the walkthrough↔chat composition fix.

**Relation 4 — Finished-thought judge:** `utterance_ended` combines VAD silence + optional semantic judge. The semantic slot is open and un-wired — a lightweight "is this a complete thought?" judge (could be a short model call or a heuristic) would eliminate false-cut naturalness problems. The scaffold is in place.

**Relation 5 — Cancel pattern:** The `gone[0]` / `client_gone` SELECT+MSG_PEEK pattern is generic and reusable. The text streaming cancel path (barge-in equivalent for typed text) can share this primitive.

**Relation 6 — Circuit identity:** The guided review surface and the voice loop are the same circuit. Improvements to one are improvements to both. The canonical design is: hear (STT or keyboard) → `chat_parts()` → speak (TTS or SSE text stream). Focus passthrough is the shared missing seam.

---

## Criteria additions (append to doc://grs/criteria — never filter)

- **V1 · Voice focus passthrough** — bridge.py:848: pass `focus` through to `chat_parts()`. FE: include `focus.selected` in the voice/stream POST or query string. (Bucket B, ~1 bridge line + ~5 FE lines)
- **V2 · Text streaming via `chat_parts`** — new `/api/chat/stream` SSE handler drives `chat_parts` with `speak_fn=noop`, emits NDJSON `{type:part,text}` per part. FE appends live. (Bucket B + C-d — same as synthesis)
- **V3 · Extract `client_gone` as reusable helper** — move SELECT+MSG_PEEK pattern out of `_voice_stream` inline scope so `/api/chat/stream` handler can use the same interruptible-streaming primitive.
- **V4 · Semantic turn-detection hook (open slot)** — `utterance_ended`'s `semantic_complete` parameter is unwired in the live route. A lightweight "finished thought?" judge wired in here would improve naturalness without architecture change.
- **V5 · `transcribe_partial` for live caption** — the partial-transcript scaffold (voice/stt.py:218–228) is unused by the surface. Wiring it gives real-time "what I'm hearing" display in the dialogue UI — zero backend change.
