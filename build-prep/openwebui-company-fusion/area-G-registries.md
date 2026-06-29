---
type: map
area: small-registries
coverage:
  files_read: all target directories
  files_total: 130+
  last_read: 2026-06-28
status: confirmed
register: descriptive
---

# Area G: Small Registry/Type Directories — Complete Inventory

This is a COMPLETE, exhaustive map of the 15 small registry-is-truth content directories in `/home/tim/company/`. These are declarative-data registries where **add-a-row = drop a file** (zero code edit); the ONE file-discovered registry mechanism reused across all.

---

## Index: Directory + Purpose + Entry Count

| Directory | Kind | Entries | Mechanism | Governs |
|-----------|------|---------|-----------|---------|
| **mark_types/** | mark-type vocabulary | 13 | file-discovered, `MARK_TYPE` dict per file | M1/M4/P1 cognition findings |
| **item_types/** | board item-type lifecycle | 11 | file-discovered, `ITEM_TYPE` dict + state-machines per file | board item vocabulary |
| **relation_types/** | corpus semantic edge-kinds | 6 | file-discovered, `RELATION_TYPE` dict per file | L3 inversion-finder edges |
| **axes/** | resolver coordinate dimensions | 8 | file-discovered, `AXIS` dict per file | resolver projection space |
| **flows/** | production-line chains | 9 | file-discovered, `FLOW` dict + `run()` function per file | GC1 executable flows |
| **generation_policies/** | LLM generation regimes | 6 | file-discovered, `GENERATION_POLICY` dict per file | O2/P1 generation sampling |
| **mode_detection_rules/** | presence-mode detection rules | 3 | file-discovered, `MODE_DETECTION_RULE` dict per file | activation mode detection |
| **attachment_types/** | board-item attachment kinds | 7 | file-discovered, `ATTACHMENT_TYPE` dict per file | channel attachment vocabulary |
| **platforms/** | external platform wiring | 4 | file-discovered, `PLATFORM` dict per file (pure data; _wiring.py bootstrap) | Mirror-Registry adapters |
| **board_edges/** | board item relation-edges | 13 | file-discovered, `RELATION_TYPE` dict per file (reuses RelationTypeRegistry) | board structural edges |
| **ai_tics/** | AI-fingerprint vocabulary | 7 | file-discovered, `AI_TIC` dict per file | M4 denoising catalogue |
| **decisions/** | pending operator decisions | 25 | file-discovered, `DECISION` dict per file (NOT state-stored, schema validated) | decision surface |
| **introspection/** | Mirror-Registry engine + adapters | 11 | module-level code + adapter classes (NOT row-discovered) | Level-1 platform introspection |
| **ui-contract/** | UI transport & service contract | 6 docs + 4 subdirs | markdown specification + coverage/journey/resource/tool-spec subdirs | surface contract |
| **(item_types duplicate)** | board item-type lifecycle | 11 | (same as row 3) | (same as row 3) |

**Key facts:**
- **Total small-registry entries: 128 rows** (excluding introspection module + ui-contract spec)
- **Unified mechanism:** all discovered via `runtime/registry.py` family + parallel discovery classes (ItemTypeRegistry, MarkTypeRegistry, etc.)
- **Pure-data discipline:** all row files are imports + dict declarations, no def/class (introspection is exception: it's the Level-1 engine)
- **Validation:** each registry's builder gate (_build_*) fails loud on malformed entries

---

## Directory Details

### mark_types/ — Mark-Type Vocabulary (M1/M4/P1)

**What it is:** The declared VOCABULARY of dispositions a coherence mark-pass writes over corpus units. A **mark** = the coherence-finding disposition (target / mark_type / value / confidence / source_pass / evidence / status). Mark-passes append findings with mark-types DRAWN FROM this registry.

**Self-registration pattern:** File stem MUST equal `MARK_TYPE["id"]`. Module-level `MARK_TYPE` dict with schema: `{id, value_shape, direction, desc}`. Required: `id` (==filename), `value_shape` (score/label/bool/span/free), `direction` (surface=positive | subtract=denoising, default surface). Validated fail-loud at `MarkTypeRegistry` discovery.

**Entries (13 total):**
- **Analysis types:** `ai_fingerprint` (label, subtract), `gold_likelihood` (score, surface), `contradiction` (span, surface), `built_twice` (claim, surface), `overlap` (claim, surface), `strain` (score, surface)
- **Interaction types:** `comment` (free, surface — operator direction), `reaction` (label, surface — operator stamp), `favour` (score, surface — operator favour), `decision_take` (free, surface — operator choice on decision), `decision_retract` (free, surface — operator undo), `decision_update` (free, surface — RHM proposal), `decision_update_accept` (free, surface — operator apply)

**Where it's consumed:** `subtractive()` (inversion set), `as_records()` (cognition_info). Read-only registry — mark-passes NEVER resolve, they APPEND findings.

**Discovered by:** `runtime/mark_types.py:MarkTypeRegistry` (mirrors ProjectionRegistry/RoleRegistry).

**Seam:** To author from agent face, a future `create_mark_type` (declarative-direct) reuses THIS registry's `_build_mark_type` gate; long-term home `runtime/authoring.py` + `Suite.create_mark_type` (flagged UNBUILT).

**Notable:** `decision_update` + `decision_update_accept` are L5 (2026-06-22 Tim-approved); they prove the RHM-proposed refinement + operator-apply pattern on a live card without state mutation.

**Entry reference:** `/home/tim/company/mark_types/AGENTS.md:11-88`

---

### item_types/ — Board Item-Type Lifecycle (11)

**What it is:** The file-discovered ITEM-TYPE registry for the Company NOTICEBOARD (`runtime/cc_board.py`). A row = one KIND of board record WITH its own lifecycle (legal state-machine). An item's `type` REFERENCEs into this registry; its legal state moves are a PROPERTY of its type's row.

**Self-registration pattern:** File stem MUST equal `ITEM_TYPE["id"]`. Module-level `ITEM_TYPE` dict with schema: `{id, initial, states, transitions, label, desc}`. Required: `id` (==filename), `initial` (∈ states), `states` (non-empty list), `transitions` ({from_state: [allowed_to_states]}). All keys/targets MUST ∈ states. Validated fail-loud at ItemTypeRegistry discovery.

**Entries (11 total):**
- `request` — an ask to add/change. open → picked-up → building → done / declined
- `issue` — bug/wrong-behaviour. open → triaged → fixing → resolved / wontfix
- `tip` — discovered better way. posted ⇄ archived
- `guide` — how-to / living doc. living ⇄ archived
- `idea` — seed/thought; promotable. captured → discussing → promoted / dropped
- `signal` — fabric SIGNAL a lane consumes to ACT (decision.decided the first instance). raised → consumed / superseded
- `artefact` — self-contained rich HTML page. draft → active → archived (reversible)
- `block` — a discrete work unit. open → in-progress → done / blocked
- `document` — ordered markdown blocks. draft → published → archived
- `message` — a conversational message. posted → (no transitions, append-only on channels)
- `note` — an operator note. captured → (append-only)

**Where it's consumed:** `cc_board.reset_registries()` (discovery), `file_item` (type validation), transition logic (validates move against type's declared lifecycle).

**Discovered by:** `runtime/item_types.py:ItemTypeRegistry`.

**Notable:** `signal` is a shared-tree / floor-clean half of the operator-cycle's resume wire (cross-session-via-shared-tree). Latest `decision_take` mark on a decision address composes the decided state; signals fire when that decision resolves.

**Entry reference:** `/home/tim/company/item_types/AGENTS.md:11-38`

---

### relation_types/ — Corpus Semantic Edge-Kinds (L3, 6)

**What it is:** The declared KIND of typed/directional edge between two corpus units. `find_relations` (L3 inversion-finder) composes/labels its discovered relations with types FROM this registry. Cross-level query: `find_relations(item, near_space, far_space)` = inversion-finder (near/far projection set-intersection).

**Self-registration pattern:** File stem MUST equal `RELATION_TYPE["id"]` (python identifier). Module-level `RELATION_TYPE` dict with schema: `{id, directed, inverse, near, far, label, desc}`. Required: `id` (==filename), `directed` (bool — A→B vs A↔B). Optional: `inverse` (the reciprocal label), `near`/`far` (projection space names for inversion), `label` (human-readable, can be hyphenated), `desc`. Validated fail-loud at RelationTypeRegistry discovery.

**Entries (6 total):**
- `principle_beneath` (label: principle-beneath) — DIRECTED · near=principles. A expresses principle beneath B (principle under instance)
- `fragment_of` (label: fragment-of) — DIRECTED · inverse: has_fragment · near=topics. A is fragment of whole B
- `contradicts` — DIRECTED · near/far=principles. A contradicts B (tension surfaced for review)
- `sibling` — SYMMETRIC (directed: False) · near=topics. A and B are siblings
- `depends_on` — DIRECTED · inverse: unlocks. Agent-authored (2026-06). This unit requires target (gate; inverse: target unlocks this)
- `precedes` — DIRECTED. Agent-authored (2026-06). This unit comes before target in declared order (stage/step)

**Where it's consumed:** `directed()` / `symmetric()` branches (find_relations), `as_records()` (cognition_info). Read-only — relations DESCRIBE, judgment is a later reduce pass.

**Discovered by:** `runtime/relation_types.py:RelationTypeRegistry`.

**Seam:** `find_relations` labelling edges with types is a SEPARATE coordinated wiring pass (flagged UNBUILT).

**Notable:** `depends_on` and `precedes` are agent-authored (created via declarative-direct face), proving the create-mark-type / create-relation-type seam will work.

**Entry reference:** `/home/tim/company/relation_types/AGENTS.md:11-76`

---

### axes/ — Resolver Coordinate Dimensions (8)

**What it is:** The file-discovered VOCABULARY of the resolver's COORDINATE dimensions. Each `<id>.py` declares an orthogonal dimension the resolver uses to project visuals. **ADD AN AXIS = DROP A FILE** (zero engine code; the coordinate-space self-extends — Tim's "axes ARE registries").

**Self-registration pattern:** File stem MUST equal `AXIS["id"]` (namespace key). Module-level `AXIS` dict with schema: `{id, namespace, fields, value_source, desc}`. Required: `id` (==filename), `namespace` (the coordinate key). Optional: `fields` ({sub_field: continuous|discrete}), `value_source` (live/ref/pending), `desc`. Validated at `AxisRegistry` discovery.

**Entries (8 total):**
- `device` — device context (width, height, orientation)
- `viewer` — viewer context (role, presence)
- `mode` — presence mode (off, suggest, auto, focused)
- `register` — registration (pending, flagged, live)
- `type` — item type (request, issue, tip, guide, idea, signal, etc.)
- `state` — item lifecycle state (open, draft, active, archived, etc.)
- `resolution` — coarse/medium/fine GRAIN + depth (dragnet & MRL multi-scale rollup) — **DISTINCT from design axis**
- `design` — design-language context (line/opacity/colour_role/shape — LOCKED, 4 dimensions driven by visual-identity decisions)

**Where it's consumed:** The resolver (runtime/resolver.py) is list-AGNOSTIC; this registry is the coordinate VOCABULARY, not a switch. Projection coordinate-computation. Host read `as_records()`.

**Discovered by:** `runtime/axis_registry.py:AxisRegistry`.

**Notable:** The SPINE-TIE: design's sub-field MEANINGS are SET by visual-identity DECISIONS (line-language/opacity-meaning/core-shape/figure-gold-value); the axis resolves visuals against this vocabulary. One invariant visual, never variants; the design-coordinate selects the treatment. NAMING COLLISION CAUGHT (design.py line 6): this DISTINCT from resolution axis (same informal name, different concept).

**Entry reference:** `/home/tim/company/axes/AGENTS.md:1-20`

---

### flows/ — Production-Line Chains (GC1, 9)

**What it is:** The file-discovered FLOW registry (GC1). A flow is a REGISTERED, multi-primitive PRODUCTION LINE — committed code composing engine primitives into a proven, re-runnable chain. Invocable through the company MCP by name with declared params.

**Self-registration pattern:** File stem MUST equal `FLOW["id"]`. Module-level `FLOW` dict with schema: `{id, label, description, params, proposes_only}` + a module-level `run(**params)` function. Required: `id` (==filename), `label`, `description`, `params` ({name: {desc, default}}). ENFORCED: `proposes_only: True` (flows compute, propose artifacts, surface cards; never resolve/approve/dispatch). Validated fail-loud at FlowRegistry discovery.

**Entries (9 total):**
- `registry_generation` — mockup→dossier chain (GC2): GROUND → MAP → cluster-dedupe → floor+jury CONFIRM; resume-safe batches
- `transcript_mine` — ③/G23: transcripts → distilled exchange extracts, embedded space='history' (durable memory); exchange-granular idempotent
- `pattern_cluster` — ③/G13: self-study REDUCE — tally + embed-cluster every pattern_tag; feeds G13-PATTERN-REPORT
- `repo_ingest` — ①/G21: repo-exocortex ingest — walk → repo_digest MAP → capture+embed into space='repo' keyed code://; hash-aware incremental
- `drift_radar` — ②: built-twice/overlap/doc-drift sweep over repo space → near-pair clusters → judge_drift confirm → surface-direction marks
- `floor_walk` — standing cross-lane sweep: stranded files · unmounted components · stale decisions · phantom corpus sources (deterministic, report+one-card)
- `dragnet_extract` — corpus dragnet (bulk extract of identified items/relations from input directory)
- `ts_backfill` — timestamp backfill (populate creation timestamps on historical records)
- `cc_registry_refresh` — Mirror-Registry LANE-REFRESH: compare live claude version → diff → surface ONE inbox item (F-FIX-4 fail-closed)

**Where it's consumed:** Invoked through company MCP (`flows` tool: list|describe|run). Read-only registry — flows PROPOSE ONLY.

**Discovered by:** `runtime/flows.py:FlowRegistry`.

**Seam:** Flow authoring is the file-drop path; MCP create tool would reuse the gate but is flagged UNBUILT.

**Notable:** `cc_registry_refresh` is the REFRESH verb (Level-2 platform system); it demonstrates fail-closed write order (stamp write is post-approval only, proposes-only discipline).

**Entry reference:** `/home/tim/company/flows/AGENTS.md:1-58`

---

### generation_policies/ — LLM Generation Regimes (O2/P1, 6)

**What it is:** The file-discovered GENERATION-POLICY registry (O2). A generation-policy is the declared, per-content GENERATION REGIME a `run_role` call uses — **NOT static knobs in code**. Proves "NOTHING static": the repetition_penalty regime is a registry ROW with a **ladder as DATA**.

**Self-registration pattern:** File stem MUST equal `GENERATION_POLICY["id"]`. Module-level `GENERATION_POLICY` dict with schema: `{id, rep_penalty_ladder, diff_against_source, json_schema, temperature, budget, desc}`. Required: `id` (==filename), `rep_penalty_ladder` (non-empty ascending list of floats — default → escalate-on-length → exhausted=fail-loud). `diff_against_source` (bool — never-silently-lossy guard). Optional: `json_schema`, `temperature`, `budget`, `desc`. Validated fail-loud at GenerationPolicyRegistry discovery.

**Entries (6 total):**
- `capture_default` — corpus-capture regime: ladder [1.1, 1.2], diff_against_source: True, json_schema: True, temp: 0.0 (greedy, the loop-trigger surface this ladder cures). **THE entry that proves "NOTHING static"**
- `prose_default` — free-prose (reduce/consult): ladder [1.1] (single rung — prose not grammar-constrained loop surface), diff_against_source: False, temp: 0.3
- `policy.risk-grounding` — authorize-subtype explanation: ladder [1.1], diff: False, json_schema: False, temp: 0.0 (greedy, careful + precise on security)
- `policy.technical-recommendation` — technical recommendation: ladder [1.1], diff: False, json_schema: False, temp: 0.3
- `policy.theorem-grounding` — theorem-grounding explanation: ladder [1.1], diff: False, json_schema: False, temp: 0.0
- `policy.trade-off-neutral` — trade-off decision explanation: ladder [1.1], diff: False, json_schema: False, temp: 0.3

**Where it's consumed:** `policy_for(id)`, `next_rep_penalty()` (run_role read), `as_records()` (cognition_info).

**Discovered by:** `runtime/generation_policies.py:GenerationPolicyRegistry`.

**Notable:** The 4 policy.* entries (2026-06-21) demonstrate that the ladder need not be multi-rung and flags vary per regime. All are tied to decision-subtypes' explanation_policy contract. **FLOOR TOKEN**: no `.resolve(` method in this module (floor-safe if enrolled in COG_SOURCES).

**Entry reference:** `/home/tim/company/generation_policies/AGENTS.md:1-77`

---

### mode_detection_rules/ — Presence-Mode Detection Rules (Group I, 3)

**What it is:** The file-discovered MODE-DETECTION-RULE registry (Concurrent Cognition Group I). A mode-detection-rule maps a SIGNAL CONDITION → a candidate presence mode. The detector (`runtime/activation.py:detect_mode_candidate`) reads the live `activity_signal()` snapshot, walks DISCOVERED rules in PRIORITY order (first-match-wins), produces a candidate mode.

**Self-registration pattern:** File stem MUST equal `MODE_DETECTION_RULE["id"]`. Module-level `MODE_DETECTION_RULE` dict with schema: `{id, candidate, why, when, priority}` **all required**. `id` (==filename), `candidate` (mode id, validated ∈ suite.MODES at DETECT), `why` (one-line legible rationale, surfaces with suggestion), `when` (condition data-AST using `rules.RULE_OPS` grammar — NOT lambda/eval), `priority` (int; lower fires first, first-match-wins). Validated fail-loud at ModeDetectionRuleRegistry discovery.

**Entries (3 total):**
- `background` (priority 10) — long-idle: when idle_seconds >= 900, propose background (low-noise). Fires first.
- `focus` (priority 20) — sustained-activity-and-clear-inbox: when idle_seconds < 90 AND inbox == 0, propose focus (protect deep work). Guard idle-seconds not-None FIRST.
- `listening` (priority 30) — work-is-piling-up: when inbox > 0, propose listening (be present/conversational). Fallback signal.

**Where it's consumed:** `Suite.autodetect_mode` toggle (the detector PRODUCES candidate, toggle owns posture — suggest surfaces, auto switches).

**Discovered by:** `runtime/activation.py` (instantiated in Suite.__init__ as `self.mode_detection_rule_registry`).

**Notable:** Uses the SAME `rules.RULE_OPS` data-AST grammar as G3 cognition rules (boolean/comparison/arithmetic/field-access/membership) — ONE predicate language, reuse-don't-parallel. **ORDER IS BEARING** (first-match-wins); detection driven by declared `priority`, never listdir order (the ordering trap).

**Entry reference:** `/home/tim/company/mode_detection_rules/AGENTS.md:1-94`

---

### attachment_types/ — Board-Item Attachment Kinds (7)

**What it is:** The declared KINDS of content a board item can ATTACH. Attachment is HOW a board item carries richness — links to sessions / docs / dragnet-run records / image artifacts / recall snapshots.

**Self-registration pattern:** File stem MUST equal `ATTACHMENT_TYPE["id"]`. Module-level `ATTACHMENT_TYPE` dict with schema: `{id, label, target_kind, multi, desc}`. Required: `id` (==filename). Optional: `label`, `target_kind` (address/url/reference), `multi` (bool — can item carry multiple?), `desc`. Discovered by `runtime/attachment_types.py:AttachmentTypeRegistry`.

**Entries (7 total):**
- `board_items` — attachment to other board items (references)
- `cloning` — cloning metadata/source
- `docs` — attached markdown/document content
- `dragnet_runs` — tracked dragnet RUN records (run://corpus/.../dragnet/<id>); the run telemetry (started/ended/duration/throughput/coverage)
- `images` — attached image artifacts (image://<channel>/<path>); operator-attached phone images render inline under comments
- `recall` — recall snapshot attachments (session state snapshots)
- `sessions` — attached session-state / session-link records

**Where it's consumed:** `cc_board` board item link validation, channel attachment inventory.

**Discovered by:** `runtime/attachment_types.py:AttachmentTypeRegistry`.

**Notable:** `dragnet_runs` is a tracked RUN RECORD address (not just a link) — the introspective record of the dragnet process; channels accumulate run-history, queryable.

**Entry reference:** `/home/tim/company/attachment_types/` (no AGENTS.md; discovered by mechanism)

---

### platforms/ — External Platform Wiring (Mirror-Registry Level 2, 4)

**What it is:** The **Level-2 platform table as DATA** — one `platforms/<id>.py` per external platform the Company mirrors. Each declares a module-level `PLATFORM = {...}` dict (validates against `contracts/platform_entry.py:PlatformEntry`). `PlatformRegistry` (`introspection/platforms.py`) discovers these files. A platform is ONE ROW; the engine (`introspection/`, Level 1) never knows its identity.

**Self-registration pattern:** File stem matches `PLATFORM["id"]` with `_`↔`-` normalization (Python module naming). Module-level `PLATFORM` dict (validated via `PlatformEntry.model_validate(dict)`). **PURE DATA DISCIPLINE**: imports + dicts, NO def/class. The one binding a Pydantic model cannot hold (head_builder thunk — F-FIX-2) lives in **`platforms/_wiring.py`** (a `_`-prefixed bootstrap the registry's discovery skips). Fail-loud at discovery: a novel `discovery_sources[].type` / `inject_transport` value → Pydantic RAISES on invalid Literal.

**Entries (4 total):**
- `claude_code` (claude-code) — Claude Code (Commander.js CLI). Instance #1: pure-data row + SPAWN_FLAG_BODY_KEY_MAP + head_builder binding in _wiring.py. Consumed by engine + closed adapters + 5 rules + session supervisor.
- `gh_cli` (gh-cli) — GitHub CLI (`gh`, Cobra-family tool). Instance #2 (2026-06-14, the generalization-proof): PURE-DATA row reusing EXISTING cli-help adapter, ZERO engine edits. Proves a 2nd known-kind platform is almost-free. Registered-only (no live consumer yet).
- `codex_cli` (codex-cli) — OpenAI Codex CLI (`codex`, RUST/clap tool). Instance #3 (2026-06-28, a THIRD tool family): PURE-DATA row, unchanged machinery, 24 flags classified. **First platform with LIVE fabric consumer** (`ops/ledger_interpret_codex.py`). Adapter gap: clap prints descriptions on next line (future clap-options parse_rule).
- `_wiring.py` — bootstrap module (NOT discovered as a row). Binds head_builder thunks (F-FIX-2), supplies live SPAWN_FLAG_BODY_KEY_MAP. Imported by `runtime/suite.py` + crosscheck test; `introspection/` never imports it (cycle-free PG-D6).

**Where it's consumed:** Mirror-Registry engine (introspection/), session supervisor (platform-posture reading), downstream consumers (flows/cc_registry_refresh, ops/hooks/registry_freshness).

**Discovered by:** `introspection/platforms.py:PlatformRegistry` (importlib registry-family pattern).

**Notable:** LOAD-BEARING discipline (F-FIX-10): Level-1 code (introspection/) carries ZERO platform-name literals. Acceptance test greps for `claude`, `dangerously`, `--mcp-config` in Level-1 files and **FAILS on hit**. Legitimate home: `platforms/` (Level 2). Converse: a platform declaring unbuilt adapter type → `MissingAdapterError` naming missing class (§8.3 boundary, C-GENPROOF).

**Entry reference:** `/home/tim/company/platforms/AGENTS.md:1-95`

---

### board_edges/ — Board Item Relation-Edges (13)

**What it is:** The file-discovered EDGE-KIND registry for Company NOTICEBOARD items (`runtime/cc_board.py`) — the typed cross-registry links a board item carries (`links: [{kind, target}]`). A row is a RELATION-TYPE (same row shape as relation_types/). Discovered by REUSING `runtime/relation_types.py:RelationTypeRegistry` VERBATIM — **ONE mechanism, SEPARATE vocabulary dir** (like roles/ + projections/ are separate dirs on one mechanism).

**Self-registration pattern:** File stem MUST equal `RELATION_TYPE["id"]`. Module-level `RELATION_TYPE` dict with schema: `{id, directed, inverse, near, far, label, desc}` (identical to relation_types/). Required: `id` (==filename), `directed` (bool). Optional: `inverse`, `near`, `far`, `label`, `desc`. Validated fail-loud by `runtime/relation_types.py:_build_relation_type`.

**Entries (13 total):**
- `authored_by` (authored-by) — DIRECTED · item → session://<id>. Item authored by this session (cross-registry provenance)
- `attached_to` (attached-to) — DIRECTED · item → channel/Space. Item attached to a channel
- `sourced_from` (sourced-from) — DIRECTED · item → source-type row. Item's origin source
- `promoted_from` (promoted-from) — DIRECTED · inverse: promoted_to · item → board://<id>. Promoted from another (e.g. request ← idea)
- `part_of` (part-of) — DIRECTED. Item is part of a larger structure
- `reply_to` (reply-to) — DIRECTED. Item is a reply to another
- `references` — DIRECTED. Item references another (link, citation)
- `blocked_by` (blocked-by) — DIRECTED. Item blocked by another
- `composes_with` (composes-with) — work units that compose together
- `commented_on` — DIRECTED. Someone commented on this item
- `attachment` — DIRECTED. Item carries attached artifact (image/file); inverse: attached_to
- `refutes` — DIRECTED. Item refutes/contradicts another
- `same_law` (same-law) — structural symmetry (items under same governance)

**Where it's consumed:** `cc_board._edges_reg()` (a RelationTypeRegistry instance over THIS dir), `file_item` (validates each link's `kind` fail-loud).

**Discovered by:** `runtime/cc_board.py:_edges_reg()` (RelationTypeRegistry instantiated over board_edges/ dir).

**Why SEPARATE from relation_types/:** decision 2026-06-15 (lead + fork + advisor). Board edges are STRUCTURAL/PROVENANCE (item→session/channel/source), distinct from relation_types/ CORPUS-SEMANTIC edges (fragment-of/sibling) that `find_relations` inversion-finder reads with near/far. **One grammar satisfied by ONE MECHANISM** (RelationTypeRegistry class), NOT one dir. Keeps board edges uncoupled from cognition-engine corpus vocabulary. Unify deliberately into relation_types/ only when the Heart's cross-registry resolution lands and a consumer genuinely traverses one unified relation graph.

**Entry reference:** `/home/tim/company/board_edges/AGENTS.md:1-35`

---

### ai_tics/ — AI-Fingerprint Vocabulary (M4, 7)

**What it is:** The file-discovered AI-TIC registry (M4). An **AI-tic** is a declared, CATALOGUED generic-AI fingerprint — a recurring tell of machine-generated (not Tim-meaning) content. The fingerprint pass (M4, the inversion) matches the coined-vocab projection against THIS registry → `ai-fingerprint` marks (direction `subtract`): generic+recurring = a tic to SUBTRACT (denoising = surfacing, opposite direction).

**Self-registration pattern:** File stem MUST equal `AI_TIC["id"]`. Module-level `AI_TIC` dict with schema: `{id, markers, label, desc}`. Required: `id` (==filename), `markers` (non-empty list of non-empty strings — the cues the fingerprint pass matches). Optional: `label`, `desc`. Validated fail-loud at AiTicRegistry discovery.

**Entries (7 total):**
- `framework_imposition` (framework-imposition) — imposing generic framework/terminology over content's native shape (Tim actively rejects standard frameworks)
- `versioning` — v2/round-N/dated copies instead of updating canonical in place (named frustration: no-versioning)
- `false_finality` — declaring done/fixed/complete without proof (named frustration: verify-before-claiming)
- `silent_fallback` — routing around a problem / swallowing error instead of failing loud (named frustration: no-silent-failures)
- `agent_arch` — defaulting to agent-architecture where work is content/dataflow (named distinction: not-agent-architecture-by-default)
- `closure_form` — closure-form writing (summarized/finished, expansion-ratio<1) that kills institutional memory (named frustration: open-future-writing)
- `mvp` (MVP) — MVP/impact-prioritization/scope-cutting (named frustration: no-MVP, all-or-nothing)

**Where it's consumed:** `all_markers()` (flat cue set), `as_records()` (cognition_info + fingerprint pass catalogue).

**Discovered by:** `runtime/ai_tics.py:AiTicRegistry`.

**Notable:** All 7 are seeded from Tim's NAMED frustrations — the generic-AI tells to subtract. Catalogue is EXTENSIBLE — as Tim discovers new tics, add a file.

**Entry reference:** `/home/tim/company/ai_tics/AGENTS.md:1-72`

---

### decisions/ — Pending Operator Decisions (25)

**What it is:** The file-discovered DECISION registry. Each `<id>.py` declares ONE real pending decision the company surfaces to its operator (Tim) or settles in-fabric. The decision surface resolves it into a card he can read and decide in. **NOT state-stored** (state resolves from latest `decision_take` mark on the address).

**Self-registration pattern:** File stem MUST equal `DECISION["id"]`. Module-level `DECISION` dict with schema: `{id, meaning, options, scope, subtype, explanation_source, legibility}`. Required: `id` (==filename — addressable as decision://<scope>/<id>; fail-loud if mismatched), `meaning` (operator altitude), `options` (2+ choices, each {label, implication, recommended?}), `scope` (global). **MANDATORY IN PRACTICE**: `subtype` (discriminator for owner/card_variant/required_elements; NO FALLBACK; omit it and decision VANISHES). Optional: `explanation_source` (traceable provenance pointer to real source), `legibility` ({name, is, why} — how it reads in operator surface). Validated fail-loud at DecisionRegistry discovery.

**Entries (25 total):**
- **Design-language decisions:** `adopt-claude-design`, `card-refine-posture`, `card-visuals-source`, `core-shape`, `dimension-meaning`, `figure-gold-value`, `line-language`, `lock-card-look`, `opacity-meaning`, `visual-fidelity`, `steer-visual-direction`, `control-density`
- **Structural/system decisions:** `build-consent-posture`, `cluster-identity`, `connector-full-access`, `event-streams`, `file-identity`, `form-taxonomy`, `merge-sa-authorize`, `real-v-symbol`, `reconnect-tools`, `rerank-loadout`, `substrate-home`, `substrate-spine`, `cube-3d`

**Where it's consumed:** Decision surface (`contracts/decision_registry.compose_state`), RHM explanation/refinement ground.

**Discovered by:** `runtime/decision_registry.py:DecisionRegistry`.

**Notable:** **HOLE-2 GUARD**: `explanation_source` must be a POINTER traced through to REAL content (verbatim-containing the decision's specific content), **NEVER a re-stated prose claim** of the origin. Wrong-origin pointer is WORSE than none. **SUBTYPE IS MANDATORY**: on 2026-06-21, 10 of 24 rows were authored without subtype and were invisible on the LIVE operator surface (including `substrate-home`, frame-first keystone). `decision.schema.json` does not yet force subtype (future work), so YOU must set it. Pick from `decision_subtypes/` vocabulary (authorize/trade-off/theorem-fork/cross-lane); derive new subtype if genuinely novel (add `decision_subtypes/<id>.py` row).

**Entry reference:** `/home/tim/company/decisions/AGENTS.md:1-74`

---

### introspection/ — Mirror-Registry Engine (Level 1, 11 files)

**What it is:** The **platform-agnostic Mirror-Registry engine** (Level 1) + the **instance-#1 CLI adapters**. The engine operates ONE four-verb circuit — **DISCOVER → CLASSIFY → PROJECT → REFRESH** — over a `PlatformEntry` (contracts/platform_entry.py) and two registries (Platform Registry + Capability Registry).

**NOTE:** This is NOT a row-discovered registry (unlike the 13 above). It's the **Level-1 engine code** — module-level real code + adapter classes. Listed here for complete coverage.

**Structure (11 files):**
- `__init__.py` — module marker
- `discover.py` — DISCOVER verb: resolve executable, run declared DiscoverySources through closed adapters, collect CapabilityEntry rows. Fail-loud on unbuilt adapter or floor-guard parse breach.
- `engine.py` — core four-verb dispatch: DISCOVER → CLASSIFY → PROJECT → REFRESH. Platform-agnostic (zero platform-name literals; acceptance test greps and FAILS on hit).
- `platforms.py` — PlatformRegistry (importlib registry-family pattern, mirrors runtime/roles.py). Discovers `platforms/<id>.py` rows via module import + `PLATFORM` dict extraction.
- `registry.py` — CapabilityRegistry singleton + `set_capability_registry()` + lazy `capability_registry()`. **DELIBERATE divergence** from sibling registries (fresh-discover-on-each-call factories) — binary discovery is EXPENSIVE; singleton caches deferred-discovered capabilities. LANE-CAP-WIRE built 2026-06-13.
- `rules.py` — CLASSIFY verb: the five closed rules R1–R5 at priority R1 > R2 > R3 > R5 > R4. Posture is DERIVED (not opinion): `(posture, posture_rule, axis)` is reproducible from `(flag_name, signal_sets)`.
- `adapters/__init__.py` — DISCOVERERS + INVOKERS registration maps (single registration point). CliHelpDiscoverer, StreamInitDiscoverer, VersionProbe, SubprocessAdapter are BUILT. REST/GraphQL/MCP/library/grpc/sdk are NAMED-but-UNBUILT (gap-surface; platform selecting one FAILS LOUD naming missing class).
- `adapters/cli_help.py` — CliHelpDiscoverer: parse Commander `--help` option-rows. Reused by instances #2 (gh-cli, Cobra) + #3 (codex-cli, clap) with ZERO edits.
- `adapters/stream_init.py` — StreamInitDiscoverer: running-session init self-declare. LEAD-only live verify.
- `adapters/version_probe.py` — VersionProbe: read running version from a VersionSource.
- `adapters/subprocess_invoke.py` — SubprocessAdapter: run-invocation primitive (find_executable: env → PATH → known_paths, **fail loud** if absent).

**Where it's consumed:** Mirror-Registry system (platform registry loading, capability discovery, session supervisor wiring, downstream consumers registry-driven).

**The lift (F-FIX-10, load-bearing):** introspection/ carries **ZERO platform-name literals** — no `claude`, no `dangerously`, no `--mcp-config`. Every platform-specific string arrives as DATA on a PlatformEntry/SignalSets. Tests grep for banned strings and **FAIL on any hit** (acceptance test: `tests/introspection_acceptance.py`).

**C-GENPROOF (proven by use with instances #2 + #3):** a 2nd known-kind platform is almost-free (single data row, zero engine edits). A platform declaring an unbuilt adapter type → MissingAdapterError naming missing class (fail-loud boundary).

**Entry reference:** `/home/tim/company/introspection/AGENTS.md:1-245`

---

### ui-contract/ — UI Transport & Service Contract (specification directory, NOT a row registry)

**What it is:** The **UI/surface contract specification** — markdown documentation + subdirectories for coverage/journey/resource/tool specifications. NOT a row-discovered registry (unlike the 13 above). This is the **formal contract** the surface (canvas/app, Open WebUI) reads to render board items, decisions, etc.

**Contents (6 docs + 4 subdirs):**
- `README.md` — overview + entry points
- `CONTRACT-FORMAT.md` (64KB) — formal service contract format (the binding spec)
- `CONVENTIONS.md` (18KB) — surface convention rules
- `COVERAGE.md` (28KB) — feature coverage checklist
- `TASKS.md` (16KB) — task/user-journey definitions
- `TRANSPORTS.md` (16KB) — transport mechanism specifications (HTTP/SSE/etc.)
- `atlas/` — subdir (indexed map of visual patterns)
- `coverage/` — subdir (coverage artifacts)
- `journeys/` — subdir (user-journey specifications)
- `resources/` — subdir (resource definitions)
- `tools/` — subdir (tool-spec subdirs)

**Entry reference:** `/home/tim/company/ui-contract/README.md`

---

## Notable / Surprising Facts

### Notable Patterns

1. **Unified mechanism, separate vocabularies:** All 13 small registries + board_edges reuse the SAME discovery pattern (file-per-entry, module-level dict, fail-loud validation). **Registry-is-truth**: add-a-row = drop a file, zero code edit elsewhere.

2. **Validation is loud:** Malformed entries FAIL LOUD at discovery; a non-entry/`_`-prefixed file is skipped (never silent acceptance or inference).

3. **The file-stem discipline:** `MARK_TYPE["id"]`, `ITEM_TYPE["id"]`, etc. MUST equal the file stem; fail-loud if mismatched (addressable-by-file discipline).

4. **Ordering matters only in mode_detection_rules:** Most registries are unordered dicts. mode_detection_rules is the EXCEPTION: `priority` field drives first-match-wins detection order (never listdir order — the ordering trap).

5. **Pure-data discipline:** All row files are imports + dict declarations, NO def/class. Exception: introspection/ is the Level-1 engine (real code). platforms/_wiring.py is a bootstrap binding module (Level-2 only, not discovered as a row).

6. **Seams, not built:** Many registries list FUTURE authoring contracts (create_mark_type, create_relation_type, create_generation_policy, create_ai_tic, create_mode_detection_rule). These are flagged UNBUILT — the wiring is a SEPARATE coordinated pass, not built in the registry lane.

7. **Cross-registry edges:** board_edges uses the SAME RelationTypeRegistry class as relation_types/ (mechanism reuse), but in a SEPARATE dir (data separation). Deliberate: keeps board edges uncoupled from cognition-engine corpus vocabulary.

### Surprising / Gap Facts

1. **Decisions have NO state column:** `decision.decided` state resolves from the LATEST `decision_take` mark on the address (append-only, audit-preserving). A `decision_retract` appended AFTER a take (newer ts) returns it to pending; a later take re-decides. **NO state field on the DECISION row itself** (pure registry-is-truth: deleted 2026-06-20, "the whole resolution chain hangs on subtype").

2. **SUBTYPE IS MANDATORY but unenforced:** `decision.schema.json` does NOT validate subtype presence. On 2026-06-21, 10 of 24 rows were authored WITHOUT subtype and were **INVISIBLE on the LIVE operator surface**, including `substrate-home` (frame-first keystone). The whole resolution chain hangs on it: `decision.subtype` → `decision_subtypes/<subtype>.py` → owner/card_variant/required_elements. **No subtype = no owner = silently excluded from Tim's queue.** Future: schema will force it.

3. **Platforms are pure data ONLY:** The head_builder thunk (F-FIX-2) moved OUT of the row into `platforms/_wiring.py` (2026-06-14). This proves row-purity (no def/class) is load-bearing: `_wiring.py` imports `runtime` (→ cycle-free PG-D6); `introspection/` never imports it.

4. **Mirror-Registry is instance-proven at #3:** The generalization-proof (C-GENPROOF) holds through THREE tool families: Commander.js (claude-code), Cobra (gh-cli), clap (codex-cli). Instance #3 (codex-cli, 2026-06-28) is the FIRST with a LIVE fabric consumer (`ops/ledger_interpret_codex.py`). **Adapter gap:** clap prints descriptions on next line (future clap-options parse_rule).

5. **Mode detection uses cognition-engine grammar:** `mode_detection_rules.when` is a `rules.RULE_OPS` data-AST (the EXACT grammar G3 cognition rules use), NOT lambda/eval. Proves the ONE predicate language law (reuse-don't-parallel).

6. **Flows are PROPOSE-ONLY by law:** All 9 flows are enforced `proposes_only: True` at discovery. They compute, propose artifacts, surface cards; never resolve/approve/dispatch. The floor's executable-code half.

7. **ai_tics are catalogued frustrations:** All 7 are seeded from Tim's NAMED frustrations — not invented by agents. Tim says "I hate X" → add an ai_tic. The catalogue is EXTENSIBLE (Tim-driven).

8. **attachment_types differs from relation edges:** Attachment is HOW a board item carries richness (links to sessions/docs/dragnet-runs/images/recalls). Distinct from board_edges (structural cross-registry links). Not a row-discovered registry in the classic sense (lighter mechanism).

### Open Seams (Flagged Unbuilt)

- `create_mark_type` — declarative-direct authoring face (long-term home: `runtime/authoring.py` + `Suite.create_mark_type`)
- `create_relation_type` — same (flagged UNBUILT)
- `create_generation_policy` — same
- `create_ai_tic` — same
- `create_mode_detection_rule` — same (MCP create tool; needs coordination with MCP face)
- `create_attachment_type` — same
- LANE-CAP-WIRE full live-verify — C-WIRE-1/2/3 queued (live-binary `discover()`, real `cap://` resolution from running server)
- LANE-REFRESH full stamp+cache persist — post-approval write governance action

---

## Summary Index (One-Liner Per Directory)

| Directory | What | Entries | Mechanism |
|-----------|------|---------|-----------|
| mark_types/ | Coherence mark vocabulary (M1/M4) | 13 | file-per-entry, `MARK_TYPE` dict |
| item_types/ | Board item lifecycles (state-machines) | 11 | file-per-entry, `ITEM_TYPE` dict + transitions |
| relation_types/ | Corpus semantic edge-kinds (L3) | 6 | file-per-entry, `RELATION_TYPE` dict |
| axes/ | Resolver coordinate dimensions | 8 | file-per-entry, `AXIS` dict |
| flows/ | Production-line chains (GC1) | 9 | file-per-entry, `FLOW` dict + `run()` function |
| generation_policies/ | LLM generation regimes (O2) | 6 | file-per-entry, `GENERATION_POLICY` dict (ladder as DATA) |
| mode_detection_rules/ | Presence-mode detection rules (Group I) | 3 | file-per-entry, `MODE_DETECTION_RULE` dict + priority order |
| attachment_types/ | Board-item attachment kinds | 7 | file-per-entry, `ATTACHMENT_TYPE` dict |
| platforms/ | External platform wiring (Mirror-Registry L2) | 4 | file-per-entry, `PLATFORM` dict (pure data) + _wiring.py bootstrap |
| board_edges/ | Board item relation-edges (structural) | 13 | file-per-entry, `RELATION_TYPE` dict (reuses RelationTypeRegistry) |
| ai_tics/ | AI-fingerprint catalogue (M4) | 7 | file-per-entry, `AI_TIC` dict (Tim's named frustrations) |
| decisions/ | Pending operator decisions | 25 | file-per-entry, `DECISION` dict (state resolves from marks, NO state column) |
| introspection/ | Mirror-Registry engine (Level 1) | 11 files | module-level engine code + closed adapters (NOT row-discovered) |
| ui-contract/ | UI/surface contract spec | 6 docs + 4 subdirs | markdown + subdirs (specification, NOT row-registry) |

**TOTAL ENTRIES: 128 rows** (excluding introspection engine + ui-contract specification)

