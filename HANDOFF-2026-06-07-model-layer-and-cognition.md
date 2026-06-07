---
type: handoff
module: root
aliases: ["Handoff 2026-06-07", "Model Layer + Concurrent Cognition Handoff"]
tags: [company, handoff, session, models, vram, voice, cognition]
status: living
---

# HANDOFF — 2026-06-07 · Model/VRAM layer, voice co-residence, persona identity, + the Concurrent Cognition loop

**Read order for a fresh agent:** `AGENTS.md` → `MAP.md` → `STATE.md` → `HANDOFF.md` (the 2026-06-06 voice-live session) → **this** (the 2026-06-07 model-layer + co-residence + cognition session). `STATE.md` + the tests are canonical; if this disagrees, fix this.

**Why this exists:** a parallel session is doing a large merge + further work. Everything below is committed to `main`. This documents (1) what changed and where, (2) the exact files that are merge-conflict territory, (3) the current live/persisted config, and (4) **what the next loop (Concurrent Cognition) will build, so other sessions account for its territory.**

---

## 0. TL;DR — what this session delivered (all on `main`, 8 commits)

| Commit | What |
|---|---|
| `9412e01` | **Model/VRAM layer**: measured real footprints; **config-block sizing as the one source**; `_profile` auto-util; `gpu.fit_report` → `/api/fit`; the **settings fit-surface** (a bar: will this selection fit the 16GB card?). |
| `5746211` | **Persona identity hookup**: the persona's `brain` character now reaches the prompt (was names-only); **any-persona × any-engine** voice mapping. |
| `1b51437` | **qwen3tts/cosyvoice sizing** (measured, config blocks, engines read config) + the **co-residence shrink mechanism** (`_apply_model_ctx`, `_local_brain_key`, `coresident_brain_ctx`). |
| `796be31` | **Co-residence DELIVERED**: 4-bit AWQ Orpheus → **64K brain co-resident with the voice** (proven server-side); judge rebound to the resident 4B. |
| `a89dab1` | **Fix**: click-to-indicate gated behind a deliberate `◎ point` mode (default off) — fixes the Settings close button + the translucency bug. |
| `0829118` | this handoff doc + the **Concurrent Cognition** research landscape (`build-prep/concurrent-cognition/`). |
| `799a08a` | **Whisper-offline fix**: restarted the CPU ear (I'd stopped it during GPU clearing) + a UI **▶ start** affordance for a down ear (`STT_PROVIDERS` carry a `service`; Settings ear-status line). |
| `e9ac048` | **Detailed voice trace**: every turn → durable `voice.stream`/`voice.turn` records (turn_id · transcript · reply · per-step ms · errors-with-step), `judge` logs the text it judged, NEW `/api/voice/log` → `voice.client` for the browser's auto-listen/recording/playback steps. |

**Current live state (2026-06-07):** brain `chat-4b` (Qwen3.5-4B-AWQ) resident @ **64K / util 0.49**; voice = **4-bit AWQ Orpheus** (`Hariprasath28/orpheus-3b-4bit-AWQ`) @ util 0.32, **co-resident**, ~2.4 GB headroom; judge bound to the resident 4B; the full voice loop (judge + tool-call + synth) proven server-side with both resident. Serving at `https://workstation001.tail777bc2.ts.net` (bridge :8770 + canvas :5173 via `tailscale serve`).

---

## 0.5 ⚠️ VERIFICATION STATUS — be honest (this is pre-production; a lot is UNVERIFIED)

**The frame (Tim, 2026-06-07):** "we don't know if a lot of things work, and it's very likely there will be updates/additions before production." This section is deliberately blunt so no one downstream mistakes *code-complete* for *working*. Three buckets:

**✅ PROVEN BY USE (server-side / headless — I drove it and saw the result):**
- Model footprints measured by actual load (4B, qwen3tts, cosyvoice, BF16/w8a8/4-bit Orpheus).
- `config`-block sizing, `_apply_model_ctx` auto-util, `gpu.fit_report`/`/api/fit` — curl + the budget gate refusing over-capacity loads.
- 4B brain **64K co-resident with 4-bit AWQ Orpheus** — both processes up; **judge** (FINISHED/MORE on the resident 4B), **tool-call** (`get_weather`), **Orpheus synth** (valid WAV) all with both resident.
- Persona `brain` prose reaches the prompt — `persona=sable` replied in Sable's character.
- A **full streaming voice turn server-side** — fed an Orpheus WAV back in → whisper transcribed → brain replied → Orpheus re-synthesised in chunks; the **voice trace** captured it (`voice.stream`/`judge`/`voice.client` records with texts+timings).
- Settings ✕-close + no-translucency (browser-verified); whisper ear online + the ear-status render (browser-verified); FE builds clean; `drift_acceptance` 5/5; `e4_registry` passes.

**🟡 CODE-COMPLETE BUT NOT VERIFIED BY USE (built, compiles/parses, but never actually exercised):**
- **any-persona × any-engine** — only the *voice-arg MAPPING* is verified (the matrix resolves). **No persona was actually synthesised on a non-default engine.** The clip engines (**xtts/chatterbox**) need `COMPANY_VOICE_REF`, which **does not exist** → those personas will **fail loud** until a reference clip is made. kokoro voices assigned, never synth-tested.
- **qwen3tts/cosyvoice reading their new `config` block** — `_reg_config()` was added, but I measured their footprints via the OLD env path and **did not restart them to confirm they read the config block correctly.** Unverified.
- **The co-residence SHRINK mechanism on a real switch** — `796be31` proved both *already resident* at 64K; the `/api/voice/switch` "shrink the brain for a heavy voice" path was **not driven end-to-end through the UI** (it's a no-op for AWQ Orpheus since coresident_ctx == default, so the *shrinking* branch is effectively untested).
- **The voice `voice.client` browser reports** — the `api.voiceLog` calls compile; they only *fire* in a real browser session, which hasn't happened. Server endpoint + records proven; the client emitters are not.
- **`/api/model/config` context-resize + restart** under a resident voice — the budget-gated-refuse path is reasoned, only partially exercised.

**🔴 KNOWN-UNKNOWN / NOT DONE — expect work before production:**
- **The on-device live voice conversation has NEVER been verified.** mic capture → STT → brain → streamed TTS → **iOS audio playback** on Tim's actual phone: unproven end-to-end with this config. This is the headline UX and it is **not** known to work.
- **Auto-listen (the VAD→judge→fire loop) is unverified on-device** — Tim reported "listening doesn't seem to detect." That issue is **NOT resolved** — the new trace exists *so it can be investigated*, not because it's fixed. Treat auto-listen as unproven.
- **4-bit Orpheus audio QUALITY** — never heard. 4-bit may degrade pronunciation; w8a8 int8 (`nytopop/...w8a8`, ~4.75 GB) is cached as a higher-quality fallback but doesn't co-reside at 64K.
- **Mobile FORM** of the new surfaces (fit-surface bar, ear-status, settings) at 390px — rendered once early; not re-verified after subsequent changes.
- **Concurrent Cognition** — entirely unbuilt (research landscape only).
- General: this is single-developer-via-AI, pre-deploy. The substrate is proven in pieces; the *integrated product experience*, especially voice on a phone, is largely unproven.

---

## 1. The Model/VRAM resource layer (`9412e01`)

**What it is.** The single VRAM authority + a sizing model where a service's `config` block is the ONE source that both the budget gate AND the launch read — no drift between "what the fit-gate thinks it costs" and "what it grabs."

**How it works.**
- `ops/cli/gpu.py` — `budget_vram(reg,key)`: for a config-model, budget = `config.gpu_util × vram_ceiling_mb` (authoritative, immune to stale telemetry); else `learned_vram` / `vram_mb`. `check_fit`, `plan_eviction` ({models:0,brain:1,voice:2}), `teardown` (cgroup, reaps vLLM EngineCore), `format_state`. **NEW: `fit_report(reg, keys)`** — the "will this selection fit?" answer (per-item budget, sum vs ceiling, measured free, fits_card/fits_now, evict list).
- `ops/services.json` — each GPU model carries a `config` block. `chat-4b` carries a measured **`_profile`** `{fixed_mb: 5838, kv_kb_per_token: 31.7}` + `max_model_len_ceiling: 262144`, so util can be derived from any context.
- `runtime/bridge.py` — **`_apply_model_ctx(key, ctx)`** (shared helper): set a model's context window, **auto-size `gpu_util` from `_profile`** so vLLM gets the KV pool that context needs, budget-gated restart (fail loud, never OOM). Endpoints: **`GET /api/fit?services=a,b`** (→ `gpu.fit_report`); **`POST /api/model/config`** (context window + auto-util + restart, delegates to `_apply_model_ctx`); `POST /api/model/load` (budget-gated on-demand load).
- `canvas/app/src/regions/Settings.tsx` — the **fit-surface**: a bar (each piece's share of the 16GB card) + a verdict + "won't fit → unload X". `useAppController.ts` `fitReport` + `refreshFit()` (maps selected brain + persona-engine → service keys → `api.fit`). `api.ts` `fit()`.

**Measured facts (RTX 4080, 16376 MB ceiling, ~15.3 GB usable after WSL baseline):** 4B (hybrid Mamba-attention, **only 8 of 32 layers carry KV**) = fixed ~5.84 GB + KV ~31.7 KB/tok → 256K solo ≈ 14.2 GB (fits solo, proven). qwen3tts ~4.4 GB, cosyvoice ~4.1 GB (not vLLM — fixed footprint, `vram_mb` not a util knob).

## 2. Persona identity — fully hooked up (`5746211`)

**The bug found:** the prompt injected the bare persona id (`"sable"`); the rich `brain` character in `voice/personas.py` **never reached the model**. Personas were names-only in practice.

**Fix (`runtime/suite.py`, in `chat()` ~line 3369):** expand the persona id → its `brain` prose via `voice.personas.get_persona(id)["brain"]` (free-text/unknown falls through). Verified: persona=sable now replies in Sable's character.

**Any-persona × any-engine (`voice/loop.py` + `voice/personas.py` + `runtime/bridge.py`):** `_voice_arg_for(persona, engine)` now keys off the **selected** engine, not the persona's default — so any of the 5 personas works on any of the 6 engines. Design engines (qwen3tts/cosyvoice) → `voice_description`; orpheus/kokoro → a per-persona **`voices` map** (added to each persona); xtts/chatterbox → the reference clip. Both synth paths (`/api/voice/stream` + `/api/voice/turn`) pass the override engine/voice through.

## 3. qwen3tts + cosyvoice sizing (`1b51437`)

Not vLLM (transformers VoiceDesign / CosyVoice's own repo) → **fixed footprint, measured `vram_mb` (not gpu_util)**. Measured: qwen3tts ~4385 MB (`vram_mb` 4500), cosyvoice ~4073 MB (`vram_mb` 4200). Each got a `config` block (model/device/attn/lang · model_dir/repo) that the engine reads (env fallback), mirroring orpheus. `voice/engines/qwen3tts.py` + `cosyvoice.py` now read their config block.

## 4. Voice co-residence — the non-negotiable, delivered (`1b51437` mechanism + `796be31` proof)

**Requirement (Tim):** the finished-thought judge runs on the brain, so during a voice conversation the brain must stay **resident WITH the voice** — co-residence is non-negotiable.

**The mechanism (`runtime/bridge.py` `/api/voice/switch`):** before loading a voice, shrink+restart the brain to the context the registry records as co-resident-safe for THAT voice — `config.coresident_brain_ctx` (a **stored** value, not auto-computed, per Tim) — via `_apply_model_ctx` + `_local_brain_key(reg,rc)` (finds the active local brain service). Light voices record nothing → brain stays at default.

**The finding + resolution:** BF16 Orpheus (~9 GB) and w8a8 int8 Orpheus (~7.4 GB) both proved (by repeated OOM) **too heavy** to co-reside with a usable brain on 16 GB. The **4-bit AWQ Orpheus** (`Hariprasath28/orpheus-3b-4bit-AWQ`, awq_marlin, ~5.8 GB @ util 0.32) is the enabler: the 4B brain co-resides at **full 64K** (util 0.49, fast graph path). **Proven by use, both resident:** judge (FINISHED/MORE on the resident 4B), tool-call (`get_weather Sydney celsius`), Orpheus synth (valid WAV). `orpheus.coresident_brain_ctx=65536` (= brain default → the switch is a no-op; 4-bit needs no shrink).
- **Also fixed:** the judge was bound to `qwen3.5-9b` on ollama (unloaded → empty verdicts); rebound to its recommended resident 4B (via `rhm_config.roles.judge`).
- **Cached models:** w8a8 int8 (`nytopop/orpheus-3b-0.1-ft.w8a8`, ~4.75 GB, higher quality) is downloaded as a solo fallback; original BF16 still cached.
- **needs-Tim:** the 4-bit Orpheus AUDIO QUALITY by ear (it produces valid audio; whether it sounds good enough is unverified — w8a8 is the higher-quality fallback).

## 5. Click-to-indicate gating fix (`a89dab1`)

Click-to-indicate was a **global** capture listener (`useAppController.ts` `onDocClick`) — every tap painted `.ui-indicated` and disrupted the element's onClick. On the Settings modal: the ✕ wouldn't close + tapping any non-input area went translucent (revealing the RHM). **Fix:** an `indicateMode` (default OFF) gates the handler; a **`◎ point`** toolbar toggle enters/leaves it; modals (`.settings`/`.workshop`) are excluded even when on. Verified by use.

---

## 6. ⚠️ MERGE-CONFLICT TERRITORY — files this session changed

A large merge should expect conflicts in these (with the regions I touched):

- **`runtime/suite.py`** — `chat()` persona-prose expansion (~3369). HOT FILE.
- **`runtime/bridge.py`** — NEW module fns `_apply_model_ctx`, `_local_brain_key` (~line 40); endpoints `/api/fit`, `/api/model/config` (refactored), `/api/voice/switch` (co-residence shrink), `/api/voice/stream` + `/api/voice/turn` (voice_arg keyed on selected engine). HOT FILE.
- **`ops/services.json`** — config blocks for `chat-4b` (_profile, ceiling), `tts-orpheus` (model=4-bit AWQ, gpu_util 0.32, max_model_len 12288, coresident_brain_ctx 65536), `tts-qwen3tts`, `tts-cosyvoice`. HOT FILE (registry).
- **`ops/cli/gpu.py`** — added `fit_report`. **`ops/cli/registry.py`** — `_coerce` now passes through non-strings.
- **`ops/AGENTS.md`** — models/VRAM type-view block extended (config-block sizing, fit-surface).
- **`voice/personas.py`** — `voices` map per persona. **`voice/loop.py`** — `_voice_arg_for(persona, engine)`.
- **`voice/engines/{orpheus,qwen3tts,cosyvoice}.py`** — read settings from the registry config block (env fallback).
- **`canvas/app/src/useAppController.ts`** — `fitReport`/`refreshFit`; `indicateMode`/`toggleIndicateMode` + the gated `onDocClick`. HOT FILE.
- **`canvas/app/src/regions/Settings.tsx`** — the fit-surface section. **`regions/Toolbar.tsx`** — the `◎ point` toggle. **`api.ts`** — `fit()`. **`app.css`** — `.settings-fit*`, `button.b.ghost.on`.

- **Added since (`799a08a`,`e9ac048`) — same hot files:** `runtime/suite.py` (`voice_log` method ~line 342; `is_finished_thought` logs `text`). `runtime/bridge.py` (`/api/voice/log` endpoint; `/api/voice/stream` + `/api/voice/turn` enriched records with turn_id/transcript/reply/step + durable error logging). `voice/stt.py` (`service` key on `STT_PROVIDERS` + `_probe_provider`). `canvas/app/src/useAppController.ts` (`startVoiceService`; `api.voiceLog` reports through the auto-listen loop + ptt + playback). `canvas/app/src/api.ts` (`voiceLog`, `modelLoad` already). `canvas/app/src/regions/Settings.tsx` (ear-status line + ▶ start). `STATE.md` (the 2026-06-07 status line + the voice-trace line).

Tests: `tests/drift_acceptance.py` passes; `tests/e4_registry.py` passes. FE builds clean (`canvas/app && npm run build`).

---

## 7. THE NEXT LOOP — Concurrent Cognition (what I'll be building; account for its territory)

**Full landscape:** `build-prep/concurrent-cognition/00-LANDSCAPE.md` (+ 01–06 per-thread, with file:line evidence). Memory: `[[project-concurrent-cognition]]`.

**The idea (Tim's, 2026-06-07):** the right-hand-man's reply becomes a **staged stream spoken in PARTS**, fed by a **swarm of ~32 concurrent small-model ROLES** (concurrent *requests to the ONE resident 4B*, vLLM-batched — not 32 models) whose structured JSON **resolves into the next part's context** (`address→resolve→inject`, the judge's primitive). Part 1 fires instantly; the swarm runs in the shadow of part-1 being spoken; the parts are also the TTS streaming units (voice-streams-as-brain-streams). The judge is role #0; `ROLE_REGISTRY` already frames it. Mode = the slot budget (attention).

**Territory it WILL touch (so a merge accounts for it) — heavy overlap with §6 hot files:**
- `runtime/suite.py` — generalise `ROLE_REGISTRY`/`resolve_role`; a `_run_swarm(roles,budget)` helper (sibling of the judge call, off the MCP face); the staged-response queue + `chat_parts()`; `THOUGHT_SHAPES` registry; a `brevity_judge`; the injection via `swarm://` addresses through `_chat_context`/`_resolve_context_at`.
- `runtime/scheduler.py` — **currently strictly serial**; the make-or-break is **parallel dispatch** (a `ThreadPoolExecutor` firing the existing blocking transport) + a `Semaphore(32)` with R reserved slots.
- `fabric/transport.py` — add a **`json_schema`** response_format branch (does `json_object` today). `fabric/client.py` — reuse validate/retry. `fabric/vram.py` — wire the `VramGate` (exists, `limit=1`, unwired).
- `nodes/llm.py` — mark **VOLATILE** (else identical role runs collapse to one memo-cached result — `scheduler.py:96`).
- `runtime/bridge.py` — a `cognition.*` SSE emit-contract + endpoints for the cognition view.
- `canvas/app/src/{App.tsx, useAppController.ts}` — a `CognitionView` region, `RoleShape`/cognition-`Edges`, a `cognition.*` branch in `openStream()` (mirrors the `decision.*` branch).
- `ops/services.json` — possibly role/model bindings.

**Pending Tim decisions before the loop starts (the two soul-forks):** (1) the **grain of a "part"** (sentence/beat/paragraph, mode-dependent?); (2) the **first role cast** beyond the judge (memory-recall, screen-reader, relevance-scorer, contradiction-checker, tone-shaper, fact-grounder…). The plan opens with a **proving spike**: generalise the judge into a 2-role registry feeding one injected second part.

---

## 8. Open / pending / needs-Tim
- **4-bit Orpheus audio quality** — by ear (w8a8 cached as higher-quality fallback).
- **Concurrent Cognition** — awaiting Tim's two soul-forks + green-light; then loop-prep triad → build.
- **Live phone conversation** — proven server-side; the on-device mic→speaker round-trip is needs-Tim (push-to-talk now; auto-listen toggle in settings; persona Sable currently engine-overridden to the resident Orpheus — Pip is Orpheus's *dedicated* persona).
- Standing (from memory): ElevenLabs/OpenAI key rotation pending; vhdx compaction pending.

## 9. How to drive / verify
- Card state: `cd ~/company/ops/cli && python3 -c "import registry,gpu;print(gpu.format_state(registry.load()))"`.
- Fit a selection: `curl 'http://127.0.0.1:8770/api/fit?services=chat-4b,tts-orpheus'`.
- Judge: `curl -XPOST http://127.0.0.1:8770/api/voice/finished-thought -d '{"text":"..."}'`.
- Settings/point-mode: open ⚙ settings (closes via ✕ now); `◎ point` toggles indicate.
- Bridge restart (load backend changes): `systemctl --user restart company-bridge.service`.
- **Investigate a voice turn (the new trace):** `grep '"op": "voice.stream"' .data/store/events.jsonl | tail` (per-turn: turn_id·ok·transcript·reply·timings·step-on-error); `grep '"op": "judge"'` (utterance + verdict); `grep '"op": "voice.client"'` (the browser's auto-listen/VAD/recording/playback steps). All in `.data/store/events.jsonl`, seq-ordered, correlate by `turn_id` or timestamp. This is how to debug a reported voice issue with evidence instead of guessing.
