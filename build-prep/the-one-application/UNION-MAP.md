Confirmed: canonical SCHEMES = 16 schemes, and `channel` is NOT in the tuple (real gap). The reports citing 6/8/14 were stale or partial reads. I have my ground truth. Writing the union map now.

---

# THE UNION MAP
### One address-space, one registry-of-registries — the patchwork resolved

The nine coverage reports are **nine viewpoints on one system**, not nine systems. The same registry mechanism appears in 7 reports; the same `SCHEMES` tuple in 6; the same `vec://` vectors in 5. This map deduplicates them into one inventory, then shows the unions.

**Authoritative reconciliation (reports disagreed):**
- **Scheme count = 16**, verified against `contracts/address.py:116`: `run, cas, blob, vec, ui, code, skill, context, session, cap, board, clone, mind, exchange, file, project`. Reports citing 6 (prior-substrate/AREA-1), 8 (rendering/canvas), 14 (store) were stale/partial reads.
- `channel://` and `cluster://` are **used but NOT in SCHEMES** — verified absent from the tuple. These are real gaps, not part of the 16.
- `_CORPUS_REGISTRIES` = 6 rows; tests assert 4; `create.py:_DRIFT_HOME` missing `mind` — a three-way drift, itself a patchwork item.
- Vectors: ~5,860 active + **2,793 unreachable** `vectors.bge-backup-20260615/` (the 5,852/5,862 wobble is noise; the unreachable backup is the load-bearing fact).

---

## 1. THE PATCHWORK INVENTORY — every distinct address/registry/type/edge system, deduped, with granularity

### 1A. Address schemes — ONE grammar, declared once (`contracts/address.py:SCHEMES`)

| Scheme | Granularity | Status today | Resolver / home |
|---|---|---|---|
| `run://` | node-instance output (`run://<graph>/<node>[#port]`) | **resolvable** | `cognition.resolve_run_ref` → head→get_content |
| `cas://` | content-hash blob | **resolvable** | `store.get_content` |
| `skill://` | skill file | **resolvable** | SkillRegistry.read() |
| `context://` | context file | **resolvable** | ContextRegistry.read() |
| `session://` | session uuid (+`/step/<tuid>`) | **resolvable** | `store.load_agent_session` |
| `cap://` | capability sub-file (`kind/name`) | **resolvable** | CapabilityRegistry (singleton) |
| `board://` | board item file | **resolvable** | `cc_board.get_item` |
| `clone://` | forked session + cut (`<sid>/<cut>`) | **resolvable** | `cc_clone.get_by_address` |
| `mind://` | mind file | **resolvable** | `mind_registry().resolve` (flat — no parse_mind_address yet) |
| `blob://` | large binary | **deferred / fail-loud** | none wired |
| `vec://` | per-(item, space, emb) | **deferred in resolver** | reached via `store.put_vector`, NOT `resolve_address` (seam gap) |
| `ui://` | UI element (`<region>/<elem>[@state]`) | **deferred in resolver** | `Suite.resolve_scope` + `addresses.json` (side path) |
| `code://` | code symbol (`file-stem/symbol`) | **deferred in resolver** | `Suite.resolve_scope` + `code-symbols.json` (side path) |
| `exchange://` | conversation exchange | **register-but-defer** | recollection lane (promised) |
| `file://` | file node | **register-but-defer** | recollection crossings graph |
| `project://` | project node | **register-but-defer** | recollection containment graph |
| **`channel://`** | channel/gathering | **USED, NOT IN SCHEMES** | `session_channels` output uses it; resolver would fail-loud |
| **`cluster://`** | theme centroid (`<space>/k<K>/<label>`) | **USED, NOT IN SCHEMES** | `bridge.py` vector clustering |

**The granularity point:** granularity is **a field on the scheme row**, not a separate system. UI-element, node-instance, content-hash, item, uuid, per-(item,space,emb), capability-sub-file — these are all *one address space at different granularities*. That is what "subsumes all granularities" means.

### 1B. Registries — ONE mechanism, copied ~18–25 times

