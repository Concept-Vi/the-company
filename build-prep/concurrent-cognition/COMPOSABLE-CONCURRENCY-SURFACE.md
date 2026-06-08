# The Composable Concurrency Surface — design capture & unification

> **Status: open / generative / core-unification (open-future).** Tim's thinking-out-loud (2026-06-08) on how the concurrency system is *exposed, configured, viewed, and leveraged* — broadly, not just for cognition. This doc captures his vision verbatim-in-spirit, **expands** it (per his instruction: add more, connect more), states honestly **what's built vs net-new**, and frames the **adjacent-system research** needed for integration + review. It is part of a larger unification; there is much more to it.

> **Epistemic tags:** **Built** (verified, file:line) · **Net-new** (designed, not built) · **Open** (decide/expand with Tim). Addressing is `run://` throughout. Aesthetics/feel = `needs-tim`.

---

## 0 · The one sentence
A **concurrent step** is N runs (the count *calculated* from a declared allocation strategy over the resolved input); the operator sees a step as a **vertical segmented bar** (segments = role-types, height ∝ proportion of the step's runs, inner lines = individual runs by semantic zoom); a **multi-step process** is a left-to-right **timeline of columns** with inputs/outputs in the gaps; the operator selects at **column / segment / run** levels, multi-selects, and applies any config/condition/trigger/model-change then runs — and the whole thing is one render-mode of the same `run://`-addressed substrate the cognition View draws, interwoven with the RHM's context-resolution + action layer.

---

## 1 · What's BUILT today (the substrate this rests on)
- **Resource-connected budget (Built).** `runtime/cognition.py SlotBudget.from_registry` reads `ops/services.json` (`max_num_seqs`, `gpu_util`) JOINed to `gpu.py` → the concurrency cap is `min(max_num_seqs − R, free_KV // per_role_ctx)`, derived from live resource truth, never hardcoded. **Not yet driven:** the per-mode loadout SWAP (9b+4b / 4b-solo via `company up/swap --evict`) is declared, not actuated from a mode (needs-tim — Tim's experimentable lever, H8).
- **Role authoring (Built — AUTH commit 44b9cf9).** `propose_role`/`apply_role` (propose-not-apply, operator-approved) sets: **prompt** (`prompt_template`), **structured output** (`output_fields` → BaseModel, decode-enforced by L-transport), **context/inputs** (`input_addresses` + `/api/cognition/inputs`), **model binding** (`requires` → the capability query), **rules** (declared-AST conditions). Test: `dry_run_role`, `preview_turn`.
- **The data the bar renders from (Built).** `cognition.*` lifecycle events on `/api/stream` (turn.start · role.fire · role.ran · inject · part · turn.done) + `run://<turn>/<role>` addresses + the `cognition_info` projection. The cognition View (Pulse→River→Nodes, L-fe) already renders this — reflects-never-owns.
- **Rules = conditions/triggers (Built — G3).** declared-AST grammar (`RULE_OPS`), 5 destinations (inject/chain/address/surface/lane), deterministic, renderable, the claude-p floor unforgeable.
- **THOUGHT_SHAPES fanout seam (Built, partial).** `fanout: "cast"` (fire each role once) | `"draws"` (jury: N varied draws of the SAME input). The `scatter-route`/`scatter-write` archetypes exist as seams.

## 2 · The NET-NEW core: input-driven concurrency allocation
**The capability Tim's message is the spec for.** Today fanout is cast-once or N-identical-draws. Net-new: **one role → N runs by PARTITIONING the resolved input**, the count *calculated* from a declared **allocator**:

```
role.allocator = { strategy: <how>, ...params }   →   computed at runtime over the resolved input → N input-slices → N runs
```
**Allocation strategies (a registry — extensible, like RULE_OPS/destination_kinds):**
| strategy | N runs = | params |
|---|---|---|
| `by-size` | `ceil(total_tokens ÷ max_tokens)` (Tim's folder example: 12k ÷ 4k = 3) | `max_tokens`, `source` |
| `by-file` | one per file | `source` (a folder/glob address) |
| `by-tag` | one per tag/category | `tag_field` |
| `by-tag+size` | partition within tag by size | `tag_field`, `max_tokens` |
| `by-cluster` | embed + cluster the material → one per cluster | `embed_model`, `k`/threshold |
| `by-list` | map 1:1 over an upstream step's output list | `source_address` |
| `by-count` | fixed N (= today's jury `draws` — a degenerate case) | `n` |

**Key properties:**
- The allocator **subsumes** what exists: jury `draws` = `by-count`; the cast = `by-list` over the mode's roles. So it's a generalization, not a parallel system.
- The number of runs is **DATA, computed at runtime** from the resolved input (not a fixed config int). The allocator declares the *rule*; the input determines the *count*.
- **Resource interplay (honest):** the allocator proposes N; `SlotBudget` caps concurrent in-flight to the slot knee; the rest queue. A step therefore has three honest numbers — **wanted · running · queued** — which the bar shows directly. A huge allocation doesn't blow the GPU; it serializes under the budget (fail-loud if it can't fit at all).
- **Allocator is registry-driven + renderable** (L1/the no-text-wall law): a small declared config on the role, shown on the segment.
- **Net-new engine work:** the allocator registry + the input-partitioning executor in `run_swarm` (it currently takes a fixed role list; it must expand a role+allocator into N input-sliced run specs), + the source-resolution (folder/glob/address → material). The `by-cluster` strategy pulls in embeddings (the E-lane work).

## 3 · The visual: the sequencer / timeline (Tim's model, expanded)
**One step = a vertical segmented bar.** Segments = distinct role-types in the step; **segment height ∝ (that type's run-count ÷ total runs in the step)**; colour = role-type/category; **inner lines (semantic zoom) = the individual concurrent runs** within a segment. A segment can hold multiple runs (the allocator's N).

**Multi-step = a left-to-right timeline of columns**, inputs/outputs drawn in the **gaps between columns** → it reads as a **sequencer/timeline** (Tim's words). Each column is a *stage*; the timeline IS the graph laid out temporally.

**Three selection levels (= the altitude layers):**
- **Column** = the whole step/stage (a group / "stacked nodes") — select to operate on the step.
- **Segment** = a role-type within the step — click → its **inspector** (the existing Inspector/config-form pattern).
- **Run** = one concurrent run (a line within a segment, at deep zoom) → its `run://` output.

**Multi-select + apply (batch authoring over the timeline):** select segments/columns across the timeline → apply a **config / condition / trigger / model-change** to all → **run**. Rides the AUTH backend (propose/edit role, attach rule) over a selection set. Every loaded-model capability must be available to alter + run.

**The unification realization:** the **Pulse→River→Nodes** cognition View and this **Timeline→Column→Segment→Run** sequencer are *the same three-altitude idea over the same `run://` data* — two render-modes of ONE substrate. River fits the single converging cognition *turn*; the timeline fits the multi-step compositional *pipeline*. Both reflect-never-own from the same events. (The canvas already picks render-modes per node-type — this extends that.)

**Built vs net-new for the visual:**
- Built: the data (`cognition.*` + `run://`), the View's altitude pattern, the Inspector/config-form, semantic zoom (`NodeShape` `expanded = zoom>0.5`), the reflects-never-owns SSE store.
- Net-new (FE session): the segmented-bar shape (height ∝ run-proportion), the column-timeline layout (I/O in the gaps), column/segment/run multi-select + batch-apply, the column-as-group ("collapse a stage's parallel runs into one bar" — related to but NOT the existing `portal` reference node; portals resolve a subgraph by address, they don't visually group parallel runs).
- Net-new (backend to expose for the bar): per-step run-records **grouped by role-type with counts** (for segment proportions), the **wanted/running/queued** numbers, the allocator config per role, the I/O addresses between steps.

## 4 · The unification — "it's everything in the system"
This is not cognition-specific. A step of N input-partitioned runs feeding the next step is the shape of **any concurrent compositional process**: retrieval fan-out · document pipelines · codebase map-reduce · cognition (one instance). Same substrate, same view.

**Interweave with the RHM (right-hand-man):**
```
   the CONCURRENCY engine                     the RHM
   roles · allocator · run:// outputs    ⇄    dynamic context resolution (address→resolve→inject)
   rules route/surface                   ⇄    takes actions · the inbox · governance posture
```
- The allocator's input **source** can be an RHM-resolved address (dynamic context resolution feeds the fan-out).
- A rule's `surface` destination lands in the **RHM inbox**; the RHM approves/acts (the governance floor: the engine surfaces, the operator/RHM resolves).
- The RHM can **read the bar's live state** (its own cognition is addressable, C7.2) and act on it — close the loop.
- A role/step can be **triggered** by the RHM's activation-contexts (background/sense/rollup, G5).
→ They are interwoven: the concurrency engine is *how the RHM thinks in parallel*; the RHM is the engine's *context + action + governance layer*.

## 5 · Honest open questions (expand with Tim)
- **Tools in authoring** — the role schema has a `tools` field (judge-preserved) + the 4B tool-calls, but `propose_role` doesn't yet expose tools. Net-new authoring field.
- **The allocator strategy set** — `by-size/file/tag/cluster/list/count` is a starting registry; more exist (by-time, by-query, by-embedding-similarity, by-operator-partition). Which ship first?
- **Step vs turn** — is a "step" always a graph stage, or can a single cognition turn's wave be a step too? (Likely: a turn IS a one-step instance; a pipeline is multi-step. Same data.)
- **The timeline as the graph's temporal layout** — does the column-timeline REPLACE or COMPLEMENT the spatial node-graph? (Likely a render-mode toggle: spatial graph ⇄ temporal sequencer, same backend.)
- **Queue semantics** — when wanted > slot-knee, FIFO? priority? per-role reservation? (Resource policy, connects to the loadout lever.)
- **Cross-step I/O** — the gaps carry addresses; is a gap a join/reduce, a pass-through, a filter? (The rule destinations + the join archetypes.)

## 6 · The adjacent-system research (per Tim: "after that, research those other systems for integration + review")
Three research threads, to integrate + review the unification:
1. **The RHM's dynamic context-resolution + action system** — how address→resolve→inject works end-to-end, what actions it can take, the inbox/surface/governance, how a role/step plugs into it.
2. **The canvas grouping / collapse / timeline / multi-select capability** — what tldraw + the canvas already do for grouping, collapsing a subgraph, multi-select, temporal layout (so the sequencer reuses, not reinvents); the `portal` reference node's real semantics.
3. **The broader unification surface** — how this connects to the decision-wire, the operable composition surface, voice, modes, the resource/loadout CLI — the seams where the concurrency surface meets the rest of the Company.

## 7 · Research findings (folded as threads land)

### Thread 1 · RHM context-resolution + actions — LANDED (2026-06-08). Verdict: integration is REUSE, not reinvention.
The concurrency engine and the RHM share **one substrate** (`run://`-addressed, store-resolved via the `Resolver` protocol) and **one governance spine** (`governance.POLICY` posture + the `RHM_VERB_SPECS` whitelist + the operator-only inbox). Traced to code:
- **(a) A role/step's `run://` output is ALREADY RHM-resolvable.** The swarm writes `run://<turn>/<role>` (`cognition.py:559/573`); `_resolve_context_at`'s `_r2_run_strata` bridge (`suite.py:1872`) already pulls `run://<graph>/<node>` strata into a turn's context, scored by recency·proximity·pin·semantic-relevance, when the operator's `ui://` locus matches. The `ui://↔run://` map (`suite.py:1827`) is the load-bearing bridge. **No glue needed for outputs→context.**
- **(b) A rule's `surface` ALREADY closes through the same inbox.** `rules.py:562 route(dest="surface")` → `suite.surface_review(origin="responsive")` → the one `Inbox` (`governance.py:78`) → operator `resolve_surfaced` (`suite.py:6950`, operator-only, off the MCP face). Emits an `ask` (`resolved=None`), **never forges a resolve** (the C3.2/C9.2 floor). **No glue needed.**
- **(c) Activation-contexts ALREADY have entry points** (`activation.py:141 fire_activation` → `run_swarm`, routes only non-consequential destinations; `consolidate_rollup` → `run://rollup/<id>`). **Net-new = the always-on DRIVERS only** (idle-loop daemon / OS event-hook / `.timer`) — needs-tim (GPU/lifecycle), the reserve floor `FLOOR_RESERVE_R` already protects the live per-turn slots.
- **(d) The claude-p floor holds by CONSTRUCTION.** The engine fires roles + routes rules over 5 destinations; it has **no resolve verb**, and `FORBIDDEN_DESTINATION_VERBS` keeps resolve/approve/dispatch out of a rule. The only path to `claude -p` is operator `resolve_surfaced(approve)` + `wire_armed` + `is_build_intent` — operator-face only. **The engine cannot reach it.**
- **The action model (for the bar's "apply"):** one whitelist `RHM_VERB_SPECS` (`suite.py:2169`: run·propose·build·consult·show·panel·extend + configure); each carries a governance class; `POLICY` (`governance.py:12`) maps class→posture (AUTO act-now / CONFIRM surface-draft / LOCKED never-auto) on reversibility·cost·externality. `act()` (`suite.py:3000`) is the deterministic operator-click path with an **address-keyed tier gate** (`_tier_for_address`: a CONFIRM/LOCKED address surfaces, doesn't dispatch) — directly relevant to the bar's multi-select+apply.
- **NET-NEW GLUE (small, pointed):** (1) the **allocator calling the existing resolver to PARTITION a resolved input** into N runs (the inverse of resolution-feeds-context — the resolver primitives exist; the allocator using them is new); (2) the always-on activation **drivers** (needs-tim).

### Thread 2 · canvas grouping/collapse/timeline — LANDED (2026-06-08). Verdict: a real SUBSTRATE FORK (Tim-decision) + mostly-reuse encodings.
**⚠ THE FORK (Tim-level architecture call — surfaced, not decided):** the segmented-bar timeline can live in either of two substrates already proven in this app, with opposite properties:
| | **tldraw board** (`NodeShape.tsx`) | **SVG region** (`CognitionView.tsx` — the River) |
|---|---|---|
| renders | `api.graph()` authored nodes (position backend-owned, round-trips) | `cognition.*` SSE events (live runs, ephemeral position) |
| native group/multi-select free? | **Yes** (`editor.groupShapes`/`FrameShapeUtil` ship in tldraw 3.13.1, unwired) | No (not a tldraw surface) |
| prunes invented shapes? | **Yes** — `loadGraph` deletes any shape whose nodeId ∉ graph (`NodeShape.tsx:214`) | N/A |
- **The River ALREADY made this exact choice and chose SVG deliberately** (`CognitionView.tsx:94-100`: roles are cognition EVENTS, not `api.graph()` nodes — `loadGraph` would prune an invented role shape; inventing positions violates reflects-never-owns). The timeline's runs are the **same kind of data** (`run://<turn>/<role>` event outputs, not authored nodes) → **by the River's own logic the timeline leans SVG** → which means **tldraw's native grouping/multi-select would NOT apply** (the reuse becomes the River's SVG idioms + the inspector card pattern, not tldraw shapes). Both substrates are real + built; this is a genuine Tim/architecture decision, surfaced for the build-plan.
- **`portal` is NOT grouping (confirmed):** `nodes/portal.py` = a live window onto a SINGLE address (`config.ref`), reference-resolved, scheduler-skipped — not subgraph-collapse, not run-aggregation. "Collapse parallel runs into one bar" is net-new **regardless of substrate**.
- **Multi-select EXISTS + is consumed** (`useAppController.ts:558/597/796` — delete/wire/chat-focus loop over `getSelectedShapes()`), but the **inspector is single-select only** (`getOnlySelectedShape`, `:1132`) and **batch config-apply is net-new** (the per-node write `setNodeConfig`→`/api/set` + the loop-over-selection both exist to reuse; the batch UI does not; `applyCfg` is RHM-config, a false friend).
- **Semantic zoom is built + exactly the inner-lines-by-zoom pattern** (`NodeShape.tsx:47-49` `expanded = zoom>0.5`, a live tldraw signal; the River uses a discrete `altitude` 0/1/2 toggle instead, `CognitionView.tsx:49`). The Run-level "lines inside a segment at deep zoom" = the same threshold gate; net-new is the segment content.
- **Layout:** backend-authoritative for the board (`n.position`, the `/api/move` round-trip, `source:'user'` filter means a FE columnar layout won't fight it but is ephemeral unless written back); **moot for SVG** (compute column x from step-order directly). An unused `size`/`WH` field exists on nodes (`suite.py:777`) if persisted bar dimensions are wanted.
- **CognitionView IS the timeline's nearest ancestor (the strongest reuse if SVG wins):** reuse verbatim — `statusToken` (registry→token colour, `:34`), proportional encoding (River stroke-width ∝ contribution → bar segment-height ∝ run-proportion, the `maxChars`-normalize pattern `:104-116` → run-count normalize), the altitude toggle (= Column/Segment/Run levels), per-run `data-ui-ref="run://…"` already in the DOM (`:167`). **The doc's §3 unification claim (Pulse→River→Nodes ≡ Timeline→Column→Segment→Run, two render-modes of one substrate) is architecturally CONSISTENT with what's built** — both fold the same events, reflect-never-own, registry-driven. Net-new: the left-to-right multi-column layout (no temporal axis exists today), I/O in the gaps, segment geometry (stacked rects), selection-set state.

**Corrections to THIS doc that thread 2 flagged (applied honestly):**
- §3 said "the canvas already picks render-modes per node-type" — **overstated.** There is ONE generic `NodeShapeUtil` with an `isPortal` branch, NOT a registered render-mode-per-type system. Don't expect that infrastructure.
- §1/§3 `portal` = "resolves a subgraph by address" — tighten to **a SINGLE address** (not a subgraph).
- §3 "column-as-group is net-new" — read as **net-new-to-WIRE but tldraw-native-if-on-board** (`groupShapes`/`FrameShapeUtil` exist unused) — only if the Fork picks the board.
### Thread 3 · broader unification seams — LANDED (2026-06-08). Verdict: 5 seams, mostly already-connected; ONE small high-leverage net-new unlocks the rest.
**The spine (why these are seams, not bolt-ons):** five primitives are shared by EVERY system the surface touches — ONE event log · universal `run://` addressing · propose→apply governance · reflects-never-owns · the lead-only claude-p floor. "It's everything in the system" is literally true at the substrate level.
- **Integration precondition (step 0):** the whole engine (`cognition.py`/`roles.py`/`rules.py`/`authoring.py`/`activation.py`/`capabilities.py`/`roles/`) lives ONLY on the `concurrent-cognition` worktree — **main lacks all of it. Landing the branch is integration step zero** (a Tim decision — the build was deliberately worktree-isolated; the merge is his call).
- **Seam 1 · the decision-wire — ALREADY WIRED.** A rule's `surface` destination → the SAME inbox the wire dispatches from (`surface_review`→`resolve_surfaced`→`dispatch_decision`→`claude -p`→verify→re-surface). A concurrency step's output reaching a dispatchable decision needs **no structural glue**; the floor holds (a rule can't forge a dispatch); `wire_armed()` gates the production path (inert by default).
- **Seam 2 · the node-graph — THE KEY NET-NEW (smallest, highest-leverage).** The timeline-of-columns **IS a render of a graph**, proven by the walkthrough-as-Graph precedent (`suite.py:4429` — a review session compiles to nodes the scheduler runs). BUT: **`run_swarm` is NOT a registered node-type** (the `nodes/` dir has no swarm/cognition node; run_swarm is called only from `activation.py:214` + `suite.py:3997`). **Author a swarm-step node-type** (a `nodes/` module: PORTS_IN/OUT + a `run()` invoking allocator+run_swarm) → file-discovery registers it → a concurrent pipeline IS a graph → `run_graph`+the scheduler drive it for free, the gaps-between-columns ARE the edges (`join`/`gate` cover reduce/branch). This one piece unlocks the whole timeline framing.
- **Seam 3 · the resource/loadout CLI — JOINED, one declared-not-driven gap.** `requires⊆provides` (the model-select) + `SlotBudget.from_registry` (the knee from live `services.json`+`gpu.py`) are built; `MODEL_CAPABILITIES` even carries the measured C0.5 `loadout_points`. The gap: each mode declares a `brain_config` STRING (`voice-64k`/`swarm-16k`) but nothing **actuates** it — the CLI has the lever (`company swap --evict`). Net-new = a thin mode→loadout actuator (needs-tim, H8 — the always-on GPU concern, deliberately deferred).
- **Seam 4 · modes/voice/activation — mode is the dial (built).** `ACTIVATION_ALLOCATION` maps mode→{live activation-contexts, slot budget, brain_config}; `cast_for_mode` selects roles; the reserve floor is sacred; voice consumes a step's output as parts (the staged-voice path). Net-new = the always-on activation DRIVERS (needs-tim, GPU).
- **Seam 5 · the introspective loop — ALREADY CLOSED; the bar IS its render.** `emit_run_record`→the one log→`run_stats` distributions→pre-warm/loadout decisions. The bar's per-step records + wanted/running/queued ARE these same records. Net-new = a `run_stats` projection grouped by role-type with counts (for segment proportions).

**THE INTEGRATION ORDER (dependency-first, from the evidence):**
```
0 · land concurrent-cognition on main          (precondition — Tim's merge call)
1 · swarm-step NODE-TYPE                        (smallest; makes a pipeline a graph for free → unlocks the timeline)
2 · the input-driven ALLOCATOR engine          (doc §2 — the net-new core; by-cluster waits on embeddings/E-lane)
3 · bar/timeline backend-expose                (run-records grouped-by-type + wanted/running/queued — a run_stats projection)
4 · FE render-modes                            (segmented bar · column-timeline · multi-select+batch-apply — the SEPARATE FE session)
5 · mode→loadout actuator  +  6 · always-on drivers   (both needs-tim, both touch live GPU — gate behind Tim)
```

---

*This doc is the common reference. **All 3 research threads LANDED + folded (2026-06-08).** Verdict: the integration is overwhelmingly REUSE on one shared substrate; the net-new is small and ordered (§7 integration order): the swarm-step node-type (unlocks the graph/timeline framing), the input-driven allocator (the core capability), the bar backend-expose, the FE render-modes (separate session), and two needs-tim GPU actuators. Ready for Tim's A/B/C steer → a loop-prep triad → build + review.*
