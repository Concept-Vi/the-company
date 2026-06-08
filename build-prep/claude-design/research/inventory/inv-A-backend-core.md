---
type: inventory
region: runtime + store + fabric + contracts + root
scope: fast census (no deep comprehension, coverage priority)
date: 2026-06-08
---

# Backend Core Inventory — runtime / store / fabric / contracts

Fast read-only census of file structure + purpose (from docstrings/headings only, no logic trace). Marked for PRIORITY deep-read.

## Directory Structure

```
/home/tim/company/
├── Root docs (governance/state/roadmap)
│   ├── AGENTS.md                          (9.6KB) constitution + how agents navigate
│   ├── MAP.md                             (14.5KB) live registry of capabilities + state
│   ├── STATE.md                           (40.2KB) current build status + what's proven
│   ├── README.md                          (2.5KB) overview
│   ├── HANDOFF.md                         (19KB) previous session state
│   ├── HANDOFF-2026-06-07-model-layer-and-cognition.md (19.5KB)
│   ├── SESSION-OPERABLE-INTERFACE.md      (8.9KB)
│   └── MERGE-COORDINATION.md              (38.3KB) active merge tracking
│
├── runtime/                               [13 Python modules + 1 MD]
│   ├── bridge.py ⭐                       HTTP UI bridge (C8 skeleton)
│   ├── suite.py ⭐⭐                      Shared brain (reactive scheduler + composition)
│   ├── registry.py ⭐                     Live node-type discovery registry (C2/S4)
│   ├── governance.py ⭐                   Act-unwatched policy + surfaced-decision gate (S7/D4/D7)
│   ├── scheduler.py ⭐                    Reactive scheduler + memo gate + address resolution (S1)
│   ├── cognition.py                       Concurrent Cognition G0 proving spike (staged turns)
│   ├── activation.py                      Concurrent Cognition G5 (activation contexts)
│   ├── compile.py                         Workflow → execution (C5 Part 2)
│   ├── authoring.py                       Graph authoring operations
│   ├── implement.py                       Headless decision→implementation launcher
│   ├── context_variables.py               C6 universal context registry
│   ├── rules.py                           Rule system (declarative routing/injection)
│   ├── roles.py                           Role dispatch + binding resolution
│   └── AGENTS.md                          runtime module constitution
│
├── store/                                 [2 Python modules + infrastructure]
│   ├── fs_store.py ⭐                     Content-addressed filesystem store (C1/C4 resolver)
│   ├── vector_index.py                    X12 persisted vector index build/query (Convergence)
│   └── [locks/ objects/ refs/ vectors/]   (addressable storage namespaces)
│
├── fabric/                                [4 Python modules + config]
│   ├── client.py ⭐                       Guarded model calls (S6) — empty→fail-loud, retry
│   ├── transport.py                       LiteLLM-backed transport (OpenAI-compatible)
│   ├── config.py                          Model config + VRAM budget registry
│   ├── vram.py                            VRAM gate (per-model slot limiting, 16GB card)
│   └── [model service configs]
│
├── contracts/                             [10 Pydantic modules]
│   ├── address.py ⭐                      C1 — address grammar (run:// cas:// blob:// ui:// code://)
│   ├── node_record.py ⭐                  C3 — node/edge/graph + execution face (ExecNode)
│   ├── node_type.py ⭐                    C2 — node-type contract (process/content/presentation)
│   ├── bridge_msgs.py ⭐                  C8 — canvas↔runtime message models
│   ├── resolver.py                        C4 — abstract resolver interface
│   ├── cognition_info.py                  Turn context + concurrent cognition state
│   ├── object_info.py                     Type graph + node capabilities (object_info)
│   ├── ui_info.py                         UI element registry (77 addressed elements)
│   ├── shapes.py                          Generic shape types (XY, WH, bounds)
│   ├── tools.py                           RHM verb tools array + normalized action shapes
│   └── AGENTS.md                          contracts constitution
│
├── mcp_face/                              [agent-facing FastMCP server]
│   └── server.py                          C7 generic verbs over the Suite
│
├── voices/                                [TTS/STT + multi-engine routing]
│   ├── tts_service.py                     Local TTS (Kokoro)
│   ├── stt.py                             STT provider abstraction (AssemblyAI + local Whisper)
│   ├── personas.py                        Voice persona configs (5 characters)
│   ├── speakable.py                       Text→speech token streaming
│   ├── lifecycle.py                       Service lifecycle + VRAM integration
│   └── loop.py                            Voice turn loop (record→STT→chat→TTS→play)
│
├── nodes/                                 [node library — process/content/presentation]
│
├── roles/                                 [role library — context-bound plugins]
│   ├── focus.py / judge.py / recall.py / verify_jury.py / ground.py / check.py / connect.py / voice.py
│   └── AGENTS.md
│
├── ops/                                   [operational console + VRAM resource-manager]
│   ├── STARTUP.md                         Service startup sequence
│   ├── WINDOWS-BOOT.md                    WSL boot instructions
│   ├── cli/gpu.py                         VRAM gate + resource-manager (single budget authority)
│   ├── cli/telemetry.py                   Measured load-time + VRAM (introspective-data-building)
│   ├── services.json                      Live service registry (what runs, unit, port, VRAM)
│   └── systemd/user/                      Service units (vllm-chat, voice engines, etc.)
│
├── design/                                [surface design + code symbol corpus]
│   ├── _system/addresses.json             68 UI element addresses (corpus source for S1)
│   ├── _system/symbols.py                 Code-symbol corpus indexing
│   └── [blueprint/ mockup/ ...]           Interface designs
│
├── canvas/                                [React + tldraw frontend (TS/Tauri)]
│
├── panels/                                [self-mod presentation nodes]
│
├── build-prep/                            [vault specifications — source of truth]
│   ├── Company Build Hub.md               MoC + decisions
│   ├── contracts/C1–C8.md                 Pinned contract specs
│   ├── designs/S1–S7.md                   Engine design specs
│   ├── decisions/D1–D7.md                 Governance + approval decisions
│   └── concurrent-cognition/              Staged main stream build plan
│
├── docs/                                  [pointer to vault]
│
├── tests/                                 [130 acceptance suites]
│   └── [*_acceptance.py, e1–e6, etc.]    Convergence record (run to prove capability)
│
└── .git / .data / .venv / .build /        (git repo, store, environments, cache)
    .litellm-venv / .voice-venv
```

