# RESEARCH SYNTHESIS — The Instrument Surface (the fresh paper-aesthetic front end)

**Companion to:** `MANDATE.md` (the gospel). **Role:** the second of the three loop-prep documents.
This synthesizes 7 parallel explorer waves (4 inward, 3 outward) into one navigable, build-driving document.
Every section answers three things: **what was explored** (concrete locations/URLs), **what was found**, and
**WHAT IT MEANS FOR THE BUILD** (reuse this / avoid that / this constrains X).

> Epistemic note (for Tim): findings from the inward explorers are **code-grounded** (file:line citations to
> the live repo) — treat as Observed unless flagged otherwise. Findings from the outward explorers are
> **research-grounded** (2026 design sources) and are *proposals* — the palette, type, motion values are
> starting points you correct by reacting to renders (§8 of the MANDATE), not settled law. Where a finding is
> an inference rather than a verified fact, it is marked. Nothing here has been verified by running the new
> surface (it does not exist yet); the citations prove the *substrate* the surface will bind to exists and works.

---

## NAVIGATION

- **§A — The One Thing To Inherit:** the address-on-UI + context-attach mechanism (L10).
- **§B — The Bridge API Catalogue:** the 61+ endpoints the surface binds to.
- **§C — The Complete Real-Data Inventory:** every store, every count (the "heaps somewhere").
- **§D — The Equation / Seed Proportions + The Lens Catalogue:** Groups 2–12, to re-home.
- **§E — The Fresh Design Language:** the proposed starting token set (palette / elevation / type / pigment / geometry).
- **§F — The Rendering Substrate + The Single Motion System:** SVG+Canvas hybrid + one motion system (no-teleport).
- **§G — Per-Orientation Layout Specs + The Disclosure Grammar:** desktop / portrait / landscape + peek→open→pin→dismiss.
- **§H — CORRECTIONS TO THE MANDATE / GUIDE:** what the findings imply should change.
- **§I — OPEN — TIM DECIDES BY REACTING TO RENDERS:** the taste calls, consolidated.

---

## §A — THE ONE THING TO INHERIT: ADDRESS-ON-UI + CONTEXT-ATTACH (L10)

This is the **single inheritance** the MANDATE permits (L10: "you should not follow any of the rest of the UI,
don't even look at it"). Everything else in the current canvas is the **disposable harness**. This section is
the most load-bearing in the document: get this wrong and the fresh surface is not part of the Company's circuit.

### What was explored (code-grounded)
- `contracts/ui_info.py:180-191` (grammar), `:194` (`parse_ui_address`) — the S0 address contract.
- `runtime/suite.py:8943` (`UI_REGISTRY` hand-authored rows), `:32` (`_load_corpus_element_addresses`).
- `design/_system/addresses.json` — the corpus data source for element addresses (registry-is-truth).
- `canvas/app/src/useAppController.ts:1062-1063` (click capture), `:846` (indicate), `:1744` (spotlight), `:1703-1815` (resolve).
- `runtime/bridge.py:2082` (`/api/annotate`), `runtime/suite.py:5410` (`annotate`), `:5437` (`ingest_comment`), `:5572` (`/api/attach-chat`), `:5598` (`attach_chat`), `:5724` (`/api/presentation-pref`).
- `store/fs_store.py:620` (`append_annotation`), `:636` (`annotations_for`), `:581` (`append_chat`).
- `runtime/suite.py:4234` (`context_at`), `:3942` (`_r2_gather`), `:3965-4030` (full walk), `:4172` (`_resolve_context_at`), `:4470` (`chat`), `:2573` (`_r2_ancestors`).
- `mcp_face/server.py:426` (`inspect_address`), `runtime/cognition.py:resolve_address`.

### What was found — the mechanism in THREE layers

**1) ADDRESSING (mint + stamp).** One canonical grammar: `ui://` + ≥1 `/`-delimited segment + optional `/@state`
or `@state`. Examples: `ui://inbox` (region), `ui://inbox/build-review` (element), `ui://canvas/<node-id>`
(typed/dynamic), `ui://toolbar/run@running` (state-suffixed). `parse_ui_address()` validates **on the wire** and
**fails LOUD** on malformed (no silent empty). Two mint sources:
  - **9 hand-authored chrome/canvas regions** (toolbar, inspector, inbox, activity, chat, workshop, walkthrough,
    deferred-queue, `*`) — registry rows keyed bare (`'inbox'`), stamped `data-ui-ref='inbox'`.
  - **24+ element-level addresses** READ from `design/_system/addresses.json` at `Suite.__init__` via
    `_load_corpus_element_addresses()`, keyed by full canonical string, stamped as the **literal full string**
    `data-ui-ref='ui://inbox/build-review'` (the baked-in convention — no interpolation on render).
  - **Dynamic canvas addresses** (`ui://canvas/<node-id>`) are **mint-on-read** (no pre-registration; live
    node-ids resolve directly). The corpus is the single source of truth — **never fabricate an address (rule 8)**.

**2) ATTACHMENT (write face).** Context POSTed and persisted **address-keyed, append-only**:
  - `POST /api/annotate` → `Suite.ingest_comment(address, text, source)` → S0-validates → `append_annotation`
    to `annotations.jsonl`. **Also emits one located-gold chat turn** (the L4 coherence seam) so a comment
    feeds both the annotation thread (I6) AND the gold-label training signal (I7).
  - `POST /api/attach-chat` → `Suite.attach_chat(address, turn, …)` → `append_chat` to `chat.jsonl`, address-keyed.
  - `POST /api/presentation-pref` → `Suite.set_presentation_pref(address, pref)` → `append_annotation` with
    `kind='presentation_pref'` (rides the same leaf as comments, filtered separately at gather).
  - All paths S0-gate the address and **fail loud** on malformed. Append-only ⇒ a locus accrues a **thread**,
    not last-writer-wins. The store is **dumb** (does NOT validate addresses — the S0 gate lives in `Suite`).

**3) RESOLUTION (read face — the R2 engine).** The ONE scored context resolver:
  - `GET /api/context?address=<ui://…>` → `context_at` → S0-validate → `_r2_gather` (walks `_r2_ancestors`,
    collects annotations + chats + events + howto + presentation_prefs + run-strata at each ancestor) →
    `_r2_dedup` (collapse double-counts) → `_r2_score_and_cap` (rank by **recency · proximity · pin** decay,
    cap at **R2_BUDGET = 4000 chars**) → returns highest-relevance first.
  - The **ancestor walk**: `ui://inbox/build-review` → `[ui://inbox/build-review, ui://inbox, ui://]` (consume
    segments right-to-left). Context attached at a region auto-resolves at its sub-elements; howto attached at a
    leaf resolves only there. O(depth) (typically 1–3), silent-skips malformed candidates so a corrupt ancestor
    never crashes the gather.
  - Sibling reads: `GET /api/annotations?address=` (locus-only comment thread, oldest-first, no ancestors);
    `GET /api/address-help?address=` (three legs: what-this-is + how-to-change + how-to-use);
    `GET /api/address-history?address=` (every event/turn stamped at the address).
  - **`chat()` calls the SAME `_r2_gather`/`_r2_score_and_cap` on every turn** — so the locus + ancestors'
    context auto-injects into the RHM at that locus. This is the relational spine made operational.

