---
type: proposal
title: VOICE + EARS Fusion — OpenWebUI voice through the Company's ONE circuit
area: channels + voice (fusion)
register: prescriptive
status: unconfirmed
posture: both sides incomplete · AI-generated · unreviewed · no source of truth · no horizon · best parts fused INTO the company · no duplicates
sources:
  - build-prep/openwebui-company-fusion/area-D-channels-voice.md
  - build-prep/openwebui-company-fusion/owui-side-map.md (§3 Voice)
verified_live: 2026-06-28 (probes + drive-by-use, see §5)
created: 2026-06-28
relates-to: ["[[area-D-channels-voice]]", "[[owui-side-map]]"]
---

# VOICE + EARS Fusion

> The brief said "verify nothing, trust nothing." Doing so already overturned three of its
> stated facts (ref clip exists; kokoro mouth is currently dead; the STT shim isn't a clean
> separate-circuit reassembly — it's pinned/broken). Findings are tagged Observed / Verified / Inferred.

---

## 1. BEST PARTS

### Company — the one CIRCUIT, not a TTS↔STT pair
- **ONE turn endpoint** `runtime/bridge.py:2842` `/api/voice/turn` = hear→think→speak as a single call,
  reusing `voice/loop.py:186 loop_turn()` (NOT a parallel hear/think/speak). The **brain is injected
  in-process** (`SUITE.chat`, bridge.py:2898) — one event log, one store, no HTTP self-call. **Observed.**
- **Streaming twin** `/api/voice/stream` (bridge.py:2915) — speak sentence-by-sentence (the long-reply
  latency fix, bridge.py:2312). **Observed.**
- **Loadout-driven, one source.** `runtime/suite.py:2691 rhm_config()` returns `stt` (ear), `tts_engine`,
  `tts_voice`, `persona` — persisted via `set_rhm_config` (suite.py:2732). The bridge resolves voice the
  SAME way everywhere: `tts_engine` override → persona.engine → kokoro (bridge.py:2811-2818, mirrored at
  2874-2876). Ear = `rhm_config().stt or active_ear()` (bridge.py:2889). **Observed.**
- **Engine variety** — 6 TTS (`voice/tts_service.py` kokoro + 5 wrappers under `voice/engines/`),
  7 STT ears (`voice/stt.py:68 STT_PROVIDERS`), boot ear moonshine (voice.env). **Observed (registry).**
- **Personas** `voice/personas.py` (viv/tess/sable/pip/wren) — persona = brain prompt + suggested engine +
  voice-arg, a data row. **Observed.**
- **Speakable layer** `voice/speakable.py` — ONE pre-TTS transform on every reply→speech path (turn,
  stream, /api/tts), engine-aware expression-tag mapping. **Observed.** Applied on the generic
  `/api/tts` path too (bridge.py:2828-2830).
- **Fail-loud, no silent ear fallback** (stt.py raises naming provider+endpoint; AGENTS.md rule 4).

### OpenWebUI — the UX primitives (owui-side-map §3)
- **Streaming sentence-split TTS + SHA256 cache** — `routers/audio.py:579 POST /speech`, cache
  `cache/audio/speech/{hash}.mp3` (:597), knob `AUDIO_TTS_SPLIT_ON` default `punctuation`
  (config.py:2447). The frontend splits the streaming reply on punctuation and fires `/speech` per
  chunk → audio starts before the message finishes. **The good UX primitive.**
- **The voice-call UI** — mic capture / turn-taking / per-sentence playback lives in the **compiled
  SvelteKit frontend** (owui-side-map §3 + §8). Backend is a stateless TTS↔STT pair the client loops.
  **This is the constraint that shapes the whole fusion (see §2): you cannot change what the OWUI voice
  UI calls without forking the frontend.**
- Honest limits: real conversational VAD/turn-taking is frontend-only; backend VAD is only whisper
  silence-trim, off by default. Voice lives **in chats, not channels**.

---

## 2. THE FUSED VOICE — resolve the duplication

### The brief's hypothesis, corrected
> "Should OWUI voice route through `/api/voice/turn` instead of my two shims that reassemble it?"

**No — and the framing is the trap.** Verified reasons:

1. **OWUI's voice UI is compiled and can ONLY call two stateless OpenAI endpoints**
   (`/v1/audio/speech`, `/v1/audio/transcriptions`) — owui-side-map §3/§8. It architecturally cannot
   call a single fused-turn endpoint, and we cannot change that without forking the frontend (license-
   capped, §8). So a shim PAIR is the *correct, only* seam for OWUI-native voice. The shims are not a
   mistake; pointing them at the wrong backend is.
2. **`/api/voice/turn` injects the COMPANY brain** (`SUITE.chat`, bridge.py:2898). Routing OWUI's
   *in-chat* voice through it would **bypass OWUI's own chat pipeline** (its selected model, its RAG,
   its tools). Wrong for voice-in-a-chat: the user picked an OWUI model; voice must speak *that* model's
   reply, not re-think it through the company brain.

