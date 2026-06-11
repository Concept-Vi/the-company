---
type: contract-entry
resource: voice
summary: The Company's speech circuit — spoken audio in (a swappable STT-ear registry) → the in-process brain → spoken audio out (a swappable TTS-engine + persona/voice registry), exposed as one streamed conversational turn (audio-in → ndjson with per-sentence wav). The full local voice stack is REAL and proven by use; auto-listen feel + on-device iOS playback are device-only and unflipped.
schemes: []
status: building
relates-to: ["[[session]]", "[[model]]", "[[events]]", "[[fabric-config]]", "[[remote]]"]
---

# Resource: voice

## Identity
**Voice is keyed by the speech-circuit selection a turn runs under — an EAR (STT provider id),
an ENGINE (TTS service id), and a PERSONA/voice — not by a standalone record; there is no
`voice://` scheme.** The Company runs a complete local voice stack (Atlas class CC-14: dictation
in, TTS out, multiple engines, push-to-talk vs auto-listen/VAD, real-time streaming, audio
playback; source `Feature Atlas.md#14-voice-audio-inputoutput` + `voice-dictation.md`, vault
`claude-code-atlas`). UNLIKE native Claude Code voice dictation — which streams mic audio to
Anthropic for transcription, is Claude.ai-account-only, and does NOT work in remote/SSH/web
environments (`voice-dictation.md#requirements`) — the Company circuit is ON-MACHINE STT + local
TTS, so it survives the tailnet/PWA path that native dictation cannot ([[remote]]). This resource
contracts the Company's own faces; each op marks whether the slice is `building` (a real bridge
route) or `planned` (the device-only feel, named as the gap).

## Representation
**A voice selection is three registry picks — `ear` (STT provider), `engine` (TTS service) +
`voice`/`persona`, plus the per-mode `voice_enabled` toggle — each drawn from a LIVE registry, not
a fixed enum; the available sets are read, never assumed (registry-is-truth).**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/voice.selection",
  "type": "object",
  "properties": {
    "ear":     { "type": "string", "description": "STT provider id from the live ear registry — e.g. whispercpp (CPU floor, :2022), parakeet (:2031), canary (:2032), granite (:2033), assemblyai. Read the set via voice.list, never hardcode" },
    "engine":  { "type": "string", "description": "TTS service id from the live engine registry — kokoro (:4123 default), chatterbox (:4124), orpheus (:4125), cosyvoice (:4126), xtts (:4127), qwen3tts (:4128)" },
    "voice":   { "type": "string", "description": "the named voice WITHIN an engine (engine-specific; from that engine's GET /voices)" },
    "persona": { "type": "string", "description": "a cast identity from the 5-persona registry ([[voice#op: voice.list]] personas) — binds engine+voice+voice_description as one named face" },
    "voice_enabled": { "type": "boolean", "description": "the per-mode speak/listen toggle (Suite.voice_enabled()) — voice-off makes speak a no-op while text still flows" } } }
```
| field | type | volatile? | changed-by | address? → resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| ear | string | yes (operator/UI swap) | the selection write (`rhm_config.stt` / `/api/voice/switch`) | — | LIVE registry: whisper.cpp CPU floor is always-available; 3 GPU ears (parakeet/canary/granite) are loadable on demand, VRAM-budgeted (`voice/lifecycle.py`); assemblyai is cloud. Read via [[voice#op: voice.list]] |
| engine | string | yes | the selection write | — | 6 engines registered (`ENGINE_PORTS` + kokoro default, `runtime/bridge.py:208`); each its own HTTP service + venv + port. ALL 5 trial engines verified reliable-by-use (load→synth→teardown), per `project-voice-stack` |
| voice | string | yes | the selection write | — | engine-specific; orpheus has a named bank (tara/leah/jess/leo/dan/mia/zac/zoe); clone engines (xtts/chatterbox) clone `COMPANY_VOICE_REF`; qwen3tts describes-in-words |
| persona | string | yes | the selection write | — | 5-cast registry (`voice/personas.py`, `GET /api/personas`) — all share one refined-Australian-woman `voice_description`, each showcased on a different engine. one-vs-cast binding = OPEN (Tim's call) |
| voice_enabled | bool | yes | the per-mode toggle | — | `Suite.voice_enabled()` — surfaced on `GET /api/voice` |

## State model
**State model: stateless (a per-turn selection).** A voice selection has no lifecycle of its own
— it is read at turn time and applied to the circuit. The TTS engines and GPU ears DO have a
load lifecycle (down → warming → up, VRAM-arbitrated), but that lifecycle belongs to the SERVICE
([[fabric-config]]'s resource-manager view); a selection just names which service the turn uses,
booting it on demand if down ([[voice#op: voice.act]] `boot=1`).

## Caller
**Speaking/listening is anonymous-local over bridge-http (the same vantage as every bridge read);
over the tailnet the caller is the operator's PWA on a real-HTTPS origin — which the browser mic
REQUIRES (`getUserMedia` secure-context).** There is no per-consumer voice identity: a turn
carries its ear/engine/persona selection explicitly in the query, never an ambient default. The
secure-context requirement is WHY the tailnet HTTPS path ([[remote]]) is load-bearing for voice:
plain-LAN http leaves `mediaDevices` undefined on iOS, so browser voice-in only works through the
tailscale-serve HTTPS origin (verified, `project-mobile-access-tailscale`).

## Operations

## op: voice.list
**`voice.list` is the circuit-inventory read: the live ear registry (with each ear's up/loadable
state + VRAM), the per-engine TTS availability + that engine's voice list, the selected ear, the
persona cast, and the per-mode voice_enabled flag — one read that tells a consumer the whole
swappable speech surface before it picks.**
```contract:op
op: voice.list
resource: voice
kind: list
status: building
direction: outbound
atlas: [CC-14.4, CC-14.5]
tasks:
  - phrase: "what voices and engines can the company speak in"
  - phrase: "list the speech-to-text ears available"
  - phrase: "which voice personas exist"
  - alias: "show the voice options"
  - alias: "what TTS engines are installed"
  - alias: "is voice on"
