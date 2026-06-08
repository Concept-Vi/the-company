---
type: deep-read
layer: "⑤ conventions-laws-operational"
subject: "self-description mechanism + operational structure + the laws"
source-files:
  - /home/tim/company/AGENTS.md
  - /home/tim/company/MAP.md
  - /home/tim/company/STATE.md
  - /home/tim/company/runtime/AGENTS.md
  - /home/tim/company/contracts/AGENTS.md
  - /home/tim/company/canvas/AGENTS.md
  - /home/tim/company/store/AGENTS.md
  - /home/tim/company/tests/AGENTS.md
  - /home/tim/company/ops/AGENTS.md
  - /home/tim/company/nodes/AGENTS.md
  - /home/tim/company/roles/AGENTS.md
  - /home/tim/company/ops/services.json
  - /home/tim/company/ops/cli/gpu.py
  - /home/tim/company/ops/cli/capabilities.py
  - /home/tim/company/claude-design/research/inventory/inv-D-selfdesc-tests-ops.md
produced: 2026-06-08
status: BUILT (observed from source) · where noted PARTIAL or DESIGNED
relates-to: ["[[Company — read first]]", "[[Company Map]]", "[[Company State]]"]
---

# selfdesc-ops.md — Layer ⑤: Conventions, Laws, Operational Structure, Self-Description

The conventions/laws layer and the operational structure layer for the application-structure pack. Read-only deep comprehension pass. Every claim below is **observed** from primary source files; **inferred** items are labeled.


---


## I. The Laws — Consolidated

Source: `/home/tim/company/AGENTS.md` (root constitution). Status: **BUILT** (the rules are enforced by code + drift checks, not just stated).

Ten rules govern every agent working in this repo. They are non-negotiable and bind both external agents and the system's own self-coding brain equally.

### Rule 1 — Build against the contracts (BUILT)
The contracts (`contracts/`, C1–C8) are the spine. They define the shapes (addresses, node-types, records, the resolver protocol, compile/object_info, context-variables, MCP tools, the bridge). No module may define its own parallel version of a contract shape. Code implements; it does not redefine. A contract change requires CONFIRM (widest blast radius of any act). Path: `contracts/*.py`, vault-grounded at `build-prep/contracts/`.

### Rule 2 — Schema-additive, never schema-breaking (BUILT)
Add optional fields + bump `schema_ver`. A breaking change is a NEW versioned shape sitting side-by-side — never edit-in-place. Every pre-existing graph must continue loading unchanged. Consequence: C3's `Edge.kind` field (Concurrent Cognition G1) defaulted to `"data"` with `SCHEMA_VER` bumped to 2, so every pre-v2 graph loads without conversion.

### Rule 3 — One source (BUILT)
A node-type is defined once (C2) → UI, runtime, and tools all project from it. A model capability is defined once (`ops/cli/capabilities.py`) → the role-binder, fit-surface, and RHM all read it. A VRAM budget is computed once (`ops/cli/gpu.py` `budget_vram`) → the CLI `up` gate, the fit-surface, and `voice/lifecycle.py` all call it. `Suite._SELF_CHANGE_STREAMS` is the single source for the subject-classifier, the revert-tagger, and the ledger's `--grep` net — a stream can't be added without the ledger seeing it. Never duplicate a definition across surfaces.

### Rule 4 — Fail loud (BUILT)
No silent failures, no silent fallbacks. A down model endpoint renders a legible marker and warns; it never crashes or silently omits. A commit failure in the decision→implementation wire surfaces the build back as a retryable build-intent; it never marks `implemented`. An unregistered model-id returns `{"known": False, "action": "ASK"}` — never a fabricated row. A whole-tree checkpoint is refused outright. `append_event` is atomic+unique under a store-level lock. Every fail-loud boundary is covered by an acceptance suite.

### Rule 5 — ext4 storage (BUILT)
`~/company/.data/store` is on ext4. The store is never placed under `/mnt/c` (WSL `fsync` corrupts databases there). This is not a preference; it is a hard constraint baked into `store/AGENTS.md` and the run instructions.

### Rule 6 — No Gemini (BUILT)
Hard constraint. No Gemini model, ever. Unconditional.

