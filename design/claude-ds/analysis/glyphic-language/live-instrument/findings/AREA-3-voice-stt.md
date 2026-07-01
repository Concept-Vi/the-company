# AREA 3 — Voice In: STT / Transcription / the Live Speech Path

> Research-wave companion to `../ANCHOR.md`. My area: how Tim's spoken words get transcribed and
> reach a live consumer. **The verdict up front:** a complete, *operator-verified-headlessly*
> live-speech circuit ALREADY EXISTS — STT registry, VAD endpointing, a semantic finished-thought
> judge, barge-in, sentence-streamed reply, and a server-side speak-back. **But it hardwires exactly
> ONE consumer of the transcript — the conversational brain.** The glyphic extract layer is a
> *second, different* consumer of the same transcript, and that single-brain coupling is precisely
> what must open into a fan-out. The subscribe *substrate* (SSE over a shared log) exists and is
> reusable — but **no full-fidelity transcript event is broadcast live onto it today**; the only
> shared-log copies are truncated and post-turn. That gap is the build.

Evidence tags: **Observed (file:line)** / **Inferred** / **External-prior-art** / **My-idea**.

---

## 0 · TL;DR against the anchor's four questions

- **(a) Where does the transcript land — can a live consumer subscribe?** It lands in **three
  places, none of them a live full-fidelity broadcast**: (1) the **NDJSON response to the posting
  browser** (`{type:transcript,text}`, point-to-point, full text); (2) a **post-turn, truncated
  run-record** on the shared event log (`transcript=transcript[:2000]`, fires *after* think+TTS);
  (3) a **fire-and-forget 200-char browser trace** (`autolisten_stt`/`autolisten_fire`). The SSE
  subscribe substrate `/api/stream` exists and tails the shared log — **but the transcript is not
  written to that log live and whole.** So a non-browser consumer *can subscribe to the substrate*,
  but *would receive only a truncated, post-turn echo* today. **The wire is half-built.**
- **(b) Latency + turn-taking reality.** The ears are **batch ASR, not streaming**. "Live" today =
  **utterance-chunked turns**, gated by a VAD trailing-silence pause **AND** a per-pause **semantic
  judge round-trip** to a fast role-bound model. The graph would update **per finished-thought**,
  not continuously / per-token. `transcribe_partial` exists but is re-transcription of a growing
  window, not true streaming ASR (an explicit "later swap").
- **(c) Existing live transcript→consumer wire to reuse, or what's missing.** **Reuse:** the whole
  capture→VAD→STT→finished-thought→turn machinery, the `on_transcript` seam, and the SSE substrate.
  **Missing:** a designed *full-fidelity transcript event emitted live onto the shared log* +
  *opening the `transcript → single-brain` coupling into a `transcript → [brain] AND [extract
  swarm]` fan-out.* The extract layer is a new subscriber of an existing producer.
- **(d) Speak-back path for narrating the graph.** **Fully built and universal.** `POST /api/say`
  → `voice/say.py` serialized host-speaker queue (server-side, no browser), and `POST /api/tts` /
  the sentence-streamed `/api/voice/stream` for browser playback. The read-out narration ("a gateway
  holding the home, at rest") flows straight into either. The **speakable layer** (one transform,
  every reply→speech path) already cleans + engine-maps any text. Narration is a solved sink.

---

## 1 · The map — what's actually there (the speech path, end to end)

The circuit is two repos' worth of real code. The **headless circuit** is `voice/` (the ear, the
loop, the mouth); the **browser half** (mic capture, RMS-VAD, barge-in, playback) is
`canvas/app/src/useAppController.ts`; they meet at the **bridge** (`runtime/bridge.py`) HTTP seam.

```
                         BROWSER (canvas/app)                          SERVER (bridge :8770, 3.14)              VENV (.voice-venv 3.12)
  mic ──getUserMedia──▶ MediaRecorder (webm/opus)         POST /api/voice/stream (audio bytes)
        AnalyserNode RMS-VAD ─ end-of-speech pause ─┐                │
        api.stt(blob) ──────────────────────────────┼─▶ POST /api/stt ─────────────────────▶ voice.stt.transcribe()  [ffmpeg→16k wav→ear]
        api.finishedThought(text) ──────────────────┼─▶ POST /api/voice/finished-thought ─▶ Suite.is_finished_thought() [judge role-model]
        if FINISHED → api.voiceStream(blob,persona) ─┘                │
                                                        _voice_stream(): transcribe → chat_parts → speak per-sentence
        ◀── ndjson {transcript}{part}{chunk wav_b64}{reply}{done} ───┘                │
        Web Audio plays chunks; barge-in (RMS) cancels reader + stops sources
```