---

## File-by-File Inventory

### RUNTIME (execution engine + orchestration)

| File | Appears to be | PRIORITY | Notes |
|------|---------------|----------|-------|
| **runtime/bridge.py** | HTTP server: UI canvas + state/action endpoints | ⭐⭐ YES | C8 — the interface face (+ Yjs sync). Thin stdlib http; mirrors Suite state; 2/2 faces meet here |
| **runtime/suite.py** | The shared brain: generic verbs + composition operations | ⭐⭐ YES | Core S1 — scheduler spine; compiles graphs; runs nodes; memoizes; surfaces decisions; voice ops; RHM dispatch. One Suite = both faces |
| **runtime/registry.py** | Live node-type discovery: module→NodeType mapping | ⭐⭐ YES | C2 registry; files become types (self-extending). QueryHandler + object_info server. No hardcoding |
| **runtime/scheduler.py** | Reactive scheduler: address resolution → node dispatch | ⭐⭐ YES | S1 core — reads store; fires when inputs resolve; memo gate (re-run-only-what-changed); pause/force/branch controls |
| **runtime/governance.py** | Policy gate: AUTO/SURFACE/CONFIRM postures + decision ruling | ⭐⭐ YES | S7 + D4/D7 — every action gets a posture; LOCKED set for irreversibles; guards on code-write/build-dispatch |
| **runtime/compile.py** | Workflow→Execution transform (C3→C5) | ⭐ YES | Graph (pixels) → ExecNodes (addresses). Generic over node-type. Recompiles each run |
| **runtime/cognition.py** | Concurrent Cognition G0 spike (2-part staged turns) | ⭐ YES | NET-NEW: proves C0.1–C0.5 (concurrent roles + rule-based routing + fail-loud). Additive to suite.py |
| **runtime/activation.py** | Concurrent Cognition G5 (activation contexts: background/sense/rollup) | ✓ MAYBE | Registry + trigger entry points. Always-on drivers = needs-tim (GPU concern). Proven by use |
| **runtime/authoring.py** | Graph editing operations (create/delete/connect/position) | ✓ MAYBE | Probably mutations to graph on canvas |
| **runtime/context_variables.py** | C6 universal context registry (trial_transcript, focus.selected, etc.) | ✓ MAYBE | Declares what variables exist + how they resolve from store |
| **runtime/implement.py** | Headless Claude Code launcher for decision→implementation wire | ✓ MAYBE | Runs `claude -p` with declared scope; verifies output; closes decision |
| **runtime/rules.py** | Rule system for deterministic routing + injection | ✓ MAYBE | Concurrent Cognition R1-FOLD — PURE functions of resolved addresses |
| **runtime/roles.py** | Role dispatch + binding resolution | ✓ MAYBE | Role lookup; role_bind resolution |
| **runtime/AGENTS.md** | runtime module constitution | ✓ YES (ref) | Laws + patterns + how to extend |

