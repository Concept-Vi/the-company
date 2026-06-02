---
type: state
module: root
aliases: ["Company State", "STATE"]
tags: [company, state, status]
governs: []
relates-to: ["[[Company — read first]]", "[[Company Map]]"]
status: living
---

# STATE.md — where the build is (read after AGENTS.md + MAP.md)

The current status of **company** (the Vi composition suite), self-contained so a fresh AI can enter the repo, read [[Company — read first]] (the rules) + [[Company Map]] (the structure + the live registry) + this (the status), and act correctly without re-deriving anything or tripping a boundary. Maintained by integration — keep it *current and true*, not append-only. As of 2026-06-01.

> [!important] How "done" is proven here
> **`tests/*.py` ARE the convergence record** — each acceptance suite proves a capability by execution. Run them all: `for t in tests/*.py; do ./.venv/bin/python "$t"; done`. Beyond tests, the standard is **prove by USE**: operate the live system (browser canvas + the bridge API), don't just assert. Never claim something works without fresh evidence.

### Acceptance suites (the convergence record)
<!--SUITES:START--> (auto-maintained by Suite.refresh_self_description — do not hand-edit)
- 35 acceptance suites: agency_acceptance, compose_acceptance, configs_acceptance, consult_acceptance, copresence_acceptance, drift_acceptance, e1_acceptance, e2_review_fixes, e2_runtime, e3_fabric, e3_integration, e4_registry, e5_suite, e6_governance, events_acceptance, extension_acceptance, first_purpose, hardening_acceptance, inbox_acceptance, layers_acceptance, mcp_use, modes_acceptance, panel_acceptance, polr_acceptance, portal_acceptance, react_acceptance, rhm_acceptance, rhm_action_acceptance, self_growth, selfmod_acceptance, show_acceptance, trajectory_acceptance, twin_acceptance, volatile_acceptance, walking_skeleton
<!--SUITES:END-->

> [!warning] Keeping this file current is part of every change
> When you add/change a capability you MUST update the self-description: the factual blocks here + in `MAP.md` regenerate via `Suite.refresh_self_description()` (run on every apply); the **prose** above (What is built · What CANNOT be done · gotchas) you update **by integration** — change what the new piece makes untrue, keep the rest. `tests/drift_acceptance.py` **fails loud** if a registered capability or an acceptance suite isn't reflected here or in the map.

## What this is (one paragraph)
A reactive, content-addressed composition engine (nodes wired into graphs; a node fires when its input *addresses* resolve; memo gate = "re-run only what changed"). Two faces over one shared brain (`runtime/suite.py` — the `Suite`): a **UI bridge** (`runtime/bridge.py`, the React+tldraw canvas in `canvas/app/`) and an **MCP agent face** (`mcp_face/server.py`). Models come through `fabric/` (OpenAI-compatible; ollama/LiteLLM; **no Gemini**). The first real use is the system on **its own codebase**. It now also has a **right-hand-man (RHM)** — a conversational organ — and can **modify itself** (governed).

