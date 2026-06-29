---
type: handoff
module: root
aliases: ["Session Handoff", "HANDOFF"]
tags: [company, handoff, session, voice, ops]
status: living
---

# HANDOFF.md — live session handoff (2026-06-06, the merge + voice-live session)

> **⏭️ NEWER SESSION:** `HANDOFF-2026-06-07-model-layer-and-cognition.md` supersedes this for the latest work — the model/VRAM resource layer, voice co-residence (4-bit AWQ Orpheus → 64K co-resident brain), persona identity hookup, the settings/indicate fix, and **the Concurrent Cognition loop now in `build-prep/concurrent-cognition/`**. Read it after this one; it lists the exact merge-conflict files + the upcoming loop's territory.

**Read order for a fresh agent:** `AGENTS.md` (the rules) → `MAP.md` (structure + live registry) → `STATE.md` (canonical status) → **this** (what the most recent session did, how the live voice surface works, and where the seams are to add more). This file is the *narrative* of one session's work + an operator's how-to; `STATE.md` stays the canonical fact-of-record. If they ever disagree, `STATE.md` + the tests win — fix this file.

> **For the next session:** everything below is on `main` and pushed (`github.com/Concept-Vi/the-company`). The headline is: the big interactive-surface branch is merged, voice is converged onto one VRAM authority, and the **full live voice circuit works end-to-end** (you can talk to a persona and hear it reply). Operate it via the `company` console + the bridge; extend it at the seams in §8. Add your stuff on `main` (no branches — see AGENTS.md rule 10).

---

## 1. TL;DR — what changed on `main` this session

Four commits + a live standup:

| commit | what |
|---|---|
| `e1063f7` | **Merged `interactive-surface-build` → main** (60 commits: the I/S/F/R/L/X interactive-surface + convergence programme — addressed surface, click-to-indicate, R2 context ranking, code-symbol/dependency/semantic edges, blast-radius, the persisted vector index, the decision→build wire). |
| `d0be0fd` | **Voice VRAM convergence**: `voice/lifecycle.py` now drives the systemd units + budgets/tears-down through the shared `ops/cli/gpu.py` core (one VRAM authority). |
| `44101fb` | **Doc-drift fixes**: AGENTS.md/STATE.md (RHM native-tools, the voice convergence, the operational layer) + the ops-session reply (`voice/FROM-OPS-CLI-SESSION.md`). |
| `<this commit>` | This HANDOFF.md. |

**Live standup (runtime state, not a commit):** the shared bridge (`company-bridge.service`, `:8770`) was restarted onto the merged code; viv's engine pre-warmed; the **full circuit proven by use** (audio → STT → brain → TTS → spoken WAV). One **config fix applied to shared state**: the RHM brain model was `nonexistent-model:cloud` (broken placeholder) → set to `qwen3.5-9b-q8:latest` (a real, running, tool-capable ollama model). See §5.

---

## 2. The merge — what's now on `main`

The `interactive-surface-build` branch was **60 commits ahead of main, local-only (unpushed)** — i.e. at risk. It's now merged + pushed. Only 2 files conflicted (`tests/rhm_action_parse_acceptance.py`, `tests/rhm_completion_acceptance.py`), both resolved toward the **derivation-based** `RHM_VERBS == tuple(RHM_VERB_SPECS)` form (survives the next verb addition) over a hardcoded tuple. MAP.md auto-merged. The hot files (`runtime/suite.py`, `runtime/bridge.py`, `canvas/app/src/App.tsx`, `store/fs_store.py`) were untouched on main, so they took the branch's versions cleanly.

**Merge correctness (proven, not assumed):** 96/100 test suites pass; the 4 non-passing are **service-down loud-skips** (embedder `:8001`, the GPU STT ears, a worktree bridge) — environmental, not breakage. `walkthrough_acceptance.py` passes (34/34) but needs >90s (slow `mcp_face` import). `canvas/app` builds clean (1029 modules). The **L2 autonomous self-build wire is INERT by default** (`COMPANY_WIRE_PERMISSION` defaults to `plan` — it self-modifies nothing unless someone deliberately sets `acceptEdits`).