**The single pattern** (verbatim across all): `os.listdir → importlib.spec_from_file_location → fail-loud on missing FIELDS → id==filename → dict-like __getitem__/__iter__ → discover()/rediscover()`. Granularity is uniformly **one file = one row**, except where noted.

| Registry | Dir | Row schema (FIELDS) | Granularity |
|---|---|---|---|
| NodeRegistry (the original) | `nodes/` | id,inputs,outputs,config_schema,output_schema,version,kind,run | node-type file |
| RoleRegistry | `roles/` | id,spec,prompt_template,output_schema,mode_scope,draws,op,model_binding,rules,render_hint(+legacy flat) | role file |
| SkillRegistry | `skills/` | id,content,label,description | skill file |
| ContextRegistry | `contexts/` | **identical ENTRY_FIELDS to Skill** | context file |
| ProjectionRegistry | `projections/` | id,level,produced_by,embeds,field,enum,desc,stage | projection (lens) file |
| LifterRegistry | `lifters/` | id,extract(**callable**),produces,desc | lifter file |
| FormRegistry | `forms/` | id,match(**callable**),stage,policy,fallthrough,desc | form file |
| GenerationPolicyRegistry | `generation_policies/` | id,rep_penalty_ladder,diff_against_source,json_schema,temperature,budget,desc | policy file |
| RelationTypeRegistry | `relation_types/` | id,directed,inverse,near,far,desc | relation-type file |
| **board_edges/** (same class, diff dir) | `board_edges/` | **identical RELATION_TYPE schema** | board-edge file |
| MarkTypeRegistry | `mark_types/` | id,value_shape,direction,desc | mark-type file |
| ItemTypeRegistry | `item_types/` | id,initial,states,transitions,label,desc | item-type (lifecycle FSM) file |
| SourceTypeRegistry | `source_types/` | id,label,join_keys,desc | source-type file |
| AttachmentTypeRegistry | `attachment_types/` | id,label,target_kind,multi,desc | attachment-type file |
| MindRegistry | `minds/` | id,kind,role,cap,members,order{from,to,kind},desc | mind file |
| OperatorMemoryRegistry | `operator_memories/` | id,rule,why,evidence,scope,status,confirmed | rule file |
| FlowRegistry | `flows/` | id,label,description,params,proposes_only,run() | flow file |
| AiTicRegistry | `ai_tics/` | id,markers,label,desc | tic file |
| ModeDetectionRuleRegistry | `mode_detection_rules/` | id,candidate,why,priority,when(RULE_OPS AST) | rule file |
| DialRegistry | `dials/` | id,label,governs,positions,default | dial file |
| BindingRegistry | `bindings/` | id,label,angle_from,radius_from,space,poles,order_by,rung,dial | binding (equation-slot) file |
| CheckRegistry | `checks/` | id,label,description + check() callable | check file |
| VerdictPanelRegistry | `verdict_panels/` | id,label,seats,quorum | panel file |
| RoutineRegistry | `routines/` | id,prompt,cadence,goal,done_when,trigger | routine file |
| PlatformRegistry | `platforms/` | nested PlatformEntry{id,name,capabilities[]} | platform file (→ many cap rows) |

**The two declared outliers (do not force into the file-discovered count):**
- **CapabilityRegistry** — binary-discovered (claude self-report), cached module singleton, installed once at `Suite.__init__`. Granularity = `kind/name` sub-file (one platform → many cap rows).
- **UI_REGISTRY** — JSON-loaded from `design/_system/addresses.json` at Suite init, not file-discovered. Granularity = UI element.

**The hardcoded vocabularies that are NOT registries (but should be):**
- `SCHEMES` tuple — code literal in `contracts/address.py`.
- `resolve_address` dispatch — manual if/elif chain in `cognition.py`.
- `EDGE_KINDS = {data, injection, gate, fan_in}` — Python dict in `contracts/node_record.py`.
- Port-type vocabulary (`Any, Text, Vector, Number`) — bare string literals, no registry, typo-undetectable.

### 1C. Typed-edge systems — ONE law, six surfaces

| Surface | Structure | Validation home | Region |
|---|---|---|---|
| Node graph PORTS | `Number→Text` rejected at `connect()` | NodeRegistry type-graph (produces/consumes) | graph-nodes |
| relation_types | `{directed,inverse,near,far}` | RelationTypeRegistry | registries |
| board links | `[{kind,target}]` | RelationTypeRegistry@board_edges | fabric |
| minds composition order | `[{from,to,kind,as}]` | **no registry** (gap) | runtime |
| Provenance.inputs | `[address]` lineage DAG | walked by `FsStore.lineage()` | address-spine |
| source_types join_keys | shared correlation fields | SourceTypeRegistry | registries |
| DNA substrate file-edges | `source→target` + `referenced_by` | `substrate-assemble.py`, 1,050 edges | prior-substrate |

---

## 2. THE UNION — one address space + one registry-of-registries

### Spine 1 — ONE address grammar

`SCHEMES` is already the one space (16 schemes, one resolver). Three structural moves complete it:

1. **Promote `SCHEMES` from code-literal → data registry.** One row per scheme: `{scheme, status:"resolvable"|"deferred", resolver_fn, parse_fn, granularity, desc}`. The prose-comment status tracking in `address.py` (which scheme resolves vs raises) becomes a machine-readable field.
2. **`resolve_address` becomes a table lookup, not an if/elif chain.** `SCHEME_HANDLERS[scheme]` — registering a new scheme is adding a row, not editing `cognition.py`. `territory._RESOLVABLE` (the parallel drift-prone tuple) **derives from `SCHEMES.keys()`** and disappears as an independent list.
3. **All sub-address grammar lives in `address.py`.** `parse_session_address` and `parse_clone_address` already there; add `parse_vec_address` (the `#space=#emb=` fragment grammar currently buried in `fs_store.space_address`) and `parse_mind_address`. Add `channel://` and `cluster://` as rows (close the two used-but-unregistered gaps).

**Granularity subsumed:** because granularity is a field on the scheme row, every grain — UI element (`ui://`), node instance (`run://`), content hash (`cas://`), board item (`board://`), session (`session://`), vector (`vec://`), capability (`cap://`), file/project (`file://`/`project://`) — is one address space queried one way.

### Spine 2 — ONE registry-of-registries

1. **One base class.** `FileDiscoveredRegistry(dir, FIELDS, DataClass, id_attr)` collapses the ~25 copies. Each registry becomes one declaration: `RoleRegistry = FileDiscoveredRegistry("roles/", ROLE_FIELDS, Role)`. The codebase already names this the **"FUTURE NEWMOD reuse pass"** in `projections.py`.
2. **Extend `_CORPUS_REGISTRIES` to enumerate ALL registries** (today: 6 of ~25), each row carrying a `create_capable` flag and a `granularity` field. This becomes the literal **registry-of-registries** — one enumerable table, addressable by kind name, served through `cognition_info`. Fixes the 6/4/missing-mind three-way drift in one place.
3. **Merge the structural duplicates:** Skill≡Context (identical `ENTRY_FIELDS`, differ only by scheme) → one class parameterized by scheme. board_edges≡relation_types (identical RELATION_TYPE class) → one `relation_types/` dir with a `scope:["board","corpus"]` field.
4. **The two outliers stay declared as outliers:** CapabilityRegistry (cached, binary-discovered) and UI_REGISTRY (JSON-loaded) are not file-discovered — name them, don't force the count.

### Spine 3 — ONE typed-edge law

`dna/types.json` already states it: **"a valid typed edge is a VERB with an EQUAL OPPOSITE; direction is which end you read from."** The node graph (`Number→Text` rejected), `relation_types` (`directed/inverse`), board links (`{kind,target}`), minds order (`{from,to,kind}` — needs a registry), Provenance lineage, source_types join_keys, and DNA's 1,050 file-edges are **seven surfaces of this one law.** Express it once (typed-edge contract with equal-opposite + 4 axes: containment/temporal/kind/context from `dna/types.json`); each surface consumes it. The DNA substrate engine (`substrate-assemble.py`) already computes the back-link (`referenced_by`) — that is the equal-opposite, built.

---

## 3. STORAGE PICTURE — today, and where it moves

**Today: filesystem-first (ext4/WSL, never `/mnt/c`), single root `~/company/.data/store`.** Four shapes:

- **Shape A — per-noun JSON dirs** (one file/record, atomic tmp→fsync→os.replace→fsync-parent): `objects/` (CAS), `refs/`, `ref_history/`, `meta/` (provenance), `memo/`, `graphs/`, `vectors/`, `sessions/`, `agent_sessions/`. Live counts: 18,727 objects, 18,388 refs, 72 graphs, 13 agent-sessions.
- **Shape B — append-only JSONL leaves** (full-file-scan to read): `events.jsonl` (6,449 lines), `chat.jsonl`, `annotations.jsonl`, `findings.jsonl`, `marks.jsonl`, `dispositions.jsonl`, `pins.jsonl`, `agent_sessions/mail.jsonl`.
- **Shape C — CAS blobs** under `objects/`, blake2b-keyed, immutable.
- **Shape D — vectors** under `vectors/<space>/`, JSON with explicit `space/emb/dim/model/vector` fields (Supabase-portable by construction). 5,860 active (pplx 2560-dim) + 2,793 **unreachable** BGE-backup (1024-dim, no API path).

**Registries-as-storage:** every `<registry>/*.py` file **IS** a row. Git is the migration system. No DB for registry rows.

**The swap seam — and its gap:** `contracts/resolver.py` Protocol = **10 methods**; FsStore = **70 methods**; Suite calls FsStore as a concrete type, not through the Protocol. The documented seam covers ~14% of the surface. **A Supabase backend implementing only the Protocol would be immediately incomplete.**

**Where it moves (Supabase-later, AGENTS.md):**
- Extend the Protocol to all 70 method signatures; type `Suite` to `Resolver` not `FsStore`.
- Shape-B JSONL → SQL tables with `WHERE field=X` (kills full-file-scan; `events.jsonl` at 6,449 lines is already the I/O argument).
- Shape-A dirs → upsert tables keyed by id.
- Shape-C CAS → Supabase Storage or `content` table.
- Shape-D vectors → pgvector, one column per (space,emb), dims from `FsStore.layer_dims()`.
- flock → Postgres advisory locks; tmp+rename → Postgres ACID.

**Must absorb before migration:** two bypass namespaces inside the store root that skip FsStore entirely — `cascades.json` (`_ActionRegistry`) and `agent_sessions/channels.jsonl` (`session_channels`); plus the inline annotation-scan duplication in `generate_mockup.py`; plus the unreachable BGE-backup (ingest as `emb="bge-m3"` or archive out of root).

---

## 4. WHAT RENDERS THROUGH THE ONE INSTRUMENT — and how registries feed it

**The instrument = the universal projection (the wheel/lattice).** Engine: `runtime/projection.py` (`build_projection`, `project()` pure fn). Surfaces: `surface/app/` (React: `wheel/{Wheel,Nucleation,Separator,Disclosure}`). Same engine serves canvas `/api/projection` and MCP `instrument.project()` — fulfilling Tim's law *"everything that can be done through the UI must be done through the MCP doors."*

**Registries ARE the instrument's configuration (no hardcoded layout):**
- **BindingRegistry** (`bindings/`, 9 rows) fills the seed-equation slots: `angle_from`, `radius_from`, `space`, poles, order_by. The active binding row determines every sector — `x=2π/n`, `θ=kind/type sector`, `r=time-from-NOW log-scaled | semantic cosine | separator lean`, `depth=address nesting`. No hardcoded sectors.
- **ProjectionRegistry** (`projections/`, 10–11 rows) — embeddable lenses become `vec://<item>#space=<projection>` spaces the wheel queries.
- **NodeRegistry** → `/api/object_info` → ONE generic `ai-node` shape (zero per-type frontend code; `NODE_STATES` render via CSS custom-property tokens, zero hardcoded colors).
- **render_hint** on role rows (`{shape,lane}`), **mark_types.direction** (`surface`/`subtract`) — rendering intent declared as data.

**Drill-in:** wheel point tap → `projection:select {address, source, record, space}` window event → DNA `GalleryMount.tsx` renders the drilled unit. The address from the instrument resolves through the one resolver.

**The legibility gap (the root one):** the operator-surface design names six self-describing facets (address/thing, lens, element, control, destination, journey/state) but **labels are currently hardcoded strings in React**. The union: a **legibility type** — registry rows carrying self-description fields; the instrument reads them at render time (meaning-in-the-data, "every addressable thing describes itself everywhere" — Tim, 2026-06-17). This collapses the hardcoded-string problem and the legibility gap simultaneously.

**Frontend duplications to absorb:** two `address.ts` (canvas + surface) → one shared lib; dual `ui://` registry (static `addresses.json` vs runtime `/api/ui_info`, no diff gate) → static is authoritative, runtime derives, FORM-gate diffs them; `NODE_STATES` render tokens disconnected from `dna/tokens.json` → draw from the DNA semantic token tree; `company/design/` is a one-way read-copy from Windows-side canonical (silent-overwrite risk).

---

## 5. PATCHWORK / DUPLICATION TO ABSORB — clustered

**Cluster A — the ~25× copied registry mechanism.** Every `os.listdir→importlib→fail-loud→id==stem` loop is a fresh copy across `registry.py, roles.py, skills.py(×2), projections.py, lifters.py, forms.py, …`. → one `FileDiscoveredRegistry` base. (Cluster 1B above.)

**Cluster B — hardcoded vocabularies that should be registries.** `SCHEMES` literal; `resolve_address` if/elif chain; port-types as bare strings; `_safe()` address→filename transform (lives in `fs_store`, every stored filename depends on it silently — belongs in `address.py` as a declared contract); `EDGE_KINDS` dict; `CONTENT_KINDS` defined twice (`registry.py` + `suite.py`).

**Cluster C — parallel duplicate systems (same noun, two structures).**
- **Two channel registries:** `cc_channels` named-channels (member-ID = bare handle) vs `session_channels` (member-ID = bare session UUID) — incompatible, no join key, `channel://` not in SCHEMES.
- **Two mail logs:** `.data/channels/_mail.jsonl` vs `agent_sessions/mail.jsonl` — no unified inbox.
- **Two recall/vector indexes:** `session_recall` `.data/recall-index` vs corpus FsStore vector layer — same embedder, parallel indexes over overlapping content.
- **Triple materialize-at-point:** `sessions.py at=`, `cc_clone clone_at`, `session_recall "self"` — one primitive (`session_pointintime.parse_point`), three call sites re-implementing.
- **Triple capability inventory:** `capabilities` + `cognition_info` + `introspection.capability()`.
- Skill≡Context; board_edges≡relation_types; two `address.ts`; dual `ui://` registry.

**Cluster D — built-but-unwired (complete, tested, connected to nothing).** Lifters (no capture path calls `extract()`); Forms (no ingest path calls `route()`); `model_routing.resolve_model` (Phase 1 written, nothing calls it — the 3 seams `roles.resolve_binding`/`capability_providers`/`pick_ollama_model_for_context` still scattered); `up_translate('finding')` at `suite.py:5828` (RHM finding-explainer, left waiting "that's a later lane"); the three coherence gates (reachability/suite_health/registry-vs-live emit ad-hoc, none persisted/addressed/dispositioned).

**Cluster E — the disposition system exists twice in embryo.** `_ORPHAN_ROUTES` (hardcoded dict) + `governance.POLICY` (AUTO/SURFACE/CONFIRM/LOCKED). Every coherence area reached the same instruction: *unify these two, don't invent a third.*

**Cluster F — the storage swap-seam gap.** Resolver Protocol 10 vs FsStore 70; two bypass namespaces; inline annotation duplication.

---

## 6. THE SEAMS — act-layer + corpus(semantic) + substrate(structural) as ONE

**The keystone loop (substrate + triggers + routing + self-build collapse to one mechanism):**

```
ghost node detected   →   trigger fires   →   cc_launch node runs   →   writeback   →   re-census
(substrate, structural)   (act-layer)         (build, model-routed)     (corpus)        (substrate)
```

- A **trigger** = `event-kind → when-predicate → action`. All three halves **already exist**: event taxonomy in `activation.py:ACTIVATION_CONTEXTS`, when-predicate in `rules.py:RULE_OPS`, action/routing in `rules.py:DESTINATION_KINDS + route()`. **Only the binding is missing** — a file-discovered `trigger/` registry + driver (clone `mode_detection_rules.py`, the strongest template).
- **THE ONE CRUX (the single hinge across triggers/forms/lifters):** their recognisers (`forms.match`, `lifters.extract`, `triggers.when`) are **Python callables** → blocked from the Tier-B authoring gate by the callable-guard (`suite.py:9886`). **Fix: recognisers-as-data via `RULE_OPS` data-AST** (prior art: `mode_detection_rules`). This one move makes forms + lifters + triggers ALL `_CORPUS_REGISTRIES` Tier-B rows, agent-authorable through one gate. It is Tim's theorem applied to the recogniser layer: everything declared, in registries, no hardcoding.
- **Self-trigger guard:** a reply `file_item` re-emits `board.filed` → runaway spawn loop; exclude `responds_to`-edged items in the `when` (mirrors `OPERATOR_ACTIVITY_KINDS` exclusion).
- **Structured-output gap:** `session_supervisor._turn_done:1086` does NOT read `ev["structured_output"]` — a CC launched with `--json-schema` has its output dropped. 3-line fix across `session_supervisor.py`, `cc_clone.py`, `routine_runner.py`. Blocks the entire `cc_launch` structured path.

**Corpus (semantic) and substrate (structural) are two lenses on the SAME addressed units:**
- **Substrate (structural):** the address-registry — DNA already built a first cut (`counterpart/design/substrate/`: 621 addresses, 22 types, 1,050 typed edges, 14 ghost nodes, census over 224 files). `engine/substrate-assemble.py` is the reference engine.
- **Corpus (semantic):** the same units embedded into `vec://<source>#space=<projection>` spaces, queried by cosine + jina rerank.
- **The union:** ONE engine, per-project instances. DNA's design repo becomes one project-instance the **Company's canonical engine** covers (do NOT build the Company's substrate on DNA's design-specific instance — generalize it). The `registry-generation` chain (auto-populate `ui://` from mockups via swarm — all 11 criteria 🔴) and DNA's census are **two passes of one pipeline at two granularities** (UI-element vs file). **★ Must reconcile:** is registry-generation ancestor or live? If the engine generalizes, the cascade becomes one configuration of it, not a separate chain.

**Coherence as one lens over the same substrate:** the three gates become the first three rows of a `finding-type` registry (add-a-detector = drop a file). Findings ride the **existing** event log (`kind="coherence.finding"`, address-stamped — no new store, no `coherence://` scheme). Dispositions ride the **existing** pin-overlay (last-wins, from the Inbox). Burn-down = read-time rollup (`run_stats` pattern). `CoherenceView` is a sibling of `CognitionView`, both reflecting-never-owns over the same SSE. The coherence substrate and the address substrate **are the same substrate, pointed at different aspects.**

---

### The one sentence
Every region is a viewpoint on **one addressed graph of self-describing registry rows**: one address grammar (16 schemes, granularity-as-field, table-dispatched), one registry-of-registries (one discovery base, one enumerable `_CORPUS_REGISTRIES`), one typed-edge law (verb-with-equal-opposite), rendered through one instrument (the wheel, configured by binding/projection rows), persisted behind one Resolver seam (fs today → Supabase later), acted on by one recogniser language (`RULE_OPS` data-AST) that makes triggers, forms, lifters, and the ghost-node self-build loop **the same mechanism** — corpus (semantic) and substrate (structural) being two lenses on the same units.

**Key file anchors:** `contracts/address.py:116` (SCHEMES), `contracts/resolver.py` (10-method seam), `runtime/suite.py:_CORPUS_REGISTRIES` (registry-of-registries), `runtime/projection.py` (instrument engine), `store/fs_store.py` (70-method FsStore, `_safe()`, `space_address()`), `rules.py:RULE_OPS` (the recogniser-as-data language), `counterpart/design/substrate/` (the proven substrate cut), `dna/types.json` (the typed-edge law stated).