So `/api/voice/turn` stays the company's **native** voice surface (the RHM / channels-voice horizon);
the **shims stay** as OWUI's STT/TTS adapters. The real duplication is **inside the shims**, not between
shims and circuit.

### The actual duplication to kill (Verified)
- **TTS shim hardcodes kokoro** and ignores the loadout: `ops/tts_openai_shim.py:12` posts straight at
  `:4123`, with its own VOICE_MAP — re-implementing engine routing the bridge already does at
  `/api/tts` (bridge.py:2803-2840: `tts_engine`→persona.engine→kokoro + speakable + fail-loud).
- **STT shim does NOT follow the active ear.** The committed source references an **undefined `PROVIDER`**
  (stt_openai_shim.py:58,69 — NameError); the *running* process (older, pre-commit) is pinned to a hard
  `granite` (a DOWN GPU ear). Neither reads the live `rhm_config().stt`. And it *can't* — it runs in
  `openwebui-venv`, a separate process with no `SUITE` (it imports `voice.stt`, whose `active_ear()`
  only reads the env default, not the live in-app selection). **Verified live (§5).**

### The fix — both shims become THIN adapters over the bridge (one loadout source)
Make each shim a pass-through to the bridge's already-loadout-aware routes, so the **bridge's
`rhm_config()` is the single source** and OWUI follows automatically:

| Shim (OWUI native voice) | Today (WRONG) | Fused (CORRECT) |
|---|---|---|
| `tts_openai_shim` `/v1/audio/speech` | POST direct kokoro:4123, own VOICE_MAP | POST bridge `/api/tts` with `{text}` and **no engine** → bridge resolves `tts_engine`→persona.engine→kokoro + runs speakable. WAV→MP3 transcode for OWUI. |
| `stt_openai_shim` `/v1/audio/transcriptions` | `provider=PROVIDER` (NameError) / pinned granite | POST bridge `/api/voice/stt` (bridge.py:2780, which does `rhm_config().stt or active_ear()`). The bridge picks the live ear. |

Result — **"switch ear/voice in the company → OWUI follows" becomes true by construction**: the operator
changes `tts_engine`/`tts_voice`/`persona`/`stt` in the company (one `set_rhm_config`), the bridge
resolves it, and BOTH the company's native `/api/voice/turn` AND OWUI's in-chat voice (via the thin
shims) speak/hear through the same selection. No second loadout, no VOICE_MAP, no pinned ear, no
re-implemented routing. The shim becomes ~15 lines: forward bytes, transcode, return the OpenAI shape.

### Three-way duplication resolved
- **OWUI native audio** (`routers/audio.py`) — KEEP as the *caller* (it owns the streaming-split + cache
  UX, which we want), but its engine is `openai`+base-url=shim → so it speaks/hears through the company.
- **The shims** — KEEP, but thin them to bridge adapters (above). They are the company↔OWUI translation
  membrane, not a parallel circuit.
- **The company circuit** (`/api/voice/turn`,`/stream`) — KEEP as the native surface; unchanged.
- **No duplicate engine routing, no duplicate loadout, no duplicate ear-selection.** One source: the bridge.