### Rule 7 — Stage-gated (BUILT)
Work within assigned stage. Act freely in-scope. Surface cross-cutting changes. CONFIRM anything irreversible — especially changing a contract or touching real source data. The posture classes (AUTO / CONFIRM / SURFACE / LOCKED) govern the decision→implementation wire's dispatch path. Only `AUTO`-posture classes auto-dispatch on the operator's approve; every `CONFIRM`/`SURFACE`/`LOCKED` class surfaces for the operator first.

### Rule 8 — Author from the registry; never invent (BUILT)
The source of truth for what exists is `Suite.capabilities()` — models, node-types, verbs, panels. When a needed value is not registered, **ask the operator**; do not fabricate. Making something up is the same failure as not acting. This is the **path-of-least-resistance law**: every authoring prompt is seeded from the live registry (`capabilities()` — real models/node-types/verbs/panels feed every prompt; registered select-options come from the registry, never guessed). The model-capabilities catalog (`ops/cli/capabilities.py`) records honest unknowns (`"value": None, "source": "declared"`) rather than assumed values.

### Rule 9 — AI-operated is NOT review-free; FORM is half of done (BUILT as backend law; PARTIAL on FE enforcement)
Every implemented build surfaces a review item (`decision.surfaced_for_review` event + `build_result_review` inbox item). `implemented` means "done AND surfaced for review" — never a silent terminal. The FORM half of done: any operator-facing surface is built on the design system (components + design tokens — never hardcoded values or bespoke one-offs), coherent in scale/type/spacing/layout, responsive, navigable by sight rather than by reading. A backend-only change still updates the surface that exposes it. A design-lint that fails loud on off-token/bespoke elements is the enforcement mechanism. **Status of FE enforcement: PARTIAL** — the backend wire and review surfacing are BUILT and proven; the design-lint (`design_gate_acceptance.py`) exists; but the canvas FE does not yet auto-reject off-token usage at build time (flagged in STATE.md as a separate FORM session; `node_states_render_acceptance.py` covers one piece). The rule is architecturally stated and backend-enforced; the full FE legibility gate is not closed.

### Rule 10 — Commit to main; no feature branches (BUILT)
No branches in `~/company`. Tim runs multiple parallel sessions; a feature branch left unmerged is stranded work. Work on `main`; verify by tests before committing; concurrent sessions committing to `main` is fine (git serialises). If isolation is needed, use a `git worktree` (not a branch) and merge back the same session. Shelving work without losing it: tag it (`archive/<name>`) then delete — never leave a stranded branch.

### Operative meta-law — the path-of-least-resistance law (BUILT)
Make the **correct action the AI's easiest path** — for external agents (reading AGENTS.md/MAP.md) and for the system's own self-coding brain (reading authoring prompts). This is not a separate rule but the operating principle from which rules 3, 4, 8, and 10 derive. Concretely: registry feeds every prompt; making things up is a failure; missing info surfaces a question not an invention; self-description auto-maintains so that not updating it causes a failing drift-check, not silent rot.


---


## II. The Self-Description Mechanism

Source: `AGENTS.md` (root), `MAP.md`, `STATE.md`, `tests/drift_acceptance.py` (referenced), `tests/AGENTS.md`. Status: **BUILT** (auto-maintained portions) + **BUILT, manual by integration** (prose portions).

The repo is self-describing by design. This is the mechanism that keeps it true.

### The two-tier maintenance model

**Tier 1 — Auto-maintained (generated from live registries):**
`Suite.refresh_self_description()` regenerates the factual blocks on every `apply` (every accepted change runs it). These blocks are delimited by markers and explicitly say "do not hand-edit":
- `MAP.md` `<!--REGISTRY:START-->` / `<!--REGISTRY:END-->` — the live registry of node-types (16), RHM verbs (11), modes (8), panels, and models (15). Read directly from `Suite.capabilities()` — never invented.
- `STATE.md` `<!--SUITES:START-->` / `<!--SUITES:END-->` — the complete list of 130 acceptance suites. Read from the live test discovery, never hand-curated.

**Tier 2 — Maintained by integration (prose, human-in-the-loop):**
The prose in `STATE.md` ("What is BUILT", "What is not built yet", "Gotchas"), and each module's `AGENTS.md` prose, are updated "by integration" — every agent that makes a change updates what the new piece makes untrue and keeps the rest coherent. This is a disciplined convention, not an automated process.