**Branch hygiene:** `interactive-surface-build`, `night-build`, `overnight-20260605` are now fully merged into main but still exist as **git worktrees** (`~/company-interactive`, `~/company-night`, `~/company-overnight`). I left them — `~/company-overnight` holds uncommitted work (a superseded orpheus monkeypatch + a duplicate of the voice ref clip). Don't `git worktree remove` them without checking; the committed work is all on main.

---

## 3. The voice VRAM convergence — one authority

**The bug it fixed:** voice had TWO launch/budget/teardown mechanisms for the same services. The `company` console drove voice via systemd units; `voice/lifecycle.py` (the UI path, `POST /api/voice/load`) drove them via `subprocess.Popen` with its own `vram()`/budget/`pgrep`-teardown. A UI-loaded voice left its systemd unit `inactive`, so `company`/`gpu.py` (which reads `is-active` for unit services) saw it as **down**, did **not** count its VRAM, and could green-light a second load on top → OOM.

**How it works now** (`voice/lifecycle.py`, commit `d0be0fd`):
- `load(sid)` → `systemd.control(svc,"start")` (the unit, carrying `EnvironmentFile=voice.env`), gated by `gpu.check_fit(reg,[sid])` — which counts **every** GPU service (brain + models + voice), with `gpu.plan_eviction`/`gpu.format_state` for a fail-loud "won't fit" naming what to unload.
- `unload(sid)` → `gpu.teardown(svc)` → cgroup `systemctl stop` — which **reaps vLLM's EngineCore** (orpheus). A plain SIGTERM/SIGKILL on the launcher orphans EngineCore (no OS death-link; it reparents to init and squats ~10 GB; upstream #19849). The cgroup kills the whole unit tree.
- `vram()` → `gpu.read_gpu()`; `status()` uses `systemd.is_active` as the authoritative started-signal + a health probe to tell `warming` (unit active, model loading) from `up` (health answers).
- **Import note (matters if you touch lifecycle):** it does `sys.path.insert(ops/cli)` then `import gpu, systemd, registry`. Collision-safe in the bridge because `runtime.registry` (NodeRegistry) is namespaced — the bare `registry` resolves to `ops/cli/registry.py`. Verified.

**Verified by use** (card 941 MB baseline): `tts-xtts`, `tts-orpheus` (vLLM), and `stt-parakeet` (NeMo) each: UI-path load → `company` SEES + budgets it → synth/transcribe works → cgroup unload → **card fully freed, no orphan**.

**Env-parity holds for free:** every voice unit has `EnvironmentFile=voice.env` and **no** voice service declares a per-service `load.env` override (verified) — so the unit launch loses zero config the old Popen path carried.

---

## 4. The voice stack — what's reliable

All **5 TTS engines** verified reliable by use (load → synth HTTP 200 real WAV → clean teardown), each its own venv + systemd user-unit in `voice/ops/systemd/`:

| persona | engine | port | ~VRAM | note |
|---|---|---|---|---|
| viv | chatterbox | 4124 | 3.8 GB | clones from `COMPANY_VOICE_REF`; emotion-exaggeration knob |
| pip | orpheus | 4125 | 10.5 GB | vLLM-backed; the crash-onion is solved (cached model + FLASH_ATTN + native sampler + persistent event loop) |
| tess | cosyvoice | 4126 | 4.0 GB | |
| wren | xtts | 4127 | 2.5 GB | lightest clone engine |
| sable | qwen3tts | 4128 | 4.6 GB | **Qwen3-VoiceDesign** — designs a voice from a TEXT description, needs NO ref clip (this is the identity source — see §7) |

**3 GPU STT ears** (`parakeet` :2031 ~5 GB, `canary` :2032 ~12 GB, `granite` :2033 ~6.5 GB) are unit-backed + budget-integrated but VRAM-arbitrated (load on demand, not co-resident). `whisper.cpp` (`:2022`, CPU, ~0 VRAM) is the boot-default ear. **Gotcha:** NeMo ear load is **minutes** (parakeet took ~5 min cold) — not a hang; poll patiently.

---

## 5. The LIVE voice circuit — how it works + how to operate it