bindings:
  - { kind: http, method: GET, path: /api/voice, transport: bridge-http, exposure: "exposure.json#bridge-http", note: "the omnibus voice-status read: {stt, stt_default, stt_registry, stt_active, engines:{<name>:{up,voices}}, voice_enabled}. Source runtime/bridge.py:864" }
  - { kind: http, method: GET, path: /api/personas, transport: bridge-http, exposure: "exposure.json#bridge-http", note: "the 5-cast persona registry (voice/personas.py). Source :899" }
  - { kind: http, method: GET, path: /api/voice/services, transport: bridge-http, exposure: "exposure.json#bridge-http", note: "the loadable voice services (ears+engines) with up/warming/down + VRAM (voice/lifecycle.status()). Source :906" }
liveness: snapshot
live-twin: "[[fabric-config]] resource-manager view for live VRAM/up-state; the engine `up` flags reflect live service probes (GET /voices per engine, 3s timeout)"
emits: []
verification:
  status-read: {state: probe-verified, run: "voice circuit proven end-to-end 2026-06-05 (project-voice-stack): /api/voice returns the registry; engines enumerated; personas served", date: 2026-06-12, note: "the registry reads are real; the up-flags are live probes"}
```
This is the read a config-lab / picker consumes to populate ear, engine, voice, and persona
choices — all from live registries (Tim's "n roles as slots", registry-driven, day-one
swappable). The GPU ears and trial engines that are `down` appear with their loadable state +
VRAM cost so a consumer can boot one before a turn ([[voice#op: voice.act]]). The whisper.cpp ear
and kokoro engine are the zero-VRAM always-available floor.
```contract:example
captured: synthetic            # status=building — replaced by captured evidence at flip-to-live (V11)
binding: http
request: |
  GET /api/voice HTTP/1.1
response: |
  HTTP/1.1 200 OK
  {"stt_default":"whispercpp","stt_active":"whispercpp",
   "stt_registry":[{"id":"whispercpp","label":"Whisper.cpp","kind":"cpu"},
                   {"id":"parakeet","label":"Parakeet-TDT 0.6B","kind":"gpu"}],
   "engines":{"kokoro":{"up":true,"voices":["af_heart","am_adam"]},
              "qwen3tts":{"up":false,"voices":[]}},
   "voice_enabled":true}
```
Adjacent: [[voice#op: voice.act]] (boot an engine/ear), [[voice#op: voice.watch]] (a live spoken
turn), [[fabric-config#op: fabric-config.get]] (VRAM budget), [[model#op: model.list]] (the brain
the circuit speaks).

## op: voice.act
**`voice.act` is the circuit steer: SWITCH the active ear/engine/voice/persona, LOAD or UNLOAD a
GPU ear or TTS engine (VRAM-budgeted through the one resource-manager authority), and TOGGLE
per-mode voice on/off — the real, day-one-swappable config surface; fail-loud on an unknown id or
a no-fit VRAM plan, never a silent fallback to kokoro.**
```contract:op
op: voice.act
resource: voice
kind: act
status: building
direction: outbound
atlas: [CC-14.2, CC-14.4]
tasks:
  - phrase: "switch the voice to a different engine"
    params: {act: switch, engine: orpheus}
  - phrase: "load the parakeet ear so I can dictate faster"
    params: {act: load, service: parakeet}
  - phrase: "free the GPU ear when I'm done talking"
    params: {act: unload, service: parakeet}
  - phrase: "turn voice off for this mode"
    params: {act: toggle, voice_enabled: false}
  - alias: "change the persona"
  - alias: "boot a TTS engine"
  - alias: "pick a different voice"