**Observed file inventory** (the load-bearing files for my area):

| Concern | File | Key symbols |
|---|---|---|
| Ear registry (STT) | `voice/stt.py` | `STT_PROVIDERS`, `transcribe`, `transcribe_partial`, `available_stt`, `_to_wav16`, `vad_speech_timestamps`, `vad_has_speech` |
| The headless loop | `voice/loop.py` | `loop_turn`, `listen`, `think`, `speak`, `utterance_ended`, `barge_in`, `default_ear` |
| Speak-back (server) | `voice/say.py` | `Speaker`, `say`, `get_speaker` (host-speaker serialized queue) |
| Speakable transform | `voice/speakable.py` | `speakable(reply, engine)` (one transform, every reply→speech path) |
| Constitution | `voice/AGENTS.md` | the guarantees + "where new things go" |
| Bridge seam | `runtime/bridge.py` | `/api/stt`, `/api/voice/stt-partial`, `/api/voice/turn`, `/api/voice/stream` (`_voice_stream`), `/api/voice/finished-thought`, `/api/say`, `/api/tts`, `/api/stream` (`_stream` SSE), `_stream_parts` |
| Semantic judge | `runtime/suite.py` | `is_finished_thought` (the `judge` role), `chat_parts`, `events_since`, `voice_log`, `emit_run_record`, `voice_enabled` |
| Browser live loop | `canvas/app/src/useAppController.ts` | `startAutoListen`/`listenOnce`, `recordToggle` (push-to-talk), `runVoiceTurn`, `bargeIn`, `playChunk` |
| Browser API client | `canvas/app/src/api.ts` | `stt`, `finishedThought`, `voiceStream`, `voiceLog` |

---

## 2 · How speech gets transcribed (the ear) — Observed

### 2.1 The ear is a swappable registry, not one provider
`STT_PROVIDERS` (Observed `voice/stt.py:68-119`) is the single source of which ears exist. Rows:
- `assemblyai` — **cloud** (audio leaves the machine; deliberate, configurable).
- `whispercpp` — **local_http :2022**, the boot default (`STT_DEFAULT = "whispercpp"`, Observed
  `stt.py:134`). OpenAI-compat route `/v1/audio/transcriptions` (Observed note `stt.py:64-67`:
  this build returns 404 for `/inference`, evidence-over-assumption).