**The drift-check enforcement** (`tests/drift_acceptance.py`):
This suite fails loud if any of the following is true:
- A registered capability or node-type is not reflected in `MAP.md`
- An acceptance suite that exists on disk is not listed in `STATE.md`
- A registered RHM verb or mode is not in the live registry block

Drift is caught, never silent. This is the PoLR enforcement for self-description: failing to update causes a failing test, which means the next change cannot declare itself done.

### Net-new registry drift homes (the distributed pattern)

Beyond the root MAP/STATE, each module that owns a registry declares its own **drift home** — a specific prose section (usually in the module's `AGENTS.md`) that must stay current with its registry, enforced by a named acceptance suite:

| Registry | Module | Drift Home | Enforcement Suite |
|---|---|---|---|
| `EDGE_KINDS` (edge vocabulary) | `contracts/node_record.py` | `contracts/AGENTS.md` prose | `edge_kinds_acceptance.py` |
| `RULE_OPS` (rule grammar ops) | `runtime/rules.py` | `runtime/AGENTS.md` | `rules_acceptance.py` |
| `DESTINATION_KINDS` (rule routing) | `runtime/rules.py` | `runtime/AGENTS.md` | `rules_acceptance.py` |
| `THOUGHT_SHAPES` (cognition archetypes) | `runtime/suite.py` | `runtime/AGENTS.md` | `chat_parts_acceptance.py` |
| `PART_GRAIN` (per-mode config) | `runtime/suite.py` | `runtime/AGENTS.md` | `chat_parts_acceptance.py` |
| `ACTIVATION_CONTEXTS` (trigger kinds) | `runtime/activation.py` | `runtime/AGENTS.md` | `activation_contexts_acceptance.py` |
| `COGNITION_EVENT_KINDS` (lifecycle events) | `contracts/cognition_info.py` | `runtime/AGENTS.md` | `cognition_info_acceptance.py` |
| Role registry (discovered roles) | `roles/*.py` | `roles/AGENTS.md` | `roles_acceptance.py` |
| `MODEL_CAPABILITIES` (by model-id) | `ops/cli/capabilities.py` | `ops/AGENTS.md` + module docstring | `model_capabilities_acceptance.py` |
| Node-type registry (discovered types) | `nodes/*.py` | `MAP.md` live registry block | `drift_acceptance.py` |

The pattern is consistent: add a value to a registry → add it to its drift home → the named suite will fail loud if you miss it. This is rule 3 (one source) + rule 4 (fail loud) applied to documentation.

### What is auto vs hand-maintained

| Item | Who maintains it | How |
|---|---|---|
| `MAP.md` live registry block (node-types, verbs, modes, panels, models) | `Suite.refresh_self_description()` | Auto, on every apply |
| `STATE.md` acceptance suite list | `Suite.refresh_self_description()` | Auto, on every apply |
| `STATE.md` prose ("What is BUILT", "Gotchas") | Agents, by integration | Manual, per-change |
| Each module's `AGENTS.md` prose | Agents, by integration | Manual, per-change |
| Each module's drift-home registry section | Agents, by integration + enforced by suite | Manual, failing suite catches it |
| Vault frontmatter + wikilinks | Agents, by convention | Manual, per-change |

### The self-growth loop (the point)

The system's first real use is its **own codebase** — MAP.md + the code indexed and linked, so Tim clicks and talks here and directs changes that dispatch back into these modules (governed). Every accepted change auto-regenerates the registry blocks via `refresh_self_description()`, so the surface Tim navigates is always current. The drift-check ensures that prose drift is caught before it accumulates. Together these constitute a system that stays legible to AI agents on cold entry — the convention is not documentation bolted on; it is load-bearing orientation infrastructure.


---


## III. The Where-Things-Go Table (Consolidated)

Source: `AGENTS.md` root "Where things go" table + module constitutions. Status: **BUILT** for all backend entries. **FE gap flagged** (see below).

| Want to add... | Go to | Key constraint |
|---|---|---|
| A new **node-type** | `nodes/<name>.py` | Declare VERSION/KIND/PORTS + `run`; self-registers on drop-in. Set `VOLATILE=True` if it reads mutable truth (repo, index, model-of-someone, clock) |
| A new **model or provider** | `fabric/config.py` | Repoint `DEFAULT_BASE_URL` / register; `transport.list_models` exposes them |
| A new **storage backend** | `store/` | Implement the Resolver Protocol (C4); add a backfill |
| A new **RHM action verb** | `runtime/suite.py` | Add a `VerbSpec` to `RHM_VERB_SPECS` (single source: `RHM_VERBS` / `_DESC` / `_CLASS` + native-tool param schema all derive from it) + a case in `_dispatch_rhm_action`; whitelist-gated |
| A new **presence mode** | `runtime/suite.py` `MODES` + `MODE_DIRECTIVES` | The mode IS a node (`rhm_mode`); behavior comes from its directive |
| A **settings/control panel** (declarative) | Ask the RHM (`propose_panel`) | Fields edit real config; the 'others' tier; git-reversible |
| A new **UI component** (arbitrary code) | Ask the RHM (`propose_extension`), operator-only | Build-gated → `src/extensions/` → error boundary → git-revert |
| A new **canvas surface** (structural) | `canvas/app/src/App.tsx` | External-agent edit; node/panel/extension rendering stays generic |
| A genuinely **new operation** (rare) | `mcp_face/` + `runtime/suite.py` | Add one verb (C7) — only for a new *kind* of operation |
| A new **contract** | `contracts/` | A new `Cn`; CONFIRM required (widest blast radius) |
| To **operate the running system** | `ops/` | The `company` console + `ops/services.json` (the registry) |
| A new **role** (cognition cast member) | `roles/<id>.py` | Declare `ROLE` dict; `id` must equal the filename; self-registers; update `roles/AGENTS.md` drift home |
| A new **service to the command center** | `ops/services.json` | Add an entry (group, title, port, manage, health, autostart, vram_mb); add a unit to `ops/systemd/` if needed |

### The FE legibility gap (flagged in inventory + STATE.md)

The canvas constitution (`canvas/AGENTS.md`) declares that new node-types need zero frontend code ("one generic `ai-node` shape, data-driven from `/object_info`"). The backend "where things go" table is complete and enforced. However:

**What is partially open on the FE side:**
1. `show`'s target resolver does not yet resolve the S1 element-level `ui://` addresses (first-slash partition + bare-ref keying matches only the 9 region handles, not the 68 element-level addresses added by S1). Widening to element addresses is the F4/I-group lane — flagged in STATE.md.
2. `node_states_render_acceptance.py` covers node state rendering; but the `NODE_STATES` registry (a registered single-source set, BUILT) is "FE not yet wired — a separate FORM session" per STATE.md.
3. The canvas workshop (`ui://chrome/workshop`) should render the `stream` tag for all three reversible change streams and add the operator checkpoint-mint control — flagged as "out of this runtime-scoped change" in STATE.md.
4. The design-lint gate (off-token / bespoke-element → build cannot be marked done) is stated in rule 9 and has `design_gate_acceptance.py`, but the canvas FE build does not yet enforce it at the component level.

These are the **legibility gaps flagged by the inventory** (inv-D-selfdesc-tests-ops.md §Gaps): the backend registry discipline is tight; the FE is behind the backend on the self-describing / registry-fed surface contract.


---


## IV. The Operational Structure

Source: `ops/AGENTS.md`, `ops/services.json`, `ops/cli/gpu.py`, `ops/cli/capabilities.py`. Status: **BUILT** for services/GPU/models type-views (as of 2026-06-06 to 2026-06-08); **DESIGNED (not yet instantiated)** for cognitive-layers, RHM/modes, data/memory, jobs/cron.

### What the `company` CLI is

`ops/company` (symlinked onto `PATH`) is the ONE operational control surface for the entire running system. It is stdlib-only (loads cleanly in the 3.14 bridge). Commands: `up` / `down` / `status` / `gpu` / `models` / `swap` / `config` / `telemetry`.

The CLI package (`ops/cli/`):
- `app.py` — dispatch + the `up` resource gate (refuses an over-capacity start; shows what's holding the card; `--force` overrides)
- `registry.py` — reads and parses `services.json`
- `systemd.py` — `systemctl`/`journalctl` wrapper (start/stop/status/logs)
- `gpu.py` — the VRAM resource manager (shared core with `voice/lifecycle.py`)
- `models.py` — inventory + swap
- `capabilities.py` — the model-TYPE capability registry (keyed by model-id)
- `bench.py` — benchmarking harness
- `render.py` — status/health views (pretty-print)
- `telemetry.py` — measured VRAM/load/speed records (introspective-data-building, first instance on the model layer)

The console's design law: **systemd is the muscle; this is the map + the console.** Reliable execution, `Restart=on-failure`, and autostart live in systemd user-units (`ops/systemd/`). The console drives systemd; it never replaces it.

### `services.json` — the self-describing registry

Path: `/home/tim/company/ops/services.json`. The single source of truth for what runs on the machine. An AI reads this to know the whole landscape. Adding a service = adding one entry here.

**Structure:**
- `vram_ceiling_mb`: 16376 (the 16 GB RTX 4080 card ceiling)
- `combos`: named sets of services meant to run together (e.g. `small-pair`: chat-2b + chat-08b, verified co-resident at gpu_util 0.45+0.30)
- `groups`: core / brain / voice / models / reach
- `services`: each entry declares `group`, `title`, `port`, `manage` (type + unit), `health`, `autostart`, optional `vram_mb`, `config` (for config-driven model services)

**The five groups and their services (as observed):**

| Group | Services | Notes |
|---|---|---|
| `core` | `canvas` (port 5173), `bridge` (port 8770) | Both autostart=true; the interactive Company surface |
| `brain` | `chat-4b` (port 8000, Qwen3.5-4B-AWQ) | config-driven via `serve_model.sh`; the resident local brain |
| `voice` | `tts-kokoro` (4123), `stt-whisper` (2022), `stt-parakeet` (2031), `stt-canary` (2032), `stt-granite` (2033), `tts-chatterbox` (4124), `tts-orpheus` (4125), `tts-cosyvoice` (4126), `tts-xtts` (4127), `tts-qwen3tts` (4128) | All on-demand (no autostart); VRAM-budgeted; managed as user-units for cgroup teardown safety |
| `models` | `embed-bge` (8001), `embed-jina-v4` (8002), `embed-jina-v5` (8004), `embed-qwen3` (8004†), `chat-2b` (8003), `chat-08b` (8006), `chat-nemotron` (8005), `llama-swap`, `litellm` (4100) | On-demand; VRAM-budgeted |
| `reach` | `ollama` (11434), `tailscale`, `pipeliner`, `openclaw-gw` | System-unit or user-unit; the body's connection to the world |

†`embed-jina-v5` and `embed-qwen3` both declare port 8004 — they are alternatives, not co-resident.

**The `config` block as the one source for model sizing (2026-06-07):**
For config-driven model services, `config.gpu_util × vram_ceiling_mb` IS the VRAM budget (`gpu.budget_vram`). This is also what vLLM is launched with (via `serve_model.sh`). The fit-gate and the launch never drift — they read the same config block. Services also carry `config._profile.{fixed_mb, kv_kb_per_token, measured}` for auto-sizing from a measured profile.

**No autostart at boot (Tim's call, 2026-06-06):** every service is on-demand via `company up`. The `autostart` flag means "started by bare `company up`" (only canvas and bridge); everything else requires explicit `company up <svc>`.

### `gpu.py` — the VRAM resource manager (shared core)

Path: `/home/tim/company/ops/cli/gpu.py`. Status: **BUILT**.

The single VRAM authority for both the `company` CLI and `voice/lifecycle.py`. Both import this module; there is no second budget/teardown path.

**Key functions:**
- `budget_vram(reg, key)` — priority order: (1) `config.gpu_util × ceiling` if present (authoritative for config-driven models); (2) learned telemetry (measured from previous loads); (3) registry `vram_mb` estimate
- `read_gpu()` — measured GPU memory via `nvidia-smi` → `{used, free, total, util}` or None
- `check_fit(reg, to_start)` — decides if starting a set of services fits: measured free VRAM (truth) vs budget estimates for the not-yet-running services in the set
- `fit_report(reg, keys)` — the settings fit-surface answer: answers `fits_card` (sum of config-derived budgets vs ceiling) AND `fits_now` (measured free VRAM right now); returns a dict the surface renders directly including what to evict and why
- `plan_eviction(reg, to_start, need, free)` — chooses which running services to stop to make room; evicts models→brain→voice, largest first, only as many as required
- `teardown(svc)` — orphan-safe stop: unit services → `systemctl stop` (kills the whole systemd cgroup, reaping vLLM's EngineCore which otherwise reparents to init and squats memory); manual services → process-group teardown (SIGTERM then SIGKILL)
- `format_state(reg)` — the "what's holding the card" block, shown on refuse and on every `up`

**The fit-gate policy (Tim, 2026-06-06):** `company up` REFUSES a start that would blow past GPU capacity, and ALWAYS shows what is already holding the card. `--force` overrides.

**Measured on the 16 GB card:** the 4B brain co-resides with 4-bit AWQ Orpheus at 64K context (proven by use). Orpheus (~8.5 GB) + 64K brain = over by ~0.6 GB — a switch-on-demand pair (the gate refuses, never OOMs). The 4B brain solo reaches 256K context. The KV binding flips on main-context depth: at 0.49 gpu_util + Orpheus co-resident, only ~1-2 swarm roles at 64K main; at 0.63 gpu_util + no Orpheus, ~16 roles (the `max_num_seqs` bind becomes the sole constraint).

**Eviction priority order:** `_EVICT_PRIORITY = {"models": 0, "brain": 1, "voice": 2}` — models evicted first (lowest priority to keep), voice last.

### `capabilities.py` — the model-TYPE capability registry

Path: `/home/tim/company/ops/cli/capabilities.py`. Status: **BUILT** (as of 2026-06-08 per ops/AGENTS.md); **PARTIAL** (only 2 model-ids seeded in `MODEL_CAPABILITIES` catalog; more needed as new models are registered).

The THIRD keying in the model machinery: intrinsic capability by model-id. The first keying is service deployment by service-key (`services.json`). The second is telemetry (`telemetry.jsonl`).

**Owns ONLY model-intrinsic facts** — what the weights can do:
- `tools`: can it tool-call?
- `json_schema`: does it conform to structured output constraints?
- `thinking`: is it a reasoner/chain-of-thought model?
- `context_ceiling`: the model's real capacity (max_model_len_ceiling from the served config)
- `concurrency_knee`: the C0.5 KV measurement result (formula + two loadout points, measured data, not a literal)
- `speed_profile`: decode tok/s
- `provides`: the capability TAG set matching `suite.py capability_providers()` exactly (`chat·json·tools·fast·no-think·vision·thinking·reasoning`)

It NEVER stores `gpu_util`/`vram` — those are rule 3 violations (the service layer's job). For those, it **JOINs to `gpu.py`** via `service_key_for(reg, model_id)`.

**Provenance vocabulary:** `declared` | `probed` | `measured` | `served`. Live/served wins over declared. Honest unknowns: cloud models record `"value": None, "source": "declared"` for fields that are genuinely unknown rather than assumed — recording the gap is exactly this registry's job.

**The binding queries:**
- `role_can_bind(requires, model_id)` — `requires ⊆ provides` (true iff the role's requirements are satisfied by the model's provides set)
- `suitable_models(requires)` — all catalog model-ids whose `provides ⊇ requires`
- `require_resident(model_id)` — C8.4 fail-loud: if the model is not loaded, returns `{resident: False, action: "OFFER_LOAD", load_command: "company up <key>"}` — never auto-loads, never silently degrades

**Cloud-decoupling policy as data (C8.3):** `COGNITION_PLACEMENT_POLICY` declares the swarm runs resident-always, the main brain is selectable (resident or cloud), and cloud may run background roles. This is data + a query (`placement_for(track)`, `swarm_survives_cloud_brain()`), not control-flow baked into the engine.

**Downstream consumer:** `suite.py capability_providers()` (C2.5) today hand-derives the resident's `provides`; the wire to read from this catalog instead is flagged in `ops/AGENTS.md` as "the one suite-side wire."

**Self-description / drift home (C9.4):** the module docstring + the `ops/AGENTS.md` "models/VRAM" type-view section. Drift assertion: `tests/model_capabilities_acceptance.py`.

### The D3 law — one substrate, per-type view-modes (DESIGNED, partially instantiated)

The ops console is not just services management. It is the **first instantiation** of a general console that will grow through type-views. D3 (Tim: "one substrate, per-type view-modes") declares: one console/registry mechanism instantiated per type; services is one type-view; models/VRAM, cognitive-layers, RHM/modes, data/memory, jobs/cron are other view-modes of the same mechanism, not separate tools.

**Status of type-views:**
| Type-view | Status | Notes |
|---|---|---|
| `services` | **BUILT** (live since 2026-06-04) | The first type-view |
| `models/VRAM` resource manager | **BUILT** (live as of 2026-06-06) | `company gpu/models/swap`; VRAM cost in status; hard budget gate; `ops/cli/gpu.py` |
| `model-TYPE capabilities` | **BUILT** (live as of 2026-06-08) | `ops/cli/capabilities.py`; the third keying; JOINs to gpu.py |
| `cognitive-layers` | **DESIGNED, not instantiated** | Same mechanism when built |
| `RHM/modes` | **DESIGNED, not instantiated** | Same mechanism when built |
| `data/memory` | **DESIGNED, not instantiated** | Same mechanism when built |
| `jobs/cron` | **DESIGNED, not instantiated** | Same mechanism when built |

All of these are open-future items in `ops/AGENTS.md`. The pattern is locked: don't build a new tool; extend the same console over the new type.


---


## V. The Laws + Self-Description + FE Gap — Brief Summary (for the integrating session)

### The laws (five essential ones for the surface designer)

1. **Registry-is-truth:** `Suite.capabilities()` is the ground truth for what exists. Every authoring prompt is seeded from it. Making up a value is a failure. Missing info → ask, don't fabricate.

2. **Schema-additive:** existing data (graphs, chat history, events) must continue loading forever. New fields must be optional with defaults. Breaking is a side-by-side new shape, never an edit.

3. **Fail loud:** no silent fallbacks, no pretend-success. A down endpoint is a loud marker. An unregistered model-id is an explicit unknown result with `action: "ASK"`. A build that can't be git-checkpointed fails loud instead of closing. The surface that exposes a backend change must be updated as part of the same change.

4. **Canvas reflects, never owns:** the canvas is a peer of the shared document via the bridge (C8). The runtime is authoritative. The canvas renders from `/object_info` (C5); it holds no state. New node-types need zero frontend code. This is what makes a generic surface possible.

5. **The interaction laws:** the RHM acts only through a whitelist of governed verbs (`run·propose·build·consult·show·panel·extend·configure·load_voice·unload_voice·request_change`); `apply`/`delete`/`file-write` are unreachable from it. The decision→implementation wire dispatches headless Claude Code only when the operator approves a build-intent. `claude -p` spawning is lead-only — a worker that fires it is a floor violation. No cognition event can be a `resolve`/`approve`/`dispatch`.

### The self-description mechanism

`Suite.refresh_self_description()` auto-regenerates the factual blocks in MAP.md (live registry: node-types, verbs, modes, panels, models) and STATE.md (acceptance suite list) on every `apply`. The prose (what's built, gotchas, module constitutions) is maintained by integration — agents update what the new piece makes untrue. `tests/drift_acceptance.py` fails loud if any registered capability or suite is not reflected. Each module with a net-new registry declares a drift home (a named prose section) with a named enforcement suite; the list is in Section II above. The mechanism means: an agent working in this repo on a cold start can read AGENTS.md → MAP.md → STATE.md → the relevant module constitution and act correctly — the self-description is orientation infrastructure, not optional documentation.

### The FE legibility gap

The backend registration discipline is tight and complete. The FE has three open gaps:

1. **`show`'s target resolver** does not yet resolve the 68 S1 element-level `ui://` addresses — it resolves only the 9 original region handles. The element rows exist in the `UI_REGISTRY` (S1, BUILT, proven by `ui_registry_acceptance.py`); the resolver widening is the F4/I-group lane.

2. **`NODE_STATES` registry** is a registered single-source set (BUILT, backend, `Suite.NODE_STATES`); the FE node-state rendering is not yet wired to read from it — flagged in STATE.md as "a separate FORM session."

3. **`ui://chrome/workshop`** (the self-change surface) should render the `stream` tag for all three reversible streams (`self-apply` / `self-build` / `checkpoint`) and add the operator checkpoint-mint control — the backend ledger is BUILT; the FE surface is not.

The gap pattern: the backends emit data into well-structured, registered, single-sourced shapes. The FE surface that renders those shapes lags. The integrating session's surface work should plan to consume these registered shapes rather than introduce parallel definitions — that would violate rules 1 and 3.