bindings:
  - { kind: http, method: POST, path: /api/voice/switch, transport: bridge-http, exposure: "exposure.json#bridge-http", note: "set the active engine/voice/persona; co-residence shrink runs (a heavy engine may evict a brain slice). Source runtime/bridge.py:62/261 — NEVER a silent fallback to kokoro on a typo (fail loud)" }
  - { kind: http, method: POST, path: /api/voice/load, transport: bridge-http, exposure: "exposure.json#bridge-http", note: "load a loadable voice service (GPU ear or TTS engine) via voice/lifecycle.load → the shared gpu.check_fit/teardown core. VRAM-budgeted, fail-loud on no-fit. Source voice/lifecycle.py:130" }
  - { kind: http, method: POST, path: /api/voice/unload, transport: bridge-http, exposure: "exposure.json#bridge-http", note: "cgroup stop (systemctl stop) — reaps vLLM EngineCore (orpheus) orphan-safe. Source voice/lifecycle.py" }
liveness: none
emits: []
consequences:
  - when: "load a GPU ear/engine (act=load) — the service was down"
    expect: [voice.load]
    bound: "wake ≤ the engine's cold-load (kokoro ~instant; qwen3tts/xtts/chatterbox ~25s; orpheus ~17min ⚠ swap-hostile)"
    evidence: "[[voice#op: voice.list]] (/api/voice/services) shows the service `up` with its VRAM; the bridge emits a voice.load run-record stamping wake_ms+vram_used_mb (runtime/bridge.py:908)"
  - when: "switch engine/voice/persona (act=switch)"
    expect: []
    bound: "n/a — a config write; the next turn uses the new selection"
    evidence: "[[voice#op: voice.list]] reflects the new stt_active / engine selection; a subsequent [[voice#op: voice.watch]] turn speaks in the new voice"
  - when: "toggle voice_enabled (act=toggle)"
    expect: []
    bound: "n/a — a flag write"
    evidence: "[[voice#op: voice.list]] `voice_enabled`; voice-off makes the speak step a no-op (text still flows)"
correlate: [service]
verification:
  load-unload: {state: probe-verified, run: "project-voice-stack 2026-06-05: load(qwen3tts) up ~16s/5463 MiB → synth → unload → baseline no leak; xtts+orpheus load→console-sees-it→synth→unload→card freed", date: 2026-06-12}
  switch:      {state: probe-verified, run: "the config-lab switch reuses rhm_config slots; verified via /api/voice reflecting the change", date: 2026-06-12, note: "live persona-BINDING + identity-persist are the unflipped slices (project-voice-stack)"}
  toggle:      {state: probe-verified, run: "voice_enabled gate (G4.4)", date: 2026-06-12}