**The circuit** (`runtime/bridge.py` `POST /api/voice/stream?persona=<id>`):
```
audio bytes in → STT (rhm_config.stt ear) → SUITE.chat (the ONE brain) → TTS (persona's engine) → ndjson stream out
```
The stream emits, in order: `{type:transcript,text,ms}` · `{type:reply,text,ms}` · then per sentence `{type:chunk, idx, text, wav_b64:<base64 WAV>, ms}` · `{type:done, total_ms, spoke, chunks}`. **Gotcha that cost me a false-negative:** the audio events are `type:"chunk"` with field **`wav_b64`** — NOT `type:"audio"`/`"b64"`. It is sentence-chunked + cancellable (it stops synthesising if the client disconnects mid-stream — `select`+`MSG_PEEK`).

**Proven end-to-end, by use, through the restarted `:8770`:** spoken prompt → whisper.cpp transcript ("Good evening. This is the company speaking. Let us begin.") → viv brain reply (in-character) → chatterbox spoken WAV. **Warm latency ≈ 7.7s** (STT 1.1s + brain 3.8s + ~2s/sentence TTS) — conversation-viable. **Cold** ollama-9B load is ~155s (one-time); keep it warm or use a vLLM brain for snappiness (see Gotchas §9).

**Brain.** `rhm_config().model` was the broken placeholder `nonexistent-model:cloud`; I set it to `qwen3.5-9b-q8:latest` (ollama, `base_url=http://localhost:11434/v1`, tool-capable). The faster designated production brain is **`cyankiwi/Qwen3.5-4B-AWQ-4bit`** (`chat-4b`, `vllm-chat.service`, :8000, ~2700 tok/s) — but at its configured `gpu_util:0.8` (~13 GB) it **can't co-reside with a TTS engine** on the 16 GB card. To use it for live voice, drop its `gpu_util` (e.g. `company config chat-4b gpu_util 0.5` → ~8 GB, leaves room for an engine) and repoint `rhm_config.model`/`base_url` at `:8000/v1`.

**The config lab — "change different things" live** (this is the swappable surface; all are config slots, no restart needed):
| change | endpoint / verb |
|---|---|
| switch persona | `POST /api/rhm-config {persona:"tess"}` (or pass `?persona=` per stream call) |
| brain model / base_url | `POST /api/rhm-config {model:..., base_url:...}` |
| STT ear | `POST /api/rhm-config {stt:"parakeet"}` (down ear → fail loud, no silent fallback) |
| TTS engine / voice override | `POST /api/rhm-config {tts_engine:"xtts", tts_voice:...}` |
| presence mode | `POST /api/rhm-config {mode:"listening"}` |
| load / unload an ear or engine (real VRAM) | `POST /api/voice/load {service:"tts-chatterbox"}` · `POST /api/voice/unload {...}` |
| role bindings / knobs | `ROLE_REGISTRY` / `MODEL_KNOBS` via `set_rhm_config` `roles` |
| read what's available | `GET /api/personas · /api/voice/services · /api/rhm-config · /api/roles · /api/knobs · /api/models` |
The RHM can also operate its OWN config by voice via the verbs `configure` / `load_voice` / `unload_voice` (all governance class `configure` = AUTO, reversible).

---

## 6. How to operate the system