> **Bonus the fusion unlocks free:** OWUI's streaming-split + SHA256 cache (audio.py:597) is exactly the
> UX the company's `/api/voice/stream` hand-built. With the TTS shim pointed at `/api/tts`, OWUI's cache
> now caches *company-voice* MP3s. The company can later adopt the same `{hash}.mp3` cache for `/api/tts`
> (it has none today) — harvest the primitive INTO the company, don't keep two.

---

## 3. COMPANY-INTERNAL issues

1. **Missing ref clip — RESOLVED (map+brief are STALE).** `voice/ref/company_voice_ref.wav` **exists**:
   203,564 B, `RIFF WAVE PCM 16-bit mono 24000 Hz` (Verified, `file`). The clone engines'
   fail-loud-if-absent no longer fires. **Action:** update area-D map §"Reference Clip" + finding #5 from
   "does not exist" → "minted, validated 24k/16-bit mono"; un-flag chatterbox/xtts/cosyvoice on this axis.
2. **cosyvoice build broken — confirm-or-drop.** area-D / ops/README: repo build blocker (openai-whisper
   wheel, deepspeed timeout). **Action:** it is the only ❌ engine and overlaps capability with xtts
   (ref-clip clone) + qwen3tts (instruct/description). Propose: **de-prioritise** to on-demand-experimental
   (do NOT auto-start, do NOT gate the loadout on it). Keep the wrapper; flag the wheel fix as standalone
   work. Not on the fusion critical path.
3. **GPU ear co-residence / VRAM (16 GB).** granite ~1.5–4.7 GB · parakeet ~3.05 GB · canary ~10 GB,
   vs brain ~13 GB + embeddings ~5 GB. **Resolution:** the interaction loadout is **moonshine (0 VRAM,
   CPU)** as default ear (already so) — no GPU ear in the default voice loadout, so no co-residence
   conflict at rest. GPU ears stay on-demand via `voice/lifecycle.py` (unified VRAM authority,
   systemctl-driven, fail-loud on budget). **Action:** make the *shim's* ear-selection inherit the same
   `rhm_config().stt` (default moonshine) → OWUI voice is 0-VRAM by default too, never silently lighting
   a GPU ear.