```
### Description (purpose-free)
The mandatory configuration lab made real: a consumer picks and tunes the speech circuit from
live registries, swappable day-one. SWITCH sets the active engine/voice/persona (reusing the
`rhm_config` slot mechanism). LOAD/UNLOAD drive a GPU ear or TTS engine through `voice/lifecycle`
which delegates to the ONE shared VRAM resource-manager core (`gpu.check_fit` / `gpu.teardown`) —
so a UI-path voice load is the SAME load the `company` console sees and budgets (one VRAM
authority, no dual-authority OOM). TOGGLE flips the per-mode `voice_enabled`. Every act fails loud:
an unknown engine id is rejected (NOT silently routed to kokoro — that would ship the wrong voice
and mask a typo), and a load that will not fit returns a no-fit plan rather than OOMing.
### Request
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/voice.act.request",
  "type": "object",
  "required": ["act"],
  "properties": {
    "act":     { "enum": ["switch", "load", "unload", "toggle"] },
    "service": { "type": "string", "description": "act=load/unload: a loadable voice-service id (GPU ear or TTS engine) from [[voice#op: voice.list]] /api/voice/services" },
    "engine":  { "type": "string", "description": "act=switch: a registered TTS engine id" },
    "voice":   { "type": "string", "description": "act=switch: an engine-specific voice" },
    "persona": { "type": "string", "description": "act=switch: a cast persona id" },
    "voice_enabled": { "type": "boolean", "description": "act=toggle" } },
  "additionalProperties": false }
```
### Errors
```contract:error
code: voice.unknown-engine | http: 400 | retryable: false
when: act=switch/load with an engine/service id not in the live registry
teach: "List the registry via [[voice#op: voice.list]] (/api/voice, /api/voice/services). The bridge NEVER silently falls back to kokoro on an unknown engine (that would mask a typo and ship the wrong voice) — pick a registered id."
```
```contract:error
code: voice.no-vram-fit | http: 409 | retryable: true
when: act=load when the engine/ear will not fit the 16 GB budget even after eviction planning
teach: "The shared resource-manager refused the load (fail-loud, not OOM). Unload a resident service ([[voice#op: voice.act]] act=unload), read the budget via [[fabric-config#op: fabric-config.get]], or pick a lighter engine (kokoro/whisper.cpp are the zero-VRAM floor). Orpheus (~10 GB, ~17min cold) is swap-hostile — never co-resident with a local brain."
```
```contract:example
captured: synthetic            # status=building (V11)
binding: http
request: |
  POST /api/voice/load HTTP/1.1
  Content-Type: application/json
  {"service": "parakeet"}
response: |
  HTTP/1.1 200 OK
  {"ok": true, "service": "parakeet", "state": "up", "vram_used_mb": 5100, "wake_ms": 30200}
```
Adjacent: [[voice#op: voice.list]] (the registry this steers), [[voice#op: voice.watch]] (a turn
that uses the selection), [[fabric-config#op: fabric-config.get]] (the VRAM budget the load checks
against).

## op: voice.watch
**`voice.watch` is THE live spoken turn: POST recorded audio in, receive a streamed ndjson
response that interleaves the transcript, the brain's reply parts, and per-sentence synthesised
wav (base64) so first audio plays while the brain is still thinking — the Concurrent-Cognition
voice circuit, proven end-to-end on-machine.**
```contract:op
op: voice.watch
resource: voice
kind: watch
status: building
direction: outbound
atlas: [CC-14.1, CC-14.3, CC-14.6]
tasks:
  - phrase: "have a spoken conversation turn — talk and get spoken reply"
  - phrase: "dictate audio and hear the answer streamed back"
  - phrase: "stream the voice reply sentence by sentence"
  - alias: "talk to the company"
  - alias: "voice turn"
  - alias: "push to talk"
bindings:
  - { kind: http, method: POST, path: "/api/voice/stream?persona=<id>", transport: bridge-http, exposure: "exposure.json#bridge-http", note: "the STREAMING turn (Tier-1): audio body in → application/x-ndjson out. hear→think-in-PARTS→speak-part-by-part (chat_parts G4). Source runtime/bridge.py:1187 _voice_stream" }
  - { kind: http, method: "POST (boot=1 boots the engine on demand)", path: "/api/voice/turn?persona=<id>&boot=1", transport: bridge-http, exposure: "exposure.json#bridge-http", note: "the non-streamed turn (synth WHOLE reply then return) — reuses loop_turn with the in-process Suite.chat injected (one brain, zero self-HTTP). Source bridge.py:97/fcd1ae1" }
liveness: binary-stream
frames: "application/x-ndjson, one JSON object per line: {type:transcript,text} · {type:part,idx,text} · {type:chunk,idx,text,wav_b64,ms} (per sentence, monotonic idx across parts — the wav is base64 PCM/wav the FE decodes+plays) · {type:reply,text} (assembled full reply, once) · {type:done,total_ms,reply,parts,chunks} · {type:error,...} on fail-loud then close"
resume: "none — a single turn; the connection is per-turn (Connection: close). A cancelled (client-disconnect) speculative turn is detected via select+MSG_PEEK and stops before the next synth (Tier-2 barge-in)"
keepalive: "none — chunks arrive as fast as synth completes; first audio at ~(silence+STT+part1-gen+TTS-of-one-short-sentence)"
termination: "ends after the done frame, on {type:error}, or on client disconnect (barge-in)"
emits: []
consequences:
  - when: "a spoken turn completes (engine up, voice_enabled)"
    expect: [agent_sessions.turn]
    bound: "first audio chunk ≤ a few seconds (concurrent brain↔synth); full turn unbounded-with-evidence: the part/chunk frames are the live progress heartbeat"
    invariant: "the brain is the IN-PROCESS Suite.chat (think_fn) — ONE brain, no self-HTTP; the reply is grounded in live state, spoken AS the selected persona"
    evidence: "the ndjson frames themselves (transcript→parts→chunks→reply→done); when trial_session= is set the turn is RECORDED to CAS ([[voice#op: voice.list]] /api/trial/transcript)"
correlate: [persona]
verification:
  live-circuit: {state: probe-verified, run: "project-voice-stack 2026-06-05 ★ FULL LIVE CIRCUIT: one /api/voice/turn → whisper.cpp heard the clip → in-process brain replied AS Sable grounded in live state → qwen3tts produced 1.33 MB wav", date: 2026-06-12, note: "the on-MACHINE circuit is proven. UNFLIPPED device-only: the FEEL of auto-listen (VAD finished-thought), on-device iOS playback locked-screen, always-on activation — the FORM/canvas lane, NEVER claimed live here"}
```
### Description (purpose-free)
The complete speech turn as one streamed exchange. A consumer records audio (push-to-talk: hold
or tap; the native modes Atlas CC-14 documents) and POSTs the bytes; the bridge transcribes with
the selected ear, drives the in-process brain as a SEQUENCE OF PARTS (`chat_parts`), and synthesises
each completed part's sentences with the selected engine WHILE the next part is still generating —
two overlaps compose (parts overlap brain↔TTS; sentences overlap synth↔playback on the client's
play cursor). The result is the voice-speaks-part-N-while-the-brain-thinks-N+1 design
(Concurrent Cognition G6, the PART is the TTS streaming unit). A finished-thought semantic judge
(`/api/voice/finished-thought`, its own fast model role) decides turn boundaries for auto-listen;
barge-in is client-side (disconnect cancels the speculative turn). The native voice-dictation
finished-thought + VAD FEEL, on-device iOS audio, and always-on activation are device-only and
unflipped — named, never green-painted.
### Errors
```contract:error
code: voice.engine-down | http: 409 | retryable: true
when: a turn requests an engine that is down and boot was not requested
teach: "Boot the engine first ([[voice#op: voice.act]] act=load), or pass ?boot=1 on /api/voice/turn to boot on demand. Read which engines are up via [[voice#op: voice.list]]."
```
```contract:error
code: voice.missing-persona | http: 400 | retryable: false
when: /api/voice/stream called without ?persona=<id>
teach: "The streaming turn needs ?persona=<id> (fail loud — runtime/bridge.py:1252). List personas via [[voice#op: voice.list]] (/api/personas)."
```
```contract:example
captured: synthetic            # status=building — the on-machine circuit is proven; this transcript is illustrative until harness-captured (V11)
binding: http
request: |
  POST /api/voice/stream?persona=sable HTTP/1.1
  Content-Type: application/octet-stream
  <recorded wav/webm audio bytes>
response: |
  HTTP/1.1 200 OK
  Content-Type: application/x-ndjson
  {"type":"transcript","text":"what did the build loop finish overnight?"}
  {"type":"part","idx":0,"text":"The overnight loop closed three lanes."}
  {"type":"chunk","idx":0,"text":"The overnight loop closed three lanes.","wav_b64":"UklGR...","ms":420}
  {"type":"reply","text":"The overnight loop closed three lanes. Voice, remote, and code-intel entries landed."}
  {"type":"done","total_ms":3120,"reply":"...","parts":2,"chunks":3}
```
Adjacent: [[voice#op: voice.list]] (pick the circuit), [[voice#op: voice.act]] (boot the engine),
[[model#op: model.list]] (the brain the circuit speaks), [[remote]] (the HTTPS origin the browser
mic requires).

## Errors
**Resource-level error vocabulary: `voice.unknown-engine` (fail-loud on an unregistered id —
never a silent kokoro fallback), `voice.no-vram-fit` (the resource-manager's honest no-fit refusal
instead of OOM), `voice.engine-down` (boot-first/boot=1 recovery), `voice.missing-persona` (the
streaming turn's required param).** Every refusal names the live recovery — list the registry,
boot/unload a service, pass boot=1. No error claims a circuit the stack cannot run; the device-only
feel (auto-listen, iOS playback) is named in [[voice#op: voice.watch]] verification, never as an error.

## Links
**No address-typed fields: a voice selection references service ids (resolved against the live
registry via [[voice#op: voice.list]], not a corpus scheme), an engine-specific voice name, and a
persona id — none are fabric addresses.** The synthesised `wav_b64` frames are inline audio bytes
(read by playing, never dereferenced), consistent with [[events#Links]] treating stream items as
non-addressable. A recorded trial turn's transcript IS content-addressed (CAS) but is reached
through [[voice#op: voice.list]]'s /api/trial/transcript read, not a voice-resource scheme.