- **The `company` console** (`ops/cli/`) is the control surface: `company up/down/status/gpu/swap/telemetry`. The **VRAM resource-manager** (`ops/cli/gpu.py`) is the single budget/teardown authority (shared with `voice/lifecycle.py`). `company up <svc>` REFUSES an over-capacity start (shows what's holding the card + what to evict; `--force` overrides). Add a service = add an entry to `ops/services.json` (+ a unit). See `ops/AGENTS.md`.
- **The bridge** (`runtime/bridge.py`, `company-bridge.service`, `:8770`) serves the canvas + `/api`. Restart onto new code: `systemctl --user restart company-bridge.service`. **It is a SHARED surface** — a restart blinks any session on the canvas; coordinate.
- **The canvas** is served to the **phone** via Tailscale: `https://workstation001.tail777bc2.ts.net` → vite `:5173` (serves the live frontend from `canvas/app/src`, hot-reloaded — so the frontend is always current) → proxies `/api` → `:8770`. So only `:8770` (backend) needs restarting for new backend code; vite picks up frontend changes live.
- **GPU discipline (CRITICAL — multiple sessions share one 16 GB card):** check `company gpu` / `nvidia-smi` before any load; never blind-kill GPU pids (use the cgroup teardown); the budget gate is your friend — let it refuse rather than force. ollama models idle-unload (~5 min); a vLLM unit holds its VRAM until stopped.
- **The local brain (FP8) — how to use it: `docs/brain-loadouts.md`.** Everyday brain = `company up @interaction-fp8` (Qwen3.5-4B-FP8 :8001, thinking+tools, 4×16K context via fp8-KV, recall+voice co-resident). The better brain = `company up @quality-9b --evict` (Qwen3.5-9B-FP8 solo). Thinking is per-turn (`POST /api/rhm-config {think:…}`); reasoning surfaces in `message.reasoning`. Serve flags are resolver-GENERATED from `runtime/capabilities/` + the service's `family` — tune via `company config` + `company restart`, never a hardcoded flag. (WF2 capability-resolution build, 2026-06-29.)

---

## 7. The Company voice identity (a Tim decision, open)

`COMPANY_VOICE_REF` = `voice/ref/company_voice_ref.wav` (committed on main, 24 kHz mono 4.24s, says *"Good evening. This is the company speaking. Let us begin."*). **Provenance investigated:** it is **AI-synthesised by qwen3tts (Qwen3-VoiceDesign), not a real recording** — see `voice/ops/make_reference_clip.sh`. This is a *deliberate* identity design: qwen3tts designs the voice from a written brief ("a refined, educated Australian woman, early 40s, warm mid-low pitch, dry understated wit" — `personas.VOICE_BASE`), and the three clone engines (chatterbox/xtts/cosyvoice) clone **that** → "same woman underneath, five souls on top." It's reproducible/tweakable: re-run `make_reference_clip.sh` (with qwen3tts up on :4128) to regenerate with a tweaked description/text.

**Open decisions (Tim's, not the next session's to settle):** (a) does the Company settle on ONE voice or stay a CAST of five faces (one entity, many surfaces)? (b) is *this* designed rendering the canonical identity? Both are aesthetic/identity calls — surface them, don't decide them.

---

## 8. Seams to extend — where the next session adds "their stuff"

- **A new voice engine or ear** → drop a `voice/engines/<name>.py` or `voice/ears/<name>.py` mirroring the shared `_service.py`/`_stt_service.py` contract (`POST` text/audio → wav/`{text}`; `GET /voices` or `/`), add its `ops/services.json` entry (`group:voice`, a `load` block, a `manage` unit) + a unit in `voice/ops/systemd/`. `lifecycle.py` + the config lab pick it up with **no code edit** (registry-is-truth).
- **A new model / provider for the brain** → `fabric/config.py` (repoint/register) + a `config` block + a `vllm-*.service` if it's a vLLM model; tune live with `company config <svc> <k> <v>`.
- **A new RHM action verb** → add a `VerbSpec` to `runtime/suite.py` `RHM_VERB_SPECS` (RHM_VERBS/_DESC/_CLASS + the native-tool param-schema all derive from it) + a case in `_dispatch_rhm_action`; whitelist-gated. (The old `_parse_rhm_action` text parser is RETIRED — the RHM acts via **native tool-calling**: `_rhm_tools` offers the registry-derived tools, `_json_obj_to_action` normalises the call.)
- **The listening-mode UI / mobile voice** → `canvas/app/src/App.tsx` is the canvas. The browser mic capture + speaker playback + the listening-mode UI is the FRONT-END half I could NOT verify headlessly — that's the next real lane (and Tim's hardware to confirm). The backend circuit (§5) is proven and waiting for it.
- **The decision→build wire** (live but inert) → arming it (`COMPANY_WIRE_PERMISSION=acceptEdits`) is reserved to a supervised lead, never a worker. The S8 by-use + adversarial run against a live system is still owed.
- **Semantic retrieval / the vector index** → `store/vector_index.py` + the `embed`/`retrieve` nodes; needs the embedder up on `:8001` (BGE-M3). The X11/X12 corpus edges were populated live once; re-run against `:8001`-up to refresh.

