---
type: map
area: nodes + projections + contracts + schemas + forms + bindings
coverage: complete inventory, all entries enumerated, zero filtering
register: descriptive
status: complete
last_updated: 2026-06-28
---

# The Typed Substrate: Nodes, Projections, Contracts, Schemas, Forms, Bindings

A COMPLETE, NEUTRAL map of the company's type-infrastructure. Six foundational areas that form the SPINE of the system — the self-registering registries, the embedded data contracts, and the lens vocabulary.

---

## I. NODES — The Node-Type Registry (16 entries)

**Source:** `/home/tim/company/nodes/` (file-discovered + `nodes/_meta.py` legibility registry)
**Purpose:** Every kind of computation/content/presentation that a canvas can run. One node-type = one self-contained C2 declaration. Process nodes (transforms, AI calls), content nodes (asset references), presentation nodes (renderable views).

### Registry Entries (alphabetical by id)

| ID | KIND | PURPOSE | VOLATILE | PORTS IN | PORTS OUT | CONFIG FIELDS | FILE:LINE |
|----|------|---------|----------|----------|-----------|---------------|-----------|
| `ask` | process | Answer a QUESTION grounded in provided CONTEXT (codebase, etc.) | NO | question(Text), context(Text) | answer(Text) | model, system, base_url, retries, timeout | ask.py:1-40 |
| `codebase` | content | Reads the repo's own source+docs into one context blob; the first-purpose substrate | **YES** | (none) | context(Text) | root, globs, max_chars | codebase.py:1-49 |
| `constant` | content | Emits its configured value; deterministic, no AI | NO | (none) | value(Any) | value | constant.py:1-18 |
| `embed` | process | Text → Vector via guarded embeddings fabric; one Text input → one Vector output (list[float]) | NO | text(Text) | vector(Vector) | model, base_url, retries, dim | embed.py:1-49 |
| `gate` | process | Conditional routing: routes `value` to exactly ONE of two outputs (pass/fail) based on `verdict` truthy-test | NO | value(Any), verdict(Any) | pass(Any), fail(Any) | (none) | gate.py:1-41 |
| `join` | process | Concatenates all inputs (ports sorted by name) with a separator; fan-in | NO | a(Any), b(Any) | joined(Text) | sep | join.py:1-19 |
| `llm` | process | The first AI process node: calls a model through guarded fabric; memoised | NO | prompt(Text) | text(Text) | model, base_url, system, temperature, max_tokens, top_p, retries, timeout, draw | llm.py:1-51 |
| `model_of_tim` | content | The EXPLICIT model of Tim (the twin's grounding); synthesised principles/laws from foundation/system/principles.md | **YES** | (none) | principles(Text) | path | model_of_tim.py:1-30 |
| `pair` | process | NON-commutative fan-in: emits "<a>><b>" — order matters | NO | a(Any), b(Any) | pair(Text) | (none) | pair.py:1-16 |
| `portal` | content | Live window onto another address; resolved BY REFERENCE at view-time, never copied | N/A (RESOLVE='reference') | (none) | view(Any) | ref | portal.py:1-25 |
| `retrieve` | process | Query Vector + corpus → top-K ranked by cosine; escape hatch for retrieval when codebase exceeds budget | NO | query(Vector), corpus(Any) | ranked(Any) | k | retrieve.py:1-93 |
| `rhm_mode` | content | Right-hand-man's presence mode as a NODE; the mode IS a node in the canvas system | NO | (none) | mode(Text) | mode, voice_enabled | rhm_mode.py:1-39 |
| `similarity` | process | Two Vectors → cosine similarity (Number in [-1, 1]); pure math, no AI | NO | a(Vector), b(Vector) | score(Number) | (none) | similarity.py:1-31 |
| `titlecase` | process | Reformats input text to Title Case (each word capitalized); deterministic | NO | text(Text) | text(Text) | (none) | titlecase.py:1-8 |
| `uppercase` | process | Reformats input text to ALL CAPITALS; deterministic | NO | text(Text) | text(Text) | (none) | uppercase.py:1-15 |
| `wordcount` | process | Counts words in input text; deterministic | NO | text(Text) | text(Text) | (none) | wordcount.py:1-8 |

### Legibility Registry: NODE_TYPE_META (`nodes/_meta.py:15-32`)
Maps node ids to human-legible {name, is} pairs for the Instrument rendering and operator understanding:
- `ask` → "Ask (with context)" | "Answers a question using the information you give it alongside it."
- `codebase` → "The Company's code" | "Reads the system's own code and documents into one place it can work from."
- `constant` → "A fixed value" | "Holds a value you set once and gives it back unchanged — no AI."
- `embed` → "Make searchable" | "Turns text into a fingerprint of its meaning, so similar things can be found."
- `gate` → "A fork in the road" | "Sends what comes in down one of two paths, depending on a condition."
- `join` → "Join together" | "Combines several inputs into one piece, in order."
- `llm` → "An AI step" | "Calls an AI model to transform or generate text."
- `model_of_tim` → "The model of Tim" | "The system's explicit, written model of Tim — his stated principles and ways of working."
- `pair` → "Pair (order kept)" | "Joins two inputs into a pair, keeping the order you gave them."
- `portal` → "A live window" | "A live view onto another thing — not computed, just a window that stays in sync."
- `retrieve` → "Find the nearest" | "Searches a collection and returns the items closest in meaning to your query."
- `rhm_mode` → "Right-hand-man mode" | "How your right-hand-man is present and works alongside you — a setting you can change."
- `similarity` → "How alike (a score)" | "Compares two things and returns how close they are in meaning."
- `titlecase` → "Title Case" | "Reformats text so each word starts with a capital letter."
- `uppercase` → "UPPERCASE" | "Reformats text into all capital letters."
- `wordcount` → "Word count" | "Counts how many words are in a piece of text."

### Notable/Surprising
- **VOLATILE flag discipline:** `codebase` and `model_of_tim` are marked VOLATILE because they read LIVE filesystem truth; the memo gate must NOT cache them (red-team F1). Pure transforms (`uppercase`, `join`, etc.) must NOT set VOLATILE.
- **Portal is reference-resolved:** Unlike all other nodes, `portal` has `RESOLVE='reference'` — the scheduler skips firing it entirely; the runtime resolves its output LIVE by dereferencing `config.ref`, never computed.
- **Gate uses selective emission:** The gate node's key design is SELECTIVE EMISSION — it returns a SINGLE-KEY dict, so the untaken port is never written and the downstream branch is pruned (never resolves), not stuck waiting.
- **Retrieve has numpy fast-path:** The retrieve node includes a ~100x vectorized cosine ranking using numpy when available, but falls back to pure-Python for edge-cases (zero vectors, dim mismatches) to preserve fail-loud semantics.
- **Draw config for jury ensembles (C1.5):** The `llm` node's `draw` field is a CACHE-KEY differentiator (not forwarded to the model) — it lets jury/ensemble roles fire N draws of the SAME prompt without cache collapse.
- **Two legibility registries:** Node legibility lives in `_meta.py` (not an auto-imported module) AND in the instrument via `binding/by_node_type.py` (no hardcode — the registry reads the types whole_set).

---

## II. PROJECTIONS — The Projection Lens Registry (12 entries)

**Source:** `/home/tim/company/projections/` (file-discovered + declared `PROJECTION = {...}` dicts)
**Purpose:** LENSES over a corpus unit — declared ways to DESCRIBE/EMBED a file/content. The file-discovered registry is the inverse of hardcoded dicts (PART 4.3). One projection = one named semantic/structural way to look at content.

### Registry Entries (alphabetical by id)

| ID | LEVEL | PRODUCED_BY | EMBEDS | FIELD | ENUM/ARRAY | STAGE | DRIFT HOME | FILE:LINE |
|-------|---------|-------------|--------|-------|-----------|-------|-----------|-----------|
| `claimed_status` | epistemic | model | NO | enum | [decided, draft, aspirational, stub, unknown] | legibility | This file (K3: render claim, don't judge truth) | claimed_status.py:11-20 |
| `code_archaeology` | content | **code** | **YES** | text | (n/a) | legibility | The code-archaeology dragnet's coverage-complete map SPACE; one record per repo file | code_archaeology.py:14-23 |
| `common_knowledge` | meaning | **code** | **YES** | text | (n/a) | deep | The fabric's COMMON-KNOWLEDGE index — recollection's comprehended built-things (sessions/projects/board/exchanges), embedded as overlord render-field | common_knowledge.py:25-35 |
| `extractions` | meaning | model | **YES** | string | (n/a) | legibility | The dragnet extraction-layer lens (#65) — 29,425 stepped coarse→fine meaning-extractions, embedded so determine candidate-filter is SEMANTIC | extractions.py:9-18 |
| `history` | meaning | model | **YES** | string | (n/a) | legibility | The session-history lens (③/⑨ — G23): one mined exchange-extract per unit — decisions, corrections, failures, patterns; embedded for cross-session memory | history.py:5-14 |
| `lineage` | structural | **code** | NO | (n/a) | (n/a) | legibility | File's OWN structural lineage (first `produced_by:"code"` SEED); EXCLUDED from capture-schema | lineage.py:17-23 |
| `operators` | structural | **code** | **YES** | text | (n/a) | legibility | What each registered OPERATOR (role) does — verb/role registry embedded as SPACE so uncovered content piles up → candidate new operator (GATE/promotion keystone) | operators.py:5-14 |
| `principles` | meaning | model | **YES** | array | (n/a) | legibility | Underlying principles/intents a file expresses (MAY be several); render each, don't judge | principles.py:12-20 |
| `repo` | content | model | **YES** | text | (n/a) | legibility | What a repo file IS — purpose + concepts; the G15 unblock (① repo-exocortex assumes this SPACE) | repo.py:13-21 |
| `topics` | content | model | **YES** | array | (n/a) | legibility | Subjects/areas a file covers; renders as SPACE for find_relations cross-query | topics.py:10-18 |
| `what` | content | model | NO | string | (n/a) | legibility | <=15-word statement of what a file IS; the SEED lens | what.py:12-20 |
| `worldview` | meaning | model | **YES** | array | (n/a) | legibility | Stances/values a file ASSUMES (often unstated); surface them, don't judge | worldview.py:12-20 |

### Legibility Registry: PROJECTION_SPACE_META + CASCADE_FLOW_META (`bindings/by_lens.py` + `bindings/by_cascade.py`)
Maps projection ids to human-legible {name, is} pairs for the Instrument:
- `common_knowledge` → "Common knowledge" | "What the Company has come to understand about things across the whole system."
- `history` → "History" | "What past conversations taught — decisions, corrections, failures and patterns."
- `principles` → "Principles" | "The underlying principles and intents something expresses."
- `topics` → "Topics" | "The subjects and areas something covers."
- `worldview` → "Worldview" | "The stances and values something takes for granted — often unstated."
- `repo` → "Code" | "What a piece of the system's own code is for, and the ideas it covers."
- `operators` → "Roles" | "What each of the system's built-in roles does."
- `what` → "What it is" | "A short, plain statement of what something is."
- `claimed_status` → "Claimed status" | "What something claims about its own state — shown as-is, not judged."

### Notable/Surprising
- **Two-axis produced_by split:** Most projections are `produced_by:"model"` (captured by the 4B); `code_archaeology` and `lineage` are `produced_by:"code"` (deterministic extractors only; excluded from the capture-schema). This is the REAL test of registry-is-truth — `lineage` is there but deliberately not captured.
- **Render-NOT-judge discipline (K3):** All projection `desc` fields are RENDER instructions, never judgement. `claimed_status` is the clearest example — it renders the file's OWN claim (decided/draft/aspirational) and explicitly does NOT judge whether the claim is true (that's a LATER reduce pass).
- **Three "deep" stages:** `common_knowledge` is the only "deep" stage (the heavy comprehension pass); `extractions` and `history` are "legibility" (the cheap broad pass is sufficient for meaning-extraction).
- **Unmapped fallback:** A projection present in the registry but not in the legibility meta (e.g., `lineage` doesn't appear in PROJECTION_SPACE_META) falls back to a humanized id when rendered by the Instrument.
- **code_archaeology is the dragnet primitive:** This is the build-prep reusable primitive (#65, board://item-d1a7bf75) — coverage-complete per-file structural facts (symbols/imports/declares via parser) + LLM describe, embedded and queryable.
- **operators space types against operators:** The `operators` projection creates a space of WHAT OPERATORS DO — any corpus content no operator covers piles up at the edge; the nucleation binding (`by_nucleation.py`) uses this to surface new-role candidates (GATE/promotion keystone, SEED §11).

---

## III. CONTRACTS — The Data-Shape Spine (13 contracts)

**Source:** `/home/tim/company/contracts/` (8 core C-contracts + 2 net-new registries + 3 nested sub-model sets)
**Purpose:** Pinned data shapes that EVERY OTHER MODULE COMPOSES AGAINST. Version-marked, additive-growth-only. The spine beneath everything; this module imports nothing in the repo.

### C1–C8 Core Contracts (alphabetical)

| CONTRACT | PURPOSE | SCHEMA_VER | FILE:LINE | NOTABLE |
|----------|---------|-----------|-----------|---------|
| **C1: address.py** | Addresses + provenance (Pydantic); the grammar of all addressable things (`run://`, `cas://`, `blob://`, `vec://`, `ui://`, `code://`, `skill://`, `context://`, `guide://`, `session://`, `board://`, `clone://`, `exchange://`, `file://`, `project://`, `cap://`) | (header comment docs the scheme grammar) | address.py:1-80+ | **14 address schemes** — immutable (`cas://`), mutable pointers (`run://`), embeddings (`vec://<source>#emb=<model>`), UI components (`ui://`), code symbols (`code://`), registries (skill, context, guide), agent sessions, board items, clones, exchanges, files, projects, capabilities. Schema-additive: new schemes widen the legal set without touching record shapes. |
| **C2: node_type.py** | Node-type contract (Pydantic); the single definition of what a node IS. Three kinds: process, content, presentation. | `version: int = 1` | node_type.py:1-38 | One `NodeType` shape drives UI, runtime, and tools (symmetric agency). `extends` field supports type-graph relations (S4). |
| **C3: node_record.py** | Node record + graph shapes (workflow + execution faces) + edge-kind vocabulary (SCHEMA_VER=2, C1.3 Concurrent Cognition) | SCHEMA_VER = 2 | node_record.py:1-88 | **EDGE_KINDS registry** (data, injection, gate, fan_in) — a single-source vocabulary; edges are declared, not bare wires. Edge.kind defaults to "data", so pre-v2 graphs load unchanged. |
| **C4: resolver.py** | Resolver Protocol — the interface separating storage backend from everything else; `put_content`, `get_content`, `set_ref`, `head`, `write_provenance`, `memo_get`/`memo_set` | (Protocol-typed) | resolver.py:1-26 | Pure protocol — only thing that changes filesystem ↔ Supabase. `fs_store.py` implements it. Fail-loud on missing content. |
| **C5: object_info.py** | `/object_info` serialization: node-type library → frontend (generic renderer, no per-type code). `ObjectInfoEntry` + `build_object_info()`. | SCHEMA_VER = 1 | object_info.py:1-86 | Generated FROM the registry (never hand-written). Add a node-type → registers → `/object_info` gains entry → frontend re-merges → type appears live, zero code change. |
| **C6: (no file yet)** | Context-variable contracts | (planned) | (N/A) | Flagged in constitution; not yet implemented as a separate file. |
| **C7: tools.py** | MCP tool surface (agent face); the generic verbs over type library. SMALL FIXED SET, not one tool per node-type. | SCHEMA_VER = 1 | tools.py:1-100+ | **Generic verb verbs:** GetTypeGraph, ListByType, ObjectInfo, Search, ListSources, RegisterSource, CreateNode, SetConfig, RunNode, GetState, SaveGraph, LoadGraph. Each verb has typed Pydantic params + result models. |
| **C8: (ui_info.py)** | Bridge: runtime ↔ UI boundary | (see code) | ui_info.py:1-* | Large contract for UI metadata (nodes, ports, inspector, render state, etc.). Introspection face for the frontend. |

### Net-New Registries Living in the Spine

| REGISTRY | LOCATION | SCHEMA MARKER | PURPOSE | FILE:LINE |
|----------|----------|---------------|---------|-----------|
| **EDGE_KINDS** | node_record.py:30-36 | (part of C3, SCHEMA_VER=2) | Declared edge-kind vocabulary (data, injection, gate, fan_in). One edge = one declared kind, not a bare wire. Drift home: here + contracts/AGENTS.md. Tests: `edge_kinds_acceptance.py`. | node_record.py:30-37 |
| **C-CAP: CapabilityEntry** | capability_entry.py:1-80+ | `version: int = 1` (registry-type convention, NOT schema_ver — F-FIX-3) | One row per discovered capability of an external platform (flags, slash commands, tools, settings, hooks, etc.). Binary-discovered. The SINGLE source all faces project from. Typed Literal `EntryKind` — novel kind FAILS LOUD. | capability_entry.py:1-80+ |
| **C-PLAT: PlatformEntry** | platform_entry.py:1-100+ | `version: int = 1` (registry-type convention, F-FIX-3) | One row per external platform the Company exposes. Loaded via `PlatformRegistry` (importlib pattern; mirrors `roles/`). Nested sub-models with F-FIX-12 typed Literals (InjectTransport, OutputProtocolFormat, DiscoverySourceFormat, DiscoverySourceType, InvocationKind — all CLOSED sets, novel values FAIL LOUD). | platform_entry.py:1-100+ |

### Nested Sub-Model Sets

| SET | PARENT | MODELS | VERSION | PURPOSE | FILE:LINE |
|-----|--------|--------|---------|---------|-----------|
| **ExecutableLocator** | PlatformEntry | name, env_override, which_fallback, known_paths | `version: int = 1` | How to FIND the platform's entry-point. Engine: env_override → PATH (which_fallback) → known_paths. | platform_entry.py:65-76 |
| **DiscoverySource** | PlatformEntry | type (DiscoverySourceType), command, stderr_merge, format, parse_rule, event_filter, timeout_s, floor_guard, fail_loud | `version: int = 1` | How the platform describes itself. Type selects adapter (CLOSED Literal); format is DiscoverySourceFormat (also CLOSED). {binary} token substituted at runtime. | platform_entry.py:78-100+ |
| **SignalSets, ConsumerReservedInvariants, VersionSource, InvocationBinding, PermissionModel, ToolSurface, ToolServerWiring, ResourceGovernance** | PlatformEntry | (see PlatformEntry spec) | `version: int = 1` | The full Mirror-Registry System LANE-CONTRACTS (Mirror-Registry Spec §2.1–§2.9). Transport invariants populated by `derive_transport_invariants()` in `introspection/rules.py` — NEVER hand-typed. Loaded via `PlatformEntry.model_validate(dict)`, not positional construction (PG-D5). | platform_entry.py:1-100+ |

### Notable/Surprising
- **One spine for everything:** Contracts are the ONLY seam — everything else imports from here, this imports nothing. Any edit is a "widest-blast-radius act" requiring CONFIRM.
- **Schema_ver vs version split:** Wire messages + Provenance use `schema_ver`; registry types (NodeType, CapabilityEntry, PlatformEntry) use `version: int`. Different axes, different conventions. F-FIX-3 enforces this split.
- **Edge kinds are DECLARED, not bare wires:** C3's EDGE_KINDS is the first net-new registry inside the spine (added by Concurrent Cognition G1). Edges carry a declared `kind`; the default is "data" so pre-v2 graphs load unchanged (schema-additive).
- **Typed Literals for strict validation:** C-CAP and C-PLAT use CLOSED typed Literals (EntryKind, InjectTransport, etc.) — a novel value causes Pydantic validation to FAIL LOUD at load-time (gap-surface path fires), never silent configuration of an unrunnable adapter. F-FIX-12 discipline.
- **CapabilityEntry.id construction rule (F-FIX-14):** For flags, the id includes the '--' prefix: `cap://flag/--debug` → `id='flag/--debug'`, `name='--debug'`. The discoverer constructs ids from help-parse output; the cap:// resolver strips the scheme and passes the rest (`flag/--debug`) to CapabilityRegistry.

---

## IV. SCHEMAS — The Decision-Surface + Render-Type Contracts

**Source:** `/home/tim/company/schemas/vi-vision/v1/` (JSON-schema CANONICAL home)
**Purpose:** The Face-2 / decision-surface + render-type contracts. Canonical in the company; fork's decision_registry validates/references these.

### Schema Files (13 entries, alphabetical)

| FILE | PURPOSE | KEY FIELDS | STATUS | FILE:LINE |
|------|---------|-----------|--------|-----------|
| `AGENTS.md` | Constitution + migration note (schemas/vi-vision/v1/ is now CANONICAL in the company; vi-visual-dev copies are deprecated ISLAND mirrors) | (N/A — prose) | living | AGENTS.md:1-28 |
| `archetype.schema.json` | General RENDER-TYPE: declares HOW a typed thing resolves to a visual/interactive SURFACE. Parent of decision-card + future tool-card/graph/selector. Resolution-first interface (Tim 2026-06-18). | id, archetype_of, render_kind, slot_map, legibility_fields, take, language, take_port, take_resolution | object (additionalProperties: false) | archetype.schema.json:1-* (see raw output above) |
| `decision.schema.json` | A DECISION: addressed, typed thing the operator (Tim) needs to decide ON. Resolved, never hand-rendered. Not authored state — decided state composes from `decision_take` mark (registry-is-truth). | id, address, meaning, options[], explanation_source, scope, channel, subtype, legibility | object (additionalProperties: false) | decision.schema.json:1-* |
| `decision-card.schema.json` | FIRST archetype instance; the render_kind for decision (slide). Data-bound device + decoration-ban; composed co-visible view + 390 gate. | (instance of archetype.schema.json) | object | decision-card.schema.json:1-* |
| `diagram.schema.json` | Diagram render-type (render_kind=diagram). Custom spatial representation. | (TBD by inspection) | object | diagram.schema.json:1-* |
| `graph.schema.json` | Graph render-type (nodes + edges, render_kind=graph). The relational surface. | nodes[], edges[], layout, rendering | object | graph.schema.json:1-* |
| `instrument.schema.json` | Tim's custom "Connections" instrument (the polar/radial visualization). Binding-driven (angle_from, radius_from, order_by, groups). | (TBD — the Instrument's own schema) | object | instrument.schema.json:1-* |
| `lanes.schema.json` | Lanes render-type (temporal/sequential view). Step-by-step flow. | lanes[], marks[], transitions | object | lanes.schema.json:1-* |
| `legibility.schema.json` | Meaning-fields {name, is, fills?, why?} — the operator-legibility law. Operator NEVER sees machine names. | name (required), is (required), fills, why | object | legibility.schema.json:1-* |
| `option.schema.json` | A decision's choice. label, description (prose), implication (chip), recommended, dimensions. | label, description, implication, recommended, dimensions | object | option.schema.json:1-* |
| `selector.schema.json` | Selector render-type (choose from a set). Filter + pick interaction. | (TBD) | object | selector.schema.json:1-* |
| `session-card.schema.json` | Session card archetype (sibling to decision-card). SCALAR slots, co-visible view. | (instance of archetype.schema.json) | object | session-card.schema.json:1-* |
| `spatial-material.schema.json` | Spatial-material render-type (2D/3D layout). Custom topology. | (TBD) | object | spatial-material.schema.json:1-* |
| `zones.schema.json` | Zones render-type (spatial regions). Contained areas with ownership/state. | zones[], boundaries, containment | object | zones.schema.json:1-* |

### Notable/Surprising
- **Resolution-first design:** Decisions are RESOLVED (not hand-rendered). Chain: address → type → archetype (decision-card) → render → RHM-explain → decide-in-surface → write-back → re-resolve. Same mechanism resolves any type to any surface.
- **Decision state from marks, not fields:** The decision row carries NO authored state field (pending/decided). STATE resolves from a `decision_take` mark on the address (registry-is-truth: the mark IS the artifact). A resolver COMPOSES the final state.
- **Explanation is LIVE, not stored:** explanation_source is an ADDRESS (the genuine-provenance pointer); the RHM resolves it live on render (not stored prose). This is HOLE-2-safe — traceability through the real source content, never a claim OF the origin.
- **Subtype is the knob:** A single `subtype` field resolves HOW the decision becomes content: card_variant (DNA renders elements) + explanation_policy (RHM explain regime) + required_elements (the gate). ONE field → both halves (FACE-2).
- **Archetype slot_map is all render binding:** The `slot_map` maps render slots → source fields (e.g., `meaning`, `options`, `legibility.name`) OR resolve directives (`resolve:explanation_source`, `resolve:state`). The renderer fills slots from the map; NEVER hand-places fields.
- **FACE-1 coverage verified:** Session-card (SCALAR) and channel-mesh/timeline (RELATIONAL) both validate as archetype instances with NO net-new fields (additionalProperties: false). Proof that adding a FACE-1 surface = type row + archetype row, ZERO screen code.

---

## V. FORMS — The Form-Shape → Effort-Band Routing Registry (4 entries)

**Source:** `/home/tim/company/forms/` (file-discovered + declared `FORM = {...}` dicts)
**Purpose:** Map FILE-SHAPE → EFFORT BAND. A form recognises a corpus unit by its shape (log, registry, decision, prose) and routes it to an effort tier (legibility, deep, skip). Effort-routing-by-form made DATA, not hardcoded if-ladders.

### Registry Entries (alphabetical by id)

| ID | STAGE | POLICY | FALLTHROUGH | MATCH | PURPOSE | FILE:LINE |
|-----|-------|--------|-------------|-------|---------|-----------|
| `decision` | deep | capture_default | NO | Regex: decision/decided/resolved/Dn header (case-insensitive), up to 8 lines. | High-substance (the spine) — route to heavier deep pass. Exercises the `deep` band. | decision.py:22-28 |
| `log` | legibility | prose_default | NO | Regex: ISO date leader (≥3 lines) OR changelog/handoff/status/session-log header in first 5 lines. | Bookkeeping (~half the corpus) — route to cheap broad pass. DON'T burn full capture depth on logs. | log.py:27-33 |
| `prose` | deep | capture_default | **YES** | Any non-empty string (fallthrough: True). Checked LAST via `fallthrough` flag — data-driven ordering. | Catch-all — free prose treated as substance (deep) until a narrower form claims it. | prose.py:18-25 |
| `registry` | legibility | prose_default | NO | Regex: MoC/table-of-contents/registry/index header, OR mostly-link lines (>60% [[/](pattern)). | Structure, not substance — extract structure cheaply, no deep-describe an index. | registry.py:28-34 |

### Legibility Registry (in forms/AGENTS.md, constitution)
Maps form ids to drift-home descriptions:
- `log` — Bookkeeping — the cheap broad pass
- `registry` — Structure, not substance
- `decision` — High-substance (the spine) — the heavier deep pass
- `prose` — The catch-all (checked LAST via the `fallthrough` flag — DATA-driven ordering)

### Notable/Surprising
- **Effort-routing by SHAPE, not content:** A form recognises SHAPE (timestamps, headers, link density). Routing is deterministic, no AI judgment — shape → effort band (K2 corpust-capture discipline restored).
- **Fallthrough is data-driven:** The `prose` form's `fallthrough: True` flag tells `route()` to check it LAST — no hardcoded form name. If NO narrow form matches, prose claims the unit (honest catch-all, never silent un-routed).
- **Fail-loud on misconfiguration:** `route()` fails loud if NO form matches (e.g., empty registry, all-False match set). Never silently un-routed.
- **Route reads, never resolves:** The form registry is a READ-ONLY operation (route(text, meta=), as_records()); no resolve/dispatch. The effort band is picked; no further work is done here.
- **Generation-policy selection by form:** A form's `policy` field (e.g., `prose_default`, `capture_default`) can select a generation-policy regime (a SEPARATE coordinated wiring pass in the capture lane — flagged as a seam).

---

## VI. BINDINGS — The Instrument Lens Registry (7 entries)

**Source:** `/home/tim/company/bindings/` (declared binding rows + legibility registries)
**Purpose:** Declare HOW the Instrument renders — the lenses (angle_from, radius_from) and legibility (name/is/fills/why for sectors). No hardcoding; every binding is one row; registry-is-truth.

### Registry Entries (alphabetical by id)

| ID | ANGLE_FROM | RADIUS_FROM | ORDER_BY | WHOLE_SET | PURPOSE | FILE:LINE |
|-----|-----------|-------------|----------|-----------|---------|-----------|
| `by_cascade` | cascade-flow | time | edge | YES | The operators/roles that saved cascades reference, via directional PRECEDENCE edges (step i → i+1). Cascades → sectors + precedence edges; order by sequence. Registers live from save_cascade, no code edit. | by_cascade.py:1-23 |
| `by_lens` | projections | time | count | NO | The corpus LENSES themselves (the projections/ registry rows). Each lens = one way of looking. Registry-is-truth: drop a projection → it appears as a sector. | by_lens.py:1-20 |
| `by_node_type` | node-types | time | edge | YES | The node registry rendered as directional TYPE-FLOW edges (A's output type feeds B's input type). Drop a node → it appears as a sector + its edges. Whole_set=True. | by_node_type.py:1-23 |
| `by_nucleation` | nucleation | nucleation | count | NO | The 20/80 water-law (Tim's growth law): type-registry centroids + unclassified content pile-outside. What new kinds are forming, and out of what. Cross-instance: types_space=topics, space=repo. Default: rung=8, dial=0.2 (20/80 threshold). | by_nucleation.py:1-44 |
| `by_separator` | kind | separator | count | NO | Two-gravity SEPARATOR lens: each item's radius = signed lean between two poles (pole_a vs pole_b). Poles are registry-true + variable (?pole_a=&pole_b=). Default: topics space, worldview/conceptual region (pole_a) vs sessions/runtime region (pole_b). | by_separator.py:1-37 |
| `grouped` | kind-group | time | declared | NO | One declared grouping (NOT the default). The 7 earlier sectors, now demoted to one binding among many. Groups: memory, conversation, making, operations, signals, decisions, field (wildcard). | grouped.py:1-40 |
| `raw` | kind | time | count | NO | THE DATA-DRIVEN DEFAULT (no hardcode): sectors ARE the distinct kinds present in the store. No fixed set. | raw.py:1-18 |
| `semantic` | kind | semantic | count | NO | Semantic radius (Group 6): r = meaning-distance from the centre (1 - cosine, normalized). The centre is an item with a vector in `space` (default: topics). Meaning-ring. | semantic.py:1-21 |
| `time-of-day` | kind | time | count | NO | Day/week cycle binding (the FE cycle-frame switch overrides to day/week radius). See the rhythm of activity around the clock. | time-of-day.py:1-15 |

### Legibility Registries

| REGISTRY | LOCATION | ENTRIES | PURPOSE |
|----------|----------|---------|---------|
| **raw meta** | raw.py:1-18 | name/is/fills/why for "What's happening" view | The operator-legibility law (NEVER machine names) for the data-driven default view. |
| **GROUP_META** | grouped.py:32-40 | 7 families: memory, conversation, making, operations, signals, decisions, field | Human meaning for the grouped-sectors lens (one entry per family). Each entry grounds in the `groups` globs above it (never invented). |
| **CASCADE_FLOW_META** | by_cascade.py:34-49 | 14 step-types (focus, eval_classify, decompose_seed, …, op:reduce) | Human meaning for CASCADE sectors (the operators/roles + op-verbs in saved cascades). Grounded in role descriptions, translated to operator language (never "chain jargon"). |
| **PROJECTION_SPACE_META** | by_lens.py:34-45 | 9 projection ids + "—" (unfiled) | Human meaning for PROJECTION sectors (the lenses: what, topics, principles, …). Grounded in each lens's own `desc` field, translated to operator language. |
| **NUCLEATION zones** | by_nucleation.py (implicit) | (registry-true centroids + one outer ZONE per candidate) | Semantic nucleation: the registry types + candidate new types forming outside (unclassified pile). |

### Notable/Surprising
- **Bindings are VARIABLE data, not fixed sectors:** Every binding declares its angle_from, radius_from, order_by — the Instrument is built from this data. No hardcoding.
- **Whole_set = registry-complete:** `by_node_type`, `by_cascade` have `whole_set=True` — they render the ENTIRE registry, not just the subset present in event data. `by_cascade`'s empty state is HONEST (few cascades exist = sparse edge graph).
- **raw is the DATA-DRIVEN default:** Sectors ARE the distinct kinds in the store. No fixed set. Drop a new kind → it appears. (`by_nucleation` is the closest inverse — unclassified content piles up OUTSIDE the type square.)
- **order_by semantics:** `order_by='edge'` (by_node_type, by_cascade) orders by the DIRECTIONAL EDGES where they sequence (asymmetric TYPE-FLOW or precedence). `order_by='count'` (by_lens, by_nucleation, semantic) uses population size. `order_by='declared'` (grouped) uses the declared groups order.
- **Two-gravity separator is general:** The SEPARATOR lens is a general two-pole resolution (Group 9); the "pollution" application (origin vs AI-corner) is ONE named instance. The poles below are two clustering-separated regions of topics (real, not an oracle).
- **Nucleation is cross-instance:** By default: type-registry = `topics` space (REGISTRY), content store = `repo` space (ITEMS). They're from DIFFERENT spaces — non-circular (type centroids are not means of items being typed) — so the misfit is genuine.
- **Legibility translations never use machine names:** CASCADE_FLOW_META translates role descriptions to OPERATOR language (never "chain jargon" / "map-reduce" / "criteria-group"). Operator NEVER sees machine names.

---

## CROSS-REGISTRY CONNECTIONS

### Edge-Type Flows (node-type → node-type)
The `by_node_type` binding renders the node-type registry as directed type-flow edges:
- `codebase` (Text) → `ask` (context: Text)
- `ask` (answer: Text) → `llm` (prompt: Text)
- `llm` (text: Text) → `embed` (text: Text)
- `embed` (vector: Vector) → `similarity` (a/b: Vector) / `retrieve` (query: Vector)
- `retrieve` (ranked: Any) → (downstream consumption)
- `constant` (value: Any) → `gate` (value: Any) / `join` (a/b: Any) / `pair` (a/b: Any)
- Pure transforms (`titlecase`, `uppercase`, `wordcount`, `join`, `pair`) are fan-in only (their outputs are rarely consumed by downstream types).

### Projection-to-Form Alignment
- `decision` form (deep stage) → substance units captured via model projections (principles, worldview, history, common_knowledge)
- `log` form (legibility stage) → bookkeeping units, cheap pass
- `registry` form (legibility stage) → structural extraction (lineage via code projection)
- `prose` form (deep stage) → fallthrough, rich capture

### Binding Angle-From Sources
- `by_node_type`: reads `nodes/` registry (16 types)
- `by_cascade`: reads `runtime/cascades.py` (saved cascades) + `CASCADE_FLOW_META`
- `by_lens`: reads `projections/` registry (12 lenses)
- `by_nucleation`: reads `topics` space centroids (semantic pyramid, k=8) + `repo` space items (semantic nucleation, 20/80 law)
- `grouped`: reads `kinds` + declared `groups` (7 families)
- `raw`: reads live event data (data-driven, no registry)
- `semantic`: reads `topics` space vectors (1-cosine normalized) + center item selection

---

## SUMMARY: The Typed Substrate

| AREA | ENTRIES | PATTERN | VOLATILITY | SEAM |
|------|---------|---------|-----------|------|
| **Nodes** | 16 types | File-discovered + legibility registry (`_meta.py`) | 2 VOLATILE (codebase, model_of_tim) | Canvas/runtime calls; UI renders from C2/C5 |
| **Projections** | 12 lenses | File-discovered + legibility (in bindings) | Mixed (9 embed as spaces) | Capture-schema + corpus spaces + cognition_info |
| **Contracts** | C1–C8 + C-CAP + C-PLAT + 8 sub-models | Explicitly pinned in `contracts/` | (Immutable specs) | Every module composes against; this imports nothing |
| **Schemas** | 13 JSON-schemas | Canonical in-tree (vi-vision/v1/) | (Data specs) | Decision-surface + render-type contracts; fork validates |
| **Forms** | 4 shapes | File-discovered + effort-band routing | (Deterministic reads) | Corpus capture lane (effort-routing by form) |
| **Bindings** | 7 lenses + 4 legibility registries | Declared data rows + legibility metadata | (Registry reads) | Instrument rendering (angle_from, radius_from, legibility) |

---

## NOTABLE & SURPRISING (CONSOLIDATED)

1. **Self-registering file-discovered registries (nodes, projections, forms, bindings):** Adding a FILE (never a code edit) auto-registers the entry. The test suites (`tests/*_acceptance.py`) assert every discovered entry is reflected in the drift-home documentation. This is the real test of "registry-is-truth" (PART 4.3).

2. **Two legibility axes:** EVERY registry has both a DATA-driven source (the rows in the directory) and a LEGIBILITY registry ({id: {name, is}}) so the Instrument renders HUMAN meaning, never machine names. Legibility registries live in `nodes/_meta.py`, `bindings/by_*.py` (next to the binding they render), and `contracts/AGENTS.md` (constitution).

3. **VOLATILE discipline is strict:** A node that reads MUTABLE TRUTH (codebase reads disk, model_of_tim reads a file) MUST set VOLATILE=True or the memo gate will silently serve a frozen first result FOREVER. Pure transforms (uppercase, wordcount) MUST NOT set it. This is a load-bearing anti-bug.

4. **Portal is reference-resolved, not computed:** Unlike every other node, `portal` has RESOLVE='reference' — the scheduler skips firing it; the runtime reads its output LIVE from config.ref, never computed. This enables the same asset to appear in many places at once, live, never copied.

5. **Edge kinds are DECLARED, not bare wires:** C3's EDGE_KINDS (data, injection, gate, fan_in) is the first net-new registry inside the spine (Concurrent Cognition G1). Edges carry a declared kind; default is "data" so pre-v2 graphs load unchanged (schema-additive).

6. **render-NOT-judge discipline (K3):** All projection `desc` fields are RENDER instructions, never judgement. Capture lenses DESCRIBE (render the claim); judgement of truth is a LATER reduce pass. `claimed_status` is the clearest example — it renders the file's OWN epistemic claim without assessing whether the claim is true.

7. **Retrieval + embeddings form an escape hatch:** When `codebase` context exceeds the 600k-char budget, it fails LOUD with a helpful error. The escape hatch is `embed` (text → Vector) + `retrieve` (Vector + corpus → ranked). This is the COMPOSITION design for scaling beyond context-stuffing.

8. **Nucleation is semantic, the "—" is symbolic:** The `by_nucleation` binding surfaces SEMANTIC new-type candidates (unclassified content clusters outside the type-registry square). The symbolic un-filed pile for CODE-declared type-registries (events naming no registered row) is Group 10's '—' remainder (in bindings/by_lens.py).

9. **Cascade precedence is directional, has no forced acyclicity:** The `by_cascade` binding renders CASCADE → STEP precedence edges (step i → i+1). Cycles across cascades render AS cycles (nonsequential is valid — the Company's work is not always linear; parallel/recurring work exists).

10. **Decision state from MARKS, not fields:** The decision row carries NO authored state (pending/decided). STATE resolves from a `decision_take` mark on the address (registry-is-truth: the mark IS the artifact). This separates AUTHORED row data from COMPOSED state — HOLE-2-safe provenance.

11. **Explanation is LIVE, not stored:** explanation_source is an ADDRESS. The RHM resolves it live on render (not stored prose). If no source VERBATIM-contains the decision's specific content, the field STAYS ABSENT (no fabricated grounding — honest, never a lie).

12. **Subtype is the knob:** A single decision `subtype` field resolves HOW it becomes content (card_variant + explanation_policy + required_elements). ONE field → both halves of Face-2 (render + explain).

13. **Effort-routing by FORM is SHAPE-based, never content-judgment:** A form recognises FILE-SHAPE (timestamped lines, headers, link density) and routes to effort (legibility, deep, skip). Deterministic read, no AI. ~Half the corpus is bookkeeping; don't burn capture depth on logs.

14. **Fallthrough form is data-driven:** The `prose` form's `fallthrough: True` flag tells `route()` to check it LAST — no hardcoded form name. If no narrow form matches, prose claims the unit (honest catch-all).

15. **Binding poles are DATA-driven (registry-true):** The `by_separator` lens's default poles are two clustering-separated regions of the `topics` space (measured, real, distinct corpus regions — NOT oracle/hardcoded). The separation_report is the honest witness.

16. **Type-nucleation is cross-instance:** By default: type-registry = topics space, content store = repo space. Non-circular (type centroids are not means of items); misfit is genuine — "none of this fits your registry; here are the types it wants."

17. **CapabilityEntry.id construction includes flag prefixes:** For flags, the id INCLUDES the '--' prefix: id='flag/--debug', name='--debug'. This preserves the exact help-parse output and enables cap://flag/--debug → CapabilityRegistry.get('flag/--debug').

18. **PlatformEntry uses Typed Literals for strict validation:** InjectTransport, OutputProtocolFormat, DiscoverySourceFormat, DiscoverySourceType, InvocationKind are CLOSED typed Literals (F-FIX-12). A novel value → Pydantic validation FAILS LOUD at load-time, never silent unrunnable adapter.

19. **Transport invariants are DERIVED, not authored:** PlatformEntry.signal_sets.transport_invariants are populated by `derive_transport_invariants()` in `introspection/rules.py` — NEVER hand-typed (F-FIX-2, prevents silence-lies).

20. **No net-new contracts for Face-1:** Session-card (SCALAR slots) and channel-mesh/timeline (RELATIONAL edges) both validate as archetype instances with additionalProperties=false. Proof: adding a Face-1 surface = type row + archetype row, ZERO screen code.

