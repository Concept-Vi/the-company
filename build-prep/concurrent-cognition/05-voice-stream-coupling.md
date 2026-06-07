---
type: design
module: voice
aliases: ["Voice Stream Coupling", "Staged Multi-Part Voice", "Brain-TTS Overlap"]
tags: [company, voice, concurrent-cognition, streaming, latency, design]
status: design-draft
relates-to: ["[[voice — constitution]]", "[[runtime — constitution]]", "[[canvas — constitution]]"]
---

# 05 — Voice Stream Coupling: can the spoken voice stream AS the brain produces output?

> First doc in `concurrent-cognition/` — establishes the vocabulary for "a part" as a unit of
> cognition in the voice circuit. Read-only research + a buildable design. Nothing here is built yet.

## The one-line answer (lead with the bounding fact)

**Today: NO — not at the token level.** The brain produces the **WHOLE reply before any audio is
synthesised**, then TTS streams **per-sentence**. The voice stream overlaps *TTS-synth ↔ playback*,
but it does **not** overlap *brain ↔ TTS*. This is bounded by one hard fact in the fabric:
`fabric/transport.py` sends `"stream": False` on **every** model call (lines 36, 66, 158), and
`Suite.chat` (`runtime/suite.py:3333`) is a blocking call that returns a complete `{"reply": ...}`.

**The buildable win (this design): YES at the PART level.** If the brain emits its reply as a
**sequence of completed parts** (each part a complete sub-generation), each finished part becomes the
TTS streaming unit — synth + stream part N's audio *while the brain generates part N+1*. That overlaps
*brain ↔ TTS*, which is the latency that today's circuit cannot hide. **Token-level** streaming (the
brain's tokens flowing into TTS as they emerge) is a SEPARATE, larger change — it needs `stream: True`
in transport + model SSE — and is explicitly **out of scope** of the part-level design below.

---

## Part 1 — The pipeline today, with file:line evidence

### `runtime/bridge.py` `_voice_stream` (`/api/voice/stream`, lines 357–468)

The handler is a single ndjson response. Traced in order:

1. **Read the whole clip** — `audio = self.rfile.read(Content-Length)` (line 375). The entire recorded
   utterance is in memory; STT is **batch**, not streaming.
2. **STT (batch transcribe of the whole clip)** — `heard = voice_stt.transcribe(audio, provider=ear)`
   (line 425) → `emit({"type":"transcript", ...})` (428). One transcript for the whole clip.
3. **Brain — FULL reply, blocking** — `thought = SUITE.chat(transcript, gid)` (line 431), commented
   in-code as *"the ONE in-process brain (full reply)"*. `reply = (thought.get("reply") or "").strip()`
   (432) → `emit({"type":"reply", "text": reply, ...})` (434). **The entire reply text exists before
   ANY TTS runs.** This is the `brain ↔ TTS` non-overlap.
4. **Trial recording (V3.1)** — if `?trial_session=` is set, `SUITE.trial_record_turn(... operator ...)`
   + `SUITE.trial_record_turn(... character, reply ...)` (lines 437–438). Recorded ONCE, with the full
   reply, wrapped in try/except so a record failure never breaks the turn (439–440).
5. **Sentence-split** — `sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', reply) if s.strip()]
   or [reply]` (line 444). The full reply is split AFTER the brain finishes.
6. **Per-sentence synth, streamed** — the loop (lines 447–455):
   ```
   for idx, sent in enumerate(sentences):
       if client_gone(): break                     # Tier-2 cancel BEFORE the next synth (448)
       wav = voice_loop.speak(sent, eng, voice=voice_arg)   # synth ONE sentence (451)
       emit({"type":"chunk", "idx":idx, "text":sent, "wav_b64":b64(wav), "ms":...})  # (452-454)
   ```
   Each sentence's wav is emitted as a `chunk` event **as it's synthesised** — this is the only
   overlap that exists today: synth(sentence N) ↔ playback(sentence N-1) on the client.
7. **Done** — `emit({"type":"done", "total_ms":..., "spoke":True, "chunks":..., "reply":reply})` (463)
   + a run-record (`voice.stream`, 461). A mid-stream client disconnect emits a `voice.stream.cancelled`
   run-record instead (457–460).

The in-code docstring (358–366) states the design intent plainly: *"instead of synthesising the WHOLE
reply before any audio … we split the reply into sentences and stream each one's audio AS IT'S
SYNTHESISED"* and *"Brain-token streaming is a later refinement; chunking the TTS (the dominant cost)
is most of the win."* So the repo already KNOWS brain-streaming is the next rung — this doc designs the
intermediate (part-level) rung that needs no transport change.