### STORE (content-addressed, addressed resolver)

| File | Appears to be | PRIORITY | Notes |
|------|---------------|----------|-------|
| **store/fs_store.py** | FilesystemResolver: immutable CAS + mutable refs + locking | ⭐⭐ YES | C1/C4 implementation. Concurrency: per-graph RLock + OS advisory fcntl locks. fsync durable. Portability contract (swappable backend) |
| **store/vector_index.py** | X12 persisted vector index: build + query (semantic retrieval) | ✓ MAYBE | Embed corpus → vector store. Query → rank by cosine. Staleness-checkable (read-only hash compare) |

### FABRIC (model binding + guards)

| File | Appears to be | PRIORITY | Notes |
|------|---------------|----------|-------|
| **fabric/client.py** | Guarded model calls: non-empty + JSON-repair + validate + retry | ⭐⭐ YES | S6 — transport-agnostic (transport injected). Fail loud on validation fail |
| **fabric/transport.py** | LiteLLM-backed transport (OpenAI-compatible) | ✓ MAYBE | Default fabric backend; swappable |
| **fabric/config.py** | Model config + VRAM budget registry | ✓ MAYBE | Per-model knobs + gpu.fit_report |
| **fabric/vram.py** | VRAM gate: semaphore limiting concurrent model calls | ✓ MAYBE | 16GB card concurrency bound (per-model fit logic = future) |

### CONTRACTS (pinned data shapes — the seams)