4. **moonshine new default — good, keep.** ONNX, <1 GB, 0 VRAM, ~9× realtime, built for live conv
   (area-D #4). Correct default for both the company circuit AND (via the thinned STT shim) OWUI voice.
   One nuance: `voice/stt.py:134 STT_DEFAULT` literal is `whispercpp`; the *live* default is moonshine
   via `COMPANY_STT` env (voice.env). **Action:** confirm the env is sourced by the bridge's process too
   (not only the voice units), else `active_ear()` fallback disagrees with the units. (Inferred risk —
   verify the bridge sees COMPANY_STT=moonshine.)

---

## 4. BROKEN / HALF-BUILT SEAMS (named as work)

- **S-V1 — kokoro mouth does not synthesize (CRITICAL).** `/` health = `{"ok":true}`, log says "ready",
  but `POST /tts` never completes (status 000 at 60s AND 180s; after a hand-restart the process wedges
  during model load, never reaching "ready", health goes 000). Log stalls at an onnxruntime GPU
  device-discovery warning (`/sys/class/drm/card0/device/vendor` unreadable — WSL2). **Verified live
  (§5).** Since kokoro is the only always-on CPU mouth and GPU engines are on-demand/down, **right now
  there is NO working TTS engine** → no voice turn can complete end-to-end. WORK: pin kokoro-onnx to the
  CPUExecutionProvider explicitly (stop it probing a phantom GPU), OR put kokoro under systemd with a
  warm-on-boot + health-gated readiness like the STT units. This is the top voice seam.
- **S-V2 — STT shim broken/pinned (CRITICAL for OWUI voice).** Committed `PROVIDER` NameError;
  running process pinned to a down `granite`. Neither follows the loadout. **Verified live (§5).**
  WORK: thin to bridge `/api/voice/stt` adapter (§2). One-line stopgap if kept standalone:
  `provider=_active_ear()` (already defined, stt_openai_shim.py:24) — but the proper fix is the bridge
  adapter so it follows the *live* selection, not the env default.
- **S-V3 — TTS shim hardcodes kokoro + own VOICE_MAP** (tts_openai_shim.py:12,16). WORK: thin to bridge
  `/api/tts` adapter (§2).
- **S-V4 — shims not under any supervisor.** Running by hand (`openwebui-venv` python, pids 93906/96651);
  no systemd unit, no orienteering entry. WORK: add `company-voice-stt-shim` / `-tts-shim` units (or fold
  into the OWUI launch) + an `orienteering/entries/*` note (CLAUDE.md: things in the company's orbit get
  ledgered).
- **S-V5 — voice is in OWUI chats, not channels.** owui §3. The company's `/api/voice/turn` is per-persona
  and channel-aware-capable; OWUI voice is per-chat. Fusing voice INTO channels (speak a channel
  `@model` reply) is open horizon, not built. Named, not scheduled.
- **S-V6 — s2s path declared, no runner** (bridge.py:2861 refuses `voice_path=s2s` loudly). Correct
  fail-loud; listed so it isn't mistaken for built.
- **S-V7 — cosyvoice import fail** (§3.2). Standalone wheel/deepspeed work.

---

## 5. VERIFICATION DONE (live, 2026-06-28)

**Method:** direct curl probes + drive-by-use against the running bridge :8770 and voice services.

| Check | Result | Evidence |
|---|---|---|
| Kokoro `/` health :4123 | UP `{"ok":true}` | curl |
| Kokoro `/tts` synth | **DEAD** — 000 at 60s AND 180s; restart wedges at model-load | curl ×3 + /tmp/kokoro.out (onnxruntime GPU-discovery stall) |
| moonshine STT `/` :2034 | UP `{"ok":true,"ear":"moonshine"}` | curl; systemd unit active |
| whisper.cpp :2022 | **DOWN** (000) — area-D listed it live; not up now | curl |
| Bridge :8770 | UP (200) | curl |
| `/api/voice/turn` (empty POST) | 400 — the `?persona=` fail-loud guard fires (bridge.py:2856) | curl |
| `/api/voice/turn` full turn | **NOT COMPLETABLE** — no working mouth (kokoro dead, GPU engines down). Wiring verified by code (brain-injection 2898, ear-resolve 2889, boot-on-demand 2877); cannot synth. | code + above |
| ref clip | **EXISTS**, valid 24k/16-bit mono WAV (brief+map said missing) | `file` |
| STT shim :4201 | running, but pinned to DOWN granite (returns fail-loud granite error); committed source NameErrors on `PROVIDER` | curl + git show HEAD |
| TTS shim :4200 | running, hardcoded to kokoro:4123 (→ also dead, since kokoro synth is dead) | curl 000 + source |
| GPU TTS/STT units | none active except moonshine (systemctl --user) | systemctl |

**Bottom line:** the circuit's *wiring* is sound and the loadout source is real and single; but **no TTS
engine currently synthesizes**, so no end-to-end turn completes today (S-V1 is the blocker). The fusion
design (§2) does not depend on resolving S-V1 first — it's correct regardless — but voice will not be
*demonstrable* (company-native or OWUI) until a mouth synthesizes.

---

## NEXT STEPS (options)

- **A — Fix the mouth first (unblocks everything):** pin kokoro-onnx to CPUExecutionProvider / put it
  under systemd warm-on-boot, then drive ONE real `/api/voice/turn?persona=…&tts_engine=kokoro` to a
  `wav_b64` (the missing §5 proof). Recommended first — nothing voice is demonstrable until a mouth speaks.
- **B — Build the thin-shim fusion (§2):** rewrite both shims as bridge adapters (`/api/tts`,
  `/api/voice/stt`), add their systemd units + orienteering notes, point OWUI's `openai` STT/TTS base at
  them. Delivers "OWUI follows the company loadout" — but only *visibly* works once A lands.
- **C — Harvest OWUI's cache INTO the company:** give `/api/tts` the same `{hash}.mp3` SHA256 cache OWUI
  has (audio.py:597), so the company circuit gains the cache primitive instead of two systems having it.
- **D — Map hygiene:** correct area-D §"Reference Clip"/#5 (clip exists), whisper.cpp live→down,
  re-flag kokoro synth as a seam.