- `whisper_local` — **local_lib** faster-whisper in `.voice-venv` (CPU int8 default; CUDA-13 box
  can't load the CUDA-12 CTranslate2 libs, Observed `stt.py:362-367`).
- `parakeet` / `canary` / `granite` — **local_http GPU ears** (:2031/2032/2033, NeMo/transformers).
- `moonshine` — **local_http :2034**, the **interaction-loadout default ear**: ONNX, <1GB, CPU
  ~9× realtime, *doesn't pad short clips* (fast on commands), and a built-in `IntentRecognizer`
  (semantic speech→action). (Observed `stt.py:103-110`; `ops/services.json` `stt-moonshine`.)
- `parakeet-onnx` — **local_http :2035**, int8 ONNX, ~6.3% WER, 25 EU languages, and crucially
  **HOTWORD / CONTEXT BIASING** (boost UI/command vocabulary, "up to thousands of phrases").
  (Observed `stt.py:111-118`; `ops/services.json` `stt-parakeet-onnx`.)

**Routing** (Observed `transcribe`, `stt.py:249-267`): normalise alias → `_to_wav16` (ffmpeg
decodes browser webm/opus/mp4 → 16k mono wav; **THE fix** for "mic records but transcribes nothing",
Observed `stt.py:25-44`) → dispatch by `kind` (cloud/local_lib/local_http). A selected-but-down
ear **raises loud** naming the provider + endpoint — **NO silent fallback** (Observed
`_http_transcribe`, `stt.py:304-308`; constitution rule, `voice/AGENTS.md:17`).

The active ear is a **config slot** like the chat-brain model — `rhm_config().stt`, set via
`/api/rhm-config` (Observed bridge `/api/stt`, `bridge.py:2808`). One source for both the browser
path and the headless loop (`loop.default_ear` reads `/api/rhm-config .stt`, Observed `loop.py:100-116`).

> **Anchor cross-check (§7 "moonshine/whisper/parakeet — verify"):** verified — all three exist as
> registered ears with live ports, plus `canary`/`granite`/`parakeet-onnx`/`assemblyai`. The anchor
> under-counts; there are **8 ears** in the registry. The everyday loadout default is **Moonshine**
> (lean, CPU, 0 VRAM, co-resides with the brain), per `ops/services.json` `interaction` combo.

### 2.2 VAD + endpointing live in the ear module, driven by the stream
`vad_speech_timestamps` / `vad_has_speech` (Observed `stt.py:421-434`) wrap **Silero VAD** — used
two ways: endpointing (trailing silence after last speech) and barge-in (any speech in mic buffer
while a character talks). **My note:** in practice the *browser* runs its own RMS-threshold VAD
(`AnalyserNode`, Observed `useAppController.ts:2287-2291`), not Silero — Silero VAD is the
*headless* path's detector (`loop.utterance_ended`, Observed `loop.py:246-269`). So there are **two
VAD implementations** (browser RMS for the live UI; Silero for the headless loop). *(Inferred:
favourable for the extract layer — whichever path drives capture, the transcript seam is the same.)*

---

## 3 · WHERE the transcript lands — the central question (a) — Observed + the gap

There are **three landing sites**, traced exactly:

**Site 1 — the NDJSON response to the posting browser (point-to-point, FULL text).**
`_voice_stream` emits `emit({"type":"transcript","text":transcript,"ms":stt_ms})` (Observed
`bridge.py:2424`). This is written to `self.wfile` — **the HTTP response of the browser that posted
the audio.** It is NOT a broadcast; only the poster receives it. `/api/voice/turn` similarly returns
the transcript in its single response JSON (Observed `bridge.py:2941`).

**Site 2 — a post-turn, TRUNCATED run-record on the SHARED event log.**
After think + TTS complete, `_voice_stream` calls
`SUITE.emit_run_record("voice.stream", total, ..., transcript=transcript[:2000], reply=reply[:4000])`
(Observed `bridge.py` ~2479; the `/api/voice/turn` twin at `bridge.py:2933-2937` truncates to 2000).
This **does** hit the shared log — but it is **(i) post-turn** (fires only after the whole reply was
generated and spoken) and **(ii) truncated** to 2000 chars. It is a *telemetry record*, not a live
transcript event.

**Site 3 — a fire-and-forget 200-char browser trace.**
The browser posts `autolisten_stt`/`autolisten_fire` with `text.slice(0,200)` to `/api/voice/log`
(Observed `useAppController.ts:2327,2337`) → `Suite.voice_log` → the event log (Observed
`bridge.py:3265-3273`, `suite.py:1363`). Truncated to 200, lenient ("never breaks a turn").

**The subscribe substrate that exists:** `GET /api/stream` (`_stream`, Observed `bridge.py:2119-2151`)
is **Server-Sent Events** tailing the SHARED `events.jsonl` via `SUITE.events_since(cursor)` (Observed
`suite.py:2019-2023`) — gapless reconnect via `Last-Event-ID`, 15s heartbeat. **This is a real,
reusable, multi-consumer broadcast bus.** A non-browser consumer (the glyphic extract layer) *can*
subscribe to it today.

**∴ THE GAP (the load-bearing finding for a + c):** the SSE bus exists, but **no full-fidelity
transcript event is written to the shared log at the moment of speech.** What reaches a subscriber
is only the truncated/post-turn Site-2 record or the 200-char Site-3 trace. The full transcript is
trapped in the point-to-point NDJSON response to the originating browser. **For the extract layer to
subscribe to live speech, the missing piece is a designed `voice.transcript` event — full text,
emitted live the moment STT returns, onto the shared log** (so SSE carries it) **— plus the producer
seam to emit it.** That seam already exists as a hook (`on_transcript`, `loop.py:209`; the
`{type:transcript}` emit, `bridge.py:2424`) — it just doesn't fan out to the shared log.

> *(My-idea, marked):* the cleanest extend-by-registration move is **one new event op** — at the
> STT-return point in `_voice_stream`/`/api/voice/turn`/`/api/stt`, call `SUITE`'s emit with a
> `voice.transcript` event carrying `{text (full), turn_id, partial:bool, ts}`. Then *every* consumer
> (the brain, the extract swarm, a future logger) reads the same broadcast — no second transcript
> path. This honours the design-system's "one home, reference everywhere" and the Company's
> registry-is-truth. **It does not yet exist.**

---

## 4 · THE GOLD CONTRADICTION — the transcript is hardwired to ONE consumer (contradicts naive "reuse the loop")

The anchor says "reuse the voice loop." Half-right. **The existing loop hardwires exactly one
consumer of the transcript: the conversational brain.**

`loop_turn` is, literally, `audio → transcript → think → speak` (Observed `loop.py:207-234`):
```
heard = listen(audio, ...)              # transcript
thought = think_fn(transcript) ...      # the ONE brain (Suite.chat)
wav = speak(speakable(reply, engine))   # speak it back
```
And the bridge injects `think_fn=lambda txt: SUITE.chat(txt, gid)` (Observed `bridge.py:2926`) — the
single in-process conversational brain. `_voice_stream` is the same shape with `chat_parts` (Observed
`bridge.py:2453`). **There is no fan-out. The transcript goes to the brain and nowhere else.**

The anchor's extract layer (§3 LISTEN → **EXTRACT** concurrent small local models) is a **second,
different consumer of the same transcript.** So the real shape the build must create is:

```
transcript ──┬──▶ [conversational brain]   (exists: Suite.chat / chat_parts)
             └──▶ [extract swarm]           (anchor's new fan-out — DOES NOT EXIST)
                     entities / relations / states / placement-hints (structured outputs)
                          → resolve to glyphics → reactflow
```

**This ties straight to Tim's `extraction-vs-judgment` law (anchor §3):** today there is NO extract
fan-out — there is only the **single judge-brain**. (The one existing role-resolved utility model on
the live path is the *finished-thought judge* — see §5 — which is exactly the "small fast model on
the turn path" pattern the extract layer wants, but it judges *endpointing*, not *meaning*.) The
build is: **open `transcript → brain` into `transcript → broadcast → {brain, extract-swarm}`**, and
the extract swarm is N concurrent role-resolved small-model calls (the anchor's per-concern roles),
each `extract-entities` / `extract-relations` / `extract-states` resolving to a model via the
`cognition-is-role-resolved` machinery (`resolve_role`, the same registry `is_finished_thought` uses,
Observed `suite.py:6567`). **That fan-out is the heart of this area's missing build.**

---

## 5 · Latency + turn-taking reality — question (b) — Observed, tempering the anchor's "real time"

The anchor §2/§6 worries "can small local models keep up with speech... fast enough to feel live?"
Here is the ground truth of the *speech* side of that:

1. **The ears are BATCH, not streaming ASR.** `transcribe` takes a *whole finished clip* (Observed
   `stt.py:249`). `transcribe_partial` is **re-transcription of a growing window** the FE re-posts,
   and its own docstring says a "truly STREAMING ASR (chunked partials without re-transcribing) is a
   later swap" (Observed `stt.py:236-246`). **∴ "live" today = utterance-chunked turns, not
   token-level streaming.** The glyphgraph would update **per finished thought**, not continuously.

2. **A turn fires on TWO signals, not a dumb timer.** (a) VAD trailing-silence pause (browser RMS,
   `SILENCE_MS=800`, Observed `useAppController.ts:2280`; headless Silero, `SILENCE_MS=500` default,
   Observed `loop.py:243`), AND (b) the **semantic finished-thought judge** — a per-pause model
   round-trip (Observed `is_finished_thought`, `suite.py:6544-6586`). Both must hold (Observed
   `loop.utterance_ended` `semantic_complete`, `loop.py:267-268`).

3. **The judge MUST be a fast, role-bound, no-think model — the deepseek lesson is measured.** The
   judge is the `judge` ROLE (`resolve_role('judge')`, Observed `suite.py:6567`), explicitly NOT the
   reasoning brain: "measured 2026-06-05, deepseek-v4-pro (a reasoner) needs ~256 tokens to surface a
   1-word answer and takes ~6.5s — unusable per pause" (Observed `suite.py:6552-6555`). **External-
   prior-art / measured-in-repo:** this is the single most important latency lesson for the anchor's
   extract layer — *any* per-pause / per-utterance model call on the live path must be a fast
   no-think classifier, or the live feel dies. The extract swarm inherits this constraint.

4. **Sentence-streamed reply hides TTS latency, not brain latency.** `_voice_stream` + `_stream_parts`
   (Observed `bridge.py:2332,2453`) overlap *TTS-synth ↔ playback* and (per the part design)
   *brain ↔ TTS* at the **part** level — but the brain still sends `stream:False` per call (prior
   doc `build-prep/concurrent-cognition/05-voice-stream-coupling.md`, Observed; token-level streaming
   is out of scope there). **Inferred for the extract layer:** the *extract* models should run
   **concurrently with the conversational brain reply** (both fed the same broadcast transcript) so
   graph-mutation latency overlaps speak-back latency rather than serialising after it.

**Turn-taking summary for the anchor:** the cadence is **finished-thought turns** (~silence-pause +
judge-RTT after the operator stops a thought), with barge-in to interrupt. That is a *good* cadence
for a graph that "grows as you speak a project" — it mutates on each completed thought, which is
exactly when a stable incremental layout wants a new batch of nodes (cross-ref anchor §6 stable
auto-placement). It is **not** a per-word live caption.

---

## 6 · Barge-in, push-to-talk vs auto-listen — the two switchable modes — Observed

The anchor wants both modes; **both exist and are distinct, switchable by a config slot.**
- **`voice_input_mode`** config slot: `push_to_talk` (default) vs `auto_listen` (Observed
  `useAppController.ts:321`, `RhmChat.tsx:93-95`).
- **Push-to-talk** — `recordToggle`: news up a fresh `MediaRecorder` per press → STT → chat turn
  (Observed `useAppController.ts:2197-2237`).
- **Auto-listen (hands-free)** — `startAutoListen`/`listenOnce`: persistent analyser tap + a fresh
  recorder per turn; RMS end-of-speech → `api.stt` → `api.finishedThought` → fire-or-keep; re-arms
  after each turn (Observed `useAppController.ts:2266-2358`). Carries a documented root-cause history
  (the "turn-2 headerless webm" re-arm bug, the barge-in rewrite) — this is **mature, hard-won code**.
- **Barge-in** — while a reply speaks, sustained RMS over a raised threshold (`BARGEIN_RMS=0.04`,
  `BARGEIN_FRAMES=4`, Observed `useAppController.ts:2284`) calls `bargeIn()` → `reader.cancel()` the
  in-flight `/api/voice/stream` reader + stop all live audio sources via a play-epoch (Observed
  `useAppController.ts:2111,2190-2196`).
- **Honest boundary (Observed `voice/AGENTS.md:33`, `useAppController.ts:2259`):** the live *feel*
  (does it wait for a finished thought; barge-in sensitivity; iOS audio) is **operator-verified-only
  / needs-tim** — the endpoints are verifiable headlessly, the mic/speaker loop is browser hardware.

> **Reuse verdict for the glyphic instrument:** the live-instrument surface should **reuse this exact
> capture machinery** (push-to-talk + auto-listen + barge-in + the finished-thought judge) rather
> than reinvent it. The only addition is the **transcript broadcast + extract fan-out** (§3, §4).

---

## 7 · The speak-back path for narrating the graph — question (d) — Observed, fully built

The anchor's read-out ("the graph narrates itself back") has a **complete, universal sink** — two
faces:

- **Server-side, no browser — `POST /api/say` → `voice/say.py`** (Observed `bridge.py:3007-3022`,
  `say.py`): a **serialized host-speaker queue** (one daemon worker, synth→play one line at a time
  via `paplay` → WSLg PulseServer → speakers). `say(text, engine?, voice?, who?)` enqueues and
  returns immediately. **This is how the narration would literally speak in the room while the graph
  mutates**, no canvas needed. Reuses `loop.speak` + the speakable cleaner — no parallel TTS path.
- **Browser playback — `POST /api/tts`** (`{text,voice?,engine?}` → wav, Observed `bridge.py:2821`)
  and the sentence-streamed `/api/voice/stream` chunks.
- **One transform for ALL reply→speech — `voice/speakable.py` `speakable(reply, engine)`** (Observed
  `voice/AGENTS.md:21`): strips markdown/code/emoji to natural prose and maps a canonical
  paralinguistic vocabulary (`<laugh>`, `<sigh>`) to the selected engine's syntax (or strips it).
  Applied at every pre-TTS seam. **The graph read-out passes through this unchanged** — narration
  text → speakable → engine.
- **TTS engines are a registry too** (`ops/services.json` `tts-*`; `loop.ENGINE_PORTS` derived at
  import, Observed `loop.py:38-77`): kokoro (default, CPU, ~0 VRAM), chatterbox, orpheus, cosyvoice,
  xtts, qwen3tts. Persona→engine→voice resolution is centralised (`_voice_arg_for`, Observed
  `loop.py:158-171`; "any persona × any engine", Tim 2026-06-07).

**∴ Narration is a SOLVED problem.** The glyphic read-out generates a sentence ("a gateway holding
the home, at rest") → `POST /api/say` (room) or `POST /api/tts` (browser). No build needed on the
mouth side beyond *calling* it. *(My-idea:)* the narration could even be a **third consumer** of the
same broadcast — when the extract layer mutates a node, emit a `glyph.narrate` event whose text the
say-queue speaks — keeping the read-out single-sourced from the same event bus as the extract.

---

## 8 · The no-staleness law (anchor §5) on the voice side — Observed, mostly held

The voice path is **already resolution-native** in the places that matter — good news for the law:
- Ears: `STT_PROVIDERS` registry, UI reads `available_stt()`, **never guesses** (Observed
  `voice/AGENTS.md:25`, `stt.py:222-227`). Add an ear = add a row.
- TTS engine ports: **derived from `ops/services.json`**, never hardcoded in `loop.py` — a
  hardcoded port **fails loud at import** (Observed `loop.py:38-77`, `voice/AGENTS.md:26,31`).
- The active ear / engine / voice are **config slots** (`rhm_config`), one source for browser + loop.
- The judge is **role-resolved** (`resolve_role('judge')`), not a pinned model — the extract roles
  inherit this exact pattern.

**Where staleness could sneak in (the rigor area for the extract build), Inferred:**
- The **VAD feel parameters** (`SILENCE_MS`, `BARGEIN_RMS`, `BARGEIN_FRAMES`) are **literals in the
  browser** (Observed `useAppController.ts:2280-2284`) — env-overridable on the headless side but
  hand-set in the FE. If the extract layer adds its own cadence knobs, they must NOT become a second
  set of magic numbers; route through a config slot.
- The proposed **`voice.transcript` event schema** must be registered once (one event op), not
  emitted ad-hoc at three call sites — else it drifts (the exact Site-1/2/3 fragmentation that exists
  today is the warning).
- **Extract roles** must be declared in the role registry (like `judge`), never a hardcoded model id.

---

## 9 · The process / venv boundary — Observed — and why it HELPS the anchor

The anchor §6 frets about "the browser↔Company boundary (the design system runs in a browser; the
local models are server-side)." For the *speech path*, the boundary is favourable:

- The loop runs in **`.voice-venv` (Python 3.12)** because faster-whisper + the engines live there;
  the runtime/Suite is **3.14**; a 3.12 process can't import the 3.14 Suite — so the brain is reached
  by **HTTP to the bridge** (Observed `loop.py:1-22`). When the loop runs *inside* the 3.14 bridge,
  the bridge **injects the in-process `Suite.chat`** as `think_fn` — one brain, one event log
  (Observed `loop.py:199-203`, `bridge.py:2926`).
- **The brain is ALREADY reached server-side.** The extract small-models are **also server-side**
  (Company fleet via `runtime/cognition.py` / the `company` MCP per anchor §7). So **`transcript →
  extract-swarm` is a natural server-side fan-out** — both consumers live on the same side of the
  one hard boundary, which is only **browser→bridge where the audio originates.** *(Inferred, and it
  is the favourable framing the anchor should adopt:)* once the audio crosses into the bridge and STT
  returns, *everything downstream — brain, extract swarm, narration — is server-side and can share
  one in-process broadcast.* The browser only needs to **render** the resulting graph-deltas (the
  reactflow surface, Area-of-another-agent), not run the models.

---

## 10 · The minimum real demo that proves "talk → live graph" (anchor §8) — My-idea, grounded

Built on what exists, the smallest end-to-end proof of the *speech* contribution:
1. Operator taps auto-listen, says one thing ("the buyer made an offer on the Smith Street house").
2. The existing capture→VAD→STT→finished-thought fires (REUSE, exists).
3. **NEW:** at STT-return, emit a full-text `voice.transcript` event onto the shared log (§3 gap).
4. **NEW:** an extract consumer subscribed to `/api/stream` receives it, runs ONE role-resolved
   small-model extract pass (entities+relations, structured output), emits graph-deltas.
5. Existing narration speaks the read-out via `POST /api/say` (REUSE, exists).

Steps 1, 2, 5 are **already built and headlessly verified**; steps 3, 4 are the **new wire** — the
transcript broadcast and the first extract subscriber. That is the honest scope of this area's
contribution to the live instrument.

---

## 11 · Contradictions / corrections to the anchor (the expansion-ratio payload)

- **Anchor §3 "LISTEN (STT, transcribe) → EXTRACT":** correct as a shape, but **the transcript does
  not flow anywhere a second consumer can reach today** — it is point-to-point to the posting browser
  (full) or truncated/post-turn on the log. The "→" between LISTEN and EXTRACT is **the missing wire**,
  not an existing pipe. (§3, §4.)
- **Anchor §2/§6 "in real time" / "fast enough to feel live":** the *speech* path is **utterance-
  chunked batch ASR + a per-pause judge RTT**, not streaming. "Live" = per-finished-thought, not
  per-token. Set expectations there. (§5.)
- **Anchor "reuse the voice loop":** reuse capture/VAD/judge/transcript-seam/narration — **but the
  `transcript→single-brain` coupling is exactly what must open into a fan-out.** Reusing `loop_turn`
  *as-is* would send speech only to the brain, never the extract layer. (§4.)
- **Anchor §7 "moonshine/whisper/parakeet":** under-counts — **8 ears**, incl. `parakeet-onnx` with
  **hotword/context biasing** (a real STA lever for boosting glyphic/domain vocabulary) and
  Moonshine's built-in `IntentRecognizer`. Worth the anchor's attention for the extract layer. (§2.1.)
- **Anchor §6 "browser↔Company boundary":** for speech it is **favourable** — brain + extract +
  narration are all server-side; only audio-capture is browser-side. (§9.)
- **Speak-back (anchor "narrate"):** **fully built and universal** (`/api/say` host-speaker queue +
  the speakable transform) — not a build risk, a reuse. (§7.)

---

## 12 · Open threads I'm handing forward
- The **exact `voice.transcript` event schema** and which emit op it registers under (coordinate with
  whoever owns the EXTRACT and the event-bus areas — this is the seam between us).
- Whether the extract swarm subscribes to **SSE `/api/stream`** (browser-style) or is invoked
  **in-process** at the STT-return point (server-side, lower latency, no serialization round-trip).
  *(Inferred: in-process fan-out is faster + avoids re-parsing JSON off the wire; SSE is the right
  bus for the FE/canvas to also see the live transcript. Likely BOTH — emit once, in-process
  consumers read directly, the SSE carries it to the browser.)*
- The **partial/streaming transcript** question: do we want the graph to twitch on partials
  (`transcribe_partial`, re-transcription) or only on finished thoughts? The finished-thought cadence
  is the stable choice for incremental layout; partials are a feel upgrade later.
- VAD-parameter single-sourcing (§8) — fold the FE feel-literals into a config slot before the
  extract layer adds its own.

---

### 3-line summary
A complete, headlessly-verified live-speech circuit already exists — swappable STT registry (8 ears),
VAD endpointing, a role-resolved semantic finished-thought judge, push-to-talk + auto-listen +
barge-in, sentence-streamed reply, and a fully-built universal speak-back (`/api/say` host queue +
`/api/tts` + the speakable transform) — so narration of the graph is a solved sink. BUT the transcript
is hardwired to ONE consumer (the conversational brain): it lands point-to-point in the posting
browser's NDJSON response, with only a truncated/post-turn echo on the shared SSE event log — so the
anchor's "LISTEN → EXTRACT" arrow is a *missing wire*, not an existing pipe. The build is to emit a
full-fidelity `voice.transcript` event live onto the shared bus and open the `transcript→brain`
coupling into a server-side `transcript → {brain, extract-swarm}` fan-out (extract roles resolved like
the judge), inheriting the measured "fast no-think model on the live path" constraint; latency reality
is utterance-chunked turns (per finished-thought), not per-token streaming.

Path: `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-3-voice-stt.md`