Always: **update the self-description as part of the change** (`AGENTS.md`/`MAP.md`/`STATE.md` + the module `AGENTS.md`; `tests/drift_acceptance.py` must pass) and **prove by USE, not code-reading.**

---

## 9. Gotchas (things that bit me this session — save yourself the rediscovery)

- **NeMo STT ear load is MINUTES** (parakeet ~5 min cold), CPU-heavy before GPU placement — not a hang. Poll patiently; watch for the VRAM jump as the model places.
- **ollama cold-load is ~155s** for the 9B; warm reply ~3.8s. It idle-unloads (~5 min). For live conversation, keep it warm or use a vLLM brain (faster + holds resident).
- **`/api/voice/stream` audio events are `type:"chunk"` with `wav_b64`** — not `"audio"`/`"b64"`. Parsing the wrong field reads as "no audio" when it's actually streaming.
- **The 4B-AWQ at `gpu_util:0.8` (~13 GB) cannot co-reside with a TTS engine** on 16 GB. Lower its util to co-reside.
- **`/api/voice/stream` does NOT auto-boot the engine** (only `/api/voice/turn?boot=1` does). Pre-load the persona's engine via `/api/voice/load` first.
- **`audioop` is gone in Python 3.13+** (the bridge runs `.venv`/3.14) — compute WAV RMS/amplitude manually via `wave`+`array`.
- **`pkill`/detached spawns exit 144 in this shell** — noise, not failure (it self-matches). Use `[b]ridge.py` style patterns or just ignore the code.
- **Heredoc Python under a vLLM-spawning service** can hit "safe importing of main module" — guard under `if __name__=="__main__"`.
- **tldraw `persistenceKey` + shape-schema changes white-screen old browsers.** tldraw persists the whole store to IndexedDB under `App.tsx`'s `persistenceKey` and VALIDATES every record on load. Changing the NodeShape props (the merge added `error: T.string`) without bumping the key crashes any browser with an older snapshot: `ValidationError: At shape(type=node).props.error: Expected string, got undefined` in `TldrawEditorBeforeLoading` → white-screen (vite shows it as a full-screen error overlay). **Fix = bump the key** (now `company-canvas-v3`); the persisted store is low-value (nodes/positions are backend-authoritative — only the camera resets). **Every NodeShape-props change must bump the key OR add a tldraw migration.** Durable hardening (drop persistence / add migrations) is a flagged follow-up. (From Tim's phone 2026-06-06; reproduced by injecting an `error`-less node record into the v2 IndexedDB.)
- **`GET /api/models?kind=embed` → 400 when the embedder (`:8001`/`:8004`) is down** (`Connection refused`) — the config-lab's embed-model picker can't populate. Cosmetic; does NOT affect canvas or voice. Bring the embedder up, or make the frontend degrade quietly (flagged).
- The shared `:8770` bridge had been running **6 hours on stale pre-merge code** — restarting a long-lived shared bridge is how new code reaches the live surface. Check the process start time vs your commits if "the code doesn't seem to have my change."

---

## 10. Honest status — verified vs not

**Verified by use this session:** the merge (tests + build) · the VRAM convergence (xtts/orpheus/parakeet) · the full live voice circuit (STT→brain→TTS→spoken WAV through `:8770`) · the config-lab endpoints respond.

**NOT verified (the real boundary):** the **browser mic-in / speaker-out + listening-mode UI on the phone** — that's hardware I can't drive headlessly + Tim's to confirm. The **voice trial flow** (recording/debrief) is code-complete but not run by use. **Mobile voice on iOS Safari/PWA** (getUserMedia needs the HTTPS that Tailscale provides; user-gesture to start mic) is unproven from this side.

**Pointers:** canonical state = `STATE.md`; rules = `AGENTS.md`; structure + live registry = `MAP.md`; the ops/CLI cross-session thread = `voice/FROM-OPS-CLI-SESSION.md`; voice constitution = `voice/AGENTS.md`; ops constitution = `ops/AGENTS.md`.

— the merge + voice-live session, 2026-06-06.