## What is BUILT and proven (capability → the test that proves it)
- **Engine** — reactive scheduler + memo gate + compile + content-addressed store + provenance + the contracts C1–C8 as Pydantic. `tests/walking_skeleton.py`, `e1_acceptance.py`, `e2_runtime.py`, `e2_review_fixes.py`.
- **Fabric / AI nodes** — guarded model calls (empty→fail-loud, JSON-repair, validate, retry). `e3_fabric.py`, `e3_integration.py` (live model call).
- **Registries + types** — node-types DISCOVERED from files; queryable type-graph; object_info. `e4_registry.py`.
- **Two faces, one brain + governance** — generic verbs; AUTO/SURFACE/CONFIRM; operator-only approval (agent can't self-approve). `e5_suite.py`, `e6_governance.py`.
- **First purpose** — answers about its own code; grows its own capability, governed. `first_purpose.py`, `self_growth.py`, `mcp_use.py`.
- **Interface (canvas)** — on-canvas palette/wire/delete, run, portals (live transclusion), provenance layers, now-view, event log, presence dial. `compose_acceptance.py`, `portal_acceptance.py`, `layers_acceptance.py`, `events_acceptance.py`.
- **The RHM** — grounded conversation that **abstains rather than confabulate**; acts only through a verb whitelist (`run·propose·build·consult·show·panel·extend`; apply/delete/file-write unreachable); 8 modes-as-nodes (off disables); model/provider/persona configurable; co-presence (reads the operator's selection); symmetric agency + NL→graph; COA decision-compiler + 3-lane inbox; the twin reasons from the explicit model-of-Tim + grades turns gold/working; trajectory capture; knows-its-own-design (`consult`); attention-direction (`show`). `rhm_acceptance.py`, `rhm_action_acceptance.py`, `modes_acceptance.py`, `configs_acceptance.py`, `copresence_acceptance.py`, `agency_acceptance.py`, `inbox_acceptance.py`, `twin_acceptance.py`, `trajectory_acceptance.py`, `consult_acceptance.py`, `show_acceptance.py`, `react_acceptance.py`.
- **Self-modification (update the app through its interface)** — declarative **panels** (`panel`; the 'others' tier) and arbitrary-code **extensions** (`extend`; operator-only) — both governed, additive, **build-gated**, git-committed, revertible. `panel_acceptance.py`, `selfmod_acceptance.py`, `extension_acceptance.py`.
- **Path-of-least-resistance** — registry is the source of truth (no fabrication); missing info → **ask, don't fabricate**; the map self-maintains + a drift-check fails loud. `polr_acceptance.py`, `drift_acceptance.py`.
- **Two-way voice** (`voice/`) — **TTS** local (Kokoro, CPU, proven: text→valid WAV through the bridge); **STT** a swappable provider (AssemblyAI cloud by default, key in `.secrets`; local Whisper available). Bridge `/api/stt · /api/tts · /api/voice`; canvas `listening`-mode mic→STT→chat→TTS→speaker. Endpoints verifiable by round-trip; the live mic/speaker loop is the operator's to confirm.

## What CANNOT be done yet (boundaries — do not assume these)
- **Voice — the live hardware loop** is the operator's to confirm. The STT/TTS *endpoints* are built + verifiable headlessly (round-trip), but actual **mic capture + speaker playback** in the browser can only be confirmed by the operator. STT default (AssemblyAI) is **cloud** — audio leaves the machine; flip `COMPANY_STT` to local for fully-on-machine (local Whisper not yet installed in `.voice-venv`). Needs `ASSEMBLYAI_API_KEY` in `.secrets`.
- **The twin's predictive strength** — COLD-START. It reasons from the *explicit* model-of-Tim (`foundation/system/principles.md`) and abstains; it does NOT yet *predict Tim's judgement* — that needs corpus ingestion (D8), not built. The autonomy ratchet / attention-budgeting depend on it.
- **Retrieval** — none. The `codebase`/`consult` node reads the whole repo into context, capped at 400k chars and **fails loud past it** (no silent truncation). Past that size, retrieval (embed+retrieve) is needed — not built.
- **Arbitrary self-mod is bounded** — extensions are additive `.tsx` in `src/extensions/` (may import only `react`), build-gated by an **AST checker** (`syntax-gate.cjs`: rejects non-`react` import/export specifiers, dynamic `import()`, `require()`, external-URL literals — replaced the old regex import-allowlist, which the red-team bypassed; still NOT a full type-check, `tsc` is too slow on tldraw). Each is **lazy-loaded inside an error boundary**, so a bad extension is one dead panel, not a white screen. In-place rewrites of `App.tsx`/engine internals through the brain are deliberately out (would risk the build). **Operator-approval is governance, NOT a safety guarantee for generated code** — the floors are the build-gate + error boundary + git-revert + single-user machine.
- **Tauri desktop wrap** — deferred at the operator's direction; the browser canvas is the surface.

## How to run it
- Python runtime venv: `~/company/.venv` (3.14). Bridge: `./.venv/bin/python runtime/bridge.py 8770` (serves the canvas + `/api`). Canvas dev: `cd canvas/app && npm run dev` (Vite :5173, proxies `/api` → :8770). Fabric proxy (optional): `.litellm-venv` on :4100; default fabric is ollama direct (`:11434/v1`).
- The shared store lives at `~/company/.data/store` (ext4 — never `/mnt/c`).

## The laws that bind you (see AGENTS.md for the full list)
Build against the contracts · schema-additive never schema-breaking · **fail loud** (no silent fallbacks) · ext4 storage · **no Gemini** · stage-gated (CONFIRM the irreversible) · **author from the registry, never invent — if it isn't registered, ASK** · self-modification is additive + git-reversible. These bind external agents AND the system's own self-coding brain.

## Gotchas (save yourself the rediscovery)
- After adding a capability, the factual blocks of `MAP.md` + `STATE.md` auto-update (`Suite.refresh_self_description`, run on every apply); `tests/drift_acceptance.py` fails loud if either falls behind. Update the **prose** by integration.
- `pkill`/detached spawns can exit 144 in this shell — noise, not failure; use background runs for servers.
- The extension build-gate is `canvas/app/syntax-gate.cjs` (fast `ts.transpileModule`). First call loads `typescript.js` cold (slow once); warm ~200ms.
- Specs/design notes live in the operator's vault (Windows-side, may be unreachable from an agent) — this repo is self-describing on purpose; trust `AGENTS.md`/`MAP.md`/`STATE.md` + the tests.

## Where to go next
Voice (the agreed next), then the corpus/D8 ingestion (turns the twin's mechanism into an actual learned model of Tim). Everything is pushed to `github.com/Concept-Vi/the-company`.