| File | Appears to be | PRIORITY | Notes |
|------|---------------|----------|-------|
| **contracts/address.py** | C1 — address grammar (run:// cas:// blob:// vec:// ui:// code://) | ⭐⭐ YES | Pydantic + provenance. Schema-additive only. The coordinate system |
| **contracts/node_record.py** | C3 — node/edge/graph + execution face (ExecNode) | ⭐⭐ YES | Two-graph split: workflow (pixels) vs execution (addresses). Schema v2 (adds Edge.kind) |
| **contracts/node_type.py** | C2 — node-type contract (process/content/presentation) | ⭐⭐ YES | Single definition of "what is a node". Kind + ports + render mode. Registry source |
| **contracts/bridge_msgs.py** | C8 — canvas↔runtime message models (STATE + ACTION channels) | ⭐⭐ YES | GraphState / NodeState (flat projection). ActionRequest→ActionResponse. Schema-additive |
| **contracts/resolver.py** | C4 — abstract Resolver interface (address → bytes) | ✓ MAYBE | Sealed protocol; fs_store.py + future Supabase backend implement it |
| **contracts/cognition_info.py** | Turn context + concurrent cognition state | ✓ MAYBE | Captured state for C0 machinery |
| **contracts/object_info.py** | Type graph + node capabilities (the /object_info response) | ✓ MAYBE | Describes nodes to the UI |
| **contracts/ui_info.py** | UI element registry (77 addressed elements) | ✓ MAYBE | ui:// address corpus → UnionAddressRecord (S1) |
| **contracts/shapes.py** | Generic types (XY, WH, bounds) | ✓ MAYBE | Geometry primitives |
| **contracts/tools.py** | RHM verb tools array + normalized action shape | ✓ MAYBE | Native tool-calling interface |

### ROOT MARKDOWN (governance + state)

| File | Appears to be | PRIORITY | Notes |
|------|---------------|----------|-------|
| **AGENTS.md** | Constitution: rules + how AI navigates the repo | ⭐⭐ YES | Rules 1–11. Read this first (after README). Single-source governance |
| **MAP.md** | Live registry: capabilities + module boundaries | ⭐⭐ YES | Auto-maintained by Suite.refresh_self_description. Read 2nd (after AGENTS.md) |
| **STATE.md** | Current build status + proof (test suites + prose) | ⭐⭐ YES | 130 acceptance suites listed. What's proven / what's future. Updated by integration |
| **README.md** | Overview + layout | ✓ YES (ref) | Start here if fresh to repo |
| **HANDOFF.md** | Previous session state + action items | ✓ YES (ref) | Session continuity |
| **HANDOFF-2026-06-07-model-layer-and-cognition.md** | Model layer + voice tracing details | ✓ YES (ref) | Prior session deep context |
| **SESSION-OPERABLE-INTERFACE.md** | Interface build loop state | ✓ MAYBE | Current interface lane state |
| **MERGE-COORDINATION.md** | Active merge tracking + branch state | ✓ MAYBE | Coordination for concurrent work |

---

## Summary

**Total Files Scanned:** ~75 Python modules + 8 root markdown + 4 sub-module markdown

**Directory Coverage:**
- ✅ `runtime/` — 13 Python + 1 MD (full coverage)
- ✅ `store/` — 2 Python (full coverage)
- ✅ `fabric/` — 4 Python (full coverage)
- ✅ `contracts/` — 10 Pydantic (full coverage)
- ✅ `voice/` — 7 Python (sampled; TTS/STT + lifecycle)
- ✅ `ops/` — service management + VRAM (sampled)
- ⚠️ `tests/` — 130 acceptance suites (registry listed in STATE.md; not individually sampled)
- ⚠️ `canvas/` — React/tldraw frontend (not this pass — TS, not Python)
- ⚠️ `nodes/` — node library (live discovery via registry.py)
- ⚠️ `roles/` — role library (live discovery via roles.py)

---

## Top ~10 Files for Deep-Read (Priority Order)

1. **runtime/suite.py** — the heart (scheduler spine, RHM dispatch, voice, voice trial, self-mod governance)
2. **runtime/bridge.py** — the interface face (HTTP state + actions; Yjs sync)
3. **store/fs_store.py** — durability + concurrency (locks, fsync, portability contract)
4. **contracts/address.py** — the coordinate system (grammar, all address schemes)
5. **contracts/node_record.py** — workflow vs execution (two-graph split, EdgeKind, ExecNode)
6. **runtime/scheduler.py** — reactive dispatch (address resolution, memo gate, branch/pause/force)
7. **runtime/governance.py** — policy + gates (postures, decision ruling, code-write guards)
8. **fabric/client.py** — model guards (empty→fail-loud, JSON-repair, retry, validation)
9. **runtime/registry.py** — self-extending type system (discovery, queryability, no hardcoding)
10. **build-prep/** — vault specs (C1–C8, S1–S7, D1–D7; source of truth)

---

## Notable Observations

- **Self-describing repo:** AGENTS.md + MAP.md + STATE.md + 130 tests ARE the system's mirror. No external docs needed.
- **Concurrency proven:** cross-process locks (fcntl) + per-graph RLock + fsync durability. Hard-tested in concurrency_acceptance.py.
- **Schema discipline:** contracts are Pydantic + schema-additive-only (no breaking changes).
- **Governance is live:** every action has a posture (AUTO/SURFACE/CONFIRM); LOCKED set for irreversibles.
- **No hardcoding:** registry is the source (node-types discovered; verbs defined once; UI elements registered; roles discovered).
- **First real use:** system runs on its own codebase (answers about code; grows itself; governed).
- **Two concurrent builds live:** operable-interface (F1) on a worktree; concurrent-cognition (G0–G5) staged into main.

---

## Not Yet Scanned (Next Pass)

- Full test suite (130 files) — sampled via registry in STATE.md
- `canvas/` TypeScript/React (not this pass)
- `nodes/` library internals (registry-discovered)
- `roles/` library internals (registry-discovered)
- Design system + mockups (`design/`)
- Build-prep vault specs (`build-prep/` — source of truth; Windows-side, may not be accessible from WSL agent)