**Frontend keystone:** `indicate(addr)` sets the locus + paints `.ui-indicated` + records journey step.
`resolveUiTarget(target?)` is the **SINGLE SINK** for all address-driven navigation (chat show-action +
walkthrough step + RHM present): validates grammar, checks the registry (fail loud if unknown), then dispatches —
`kind=canvas` → camera-drive; else → `querySelector([data-ui-ref='address'])` + `scrollIntoView` +
`.ui-spotlight`. Click-capture (`onDocClick`, capture phase) reads the nearest `[data-ui-ref]` ancestor;
addressing is **additive** to normal clicking (no `preventDefault`/`stopPropagation`).

**Scheme separation:** `inspect_address` (MCP) resolves store-backed schemes (`run://`, `cas://`, `skill://`,
`context://`, `session://`) via the `Resolver` protocol. `ui://` is **deliberately absent** there — it is a
UI-component-registry scheme resolved by the frontend (`resolveUiTarget`) or backend (`address_help`). Keep
this separation: store-resolved schemes go through `inspect_address`; UI-registry schemes stay in the UI domain.

### WHAT IT MEANS FOR THE BUILD
- **REUSE (faithfully, exactly):** the fresh surface MUST stamp every addressable DOM element with
  `data-ui-ref='ui://…'` as the **literal full string** *before first render*. Mirror the corpus convention — no
  interpolation on render. Mint via `addresses.json` + `UI_REGISTRY` (or dynamic `ui://canvas/<id>`).
- **REUSE the SINGLE SINK:** route ALL navigation (click, voice, gesture, RHM present, walkthrough) through one
  `indicate()`/`resolveUiTarget()` equivalent so the locus is unified across every input mode. Different input
  models (voice/gesture) still converge on the same sink.
- **REUSE the R2 ONE-CALL composition:** never hand-compose the ancestor chain. Call `context_at(address)` once
  → get the scored, capped, locus+ancestors bundle. This is the **one** composition point for addressed context.
- **CONSTRAINT — fail loud:** malformed `ui://` → 400, **never silent empty**. The surface must surface address
  errors (a Notice), never swallow them (mirrors the `act()` path; UI address errors are not recoverable).
- **CONSTRAINT — the 4000-char R2 budget** is a hard cap. If a locus is context-deep, show "n more beyond the
  cap" rather than overflow.
- **REUSE capability flags:** `pointable / spotlit / presentable / openable / drivenReadOnly` live in
  `UI_REGISTRY` / `UnionAddressRecord`, read via `/api/ui_info`. A non-pointable address is not click-indicated;
  a non-openable element does not expand on show. The surface gates its affordances on these.
- **REUSE presentation-pref (F1):** any "show me this differently" gesture POSTs to `/api/presentation-pref` so
  the learned pref persists and auto-applies on the next locus visit.
- **REUSE howto (D1):** the authored howto text is the source of truth for "what can I do here?" — surface it via
  `address_help`'s how-to-use leg; **never invent help text**.
- **AVOID:** copying any canvas chrome, layout, styling, component, or visual idiom. The address substrate is the
  ONLY inheritance. Build the rest clean from §E.

---

## §B — THE BRIDGE API CATALOGUE (the surface's data contract)

### What was explored (code-grounded)
`runtime/bridge.py:45-110` (`BRIDGE_ROUTES`, the single routing table; tests in
`tests/bridge_routes_acceptance.py` fail-loud if routes drift), plus per-route handler line cites below and
`runtime/projection.py` (the pure projection engine). 61+ endpoints across 6 categories.

### What was found — the catalogue (drive these)