**Cancellation plumbing (relevant to the design):** `client_gone()` (lines 391–404) proactively detects
a client disconnect via `select` + `MSG_PEEK` (EOF = closed), set into `gone[0]`. Today it gates only
the next **synth**. It does NOT yet abort an in-flight brain call (there's only one, and it's already
finished by the time the loop runs).

### `voice/loop.py` — the headless circuit underneath

- **`speak(text, engine, voice=None, speed=1.0)`** (lines 97–111): the TTS step. POSTs the selected
  engine's `/tts`, returns wav bytes. Per-engine `voice` semantics documented: Orpheus = a named voice;
  Qwen3-TTS/CosyVoice = a natural-language voice DESCRIPTION; XTTS/Chatterbox = a reference-clip path (or
  None → the engine's `COMPANY_VOICE_REF`). Fail-loud (names engine+port) on an unreachable engine.
- **`_voice_arg_for(persona, engine=None)`** (lines 118–131): maps a persona → the right `voice` arg for
  the **selected** engine (keys off the selected engine, not the persona's default — *"all personas work
  for all engines"*, Tim 2026-06-07). qwen3tts/cosyvoice → `voice_description`; orpheus/kokoro → a named
  bank voice; xtts/chatterbox → None (reference clip).
- **Sentence chunking lives in the BRIDGE, not loop.py** — the `re.split` is in `_voice_stream`
  (bridge.py:444). `loop.py.speak` synthesises whatever text it's handed; it has no notion of a sentence.
  This matters: the *unit* of synthesis is a caller decision, so a "part" can become the unit with zero
  change to `speak`.
- **`loop_turn`** (lines 146–188): the standalone one-shot turn (hear→think→speak). It synthesises the
  WHOLE reply in one `speak(reply, ...)` (line 185) — non-streaming; the streaming variant is the
  bridge's `_voice_stream`. `think_fn` is injectable so the in-process bridge passes `Suite.chat`
  directly (one brain, one event log — `loop.py` runs in `.voice-venv` 3.12, the Suite is 3.14;
  docstring lines 8–12).

### Frontend consumer — `canvas/app/src/useAppController.ts` + `api.ts`

- **`api.voiceStream(blob, persona, trialSession?)`** (`api.ts:112–115`): POSTs the clip, returns the raw
  `Response` so the caller reads `.body` as a stream (NOT parsed as one JSON object).
- **`runVoiceTurn(blob)`** (`useAppController.ts:1208–1239`): the consumer.
  - `playCursorRef.current = 0` at turn start (line 1216) — **resets the audio play cursor ONCE per turn.**
  - Reads the ndjson via `res.body.getReader()` + `TextDecoder`, line-splitting on `\n` (1224–1231).
  - Dispatches by `ev.type` (1232–1236): `transcript` → notice + append user turn; `reply` → append
    assistant turn; **`chunk` → `await playWavBuffer(b64ToArrayBuffer(ev.wav_b64))`** (1234); `error` →
    fail-loud notice; `done` → clear + `poll()`.
  - The chunk handler **awaits playback scheduling but the audio plays in ORDER regardless** — see below.
- **In-order playback + iOS unlock** (`useAppController.ts:1161–1188`):
  - **`primeAudio()`** (1164–1172): creates/`resume()`s a persistent Web Audio `AudioContext` (or
    webkit). MUST run inside a synchronous user gesture (mic tap / send click) so iOS unlocks the context
    for the LATER (post-async) reply playback. Idempotent. Called in `recordToggle` (1242),
    `startAutoListen` (1293), and typed-send (687).
  - **`playWavBuffer(buf)`** (1176–1188): decodes the wav, creates a buffer source, and schedules it at
    `at = Math.max(now, playCursorRef.current)` then advances `playCursorRef.current = at +
    audioBuf.duration` (1181–1183). **This is the in-order guarantee:** each chunk is scheduled to start
    exactly when the previous one ends, regardless of arrival jitter or decode time — a monotonic play
    cursor. Falls back to a one-shot `<audio>` element if the context isn't unlocked (desktop path, 1187).
- **Input modes** both route to `runVoiceTurn`: push-to-talk (`recordToggle`, 1276) and auto-listen
  (`startAutoListen` → finished-thought judge → `runVoiceTurn`, 1327). Auto-listen pauses the recorder
  during the reply so the voice isn't heard as new input (1325).

**Key FE property for the design:** the FE already consumes an **arbitrary-length ordered chunk stream**
keyed by the monotonic `playCursorRef`. It does not care how many `chunk` events arrive or what produced
them — only that they arrive in order on one stream and that the cursor is reset once per turn. This is
why a server-side N-part producer needs **zero FE changes**.

---

## Part 2 — The design: staged multi-part response makes voice-streams-as-brain-streams natural

### What a "PART" is (the unit of cognition — the load-bearing definition)

A **part** is a *complete sub-generation*: the brain produces a self-contained span of reply (a thought,
a clause group, a step of an answer), returns it fully, then produces the next. Each part is a finished
string — NOT a token. This is what makes it buildable under `stream: False`: a part is just another
blocking `Suite.chat`-shaped call whose output is a fragment of the eventual whole reply.

Concretely, a part can be produced two ways (both fit the engine; pick per use):
- **(a) Planned parts** — the brain first emits a short plan/outline, then generates each part as its own
  bounded generation conditioned on the plan + prior parts. N is known after the first call.
- **(b) Continuation parts** — the brain generates "the next part, or a STOP sentinel" repeatedly, each
  call conditioned on the conversation + parts-so-far. N is discovered as it goes. (This is the more
  natural "thinking out loud in installments" shape and maps to how the auto-listen finished-thought
  judge already gates turns — `api.finishedThought`.)

Either way, **each completed part is the TTS streaming unit**: as soon as part N's text exists, split it
into sentences (the existing `re.split`) and synth+stream them — *while the brain is already generating
part N+1*. That is the brain ↔ TTS overlap today's circuit lacks.

### The latency thesis (the contrast IS the design)

```
TODAY  (brain fully blocks, then per-sentence TTS streams):
  time-to-first-audio = STT + FULL_REPLY_GEN + TTS(sentence_1)
  |--STT--|--------------- whole reply generated ---------------|--synth s1--|▶ first audio
                                                                 |--synth s2--|▶
                                                                              ...

STAGED PARTS  (brain ↔ TTS overlap):
  time-to-first-audio = STT + PART_1_GEN + TTS(sentence_1_of_part_1)
  |--STT--|--gen part1--|--synth p1s1--|▶ first audio
                        |--- gen part2 ---|        (brain runs CONCURRENTLY with synth/playback)
                                       |--synth p1s2--|▶
                                                     |--synth p2s1--|▶ ...
```

The win: **time-to-first-audio drops from `STT + full-reply-gen + TTS(sent1)` to
`STT + part1-gen + TTS(sent1)`.** On a long reply, `full-reply-gen` is the dominant wall (the docstring
at bridge.py:360 calls it *"the ~28s-on-a-long-reply wall"*). Staging cuts the brain term in the
first-audio path from the WHOLE reply down to the FIRST part.

### What changes in `/api/voice/stream` (and what does NOT)

**Recommended architecture: ONE FE request, server-side N-part producer with a single ordered emitter.**

The handler keeps its current ndjson contract. Internally, instead of one `SUITE.chat` + one synth loop,
it runs **two concurrent roles feeding one emitter**:

1. **Brain-producer (a worker thread)** — generates parts 1..N (mechanism (a) or (b) above), pushing each
   completed part's text onto a thread-safe queue. Runs ahead of synthesis.
2. **Synth-consumer (the handler thread)** — pulls a part off the queue, splits it into sentences, and
   for each sentence calls `voice_loop.speak(...)` and `emit({"type":"chunk","idx":<monotonic>,...})`.
   `idx` is a **monotonic counter across ALL parts** (not reset per part), so the FE's `playCursorRef`
   ordering is preserved exactly as today.

Because there is exactly **one emitter** (the handler thread does all the `emit`s; the producer only
fills the queue), ndjson line-ordering is safe without locks on the socket. The producer/consumer share
a `queue.Queue`; the producer signals end-of-parts with a sentinel.

**Event sequence on the wire (superset of today — additive, schema-safe):**
```
{type:transcript, text, ms}
{type:part,  idx, text}        # NEW (optional): a part's full text, for the chat transcript / debrief
{type:chunk, idx, text, wav_b64, ms}   # per SENTENCE, monotonic idx across parts (UNCHANGED shape)
... (interleaved: chunks of part 1 stream while part 2 generates) ...
{type:done, total_ms, spoke, chunks, reply}   # reply = the ASSEMBLED full reply (see recording)
```
- The `{type:reply}` event (today's full-reply-up-front) is **replaced** by streamed `{type:part}` events
  for the chat append, with the assembled full reply still carried on `done`. The FE's `reply` handler
  (1233) becomes a `part` handler (append each part as it arrives — better streaming feel). The `chunk`
  handler (1234) is **unchanged**.
- **FE changes are minimal-to-zero:** the chunk path needs nothing. The only FE edit is appending parts
  incrementally (rename the `reply` branch to handle `part`) — and that's a *nicety*, not a requirement;
  if the server still emits a final `reply` on `done`, the existing FE works untouched.

**Alternative (the task's "each part its own request"): FE sequences N requests.**
The FE fires request 1, consumes its chunks, then fires request 2 with parts-so-far as context, etc.
- Cost: the FE must orchestrate the sequence AND must **NOT reset `playCursorRef` between requests** —
  only at turn start (1216). Each new request's chunks must continue the same play cursor, or audio
  overlaps/gaps. This is a real FE-state hazard the single-request design avoids entirely.
- Benefit: each part is independently cancellable/retryable at the HTTP layer, and the brain's per-part
  context is explicit in the request. But it pushes overlap orchestration into the browser and risks the
  cursor bug. **Recommendation: server-side single-request producer.** Keep "each part its own request"
  as a documented fallback only if a future need (e.g. per-part auth) forces it.

### Preserving the three invariants (explicit, per the preserve-list)

1. **In-order audio playback** — UNCHANGED. The monotonic `idx` + the server's single-emitter ordering +
   the FE's `playCursorRef` scheduling already guarantee order for an arbitrary chunk count. The producer
   must enqueue parts in order and the consumer must drain them in order (FIFO `queue.Queue` does this).
   `playCursorRef` is reset **once** at turn start (1216) — NOT per part. Do not touch this.
2. **iOS unlock** — UNCHANGED. `primeAudio()` runs in the gesture before the request (1242/1293/687);
   the context is persistent and resumed once; staging adds MORE chunks to the SAME unlocked context.
   No new context is created mid-turn. Nothing in the staging design touches the gesture→unlock path.
3. **Trial recording** — CHANGED CAREFULLY. Today the turn is recorded once with the full reply
   (bridge.py:437–438). With parts, **assemble the full reply across all parts and record ONCE at the end
   of the turn** (after the producer's sentinel, before `done`). Per-part recording would fragment the
   CAS transcript (the debrief reads `trial://<session>/transcript` and would see N fragments instead of
   one turn). So: accumulate `reply = "".join(parts)` (or join with the brain's own separators), then the
   existing `trial_record_turn(... operator ...)` + `trial_record_turn(... character, full_reply ...)`
   exactly as now. The run-record (`voice.stream`) gains a `parts` count alongside `chunks`.

### Cancellation across parts (extend, don't add a parallel path)

`client_gone()` (391–404) must now gate **two** expensive things, not one:
- before the next **synth** (existing, line 448) — keep it;
- before/within the next **part GENERATION** — NEW. The producer thread must check `gone[0]` between
  parts and stop generating (and signal the sentinel) so a cancelled speculative turn doesn't burn brain
  compute on parts that will never be heard. With mechanism (b) this is a natural loop-top check; with
  (a) it's a check before each part's generation. The cancelled run-record (`voice.stream.cancelled`,
  457–460) gains `parts_done`/`parts_total` alongside the existing `chunks_done`/`chunks_total`.

### What is OUT of scope (state the boundary, don't blur it)

- **Token-level brain streaming.** A part is a complete sub-generation. Streaming the brain's tokens
  into TTS as they emerge needs `fabric/transport.py` to send `"stream": True` and parse the model's
  SSE token stream, plus a sentence-aggregator that buffers tokens until a sentence boundary before
  synth. That is a fabric + client change touching `complete`/`complete_with_tools`
  (`fabric/client.py:54,92`) and every transport (`transport.py:36,66`). It is the *next* rung after
  parts; this doc deliberately does not design it, because the part-level overlap captures most of the
  first-audio win with no transport change.
- **Streaming STT.** STT is still batch over the whole clip (the recorded utterance is finished before
  the turn fires — `utterance_ended`/the auto-listen judge gate that). Streaming STT (partial transcripts
  feeding an early brain start) is a separate concurrent-cognition rung; `/api/voice/stt-partial`
  (bridge.py:490) already exists as a seed but is not wired into the brain start.

---

## Part 3 — Latency analysis (numbers as relationships, not wall-clock)

Let the per-turn costs be: `STT` (batch, fixed), `Gᴺ` (gen of part N), `Sₖ` (synth of sentence k),
`Pₖ` (playback duration of sentence k). The reply has total gen cost `G = ΣGᴺ` and total synth `S = ΣSₖ`.

| Metric | Today (full-blocking brain) | Staged parts (brain ↔ TTS overlap) |
|---|---|---|
| **Time-to-first-audio (TTFA)** | `STT + G + S₁` | `STT + G₁ + S₁` |
| **TTFA win** | — | `G − G₁` (the whole reply gen minus the first part) — large on long replies |
| **Total turn time** | `STT + G + P` (P = total real-time playback duration; synth races ahead, isn't the tail) | `STT + G₁ + max(G−G₁, P)` — brain runs concurrently with playback after part 1; gated by whichever is longer |
| **Gap risk (audio underruns)** | **None** — brain fully done before any audio; synth races ahead of playback | **Yes** if brain is slower than playback consumes |

**The honest tradeoff — gapless playback requires brain-throughput ≥ playback-consumption-rate.**
- Today CANNOT gap (the brain finishes before any audio plays — synthesis only ever races *ahead* of
  playback). It pays the *maximum* TTFA in exchange.
- Staged parts trade TTFA for **gap risk**: if part N+1's generation (`Gᴺ⁺¹`) takes longer than the
  playback of part N's audio (`ΣPₖ for part N`), the play cursor catches up to the last scheduled chunk
  and the listener hears **silence between parts** (an underrun). Whether this happens depends on the
  ratio of brain tokens/sec to speech tokens/sec for the selected models/engine.
- **Mitigation — a prebuffer knob.** Stage `B` parts (synth them) before starting playback, where `B`
  is a small config (`COMPANY_VOICE_PREBUFFER_PARTS`, default ~1). `B=0` = minimum TTFA, maximum gap
  risk; larger `B` = higher TTFA, smoother playback. This is the dial that lets the operator (or an
  introspective-data rollup over `voice.stream` run-records: `Gᴺ` vs playback duration) tune the
  feel per model/engine. It's the same shape as the existing `SILENCE_MS`/finished-thought naturalness
  levers — a per-request knob, fail-loud, registry-surfaced.

**Why parts (not just smaller sentences) help:** today's per-sentence synth already overlaps synth ↔
playback, but it CANNOT start until `G` is fully paid. Splitting the *brain* into parts is the only thing
that moves brain compute off the TTFA critical path — sentence-splitting can't, because the sentences
don't exist until the brain finishes. The two overlaps compose: parts overlap brain↔TTS, sentences
overlap synth↔playback.

---

## Summary of changes (buildable, additive, no contract break)

- `runtime/bridge.py` `_voice_stream`: replace the single `SUITE.chat` + synth loop with a
  brain-producer thread (parts → `queue.Queue`) + the existing synth/emit loop as the single ordered
  consumer; monotonic `idx` across parts; assemble full reply; record trial ONCE at end; extend
  `client_gone` gating to part generation; add `parts` to run-records; add a `COMPANY_VOICE_PREBUFFER_PARTS`
  knob. Needs a Suite method that yields parts (mechanism (a) or (b)) — built on `Suite.chat`'s shape,
  NOT a forked brain.
- `runtime/suite.py`: a `chat_parts(...)` (or a `parts=` flag on `chat`) that produces the reply as a
  sequence of completed parts. Blocking per part (no transport change). Reuses grounding/tools/persona.
  **CRITICAL — one logical turn, regardless of N parts.** Today `Suite.chat` appends a user+assistant
  pair to `store.append_chat` AND emits a `chat` event per call (suite.py:3341–3345). A naive
  `chat_parts` that loops `Suite.chat` N times would write **N turns to the chat organ and N chat events
  for one spoken turn** — polluting the history the RHM grounds on and the SSE chat stream, breaking the
  "one event log, one store" invariant (STATE.md; AGENTS rule 4). So `chat_parts` MUST append exactly
  **one** coherent assistant turn (the assembled reply) to chat history and emit exactly **one** `chat`
  event — the same record-once discipline as the trial-recording rule above. The per-part generations are
  internal cognition, not N conversation turns.
- `canvas/app/src/useAppController.ts`: OPTIONAL — handle a `{type:part}` event to append parts
  incrementally; do NOT reset `playCursorRef` per part. The `chunk`/iOS/cursor paths are untouched.
- **Out of scope (next rungs):** token-level brain streaming (needs `transport.py` `stream:True`),
  streaming STT (wire `/api/voice/stt-partial` into an early brain start).