**THE KEYSTONE — `/api/projection` (Tim's equation, pure read).** `bridge.py:1047-1115` + `runtime/projection.py`.
GET, **no store mutation**. Resolves everything from a file-discovered `BINDING` (registry-true).
- **Drivable axes (query params):** `binding=` (id) · `center=` (`ui://` address or `now`) · `at=` (epoch/ISO
  scrubber) · `limit=` · `since=` · `rung=` (coarse k) · `pole_a=` `pole_b=` (refs) · `types_space=` · `space=`
  · `dial=` (0–1) · `graph=` (scope).
- **Uniform response:** `{binding, points:[{angle, radius, sector, address, source_address, summary, depth, …}],
  scale?, separation_report?, nucleation?, error?}`. Angle θ from `binding.angle_from` (kind | kind-group |
  registry | graph | node-types). Radius r from `binding.radius_from` (time | semantic = 1−cosine | separator =
  two-gravity | nucleation = 20/80 water-law).
- **Variant helpers:** `_semantic_projection` (`:438-567`, the circle, scale-pyramid via `?rung=`),
  `_separator_projection` (`:569-633`, two-gravity, `separation_report` = THE FIFTH GATE),
  `_nucleation_projection` (`:635-750` + `projection.py:246-410`, the water-law, per-item placement +
  candidates + born flag).
- **Available bindings (file-discovered, `bindings/`):** `raw`, `by_lens`, `semantic`, `by_separator`,
  `by_nucleation`, `time-of-day`, `grouped`, `by_node_type`. **A new binding = a new file = a new lens, zero
  code edit.**

**THE LIVE SPINE — `/api/stream` (SSE).** `bridge.py:937-950, 870-930`. GET, no params. Tails the SHARED
`events.jsonl` (both faces). Cursor `?since=` or `Last-Event-ID` header (default −1 = from start). Heartbeat
~15s. Wire format `id: <seq>\ndata: <json>\n\n`. Fail-loud on real errors, silent only on client disconnect.
Reconnect resumes from the break (gapless — no teleporting; L3).

**ARRIVAL / GLANCE / SEARCH:** `/api/greeting` (`:1044`, caught-up-in-one-glance, `?since=`),
`/api/corpus-query` (`:1116-1139`, semantic search, `text=`/`space=`/`k=`, returns hits with 400-char heads),
`/api/now` (`:1042`), `/api/events` (`:1040`), `/api/conversations` + `/api/conversation` (`:1142-1145`, reopen).

**ADDRESS + CONTEXT (the §A read face):** `/api/ui_info` (`:1178`, the C1 registry + capability flags),
`/api/scope` (`:1182`, ui→code→scope), `/api/address-help` (`:1184`), `/api/context` (`:1194`, R2),
`/api/annotations` (`:1223`), `/api/presentation-pref` (`:1228`), `/api/chats` (`:1234`), `/api/address-history`
(`:1241`), `/api/self-changes-at` (`:1216`), `/api/stale-at` (`:1248`), `/api/ref-versions` (`:1258`),
`/api/up-translate` (`:1205`).

**COGNITION ENGINE (fire roles — the surface can ACT):** `/api/cognition/run_role` (`:2324`, fire one →
`run://` address + turn_id), `/api/cognition/run_items` (`:2331`, MAP one role over N), `/api/cognition/run_reduce`
(`:2336`, JOIN N `run://` → one), `/api/activation/tick` (`:2060`, manual drive of one activation — dormant by
default), `/api/cognition/list_runs` + `/api/cognition/find_runs` (`:1337-1347`, the #54 run index),
`/api/cognition/models_for_role` / `inputs` / `field_types` (`:1327-1336`, authoring selects),
`/api/cognition/find_relations` (`:1348`, L2 inversion-finder), `/api/cognition/corpus` (`:1356`).

**CONTENT / GRAPHS / SCALE:** `/api/corpus` (`:1005`, the gallery, disk-driven), `/api/graph` + `/api/graphs`
(`:1010-1013`), `/api/scale/build` (`:1985`, POST, build the pyramid) + GET (the built rungs), `/api/types`
(`:1018`), `/api/surfaced` (`:1038`).

**OPERATOR SURFACE:** `/api/inbox` (`:1148`), `/api/panels` (`:1154`), `/api/capabilities` (`:1156`,
auto-projects `api_verbs` from `BRIDGE_ROUTES` — **registry-is-truth, no hardcode list**),
`/api/capabilities/introspection` (`:1158`, the mirror-registry snapshot), `/api/object_info` (`:1014`),
`/api/cognition_info` (`:1016`), `/api/last-change` (`:1150`), `/api/self-change-log` (`:1152`, the audit ledger),
`/api/registry/proposals` (`:1180`, the RG8 proposal batch — **the seam for L15 promotion**), `/api/roles`
(`:1371`), `/api/run-stats` (`:1373`), `/api/knobs` (`:1375`), `/api/rhm-config` (`:1146`, GET/POST).

**VOICE / CHAT:** `/api/chat` (`:1140`), `/api/stt` (`:1800`), `/api/voice/stt-partial` (`:1812`), `/api/tts`
(`:1822`, routed by `ENGINE_PORTS` kokoro→4123 / chatterbox→4124 / orpheus→4125 / cosyvoice→4126 / xtts→4127 /
qwen3tts→4128, **fail-loud on unknown engine — never silent fallback**), `/api/voice` (`:1280`, STT/TTS status),
`/api/voice/engine-knobs` (`:1377`), `/api/voice/paths` (`:1379`), `/api/personas` (`:1315`), `/api/chat-models`
(`:1023`), `/api/models` (`:1020`).

**GRAPH MUTATION (builder):** `/api/run` (`:1953`), `/api/set` (`:1958`), `/api/move` (`:1963`, C5 drag-end),
`/api/node` (`:1969`, add from palette), `/api/connect` (`:1975`, type-checked wire), `/api/delete-node` (`:1980`).

**WALKTHROUGH / TRIAL / STUDIO:** `/api/review/current` + `/api/review/status` (`:1268-1271`),
`/api/journey/replay` + `/api/journeys` (`:1272-1279`), `/api/trial/sessions` + `/api/trial/transcript`
(`:1318-1326`), `/api/mockup-feedback` (`:1000`), `/api/fit` (`:1025`, S6 "tell me if my selection won't fit").

### WHAT IT MEANS FOR THE BUILD
- **The surface is THIN over a thick contract.** The "real" surface = point at `/api/projection`, render the
  geometry with addresses, wire to live `/api/stream`, pipe user actions to the cognition engine. Everything
  else is support, metadata, or operator-advanced.
- **CONSTRAINT — registry-is-truth, no hardcodes:** never hardcode sector counts, polygon geometry, color→kind
  maps, binding ids, pole vectors, or rung ladders. All resolve from the binding's `angle_from`/`radius_from`
  and the live registry. Drop a new binding file → it appears.
- **REUSE the uniform response shape:** `{binding, points, scale?, separation_report?, nucleation?}` is
  consistent across all projection variants — one renderer handles all lenses, switching on which optional
  blocks are present.
- **CONSTRAINT — fail-loud everywhere:** missing required params, type mismatches, unknown binding ids, absent
  pole vectors all surface as explicit 400s with messages, never silent 200-with-faked-value. The surface shows
  errors, never swallows them (mirrors §A).
- **REUSE the shared cognition engine:** `/api/cognition/*` is the SAME engine as `mcp_face/server.py` (never a
  parallel one). The surface fires roles directly (no MCP intermediary); responses carry `turn_id` + `op` for
  audit/retry. This is how L15 promotion actions execute.
- **REUSE `/api/capabilities`** to introspect what verbs exist — the surface can self-describe its own reach.
- **OPEN (resolve in Wave 2 / by reading):** the *complete* per-point field list from `project()`'s return; the
  exact `scale` metadata shape on coarse rungs (`scale_size`/`scale_exemplar`/`scale_members`/`scale_children` —
  always present or coarse-only?); the exact `address_help` structure (actions/context/hints); the precise
  `nucleation` per-item `sector` zone ids (`✦0…`) for candidate rendering.

---

## §C — THE COMPLETE REAL-DATA INVENTORY (the "heaps somewhere")

Tim said "there is data, there was heaps processed into the company somewhere." It was found. **Never a toy slice.**

### What was explored (code-grounded)
`/home/tim/company/.data/store/` (the unified `FsStore`), the registry directories (`roles/`, `projections/`,
`mark_types/`, `relation_types/`, `generation_policies/`, `ai_tics/`, `forms/`, `lifters/`), `projections/*.py`,
`design/_system/` (33 files), and the bridge routes that serve each store.

### What was found — the inventory

| Store / Registry | Path | Count |
|---|---|---|
| Events (full audit log) | `.data/store/events.jsonl` | **6,120** |
| Embedded corpus units (event-sourced) | `events.jsonl` `corpus.record` + `projections/` | **3,038** |
| Graphs | `.data/store/graphs/` | **72** |
| Versioned object refs | `refs/` + `ref_history/` | **18,119** |
| Cached embedding vectors | `.data/store/vectors/` | **2,793** |
| Scale pyramid records | `.data/store/scale/` | **3** |
| Marks (semantic overlays) | `marks.jsonl` (ai_fingerprint×1, built_twice×3, overlap×13) | **17** |
| Annotations (operator comments) | `annotations.jsonl` | **14** |
| Chat turns | `chat.jsonl` | **210** |
| Sessions (operator snapshots) | `sessions/` | **69** |
| Memoized computations | `memo/` (`sig_<hash>`) | **120** |
| Run metadata (exec traces) | `meta/` (`run__<graph>_<type>_<inst>.json`) | **87** |
| Cascades (declarative workflows) | `cascades.json` (`_doc`, `actions`) | **2** |
| Journeys (guided walkthroughs) | `journeys/` | **2** |
| Surfaced outputs (pre-rendered) | `surfaced/` (review×68, result×2, role_build×2, …) | **92** |
| Active locks | `locks/` | **16** |
| **Roles** (fire-able) | `roles/` | **29** |
| **Projections** (lenses incl. 5 corpus) | `projections/` | **8** |
| Mark types | `mark_types/` | **6** |
| Relation types | `relation_types/` | **6** |
| AI tics | `ai_tics/` | **7** |
| Forms | `forms/` | **4** |
| Lifters | `lifters/` | **3** |
| Generation policies | `generation_policies/` | **2** |

**The 5 corpus projection spaces (the embedded substrate):** `repo`, `history`, `topics`, `principles`,
`worldview` — extracted **live and event-sourced** (one `corpus.record` event per unit), queried via `/api/corpus`.
The three semantic spaces (`topics`/`principles`/`worldview`) each ≈162 items with **real 1024-dim BGE-M3
vectors**. **Inferred from cross-explorer cite:** repo ≈657, history ≈1,892 (the MANDATE's L0 figures; the
3,038 total is the verified union). Vectors re-used by semantic radius (G6), separator poles (G9), scale
centroids (G11), nucleation registry (G12).

**Design system:** `design/_system/` (33 files) — `addresses.json` (the `ui://` registry, **MANDATED preserve**),
`corpus-meta.json`, `tokens.json` (existing tokens — base palette reference), `mechanisms.json` (affordance
catalog), plus generators (`blueprint_emit.py`, `emit.py`, `check.py`, `navgraph.py`) and validation reports.

**One unified store.** `FsStore` is content-addressable, the SINGLE source of truth, shared by `bridge.py`
(HTTP/UI), `mcp_face/server.py` (MCP/agents), and `runtime/suite.py` (kernel). A write via the API is immediately
visible to MCP and vice versa — true one-entity system.

### WHAT IT MEANS FOR THE BUILD
- **Every lens renders non-empty.** 3,038 units, 6,120 events, 72 graphs, 2,793 vectors — every visualization
  has real backing. No placeholder/skeleton states are acceptable as the resting view (§9 of the bar: "connects
  to ALL the real data, never a toy slice").
- **REUSE the one store via the bridge** — no data silos to paper over; no parallel data path. The surface calls
  the API or (for agents) MCP; both hit the same `FsStore`.
- **REUSE the event-sourced corpus:** query the 5 projection functions once per session, cache the 3,038 units;
  they are derived live, always fresh.
- **REUSE full history:** 18,119 refs in `ref_history/` enable point-in-time recovery and version trails
  (`/api/ref-versions`, L6 prior versions) — the surface can show "how this got here," not just current state.
- **REUSE semantic search + scale:** 2,793 vectors + 3 pyramids = fast hierarchical semantic radius queries (the
  r-dimension); the scale pyramid is what makes rung transitions smooth (no-teleport, L3).
- **REUSE marks as visual hints (L2):** 17 marks + 14 annotations are semantic overlays (overlap, built_twice,
  ai_fingerprint) — render as glyphs/halos/warnings, not text walls.
- **REUSE run metadata for transparency:** 87 meta files + 120 memos let the surface show execution cost
  (time/model/tokens) per node run — transparency, not a black box.
- **CONSTRAINT (L13):** treat this entire inventory as the **starter project's data**. The data-source binding is
  a variable; nothing about these specific counts/spaces is hardcoded into the instrument.
- **CONSTRAINT (L14):** the **company MCP** (`mcp__company__create / ingest / corpus / node / run_role / mark /
  list_by_type / find_relations / …`) is the write-and-mould tool — use it to seed the starter project, embed
  registry definitions (so symbolic registries become nucleable — the previously-deferred gap), and extend spaces.
- **OPEN (resolve by reading):** whether `surfaced/` should show all 92 or latest-per-kind (ask `/api/surfaced`);
  whether the 3 scale records are per-graph or global; which corpus units carry marks (query path); how deep
  `addresses.json` is (10s vs 100s of addresses).

---

## §D — THE EQUATION / SEED PROPORTIONS + THE LENS CATALOGUE (re-home all of it)

The seed's geometry is **the visual language** (MANDATE §3), not just the data geometry. The instrument is a
**pure-read VARIABLE engine** — every slot (centre, angle, radius, depth) resolves from a declared binding.

### What was explored (code-grounded)
`runtime/projection.py` (Groups 2–12 line cites below), `runtime/scale.py` (the pyramid),
`build-prep/brain/THE-SEED-geometric-substrate.md` (§1–4, the proportions),
`build-prep/universal-projection/COMPLETION-CRITERIA.md` (§6–12 per-group criteria), `bindings/*.py`.

### What was found — the SEED proportions (the LAW, replicate exactly)

These are **constants, not parameters** — change them and the whole geometry re-orients. They are the grid the
**entire UI layout** is measured on (MANDATE L3: "nothing out of proportion"):

- **Dyadic grid:** `m = 2^d`, `d = min(segment-count, 4)` → `m ∈ {1,2,4,8,16}`. Built MSB-first per `_grid_cell`
  so a parent cell **contains** its children. Scheme-agnostic (`ui://`, `run://`, raw). (`projection.py:735-743`)
- **Concentric circles:** `rings = m/2` → `{1,2,4,8}` rings for `{2,4,8,16}` grid. (`:880-891`)
- **Even angular division (the lock):** `x = 2π/n` (TAU/n per sector). Sector i spans `[2π·i/n, 2π·(i+1)/n]`.
  Per-point jitter `θ = 2π·(i + 0.08 + 0.84·_stable_unit(ref))/n` (stable hash → spreads points within
  `[0.08n, 0.92n]` of the wedge, breaks ties deterministically). (`:774`)
- **Normalized radius band:** `[0.06, 1.0]` — the 0.06 floor keeps the nearest item off the origin (distinct
  from centre = r=0); nucleation pile rides `[1.04, 1.18]` outside the box.
- **Resonance law (SEED §4):** `2π/n = (1/n)^k` — binds angular partition (n = #types) to radial-recursive depth
  (k = #rungs). This is the commensurateness law between the wheel and the pyramid.

### What was found — the LENS CATALOGUE (re-home ALL of these)

| Group | Name | What it is | Engine cite | Binding | Operator drive |
|---|---|---|---|---|---|
| **G2** | Square / Structure | dyadic recursive grid + concentric circles (the spatial scaffold) | `projection.py:735-743, 880-891` | none (built-in) | none (read-only geometry) |
| **G3** | Time-Freed Centre / Scrubber | relative origin moves in space (address) + time (`?at=`); r = time-from-now OR tree-distance | `:607-611, 817` | `raw`, `by_lens` | scrubber ⏱, centre picker, re-centre |
| **G4** | Live SSE Pub-Sub | real-time event stream replaces polling | `bridge.py:1387-1418` | implicit | live/frozen toggle |
| **G5** | The Form Face | the lattice canvas on corpus tokens; angle-hue = geometry-colour | `canvas/.../LatticeView.tsx` | any | lens/centre picker, zoom, pick→card |
| **G6** | The Circle / Semantic Radius | r = 1−cosine meaning-distance from centre; vectorless → rim + flag | `:615-636, 779-792` | `semantic` | centre picker (must have a vector) |
| **G7** | Strain / Forbidden Zones | gap between FILED (structural r) and MEANS (semantic r); coherent → strain≈0 | `:706-733, 816-817` | none (emerges) | ⊿ strain toggle (radial tension segment) |
| **G8** | Embedding Substrate Live | 3 spaces (topics/principles/worldview, 162 ea) × 1024-dim BGE-M3 | `suite.py:capture_corpus_lenses`, `scale.py` | n/a (substrate) | none (bridge resolves vectors) |
| **G9** | Two-Gravity Separator | r = signed lean (pull_B − pull_A); **`separates` = THE FIFTH GATE** | `:650-682, 793-805` | `by_separator` | pole picker (`?pole_a=&pole_b=`), balance bar |
| **G10** | Connections / Typed Edges | sectors = registry rows; edges = directed chords (bidir = cycle) | `:426-533, 851-861` | `by_node_type`, `by_lens` | tap sector → OUT(gold)/IN(ink)/rest fade |
| **G11** | Multi-Scale Pyramid | WARD-clustered meaning-regions (centroids), nested, crossfade on step | `scale.py`, `:408+` | implicit (all semantic/nucleation) | rung-ladder picker (⊟ units/32/8), zoom-into-theme |
| **G12** | Type-Nucleation (20/80) | type items vs registry; misfits pile OUTSIDE; distinct piles → new types | `:246-410, 684-705` | `by_nucleation` | registry/store/rung pickers, **20/80 dial** |

**The two coordinate systems live on one projection:** SQUARE (discrete addresses) + CIRCLE (continuous
embeddings). Strain (G7) is the *gap between them*, rendered as radial tension. Every radius axis (time,
semantic, address-distance, separator, nucleation) returns normalized — the radial renderer treats all axes
**uniformly** (near=close, far=far); axis-switch is purely parametric (`binding.radius_from` + params), **no
per-axis branching** in the surface.

### WHAT IT MEANS FOR THE BUILD
- **REUSE the seed proportions as the LAYOUT GRID.** Every panel, control, stratum nests at dyadic depth; spacing
  respects the `m/2` rings; angular divisions even-wrap. The fresh design (§E) base spacing unit ties to the
  dyadic scale, not ad-hoc pixels. This is how "nothing is out of proportion" (L3) becomes structural, not policed.
- **RE-HOME all 12 groups** as first-class bindings in the shell. The shell swaps lenses *by name*; the engine
  resolves each binding's slots from data/params. The 8 discovered bindings are the stable palette; new ones
  auto-appear.
- **REUSE the uniform radial render** (one renderer, all axes) — keep this; it is what makes the lens-switch feel
  like one instrument.
- **REUSE the scale pyramid for no-teleport** rung transitions (crossfade, departing fades out / incoming fades
  in — never a mode switch). The centre is portable across rungs.
- **CONSTRAINT — the constants are LAW:** `m=2^k`, `m/2` rings, `x=2π/n`, the `[0.06, 1.0]` band, the
  `[0.08, 0.92]` jitter must be replicated exactly in the fresh substrate (both SVG viewBox and Canvas viewport
  lock to the same root grid — see §F).
- **REUSE the FIFTH GATE (G9):** show `separates: bool` as the headline (a calm warning when poles don't
  separate); the detailed `separation_report` is detail-on-demand (L6).
- **GROWTH FRONT (not gaps):** `relation_types` have no instances yet — G10 renders typed edges where they exist;
  as relations are declared they appear (the wheel grows). Purely-symbolic registries (no vectors) show G10
  connections but not G12 nucleation — clustering is scoped to embedded spaces. Embedding registry definitions
  (L14) is what unlocks G12 over the symbolic registries (in-scope, the deferred gap).
- **OPEN (SEED §7, Tim's structural call):** which two axes are the spine. Time is settled. The second
  (self↔world? a semantic axis? per-strata?) governs commensurate scaling via `2π/n = (1/n)^k`. **Blocks
  nothing** (the system is axis-agnostic) but is load-bearing for semantic-grid commensurateness — a render-react
  decision.

---

## §E — THE FRESH DESIGN LANGUAGE (proposed starting token set)

> **All of §E is a PROPOSAL to react to, not settled law (MANDATE §6, §8).** It translates L7 ("paper, not
> sci-fi; subtle, soft shading, elegant") into concrete tokens, every choice cited to 2026 design sources. Tim
> corrects by reacting to renders. The *direction* (warm neutral paper, soft diffuse elevation, low-saturation
> pigment, modular type, geometric polygons, unified eased motion, progressive disclosure) is **validated by
> 2026 convergence**; the exact hexes/ratios are starting points.

### What was explored (research-grounded)
zekagraphic.com, loungelizard.com, updivision.com (warm-neutral 2026 trend); ixdf.org, bighuman.com,
blog.netstager.com, fluent2.microsoft.design (neumorphism + soft-shadow elevation); fusioncharts.com,
letdataspeak.com, geeksforgeeks.org, cleanchart.app (calm data-vis = low saturation + limited palette);
ux-republic.com, imperavi.com, figma.com (modular 1.25 type scale); motion.dev, andarwaly.medium.com,
fluent2.microsoft.design (motion/easing); ixdf.org, uxpin.com, ui-patterns.com, primer.style, design.gitlab.com
(progressive disclosure); wikipedia.org/wiki/Calm_technology (calm tech = periphery); webosmotic.com,
medium.com/design-bootcamp (geometric polygons as scaffolding).

### What was found — the proposed tokens

**GROUND (warm paper neutrals — 2026 standard moves off stark `#FFFFFF`/pure black):**
- `--ground-primary: #F9F7F3` · `--ground-secondary: #F0EDEA` · `--ground-tertiary: #E8E4DF` ·
  `--ground-accent: #FEFDFB`. Warm, grounded, reduces glare, "intentional and soothing rather than empty."

**INK (warm near-black, used sparingly — softness is in shadow/shape, NOT in desaturated text):**
- `--ink-primary: #1A1612` (contrast 11.2:1 on `--ground-primary` — WCAG 2.2 AAA), `--ink-dim` for accents.
  Never pure black, never neon.

**PIGMENT (5 muted hues, 20–25% saturation, warm earth — colour MEANS, never decorates):**
- A semantic set: `arise/born` · `pile/forming` · `strain` · `lean-A` / `lean-B` · `accent`. The angle-hue
  (`sector i → hsl(360·i/n, …)`) is **preserved as colour-IS-geometry** — the one geometry-colour inheritance
  worth keeping. Pigment text where used clears 7.1:1+. (Calm aesthetics: 60/30/10 distribution; participants
  attribute a "more professional vibe" to less-saturated colour.)

**ELEVATION (Fluent-style key+ambient — "paper lift," NOT drop-box or glow):**
- 4 levels, ambient blur 2–12px (diffuse, distance), key offset 1–6px (directional, edge). Soft shadows paired
  with strong text contrast (the modern neumorphism rule: aesthetics + WCAG 2.2 AA+ coexist).

**TYPE (modular 1.25 ratio — Major Third, "harmonious, musical proportions"):**
- XS 12px → 2XL 40px; line-heights descend 1.6 (body) → 1.3 (display). One refined typeface; **words are accents**
  (L2). Serif+sans pairing for "fine paper" feel is a Tim-reacts choice (Charter+Inter / Crimson+Outfit /
  Lora+Inter).

**GEOMETRY (the seed's polygons as soft-filled shapes with hairline edges):**
- Square (structure), inscribed circle (meaning), dyadic grid (nesting), sector wheel (typed division), basins
  (two-gravity), rim blooms (nucleation). Radius: 4px cards / 2px chrome / 0px grids. "Soft circles + rounded
  corners feel warm" — calm confidence.

**SPACING (dyadic — ties the visual language to Tim's equation, §D):**
- Base 8px, doubling {8, 16, 24, 32, 48, 64, 96, 128}, 4px sub-grid. The seed's `m=2^k` proportions ARE the
  layout grid — "nothing out of proportion" (L3) by construction.

### WHAT IT MEANS FOR THE BUILD
- **BUILD A FRESH TOKEN FILE** (CSS variables) replacing the old harness palette wholesale (L7). Use the existing
  `design/_system/tokens.json` only as a base-palette *reference*, not a constraint.
- **The token system is ready for "show renders, Tim reacts"** — no foundational research gaps. Engineering can
  build the design-system infrastructure (CSS vars, animation primitives, breakpoints) in parallel with design
  refinement.
- **CONSTRAINT — accessibility is token-level, not patched at end:** WCAG 2.2 AA+ contrast, colorblind-safe
  pigments, `prefers-reduced-motion` respected. Softness lives in shadow/shape; text stays high-contrast.
- **CONSTRAINT — colour MEANS:** every pigment is bound to a data state (born/forming, fit/pile, lean A/B,
  strain) or to the angle-hue. No decorative colour.
- **AVOID:** neon-on-black, glows, hard borders as the primary elevation, saturated palettes, text walls. This is
  the opposite of the old dark harness.

---

## §F — RENDERING SUBSTRATE + THE SINGLE MOTION SYSTEM (no-teleport)

### What was explored (research-grounded + code-grounded)
aerotwist.com/blog/flip-your-animations (FLIP), caniuse.com/svg (96.7% support),
developer.mozilla.org Canvas/WAAPI docs, web.dev/animations-guide, motion.dev (Framer Motion),
developer.apple.com SwiftUI, docs.flutter.dev, benchmarks.slaylines.io (Canvas/WebGL density),
gsap.com, animate.style, en.wikipedia.org/wiki/Harmonic_oscillator (spring math),
pixijs.download (PixiJS), and the code-grounded `canvas/app/package.json` (React ^18.3.1, tldraw ^3.13.1,
Vite 6, **no motion library installed yet**).

### What was found — the recommendation

**SUBSTRATE: SVG (with a Canvas/WebGL layer for the dense point cloud) + Framer Motion / Motion.**
- **SVG + HTML DOM (React 18)** for interactive chrome: vector-crisp on retina (automatic), **native per-element
  `ui://` addressability** (L10 — every element is a real DOM node carrying `data-ui-ref`), and **free
  shared-element transitions** via Motion's `layoutId` + `layout` (the FLIP pattern: transform + opacity only,
  compositor-friendly, no teleport). SVG support 96.7% global, full on all target browsers + iOS Safari (Tim's PWA).
- **A reserved Canvas / PixiJS layer** renders ONLY the ~3,038-point cloud (embeds/events/marks) where per-element
  DOM identity isn't needed. Canvas/WebGL scale to thousands of objects where pure SVG does not. The `<canvas>`
  *container* lives in the DOM and animates via `layoutId`; points are static per-frame renders inside it.
- **AVOID pure-WebGL for everything:** it loses the DOM's free shared-element machinery and addressability and
  adds animation complexity. The hybrid keeps both.

**MOTION: ONE system, centralized (so motion feels authored, not per-component — L3).**
- **Spring presets (centralized tokens):** `gentle = {stiffness:100, damping:20, mass:1}`,
  `snappy = {stiffness:170, damping:15, mass:1}` (iOS-inspired). *Inferred from generic game-physics + Apple/
  Flutter ranges — verify against motion.dev source after build start.*
- **Durations (design tokens, not hardcoded):** appear/enter 300–400ms (spring); move/reposition 300–500ms
  (cubic-in-out); exit/disappear 250–350ms (cubic-out); colour/size 150ms (eased). Material's eased-out
  `cubic-bezier(0.4, 0, 0.2, 1)` is the validated default; spring vs eased-out is an aesthetic Tim-reacts call
  (L7 "subtle and soft" may favour gentle spring).
- **No-teleport rules:** every appear/disappear/move/resize tweens; shared `layoutId` per `ui://` element so
  hidden→shown animates without popping; reconnect on SSE drop resumes gaplessly (`Last-Event-ID`).
- **Compositor discipline:** animate ONLY `transform` + `opacity` (no margin/width/left → reflow); `will-change`
  only after observed jank; target 60fps.

### WHAT IT MEANS FOR THE BUILD
- **ADD Framer Motion / Motion** to `package.json` (currently absent; ~50KB gz; native React 18 hooks).
- **ARCHITECTURAL — addressing and layout-animation are INSEPARABLE:** every interactive node carries **both** its
  `ui://` address (L10) **and** a unique `layoutId` (L3). One identity, two faces (one for the relational spine,
  one for the motion system).
- **CONSTRAINT — proportioning at BOTH render levels:** SVG `viewBox` scaling and Canvas viewport scaling must
  lock to the same seed root grid (`m=2^k`, `x=2π/n`). Layout is parameterized on seed constants, never ad-hoc CSS.
- **REUSE one centralized motion token file** — shared easing/durations/springs applied everywhere. Inconsistent
  per-component motion reads as glitchy (an L3 violation).
- **PROGRESSIVE DISCLOSURE via `layoutId`:** hidden elements stay in the layout tree, so re-showing animates
  smoothly (no teleport) — this is how L6 and L3 cohere.
- **OPEN (resolve by prototype):** the pure-SVG ceiling for *simultaneously animated* interactive elements
  (resting state is near-empty per L6, so realistic active count may be <100 — a panel opening with ~20 moving
  sub-elements is the worst realistic case; this decides whether the cloud layer is ever needed for chrome);
  exact Motion spring defaults (verify vs source — WebFetch 404'd); how the Canvas point cloud animates in sync
  with DOM (container-via-`layoutId` is the recommendation, needs a prototype); whether any pseudo-3D
  (perspective concentric circles) is wanted (recommendation is 2D throughout — confirm by render).

---

## §G — PER-ORIENTATION LAYOUT SPECS + THE DISCLOSURE GRAMMAR

> L5 demands **three first-class form factors**, each AUTHORED, not responsive-degraded. Media queries trigger
> discrete layout-mode switches, never arithmetic scaling of one layout.

### What was explored (research-grounded)
Nielsen Norman Group (progressive disclosure, touch-target size, cognitive load, modal vs nonmodal, information
scent, visibility of system status), Apple HIG (safe areas, bottom sheets, 44pt targets, PWA iOS), Material
Design (layouts, bottom sheets, motion easing).

### What was found — the three layouts (authored independently)

**DESKTOP (1440×900):** central canvas (~1152px) + ambient side strata (256–288px, toggle) + top bar (56px) +
bottom control strip. Margins 32px, 12-col grid, base unit 8px. The instrument is centered with ambient strata.

**MOBILE PORTRAIT (390×844):** full-width canvas (358px usable) + **bottom sheet** (peek 60–80px, draggable
48pt handle, expands to 60% / 504px or full-screen for forms) + **thumb-reachable control arc** (easy zone
0–120px from bottom, center 40% width). Safe areas: 16px top (notch), 24px bottom (home indicator), 12px sides.
Base unit 4px. Word budget **2–4 words** (max density).

**MOBILE LANDSCAPE (844×390):** canvas left (~510px / 70%, full height) + **fixed right rail** (236px / 30%,
**persistent, non-modal**): top 120px = pinned detail/selection, next 120px = primary actions, rest = scrollable
secondary. The rail inverts the thumb-zone (right half = easy reach). Safe 16px top/bottom, 12px sides. Word
budget **8–12 words** (wider screen).

**Ergonomics (non-negotiable):** 44×44pt minimum touch targets, 12pt spacing (Apple HIG / Fitts' Law — "tiny
targets are the culprit, not fat fingers"). No hover-only controls on touch. Visible-but-untappable is worse than
missing (view-tap asymmetry).

### What was found — the DISCLOSURE GRAMMAR (one grammar, learned once, applied everywhere)

**Five-state cycle:** `RESTING (peek)` → `HOVERED (tooltip)` → `OPENED (panel/sheet)` → `PINNED (deliberate lock)`
→ `DISMISSED (swipe/click away)`. Universal across all three form factors.
- **Hover/tap parity:** desktop hover 200ms → tooltip, click → panel. Mobile tap-once → tooltip (tappable to
  advance), tap-twice/long-press → panel; dismissal symmetrical (hover-away/outside-click ; swipe-down/close).
- **Four patterns:** A (card/data) · B (control/action, confirmation toast auto-dismisses) · C (menu/list) ·
  D (form). Each follows the five-state cycle, adapted to context.
- **Text budget per form factor:** desktop 5–8 / portrait 2–4 / landscape 8–12 resting words. **Design
  resting-state FIRST (near-empty), graft detail onto disclosure states** — inverts the typical
  content-rich-then-prune workflow.
- **Information scent:** each control has a resting visual hint (icon/outline/faint colour) signaling "more here"
  WITHOUT text; labels specific ("Add item", "23°C"), never vague ("More", "Click here").
- **Modal vs nonmodal:** modal ONLY for critical/irreversible/required; **prefer nonmodal** for
  information-disclosure (background stays interactive — bottom sheet and right rail are nonmodal). Modal dialogs
  for low-priority content train users to ignore them (Boy-Who-Cried-Wolf).
- **Motion (shared with §F):** entrance 200ms (tooltip) → 300ms (panel), exit 200ms symmetric, same easing
  everywhere. Entrance/exit are semantic mirrors (fade-in ⇄ fade-out, slide-up ⇄ slide-down).

### WHAT IT MEANS FOR THE BUILD
- **THREE DISCRETE LAYOUT MODULES**, not one layout with breakpoint hacks. File structure includes
  form-factor-specific layout modules. Responsive collapse/expand of one layout does NOT satisfy L5.
- **BUILD A DISCLOSURE-STATE MACHINE** (resting/hovered/opened/pinned/dismissed), not ad-hoc hover/click handlers
  per component. The grammar is learned once and applied to every element — argues for uniformity over
  context-specific variation.
- **CONSTRAINT — text budgets are LOAD-BEARING** (L2), not guidelines. Audit on-screen word count per surface.
- **CONSTRAINT — safe areas** via `viewport-fit: cover` + `env(safe-area-inset-*)` for the iOS PWA (Tim's
  primary mobile). Content in unsafe zones is a hard failure.
- **CONSTRAINT — touch sizing constrains density:** a 390px portrait row fits ~6–8 buttons (44pt + 12pt) OR one
  dense column. Layout follows from the constraint, not the reverse.
- **VERIFY by DRIVE-in-browser** at 1440×900, 390×844, 844×390 — resting + hover/opened captures, real
  animations, real interactions. No "looks good in Figma." A SEPARATE design-critic judges the whole-screen
  gestalt (the §5 bar).

---

## §H — CORRECTIONS TO THE MANDATE / GUIDE

What the findings imply should change or be tightened. (The MANDATE's verbatim §0 is untouchable; these touch the
*expansions* and the downstream Implementation Guide / Completion Criteria.)

1. **The corpus is LARGER and differently-shaped than the MANDATE's mid-text figure.** §4 / L0 cites "≈3,038
   embedded units across repo (657), history (1,892), topics/principles/worldview (162 each)." The data explorer
   **verifies 3,038 total as the union** and confirms the 162×3 semantic spaces, but the repo=657 / history=1,892
   splits are **inferred (carried from the MANDATE), not independently re-counted** by the data wave. The
   Completion Criteria should cite **3,038 (verified union) + 6,120 events (verified)** and flag the per-space
   split as needing a confirming count. The MANDATE elsewhere says "6,119 events" — the live store has **6,120**;
   use 6,120.

2. **L15 "registry promotion" needs the EXACT seam named.** The MANDATE says reuse "the Company's existing
   proposal/approval seam, never a parallel one." The bridge wave found it: **`/api/registry/proposals`** (RG8,
   `bridge.py:1180`) is the read face for pending proposals; the **company MCP `propose_role` / `edit_role` /
   `delete_role`** and the cognition `run_role` path are the write face. The Implementation Guide should name
   `/api/registry/proposals` + the MCP propose verbs as THE promotion seam, and confirm whether a generic
   "promote candidate → proposal" verb exists or must be built atop `propose_*` (likely the latter — flag as
   in-scope per L14).

3. **L14 "embed registry definitions" is a real, concrete data task — not just latitude.** G12 nucleation only
   works over embedded spaces. To make the **symbolic** registries (roles, node-types, mark_types, …) nucleable
   (the keystone of L15's loop), their definitions must be **embedded into a vector space via the company MCP**
   (`ingest`/`corpus` + the `embed` role). The Completion Criteria should carry this as an explicit data-build
   criterion, not fold it into "data latitude."

4. **The substrate decision is no longer fully "engineer's call, surfaced" (MANDATE §8) — it is now grounded.**
   The substrate wave recommends **SVG + Canvas hybrid + Motion** with code-grounded reasons (addressability +
   shared-element transitions + retina + the existing React 18 stack, no animation lib yet). The Guide should
   adopt this as the recommended substrate and reserve "Tim reacts" for the *aesthetic* of motion (spring vs
   eased-out), not the substrate architecture.

5. **"No teleporting" (L3) has a concrete architectural requirement to add to the bar:** **every interactive
   element carries BOTH a `ui://` address AND a `layoutId`.** The §5 completion bar item #4 (smooth/no-teleport)
   and item #8 (addressed) are coupled by this single requirement — the Guide should state it as one rule so the
   two criteria are not built independently.

6. **The MANDATE's §4 worry "locate the heaps... somewhere" is RESOLVED** — the data is fully inventoried (§C).
   The Implementation Guide can drop the "find it" framing and replace it with the inventory table as a fixed
   reference. The remaining open items are *display* questions (all-92 vs latest, per-graph vs global scale), not
   *location* questions.

7. **`/api/projection` per-point field list and `address_help` structure are under-specified for the Criteria.**
   The bridge wave flagged that the *complete* point-field enumeration and the exact `address_help` shape aren't
   read out. The Guide should require a Wave-2 read of `projection.py`'s `project()` return and `Suite.address_help`
   before the renderer criteria are frozen (otherwise the renderer is built against an inferred shape).

8. **The query-string parsing inconsistency is a latent risk to note.** Some endpoints use `self._qs()` (flat,
   first-value) and others `parse_qs()` (nested lists). The surface should assume `_qs()` (single value per
   param). The Guide should flag this so the surface's request layer doesn't send array-style params to a flat
   parser (a fail-loud, but avoidable, 400).

9. **SSE handler line-cite conflict (two explorers disagree — reconcile by reading).** The bridge wave cites the
   `/api/stream` handler at `bridge.py:937-950` (with the route in `BRIDGE_ROUTES:45-110`); the equation/lens wave
   (G4) cites it at `bridge.py:1387-1418`. This cannot be adjudicated from the explorer reports alone. Wave 2 must
   read `bridge.py` and fix the canonical line number before the live-spine criteria are frozen — the *behavior*
   (SSE, `id:/data:` wire format, `?since=`/`Last-Event-ID` cursor, ~15s heartbeat) is consistently reported and
   is not in doubt; only the exact handler location is.

---

## §I — OPEN — TIM DECIDES BY REACTING TO RENDERS

These are taste/structural calls. Per the MANDATE, they are decided by **showing Tim renders he reacts to**,
never by asking him to spec. Consolidated from all seven waves.

**Aesthetic (show renders, Tim reacts):**
- **Typeface pairing** for "fine paper": Charter+Inter / Crimson+Outfit / Lora+Inter — render at the modular scale.
- **Pigment saturation:** is 20–25% the right "softness," or more muted? Render a data sample with all 5 pigments.
- **Dark mode:** is "dusk paper" (warm dark) a later addition, or paper-light only? (Paper-light leads regardless.)
- **Elevation steps:** are 4 shadow levels enough, or are intermediate steps needed?
- **Motion feel:** gentle **spring** vs Material **eased-out cubic** — bouncier/organic vs crisp. (L7 "subtle and
  soft" may favour spring; show both on a panel open.)

**Structural / shell topology (propose layouts, Tim reacts):**
- **Strata flow:** how do the multipurpose strata (greeting, inbox, builder, forager, panels, settings,
  self-change log, capabilities) arrange and flow into the instrument? Tabs / drawer / rail / modal stack /
  seamless slide? Propose per form factor.
- **Form-factor archetypes:** desktop two-rail · portrait full+bottom-sheet · landscape full+side-rail — native to
  Tim's use, or reshape?
- **Landscape right rail:** fixed 236px, or collapsible (icon-toggle to reclaim full canvas)?
- **Bottom sheet peek:** always show the next action (information scent), or first-tap-as-discovery?
- **Bottom sheet pinning across surfaces:** does a pinned sheet persist when navigating to another stratum, or unpin?

**Instrument display (render-react):**
- **R2 address-context display:** unify everything `context_at` returns into one stratum, or separate legs by kind
  (annotations / howto / events-timeline)? Show the pin affordance (mark "keep at top")?
- **Separation report (G9):** show the full report (distinctness, rank_corr, balance, leaders) in a detail panel,
  or just `separates` as a warning with detail-on-demand?
- **Nucleation candidates (G12):** halos? rings? zones? How is the born/forming distinction shown (the candidate
  `.born` flag)? How is the 20/80 dial gesture rendered?
- **The promotion gesture (L15):** the calm, animated, no-teleport gesture on a candidate bloom → proposal →
  on-accept the wheel re-divides live. Show the candidate evidence (size, margin, members) — text-minimal,
  visual-first. The exact gesture is a render-react decision.
- **Add-comment UX:** explicit "add comment" button per address, or implicit on the indicated locus (indicate →
  type in chat)?

**Equation (structural, Tim decides):**
- **The second spine axis** (SEED §7): time is settled; the other (self↔world? semantic? per-strata?) governs
  `2π/n = (1/n)^k` commensurateness. Blocks nothing; a render-react decision when the semantic grid is shown.

**Substrate (engineer-recommended, Tim comfort-input):**
- 2D throughout vs any pseudo-3D (perspective concentric circles). Recommendation: 2D. Confirm by render.

---

*This synthesis is grounded: the inward sections cite live code (the substrate the surface binds to exists and
works); the outward sections cite 2026 design sources (proposals to react to). Everything coheres to the
MANDATE's four quality axes — Tim's experience, the architecture, his equation, the systems. No ceiling.*